"""Generic subprocess JSONL streamer with robust error handling.

Features:
- Streams JSON objects line-by-line from stdout
- Concurrently drains stderr into a tail buffer
- Enforces deadline/timeout and kills process trees safely
- Truncates oversized lines per policy or errors
"""

from __future__ import annotations

import asyncio
import json
import os
import signal
import sys
from asyncio.subprocess import PIPE
from collections import deque
from collections.abc import AsyncIterator, Awaitable
from typing import Any, cast

import psutil

from .errors import (
    CliExitError,
    CliNotFoundError,
    CliTimeoutError,
    InnerLoopError,
)

_TAIL_PREVIEW_LIMIT = 2048


def _decode(raw: bytes, *, first_line: bool) -> str:
    return raw.decode(
        "utf-8-sig" if first_line else "utf-8", errors="ignore"
    ).strip()


def _append_tail(tail: deque[str], label: str, s: str) -> None:
    tail.append(f"[{label}] {s[:_TAIL_PREVIEW_LIMIT]}")


def _deadline(timeout: float | None) -> float | None:
    loop = asyncio.get_running_loop()
    return None if timeout is None else loop.time() + timeout


def _remaining(deadline: float | None) -> float | None:
    if deadline is None:
        return None
    loop = asyncio.get_running_loop()
    return max(0.0, deadline - loop.time())


async def _psutil_wait(
    procs: list[psutil.Process], timeout: float
) -> tuple[list[Any], list[Any]]:
    def _wait() -> tuple[list[Any], list[Any]]:
        return cast(
            tuple[list[Any], list[Any]],
            psutil.wait_procs(procs, timeout=timeout),
        )

    return cast(tuple[list[Any], list[Any]], await asyncio.to_thread(_wait))


async def _taskkill_fallback(pid: int, timeout: float) -> None:
    try:
        tk = await asyncio.create_subprocess_exec(
            "taskkill",
            "/PID",
            str(pid),
            "/T",
            "/F",
            stdout=PIPE,
            stderr=PIPE,
        )
        try:
            await asyncio.wait_for(tk.wait(), timeout=timeout)
        except Exception:
            pass
    except Exception:
        pass


async def _kill_process_tree(
    root_pid: int,
    *,
    deadline: float | None,
    grace: float = 0.5,
    windows_taskkill: bool = True,
    try_process_group_last: bool = True,
) -> None:
    try:
        root = psutil.Process(root_pid)
    except psutil.Error:
        return

    def _descendants() -> list[psutil.Process]:
        try:
            children = root.children(recursive=True)
            return [root] + children
        except psutil.Error:
            return [root]

    procs = _descendants()
    for p in procs:
        try:
            p.terminate()
        except psutil.Error:
            pass

    rem = _remaining(deadline)
    t1 = (
        0.0
        if rem is not None and rem <= 0
        else min(grace, rem) if rem is not None else grace
    )
    if t1 > 0:
        try:
            _gone, alive = await _psutil_wait(procs, timeout=t1)
        except psutil.Error:
            alive = [p for p in procs if p.is_running()]
    else:
        alive = [p for p in procs if p.is_running()]

    if alive:
        for p in alive:
            try:
                p.kill()
            except psutil.Error:
                pass
        rem = _remaining(deadline)
        t2 = 0.5 if rem is None else min(0.5, rem)
        if t2 > 0:
            try:
                await _psutil_wait(alive, timeout=t2)
            except psutil.Error:
                pass

    try:
        still = root.is_running()
    except psutil.Error:
        still = False

    if still:
        if sys.platform != "win32" and try_process_group_last:
            try:
                pgid = os.getpgid(root_pid)
                os.killpg(pgid, signal.SIGTERM)
            except OSError:
                pass
            rem = _remaining(deadline)
            g = 0.2 if rem is None else min(0.2, rem)
            if g > 0:
                try:
                    await asyncio.sleep(g)
                except Exception:
                    pass
            try:
                pgid = os.getpgid(root_pid)
                os.killpg(pgid, signal.SIGKILL)
            except OSError:
                pass
        elif sys.platform == "win32" and windows_taskkill:  # pragma: no cover
            rem = _remaining(deadline)
            budget = 1.0 if rem is None else min(1.0, rem)
            if budget > 0:
                await _taskkill_fallback(root_pid, timeout=budget)


