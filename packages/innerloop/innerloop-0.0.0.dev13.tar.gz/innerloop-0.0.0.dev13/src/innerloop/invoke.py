from __future__ import annotations

import asyncio
import logging
import os
import tempfile
import time
from collections.abc import AsyncIterator
from typing import Any, TypeVar, cast

from pydantic import BaseModel, ValidationError

from .config import InvokeConfig
from .events import ErrorEvent, OpenCodeEvent, TimeInfo
from .events import parse_event as _parse_event
from .helper import unix_ms
from .mcp import LocalMcpServer, McpServer, RemoteMcpServer
from .output import assemble_output
from .permissions import Permission
from .providers import ProviderConfig
from .request import Request
from .response import Response
from .structured import _extract_and_parse_json, build_structured_prompt
from .usage import compute_usage

logger = logging.getLogger(__name__)

P = TypeVar("P", bound=BaseModel)


def write_config_file(cfg: InvokeConfig) -> str:
    """Write config JSON to a secure temp file and return its path."""
    data = cfg.to_json().encode("utf-8")
    fd, path = tempfile.mkstemp(prefix="opencode-config-", suffix=".json")
    try:
        try:
            os.fchmod(fd, 0o600)
        except Exception:
            try:
                os.chmod(path, 0o600)
            except Exception:
                pass
        with os.fdopen(fd, "wb") as f:
            f.write(data)
            f.flush()
            os.fsync(f.fileno())
        return path
    except Exception:
        try:
            os.close(fd)
        except Exception:
            pass
        raise


def build_env_with_config_path(
    config_path: str, base: dict[str, str] | None = None
) -> dict[str, str]:
    """Return env dict with OPENCODE_CONFIG pointing to the temp file."""
    env = dict(base or os.environ)
    env["OPENCODE_CONFIG"] = config_path
    env.setdefault("OPENCODE_EXPERIMENTAL_MCP", "1")
    return env


def build_opencode_cmd(model: str, session_id: str | None = None) -> list[str]:
    """Build opencode command without prompt (prompt passed via stdin)."""
    cmd = ["opencode", "run", "--format", "json", "--model", model]
    if session_id:
        cmd += ["--session", session_id]
    return cmd


async def run_opencode_jsonl(
    prompt: str,
    *,
    model: str,
    permission: Permission,
    providers: dict[str, ProviderConfig] | None = None,
    mcp_servers: list[McpServer] | dict[str, McpServer] | None = None,
    session_id: str | None = None,
    cwd: str | None = None,
    timeout: float | None = None,
    chunk_size: int = 8192,
) -> AsyncIterator[dict[str, Any]]:
    """
    Pure functional runner: build config -> write file -> run -> JSONL stream.
    Yields parsed JSON objects from the CLI, one per line.
    Minimal guardrails here; callers can layer policies as needed.

    The prompt is passed via stdin to avoid argv length limits and issues
    with special characters like YAML frontmatter (---).
    """
    typed_mcp = cast(
        dict[str, LocalMcpServer | RemoteMcpServer] | None, mcp_servers
    )
    # Note: Request.providers (plural, user-facing) maps to InvokeConfig.provider
    # (singular) because the CLI schema uses a single top-level "provider" object.
    # Keep naming as-is to avoid API churn.
    cfg = InvokeConfig(
        permission=permission, provider=providers, mcp=typed_mcp
    )
    config_path = write_config_file(cfg)
    env = build_env_with_config_path(config_path)
    cmd = build_opencode_cmd(model, session_id=session_id)

    # Delegate to the generic process streamer
    from .proc import stream_jsonl_process as _stream

    try:
        async for obj in _stream(
            cmd,
            env=env,
            cwd=cwd,
            timeout=timeout,
            chunk_size=chunk_size,
            stdin_data=prompt,
        ):
            yield obj
    finally:
        # Best‑effort cleanup of the temp config file in all code paths
        try:
            os.unlink(config_path)
        except Exception:
            pass


