from __future__ import annotations

from typing import cast

from pydantic import BaseModel, ConfigDict, Field, field_validator

from .mcp import LocalMcpServer, McpServer, RemoteMcpServer, normalize_mcp
from .permissions import Permission
from .providers import ProviderConfig


class InvokeConfig(BaseModel):
    """Typed config that dumps to OPENCODE schema (internal)."""

    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    autoupdate: bool = False
    permission: Permission
    provider: dict[str, ProviderConfig] | None = None
    # CLI expects "mcp" key; keep field name and JSON key aligned
    mcp: dict[str, LocalMcpServer | RemoteMcpServer] | None = Field(
        default=None
    )

    @field_validator("mcp", mode="before")
    @classmethod
    def _normalize_mcp(
        cls, v: list[McpServer] | dict[str, McpServer] | None
    ) -> dict[str, LocalMcpServer | RemoteMcpServer] | None:
        out = normalize_mcp(v)
        return cast(dict[str, LocalMcpServer | RemoteMcpServer] | None, out)

    def to_json(self) -> str:
        return self.model_dump_json(exclude_none=True, by_alias=True)
