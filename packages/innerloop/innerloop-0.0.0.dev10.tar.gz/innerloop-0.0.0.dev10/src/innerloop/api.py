"""Public API: Loop class + convenience helpers and functional wrappers.

This module provides a minimal, consistent external surface:
- Loop: run/arun, session/asession
- run/arun: one-shot convenience
- allow/mcp/providers: ergonomic helpers to build config inputs
- build_structured_prompt/build_structured_reprompt: structured output helpers
"""

from __future__ import annotations

import asyncio
from collections.abc import AsyncIterator, Awaitable, Iterator
from contextlib import asynccontextmanager, contextmanager
from typing import Any, Protocol, runtime_checkable

from pydantic import BaseModel

from .helper import to_session_id
from .invoke import async_invoke, async_invoke_structured
from .mcp import LocalMcpServer, RemoteMcpServer
from .permissions import Permission, PermissionLevel
from .providers import PROVIDER_CLASSES, ProviderConfig
from .request import Request
from .response import Response
from .structured import build_structured_prompt, build_structured_reprompt


def allow(
    *tools: str,
    read: bool = True,
    write: bool = True,
    bash: bool | dict[str, PermissionLevel] = False,
    webfetch: bool = False,
) -> Permission:
    """Convenience builder for Permission.

    Semantics:
    - tools may contain "bash" or "webfetch" to allow them quickly
    - edit is ALLOW only when both read=True and write=True; otherwise DENY
    - passing a dict for `bash` enables fine‑grained tool policies
    """
    edit_level = Permission.ALLOW if write and read else Permission.DENY
    bash_level = (
        Permission.ALLOW
        if (bash is True or "bash" in tools)
        else Permission.DENY
    )
    web_level = (
        Permission.ALLOW
        if (webfetch or "webfetch" in tools)
        else Permission.DENY
    )
    return Permission(
        edit=edit_level,
        bash=bash if isinstance(bash, dict) else bash_level,
        webfetch=web_level,
    )


def jail(
    allowed_urls: list[str],
    bash: PermissionLevel = Permission.DENY,
    edit: PermissionLevel = Permission.DENY,
) -> Permission:
    """Create a Permission for safe webfetch with HTTP jail.

    Requires httpjail binary. Defaults to deny all local operations (bash, edit).
    Override individual permissions as needed.

    Args:
        allowed_urls: List of hostnames or glob patterns (e.g., "*.wikipedia.org")
        bash: Permission level for bash commands. Defaults to DENY.
        edit: Permission level for file editing. Defaults to DENY.

    Returns:
        Permission object configured for safe webfetch with HTTP jail.

    Example:
        >>> perms = jail(allowed_urls=["example.com", "*.wikipedia.org"])
        >>> # Allow editing while using jail
        >>> perms = jail(allowed_urls=["docs.python.org"], edit=Permission.ALLOW)
    """
    return Permission(
        webfetch=Permission.ALLOW,
        allowed_urls=allowed_urls,
        bash=bash,
        edit=edit,
    )


def mcp(**servers: str) -> dict[str, LocalMcpServer | RemoteMcpServer]:
    """Parse MCP specs into Local/Remote servers.

    Usage:
      mcp(biomcp="uvx --from biomcp-python biomcp run",
          context7="https://mcp.context7.com/mcp")
    Supports simple ENV=VAR tokens before the command for local.
    """
    out: dict[str, LocalMcpServer | RemoteMcpServer] = {}
    for name, spec in servers.items():
        s = spec.strip()
        if s.startswith("http://") or s.startswith("https://"):
            out[name] = RemoteMcpServer(name=name, url=s)  # type: ignore[arg-type]
            continue
        env: dict[str, str] = {}
        tokens = s.split()
        cmd: list[str] = []
        for tok in tokens:
            if "=" in tok and not cmd:
                k, _, v = tok.partition("=")
                env[k] = v
            else:
                cmd.append(tok)
        out[name] = LocalMcpServer(
            name=name, command=cmd, environment=env or None
        )
    return out


