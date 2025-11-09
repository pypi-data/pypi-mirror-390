"""Usage metrics helpers.

Provides a single place to compute aggregate usage from streamed events.
"""

from __future__ import annotations

from collections.abc import Iterable

from .events import StepFinishEvent
from .response import UsageMetrics


def compute_usage(events: Iterable[object]) -> UsageMetrics:
    inp = out = reas = 0
    total_cost = 0.0
    cache_r = cache_w = 0
    cache_seen = False
    for ev in events:
        if isinstance(ev, StepFinishEvent):
            inp += ev.part.tokens.input
            out += ev.part.tokens.output
            reas += ev.part.tokens.reasoning
            try:
                total_cost += float(ev.part.cost)
            except Exception:
                # Non-numeric or missing cost treated as zero
                pass
            if ev.part.tokens.cache is not None:
                cache_seen = True
                cache_r += ev.part.tokens.cache.read
                cache_w += ev.part.tokens.cache.write
    um = UsageMetrics()
    um.input_tokens = inp
    um.output_tokens = out
    um.reasoning_tokens = reas
    um.total_cost = total_cost
    if cache_seen:
        from .events import CacheInfo

        um.cache_tokens = CacheInfo(read=cache_r, write=cache_w)
    return um


__all__ = ["compute_usage"]
