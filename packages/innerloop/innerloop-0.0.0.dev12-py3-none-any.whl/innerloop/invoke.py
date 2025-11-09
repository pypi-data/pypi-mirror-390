from __future__ import annotations

import asyncio
import logging
import os
import shutil
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


def wrap_with_httpjail(
    cmd: list[str], allowed_urls: list[str]
) -> list[str] | None:
    """Wrap command with httpjail if available.

    Implements progressive enforcement with automatic fallback:
    1. Strong mode (default on bare metal) - netns + nftables
    2. Server mode (default in containers) - explicit proxy on 127.0.0.1
    3. Weak mode (fallback) - cooperative env vars only

    Returns wrapped command if httpjail is available, None otherwise.
    Logs warning if httpjail is not found and INNERLOOP_REQUIRE_HTTPJAIL is set.

    Args:
        cmd: The command to wrap
        allowed_urls: List of allowed hostnames or glob patterns

    Returns:
        Wrapped command with httpjail prefix, or None if httpjail unavailable
    """
    if not allowed_urls:
        return cmd

    # Check if httpjail is available
    httpjail_path = shutil.which("httpjail")
    if httpjail_path is None:
        from .httpjail import should_require_httpjail

        if should_require_httpjail():
            raise RuntimeError(
                "httpjail binary not found but INNERLOOP_REQUIRE_HTTPJAIL=1. "
                "Install httpjail with: cargo install httpjail"
            )
        logger.warning(
            "httpjail binary not found; proceeding without HTTP jail. "
            "Install with: cargo install httpjail"
        )
        return None

    # Build JavaScript predicate for host filtering
    # Pattern: ["host1", "host2"].some(h => h === r.host || r.host.endsWith('.' + h))
    # Normalize wildcard patterns: "*.example.com" -> "example.com"
    normalized_hosts: list[str] = []
    for h in allowed_urls:
        if h.startswith("*."):
            normalized_hosts.append(h[2:])  # Strip leading "*."
        else:
            normalized_hosts.append(h)

    # Note: Additional infrastructure hosts (providers, registry) are computed
    # at a higher level (run_opencode_jsonl) where model/provider context exists.

    hosts = ", ".join(f"'{h}'" for h in normalized_hosts)
    js_predicate = (
        f"[{hosts}].some(h => h === r.host || r.host.endsWith('.' + h))"
    )

    # Select httpjail mode based on environment
    from .httpjail import (
        build_httpjail_command,
        get_mode_from_env,
        select_httpjail_mode,
        should_force_weak,
    )

    force_mode = get_mode_from_env()
    force_weak = should_force_weak()
    selected_mode = select_httpjail_mode(
        force_mode=force_mode,
        force_weak=force_weak,
    )

    # Build command with selected mode
    httpjail_cmd = build_httpjail_command(cmd, js_predicate, selected_mode)

    logger.debug(
        "Wrapped command with httpjail (mode=%s): %s",
        selected_mode.value,
        " ".join(httpjail_cmd[:4]) + " ...",
    )

    return httpjail_cmd


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

    # Wrap with httpjail if allowed_urls is configured
    httpjail_mode_attempted: HttpJailMode | None = None
    if permission.allowed_urls:
        # Compute a minimal set of infrastructure hosts required for the
        # selected provider/model so the CLI can operate while the user's
        # webfetch destinations remain strictly whitelisted.
        def _host_from_url(url: str) -> str | None:
            try:
                from urllib.parse import urlparse

                netloc = urlparse(url).netloc
                return netloc.split(":", 1)[0] if netloc else None
            except Exception:
                return None

        provider_hosts: set[str] = set()
        # Infer provider from model prefix (e.g., "anthropic/...")
        provider_name = model.split("/", 1)[0]
        if provider_name == "anthropic":
            provider_hosts.add("api.anthropic.com")
        elif provider_name == "openai":
            provider_hosts.add("api.openai.com")
        elif provider_name == "openrouter":
            provider_hosts.add("openrouter.ai")
        elif provider_name == "opencode":
            # OpenCode's own hosted models
            provider_hosts.update({"opencode.ai", "api.opencode.ai"})

        # Consider explicit provider configs; include their baseURL hosts
        if providers:
            for pid, pcfg in providers.items():
                host = _host_from_url(pcfg.options.base_url or "")
                if host:
                    provider_hosts.add(host)
                # Known defaults if baseURL omitted
                if pid == "anthropic":
                    provider_hosts.add("api.anthropic.com")
                elif pid == "openai":
                    provider_hosts.add("api.openai.com")
                elif pid in ("lmstudio", "ollama"):
                    # Local providers typically run on loopback
                    provider_hosts.update({"127.0.0.1", "localhost"})

        # Some OpenCode setups fetch provider plugins from npm on first run
        # (observed: registry.npmjs.org). Allowing it ensures a smooth first run.
        provider_hosts.add("registry.npmjs.org")

        # In practice the CLI may resolve model metadata via models.dev in
        # certain configurations. Allow as observed infra.
        provider_hosts.add("models.dev")

        # Merge user allowlist with minimal infra hosts
        eff_allowed = list(
            dict.fromkeys([*permission.allowed_urls, *sorted(provider_hosts)])
        )
        logger.debug(
            "httpjail effective allowlist (user + infra): %s",
            ", ".join(eff_allowed),
        )

        wrapped = wrap_with_httpjail(cmd, eff_allowed)
        if wrapped is not None:
            cmd = wrapped
            # Extract the mode from the wrapped command for fallback tracking
            from .httpjail import (
                HttpJailMode,
                get_mode_from_env,
                select_httpjail_mode,
                should_force_weak,
            )

            force_mode = get_mode_from_env()
            force_weak = should_force_weak()
            httpjail_mode_attempted = select_httpjail_mode(
                force_mode=force_mode, force_weak=force_weak
            )

    # Delegate to the generic process streamer with retry logic for httpjail failures
    from .errors import CliExitError
    from .httpjail import (
        HttpJailMode,
        build_httpjail_command,
        get_fallback_mode,
        is_httpjail_capability_error,
    )
    from .proc import stream_jsonl_process as _stream

    base_cmd = build_opencode_cmd(model, session_id=session_id)
    max_httpjail_retries = 2  # STRONG -> SERVER -> WEAK

    try:
        for _attempt in range(max_httpjail_retries + 1):
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
                # Success - exit retry loop
                break
            except CliExitError as e:
                # Check if this is an httpjail capability error and we can retry
                if (
                    httpjail_mode_attempted is not None
                    and is_httpjail_capability_error(e.stderr)
                ):
                    fallback_mode = get_fallback_mode(httpjail_mode_attempted)
                    if fallback_mode is not None:
                        logger.warning(
                            "httpjail %s mode failed with capability error "
                            "(rc=%d, stderr=%s); retrying with %s mode",
                            httpjail_mode_attempted.value,
                            e.return_code,
                            e.stderr[:200],
                            fallback_mode.value,
                        )
                        # Rebuild command with fallback mode
                        # Re-extract JS predicate from original wrapped command
                        # (it's the arg after --js flag)
                        js_predicate = "true"  # Default fallback
                        if "--js" in cmd:
                            js_idx = cmd.index("--js")
                            if js_idx + 1 < len(cmd):
                                js_predicate = cmd[js_idx + 1]

                        cmd = build_httpjail_command(
                            base_cmd, js_predicate, fallback_mode
                        )
                        httpjail_mode_attempted = fallback_mode
                        continue  # Retry with weaker mode
                # Not an httpjail capability error, or no fallback available
                raise
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