async def async_invoke(
    request: Request,
    *,
    resume: str | None = None,
) -> Response[Any]:
    """Run a single CLI invocation and return a typed Response.

    - resume: optional session id to continue
    Structured parsing and retries live in `async_invoke_structured`/`Loop.run`
    and are not applied here.
    """
    # Always stream and assemble raw text here; structured parsing and retries
    # are handled by async_invoke_structured.
    effective_session = resume or request.session
    if effective_session == "":
        effective_session = None
    prompt = request.prompt

    # Auto-inject permission statement if permissions are non-default
    from .capabilities import _build_permission_statement

    perm_statement = _build_permission_statement(request.permission)
    if perm_statement:
        prompt = f"{prompt}\n\n{perm_statement}"

    # Stream events
    events: list[OpenCodeEvent] = []
    response_session: str | None = effective_session

    wall_start = unix_ms()
    async for raw in run_opencode_jsonl(
        prompt,
        model=request.model,
        permission=request.permission,
        providers=request.providers,
        mcp_servers=cast(
            dict[str, McpServer] | list[McpServer] | None, request.mcp
        ),
        session_id=effective_session,
        cwd=request.workdir,
        timeout=request.timeout,
    ):
        ev = _parse_event(raw)
        ev.seq = len(events) + 1
        events.append(ev)
        if response_session is None:
            try:
                response_session = ev.sessionID or None
            except Exception:
                pass
    wall_end = unix_ms()

    # Build output
    text = assemble_output(events, reset_on_tool=True, fallback_to_tool=True)
    out: Any = text

    resp: Response[Any] = Response(
        session_id=response_session or "",
        input=request.prompt,
        output=out,
        events=events,
        time=TimeInfo(start=wall_start, end=wall_end),
    )

    # Populate usage once based on events
    resp.usage = compute_usage(events)
    return resp


def invoke(
    request: Request,
    *,
    resume: str | None = None,
) -> Response[Any]:
    """Synchronous wrapper around async_invoke."""
    return asyncio.run(async_invoke(request, resume=resume))


__all__ = [
    # helpers
    "InvokeConfig",
    "write_config_file",
    "build_env_with_config_path",
    "build_opencode_cmd",
    "run_opencode_jsonl",
    "Request",
    "async_invoke",
    "invoke",
]


def _validate_output_path(path: str, workdir: str) -> str:
    """Validate output path is under workdir. Hard fail if not.

    Args:
        path: Output file path (absolute or relative)
        workdir: Working directory (must be absolute)

    Returns:
        Absolute path to output file

    Raises:
        ValueError: If path is not under workdir
    """
    abs_path = os.path.abspath(path) if not os.path.isabs(path) else path
    abs_workdir = os.path.abspath(workdir)

    # Ensure workdir ends with separator for proper prefix check
    if not abs_workdir.endswith(os.sep):
        abs_workdir += os.sep

    if not abs_path.startswith(abs_workdir):
        raise ValueError(
            f"Structured output file must be under workdir. "
            f"File: {abs_path}, Workdir: {abs_workdir.rstrip(os.sep)}"
        )
    return abs_path


def _generate_output_path(workdir: str, session_id: str) -> str:
    """Generate default output path in .innerloop/ subdirectory.

    Args:
        workdir: Working directory
        session_id: Session identifier for unique naming

    Returns:
        Absolute path to output file in .innerloop/ directory
    """
    timestamp = int(time.time() * 1000)
    # Sanitize session_id to avoid path issues
    safe_session = "".join(c if c.isalnum() else "_" for c in session_id)
    filename = f"structured_{safe_session}_{timestamp}.json"
    return os.path.join(workdir, ".innerloop", filename)


def _can_write_files(perms: Permission) -> bool:
    """Check if LLM can write files (directly or via bash).

    Args:
        perms: Permission object

    Returns:
        True if LLM has edit or bash permissions
    """
    # Direct file editing
    if perms.edit == Permission.ALLOW:
        return True

    # Can use bash commands to create files
    if perms.bash == Permission.ALLOW:
        return True

    # Fine-grained bash permissions (dict of tool: level)
    if isinstance(perms.bash, dict):
        # If any bash tool is allowed, assume file creation is possible
        return any(level == Permission.ALLOW for level in perms.bash.values())

    return False


