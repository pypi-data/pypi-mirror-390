"""Generate minimal permission statements from Permission objects.

This module provides a simple permission statement that's automatically
injected into prompts to inform the LLM what tools are allowed/denied.
"""

from __future__ import annotations

from .permissions import Permission


def _build_permission_statement(perms: Permission) -> str | None:
    """Build a minimal permission statement from Permission object.

    Returns a concise statement listing allowed/denied tools, without
    detailed documentation (which should come from the calling system's
    instructions).

    Args:
        perms: The Permission object defining tool access

    Returns:
        Permission statement string, or None if all defaults (nothing to say)

    Example output:
        ## Permissions

        Available tools: webfetch
        Denied tools: bash, edit

        Allowed domains: en.wikipedia.org, api.github.com
    """
    # Map permission attributes to actual OpenCode CLI tool names
    allowed_tools: list[str] = []
    denied_tools: list[str] = []

    if perms.bash == Permission.ALLOW:
        allowed_tools.append("bash")
    elif perms.bash == Permission.DENY:
        denied_tools.append("bash")

    if perms.webfetch == Permission.ALLOW:
        allowed_tools.append("webfetch")
    elif perms.webfetch == Permission.DENY:
        denied_tools.append("webfetch")

    if perms.edit == Permission.ALLOW:
        allowed_tools.append("edit")
    elif perms.edit == Permission.DENY:
        denied_tools.append("edit")

    # If all defaults (edit=ALLOW, bash=DENY, webfetch=DENY), skip
    # This matches the default Permission() with no customization
    if (
        perms.edit == Permission.ALLOW
        and perms.bash == Permission.DENY
        and perms.webfetch == Permission.DENY
        and not perms.allowed_urls
    ):
        return None

    lines = ["## Permissions\n"]

    if allowed_tools:
        lines.append(f"Available tools: {', '.join(allowed_tools)}\n")

    if denied_tools:
        lines.append(f"Denied tools: {', '.join(denied_tools)}\n")

    # URL restrictions
    if perms.webfetch == Permission.ALLOW and perms.allowed_urls:
        lines.append(f"\nAllowed domains: {', '.join(perms.allowed_urls)}\n")

    return "".join(lines)


# Legacy function for backward compatibility - now just calls _build_permission_statement
def capabilities_prompt(
    perms: Permission,
    *,
    include_suggestions: bool = True,  # Ignored, kept for compatibility
) -> str:
    """Generate a permission statement from Permission object.

    DEPRECATED: This function now returns a minimal permission statement.
    For automatic injection, permissions are added by InnerLoop itself.

    Args:
        perms: The Permission object defining tool access
        include_suggestions: Ignored (kept for backward compatibility)

    Returns:
        Minimal permission statement

    Example:
        >>> from innerloop import Permission, capabilities_prompt
        >>> perms = Permission(bash=Permission.DENY, webfetch=Permission.ALLOW)
        >>> print(capabilities_prompt(perms))
        ## Permissions
        Available tools: webfetch
        Denied tools: bash, edit
    """
    return _build_permission_statement(perms) or ""


__all__ = ["capabilities_prompt", "_build_permission_statement"]