def providers(**prov: Any) -> dict[str, ProviderConfig]:
    """Build a provider map from simple inputs.

    Keys: openai, anthropic, ollama, lmstudio. Values can be:
      - dict (forwarded as options/models/npm overrides)
      - str (interpreted as apiKey or baseURL if http)
      - True/None (use provider defaults)
    Unknown keys: accept ProviderConfig instances or treat dict as options.
    """

    def _opts_from_value(v: Any) -> dict[str, Any] | None:
        if isinstance(v, dict):
            return v
        if isinstance(v, str):
            return {"baseURL": v} if v.startswith("http") else {"apiKey": v}
        return None

    out: dict[str, ProviderConfig] = {}
    for name, val in prov.items():
        key = name.lower()
        cls = PROVIDER_CLASSES.get(key)

        # Uniform pass-through for any already-constructed ProviderConfig
        if isinstance(val, ProviderConfig):
            out[key] = val
            continue

        if cls is None:
            # Custom provider: only support options dict
            if isinstance(val, dict):
                out[key] = ProviderConfig.model_validate({"options": val})
            # else: ignore unsupported custom types
            continue

        opts = _opts_from_value(val)
        if opts is not None:
            out[key] = cls.model_validate({"options": opts})
        else:
            # True/None/other → defaults
            out[key] = cls()

    return out


class Loop:
    """Reusable loop that hides config and exposes simple methods."""

    def __init__(
        self,
        *,
        model: str,
        perms: Permission | None = None,
        providers: dict[str, ProviderConfig] | None = None,
        mcp: dict[str, LocalMcpServer | RemoteMcpServer] | None = None,
    ) -> None:
        self.model = model
        self.perms = perms or Permission()
        self.providers = providers
        self.mcp = mcp
        self.default_timeout: float | None = None
        self.default_workdir: str | None = None
        self.default_response_format: type[BaseModel] | None = None
        self._last_session_id: str | None = None

    def run(
        self,
        prompt: str,
        *,
        response_format: type[BaseModel] | None = None,
        session: str | Response[Any] | None = None,
        timeout: float | None = None,
        workdir: str | None = None,
        max_retries: int = 2,
    ) -> Response[Any]:
        # Avoid creating coroutine objects when running inside an event loop;
        # raising early prevents un-awaited coroutine warnings in async tests.
        try:
            asyncio.get_running_loop()
        except RuntimeError:
            # No running loop → safe to proceed with asyncio.run
            pass
        else:
            # Avoid creating coroutine objects that would trigger "never awaited"
            # warnings when raising from within an active event loop.
            raise RuntimeError(
                "asyncio.run() cannot be called from a running event loop"
            )
        sid = to_session_id(session)
        if sid is None:
            sid = self._last_session_id
        eff_timeout = timeout if timeout is not None else self.default_timeout
        eff_workdir = workdir if workdir is not None else self.default_workdir
        eff_format = (
            response_format
            if response_format is not None
            else self.default_response_format
        )
        req = Request(
            model=self.model,
            prompt=prompt,
            permission=self.perms,
            providers=self.providers,
            mcp=self.mcp,
            response_format=eff_format,
            session=sid,
            workdir=eff_workdir,
            timeout=eff_timeout,
        )
        if eff_format is not None:
            resp = asyncio.run(
                async_invoke_structured(req, max_retries=max_retries)
            )
        else:
            resp = asyncio.run(async_invoke(req))
        if resp.session_id:
            self._last_session_id = resp.session_id
        return resp

    async def arun(
        self,
        prompt: str,
        *,
        response_format: type[BaseModel] | None = None,
        session: str | Response[Any] | None = None,
        timeout: float | None = None,
        workdir: str | None = None,
        max_retries: int = 2,
    ) -> Response[Any]:
        sid = to_session_id(session)
        if sid is None:
            sid = self._last_session_id
        eff_timeout = timeout if timeout is not None else self.default_timeout
        eff_workdir = workdir if workdir is not None else self.default_workdir
        eff_format = (
            response_format
            if response_format is not None
            else self.default_response_format
        )
        req = Request(
            model=self.model,
            prompt=prompt,
            permission=self.perms,
            providers=self.providers,
            mcp=self.mcp,
            response_format=eff_format,
            session=sid,
            workdir=eff_workdir,
            timeout=eff_timeout,
        )
        if eff_format is not None:
            resp = await async_invoke_structured(req, max_retries=max_retries)
        else:
            resp = await async_invoke(req)
        if resp.session_id:
            self._last_session_id = resp.session_id
        return resp

    @runtime_checkable
    class AskSync(Protocol):
        def __call__(
            self,
            prompt: str,
            response_format: type[BaseModel] | None = None,
            *,
            timeout: float | None = None,
            workdir: str | None = None,
        ) -> Response[Any]: ...

    @runtime_checkable
    class AskAsync(Protocol):
        def __call__(
            self,
            prompt: str,
            response_format: type[BaseModel] | None = None,
            *,
            timeout: float | None = None,
            workdir: str | None = None,
        ) -> Awaitable[Response[Any]]: ...

    @contextmanager
    def session(self) -> Iterator[AskSync]:
        sid: str | None = None

        def ask(
            prompt: str,
            response_format: type[BaseModel] | None = None,
            *,
            timeout: float | None = None,
            workdir: str | None = None,
        ) -> Response[Any]:
            nonlocal sid
            if sid is None:
                # Empty string sentinel means: force new session (no reuse),
                # let CLI allocate a real session ID on first call.
                sid = ""
            eff_format = (
                response_format
                if response_format is not None
                else self.default_response_format
            )
            resp = self.run(
                prompt,
                response_format=eff_format,
                session=sid,
                timeout=(
                    timeout if timeout is not None else self.default_timeout
                ),
                workdir=(
                    workdir if workdir is not None else self.default_workdir
                ),
            )
            sid = resp.session_id or sid
            return resp

        yield ask

    @asynccontextmanager
    async def asession(self) -> AsyncIterator[AskAsync]:
        sid: str | None = None

        async def ask(
            prompt: str,
            response_format: type[BaseModel] | None = None,
            *,
            timeout: float | None = None,
            workdir: str | None = None,
        ) -> Response[Any]:
            nonlocal sid
            if sid is None:
                # Empty string sentinel means: force new session (no reuse),
                # let CLI allocate a real session ID on first call.
                sid = ""
            eff_format = (
                response_format
                if response_format is not None
                else self.default_response_format
            )
            resp = await self.arun(
                prompt,
                response_format=eff_format,
                session=sid,
                timeout=(
                    timeout if timeout is not None else self.default_timeout
                ),
                workdir=(
                    workdir if workdir is not None else self.default_workdir
                ),
            )
            sid = resp.session_id or sid
            return resp

        yield ask


