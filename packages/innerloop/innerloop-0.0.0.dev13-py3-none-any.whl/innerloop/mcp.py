"""Typed MCP (Model Context Protocol) server configuration models.

These models allow programmatic configuration of MCP servers to be forwarded
to the OpenCode CLI via the environment.
"""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, HttpUrl


class McpServer(BaseModel):
    """Base configuration for MCP servers.

    Represents a configured MCP server entry. Subclasses define their
    specific connection details (local subprocess or remote HTTP).
    """

    model_config = ConfigDict(extra="allow")

    name: str = Field(exclude=True)
    enabled: bool = True


class LocalMcpServer(McpServer):
    """Local MCP server (spawned as subprocess).

    Configure the command, arguments, and optional environment to launch a
    local MCP server process.
    """

    type: Literal["local"] = "local"
    command: list[str]
    environment: dict[str, str] | None = None


class RemoteMcpServer(McpServer):
    """Remote MCP server (accessed via HTTP).

    Provide the remote URL and optional headers to connect to an HTTP(S)
    MCP server.
    """

    type: Literal["remote"] = "remote"
    url: HttpUrl
    headers: dict[str, str] | None = None


def normalize_mcp(
    v: list[McpServer] | dict[str, McpServer] | None,
) -> dict[str, McpServer] | None:
    """Normalize MCP servers into a name-keyed dict.

    Accepts either a list of servers or an already-keyed dict. Returns None
    when input is None. This helper centralizes normalization to avoid drift
    across classes using MCP configuration.
    """
    if v is None:
        return None
    if isinstance(v, list):
        return {s.name: s for s in v}
    return v
