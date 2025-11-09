from __future__ import annotations

import time


def to_session_id(item: str | object | None) -> str | None:
    """Return a session id string from a Response or string.

    - If ``item`` is a Response, returns ``item.session_id``.
    - If ``item`` is a string, returns it unchanged.
    - If ``item`` is None, returns None.
    """
    # Avoid importing Response to prevent circular import; duck-type on attribute.
    if item is None or isinstance(item, str):
        return item
    sid = getattr(item, "session_id", None)
    return sid if isinstance(sid, str) else None


def unix_ms() -> int:
    """Current wall-clock time in Unix milliseconds as an int."""
    return int(time.time() * 1000)