def run(
    prompt: str,
    *,
    model: str,
    response_format: type[BaseModel] | None = None,
    session: str | Response[Any] | None = None,
    timeout: float | None = None,
    workdir: str | None = None,
    perms: Permission | None = None,
    providers: dict[str, ProviderConfig] | None = None,
    mcp: dict[str, LocalMcpServer | RemoteMcpServer] | None = None,
) -> Response[Any]:
    return Loop(model=model, perms=perms, providers=providers, mcp=mcp).run(
        prompt,
        response_format=response_format,
        session=session,
        timeout=timeout,
        workdir=workdir,
    )


async def arun(
    prompt: str,
    *,
    model: str,
    response_format: type[BaseModel] | None = None,
    session: str | Response[Any] | None = None,
    timeout: float | None = None,
    workdir: str | None = None,
    perms: Permission | None = None,
    providers: dict[str, ProviderConfig] | None = None,
    mcp: dict[str, LocalMcpServer | RemoteMcpServer] | None = None,
) -> Response[Any]:
    return await Loop(
        model=model, perms=perms, providers=providers, mcp=mcp
    ).arun(
        prompt,
        response_format=response_format,
        session=session,
        timeout=timeout,
        workdir=workdir,
    )


__all__ = [
    "Loop",
    "run",
    "arun",
    "allow",
    "jail",
    "mcp",
    "providers",
    "build_structured_prompt",
    "build_structured_reprompt",
]
