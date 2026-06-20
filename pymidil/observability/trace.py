from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Optional
from uuid import uuid4

from pydantic import BaseModel, Field

from pymidil.utils.time import utcnow


class TraceStatus(str, Enum):
    RECEIVED = "received"  # message arrived at the consumer
    HANDLED = "handled"  # all subscribers completed successfully
    FAILED = "failed"  # one or more subscribers raised a non-retryable error
    RETRIED = "retried"  # requeued due to a RetryableEventError


class EventTrace(BaseModel):
    """
    Immutable snapshot of a message at a single point in its lifecycle.

    Multiple traces share the same event_id — query by event_id to
    reconstruct the full timeline of any message through the system.
    """

    trace_id: str = Field(default_factory=lambda: uuid4().hex)
    event_id: str
    status: TraceStatus
    timestamp: datetime = Field(default_factory=utcnow)
    duration_ms: Optional[float] = Field(
        default=None,
        description="Wall-clock ms from first receive to this status",
    )
    error: Optional[str] = Field(default=None)

    model_config = {"frozen": True}
