from __future__ import annotations

from typing import Generic, TypeVar

from pydantic import BaseModel, Field, computed_field

from .events import CacheInfo, OpenCodeEvent, TimeInfo

T = TypeVar("T")


class UsageMetrics(BaseModel):
    total_cost: float = 0.0
    input_tokens: int = 0
    output_tokens: int = 0
    reasoning_tokens: int = 0
    cache_tokens: CacheInfo | None = None


class Response(BaseModel, Generic[T]):
    """Response object returned from loop invocation."""

    session_id: str = Field()
    input: str = Field(default="", repr=False)
    output: T = Field(repr=False)
    attempts: int = Field(default=1)
    usage: UsageMetrics = Field(default_factory=UsageMetrics, exclude=True)
    events: list[OpenCodeEvent] = Field(default_factory=list, repr=False)
    # Direct timing info for the invocation
    time: TimeInfo | None = Field(default=None)

    @computed_field
    def event_count(self) -> int:
        """Total number of parsed events (including errors)."""
        return len(self.events)

    # No computed time dict; callers can derive duration as (time.end-time.start)