async def async_invoke_structured(
    request: Request,
    *,
    max_retries: int = 2,
) -> Response[Any]:
    """Structured invoke with dual-mode file-based output.

    Supports two modes:
    1. File mode: LLM writes JSON directly to file (when edit/bash allowed)
    2. XML fallback: LLM returns JSON in <json> tags, SDK extracts and writes

    File is always created (by LLM or SDK) and path is returned in response.
    File is never deleted by SDK.

    Args:
        request: Request with response_format set
        max_retries: Maximum validation retry attempts

    Returns:
        Response with parsed output and structured_output_file path
    """
    # If no format provided, delegate to async_invoke
    if request.response_format is None:
        return await async_invoke(request)

    # 1. Determine output file path
    workdir = request.workdir or os.getcwd()

    if request.output_file:
        # User provided explicit path - use it as-is (after validation)
        output_file = request.output_file
    else:
        # No path provided - generate default in .innerloop/
        session_id = request.session or "default"
        output_file = _generate_output_path(workdir, session_id)

    # Validate path is under workdir (hard failure if not)
    output_file = _validate_output_path(output_file, workdir)

    # 2. Ensure parent directory exists (SDK responsibility)
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    logger.debug("Structured output file: %s", output_file)

    # 3. Check permissions and build adaptive prompt
    can_write = _can_write_files(request.permission)
    # Pass output_file only if LLM has write permissions; otherwise use XML mode
    base_prompt = build_structured_prompt(
        request.prompt,
        request.response_format,
        output_file=output_file if can_write else None,
    )

    # 4. Retry loop
    current_prompt = base_prompt
    attempts_used = 0
    total_events: list[OpenCodeEvent] = []
    final_session: str | None = request.session
    final_output: Any | None = None

    wall_start = unix_ms()
    while True:
        attempts_used += 1

        # Invoke CLI
        req = Request(
            model=request.model,
            prompt=current_prompt,
            permission=request.permission,
            providers=request.providers,
            mcp=request.mcp,
            response_format=None,  # We handle validation ourselves
            session=final_session,
            workdir=request.workdir,
            timeout=request.timeout,
        )
        resp = await async_invoke(req)
        total_events.extend(resp.events)
        final_session = resp.session_id

        # 5. Try file-based extraction first (LLM wrote JSON)
        file_mode_succeeded = False
        if os.path.exists(output_file):
            try:
                with open(output_file) as f:
                    content = f.read()
                final_output = request.response_format.model_validate_json(
                    content
                )
                logger.debug(
                    "Structured output: file mode succeeded (attempt %d)",
                    attempts_used,
                )
                file_mode_succeeded = True
                break
            except (ValidationError, ValueError, OSError) as e:
                logger.debug(
                    "File mode failed (attempt %d): %s", attempts_used, e
                )
                # Fall through to XML extraction

        # 6. Fallback: XML tag extraction (LLM returned JSON in output)
        if not file_mode_succeeded:
            try:
                final_output = _extract_and_parse_json(
                    str(resp.output), request.response_format
                )
                # Write SDK-extracted JSON to file for consistency
                with open(output_file, "w") as f:
                    f.write(final_output.model_dump_json(indent=2))
                logger.debug(
                    "Structured output: XML fallback succeeded, wrote to file (attempt %d)",
                    attempts_used,
                )
                break
            except (ValidationError, ValueError) as ve:
                # Both modes failed - record error and retry or fail
                err_ev = ErrorEvent(
                    timestamp=unix_ms(),
                    sessionID=final_session or "",
                    type="error",
                    message=str(ve),
                    code=None,
                    severity="error",
                )
                total_events.append(err_ev)

                if attempts_used >= max_retries:
                    raise RuntimeError(
                        f"Structured output validation failed after {attempts_used} attempts. "
                        f"Expected file: {output_file}\n"
                        f"Error: {ve}"
                    ) from ve

                # Retry with error context
                from .structured import build_structured_reprompt

                current_prompt = build_structured_reprompt(
                    base_prompt, str(ve)
                )

    wall_end = unix_ms()

    # 7. Return response with BOTH file path and parsed object
    assert final_output is not None
    out_resp: Response[Any] = Response(
        session_id=final_session or "",
        input=request.prompt,
        output=final_output,
        structured_output_file=output_file,
        events=total_events,
        attempts=attempts_used,
        time=TimeInfo(start=wall_start, end=wall_end),
    )
    out_resp.usage = compute_usage(total_events)
    return out_resp
