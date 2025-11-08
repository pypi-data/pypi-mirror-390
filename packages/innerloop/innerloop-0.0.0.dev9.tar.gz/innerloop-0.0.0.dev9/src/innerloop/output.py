"""Utilities for assembling final output text from streamed events.

Provides a single implementation used by both function-first and class-based
paths to avoid drift.
"""

from __future__ import annotations

from typing import Any


def _append_safely(current: str, new: str) -> str:
    """Append text handling both delta and snapshot streaming styles.

    - Empty current: return new
    - New starts with current: snapshot, return new (replace)
    - Overlap at boundary: find longest suffix/prefix match, append remainder
    - No overlap: delta, concatenate
    """
    if not current:
        return new
    if new.startswith(current):
        return new

    max_overlap = min(len(current), len(new))
    for k in range(max_overlap, 0, -1):
        if current.endswith(new[:k]):
            return current + new[k:]
    return current + new


def assemble_output(
    events: list[Any],
    *,
    reset_on_tool: bool = True,
    fallback_to_tool: bool = True,
) -> str:
    """Assemble final output text from event stream.

    Behavior:
      - Accumulates TextEvent.part.text via _append_safely
      - If reset_on_tool=True: resets on each ToolUseEvent
      - If fallback_to_tool=True: returns last tool output when no text exists
    """
    from .events import TextEvent as _TextEvent
    from .events import ToolUseEvent as _ToolUseEvent

    assembled_text = ""
    last_tool_output = ""

    for ev in events:
        if isinstance(ev, _ToolUseEvent):
            if reset_on_tool:
                assembled_text = ""
            last_tool_output = ev.part.state.output or last_tool_output
        elif isinstance(ev, _TextEvent):
            chunk = ev.part.text or ""
            assembled_text = _append_safely(assembled_text, chunk)

    if fallback_to_tool and not assembled_text and last_tool_output:
        return last_tool_output
    return assembled_text


__all__ = ["assemble_output"]
