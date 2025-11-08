from __future__ import annotations

from typing import TypeVar, cast

from pydantic import BaseModel, ConfigDict, Field, field_validator

from .mcp import LocalMcpServer, McpServer, RemoteMcpServer, normalize_mcp
from .permissions import Permission
from .providers import ProviderConfig

P = TypeVar("P", bound=BaseModel)


class Request(BaseModel):
    """A single, stateless invocation request (internal).

    Fields:
      - model: provider/model identifier
      - prompt: instruction text
      - permission/providers/mcp: config to forward to CLI
      - response_format: optional structured output schema (Pydantic class)
      - session: optional session id to resume
      - workdir/timeout: optional runtime hints
    """

    model_config = ConfigDict(extra="forbid")

    model: str
    prompt: str
    permission: Permission = Field(default_factory=Permission)
    providers: dict[str, ProviderConfig] | None = None
    mcp: (
        dict[str, LocalMcpServer | RemoteMcpServer] | list[McpServer] | None
    ) = None
    response_format: type[BaseModel] | None = None
    session: str | None = None
    workdir: str | None = None
    timeout: float | None = None

    @field_validator("mcp", mode="before")
    @classmethod
    def _normalize_mcp(
        cls, v: list[McpServer] | dict[str, McpServer] | None
    ) -> dict[str, LocalMcpServer | RemoteMcpServer] | None:
        out = normalize_mcp(v)
        return cast(dict[str, LocalMcpServer | RemoteMcpServer] | None, out)
