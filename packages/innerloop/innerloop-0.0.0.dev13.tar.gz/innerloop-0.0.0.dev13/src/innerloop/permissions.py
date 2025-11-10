from __future__ import annotations

from enum import Enum
from typing import Any, ClassVar

from pydantic import BaseModel, Field


class PermissionLevel(str, Enum):
    """Enumeration for the possible permission levels."""

    ALLOW = "allow"
    DENY = "deny"


class Permission(BaseModel):
    """
    Defines the permission settings for an OpenCode InnerLoop.

    This class allows for configuring what actions the loop can take,
    providing granular control over file edits, web fetching, and
    shell command execution.

    Attributes:
        edit: Controls file editing. Defaults to ALLOW.
        webfetch: Controls fetching web content. Defaults to DENY.
        bash: Controls shell command execution. Can be a single level or a
              dictionary for fine-grained control. Defaults to DENY.
    """

    ALLOW: ClassVar[PermissionLevel] = PermissionLevel.ALLOW
    DENY: ClassVar[PermissionLevel] = PermissionLevel.DENY

    edit: PermissionLevel = Field(default=PermissionLevel.ALLOW)
    webfetch: PermissionLevel = Field(default=PermissionLevel.DENY)
    bash: PermissionLevel | dict[str, PermissionLevel] = Field(
        default=PermissionLevel.DENY
    )

    def to_dict(self) -> dict[str, Any]:
        """Serializes the permissions into a dictionary for the opencode config."""
        return self.model_dump(exclude_none=True)