async def stream_jsonl_process(
    cmd: list[str],
    *,
    env: dict[str, str] | None = None,
    cwd: str | None = None,
    timeout: float | None = None,
    max_line_bytes: int | None = None,
    chunk_size: int = 8192,
    tail_lines: int = 50,
    windows_taskkill: bool = True,
    grace_terminate: float = 0.5,
    oversize_policy: str = "truncate",
    stdin_data: str | None = None,
) -> AsyncIterator[dict[str, Any]]:
    """Run a subprocess and yield parsed JSON objects from JSONL stdout.

    Args:
        stdin_data: Optional string to write to process stdin.
    """
    if max_line_bytes is None:
        max_line_bytes = 16 * 1024 * 1024
    assert max_line_bytes is not None

    try:
        creationflags = 0
        if (
            sys.platform == "win32"
        ):  # pragma: no cover - exercised on Windows CI
            import subprocess  # local import to avoid overhead on non-Windows

            creationflags = getattr(subprocess, "CREATE_NEW_PROCESS_GROUP", 0)
        proc = await asyncio.create_subprocess_exec(
            *cmd,
            stdin=PIPE if stdin_data is not None else None,
            stdout=PIPE,
            stderr=PIPE,
            env=env,
            cwd=cwd,
            start_new_session=(os.name != "nt"),
            creationflags=creationflags,
        )
    except FileNotFoundError as e:
        raise CliNotFoundError("Command not found") from e

    # Write stdin if provided and close
    if stdin_data is not None and proc.stdin is not None:
        try:
            proc.stdin.write(stdin_data.encode("utf-8"))
            await proc.stdin.drain()
            proc.stdin.close()
            await proc.stdin.wait_closed()
        except Exception:
            # Best effort; process may have exited early
            pass

    assert proc.stdout is not None
    stdout = proc.stdout
    stderr_tail: deque[str] = deque(maxlen=tail_lines)
    tail: deque[str] = deque(maxlen=tail_lines)

    async def _drain_stderr() -> None:
        if proc.stderr is None:
            return
        first = True
        while True:
            chunk = await proc.stderr.readline()
            if not chunk:
                break
            text = _decode(chunk, first_line=first)
            first = False
            _append_tail(stderr_tail, "stderr", text)

    stderr_task = asyncio.create_task(_drain_stderr())
    dl = _deadline(timeout)
    buffer = bytearray()
    first_line = True

    async def _wait_until(
        awaitable: Awaitable[Any], deadline: float | None
    ) -> Any:
        if deadline is None:
            return await awaitable
        loop = asyncio.get_running_loop()
        rem = max(0.0, deadline - loop.time())
        return await asyncio.wait_for(awaitable, timeout=rem)

    try:
        while True:
            while True:
                nl = buffer.find(b"\n")
                if nl == -1:
                    break
                raw = bytes(buffer[: nl + 1])
                del buffer[: nl + 1]

                if len(raw) > max_line_bytes:
                    if oversize_policy == "error":
                        await _kill_process_tree(
                            proc.pid,
                            deadline=dl,
                            grace=grace_terminate,
                            windows_taskkill=windows_taskkill,
                        )
                        raise InnerLoopError(
                            f"JSONL line exceeds maximum {max_line_bytes} bytes"
                        )
                    text = _decode(raw[:max_line_bytes], first_line=first_line)
                    first_line = False
                    _append_tail(tail, f"truncated:{max_line_bytes}", text)
                    continue

                text = _decode(raw, first_line=first_line)
                first_line = False
                if not text:
                    continue
                try:
                    yield json.loads(text)
                except json.JSONDecodeError:
                    _append_tail(tail, "non-json", text)

            try:
                chunk = await _wait_until(stdout.read(chunk_size), dl)
            except asyncio.TimeoutError as e:
                await _kill_process_tree(
                    proc.pid,
                    deadline=dl,
                    grace=grace_terminate,
                    windows_taskkill=windows_taskkill,
                )
                try:
                    await _wait_until(
                        proc.wait(), asyncio.get_running_loop().time() + 1.0
                    )
                except Exception:
                    pass
                raise CliTimeoutError(
                    f"CLI operation exceeded timeout of {timeout}s",
                    timeout=float(timeout or 0),
                ) from e

            if not chunk:
                if buffer:
                    raw = bytes(buffer)
                    buffer.clear()
                    if len(raw) > max_line_bytes:
                        if oversize_policy == "error":
                            await _kill_process_tree(
                                proc.pid,
                                deadline=dl,
                                grace=grace_terminate,
                                windows_taskkill=windows_taskkill,
                            )
                            raise InnerLoopError(
                                f"JSONL line exceeds maximum {max_line_bytes} bytes"
                            )
                        text = _decode(
                            raw[:max_line_bytes], first_line=first_line
                        )
                        first_line = False
                        _append_tail(tail, f"truncated:{max_line_bytes}", text)
                        break
                    text = _decode(raw, first_line=first_line)
                    first_line = False
                    if text:
                        try:
                            yield json.loads(text)
                        except json.JSONDecodeError:
                            _append_tail(tail, "non-json", text)
                break
            buffer.extend(chunk)

        try:
            rc = await _wait_until(proc.wait(), dl)
        except asyncio.TimeoutError as e:
            await _kill_process_tree(
                proc.pid,
                deadline=dl,
                grace=grace_terminate,
                windows_taskkill=windows_taskkill,
            )
            from contextlib import suppress

            with suppress(Exception):
                await _wait_until(
                    proc.wait(), asyncio.get_running_loop().time() + 1.0
                )
            raise CliTimeoutError(
                f"CLI operation exceeded timeout of {timeout}s",
                timeout=float(timeout or 0),
            ) from e

        if rc != 0:
            stderr_tail_text = (
                "\n".join(stderr_tail)
                if stderr_tail
                else ("\n".join(tail) if tail else "(no error output)")
            )
            raise CliExitError(
                f"Process exited with code {rc}.",
                return_code=rc,
                stderr=stderr_tail_text[:1024],
            )
    finally:
        from contextlib import suppress

        with suppress(Exception):
            stderr_task.cancel()
        if getattr(proc, "returncode", None) is None:
            with suppress(Exception):
                await _kill_process_tree(
                    proc.pid,
                    deadline=(
                        asyncio.get_running_loop().time() + 1.0
                        if dl is None
                        else dl
                    ),
                    grace=grace_terminate,
                    windows_taskkill=windows_taskkill,
                )
                await _wait_until(
                    proc.wait(), asyncio.get_running_loop().time() + 1.0
                )


__all__ = ["stream_jsonl_process"]
