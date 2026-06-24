"""Telemetry envelope (M0.1 contract).

The wire shape an emitter produces and the Observatory API ingests. Kept aligned
with ``midil-observatory-api``'s ``TelemetryEnvelopeIn``; ``model_dump(mode="json")``
yields exactly that payload.
"""

from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Any, Dict, Optional

from pydantic import BaseModel, Field

from pymidil.utils.time import utcnow


class EventStatus(str, Enum):
    """Terminal outcome of a single dispatch observation."""

    SUCCESS = "success"
    FAILED = "failed"
    RETRYING = "retrying"
    DLQ = "dlq"
    DUPLICATE = "duplicate"


class TelemetryEnvelope(BaseModel):
    """One observation of an event as it flowed through one consumer."""

    event_id: str = Field(
        ..., description="Business event id; shared across consumers/hops"
    )
    event_type: str = Field(..., description="e.g. BookingCreated, PaymentAuthorized")
    status: EventStatus
    broker: str = Field(
        ..., description="Transport: sqs, sns, kafka, rabbitmq, redis, …"
    )

    id: Optional[str] = Field(
        default=None, description="Stable observation id; generated if omitted"
    )
    occurred_at: datetime = Field(default_factory=utcnow)
    consumer: Optional[str] = None
    source_service: Optional[str] = None
    attempts: int = 1
    processing_time_ms: Optional[float] = None
    trace_id: Optional[str] = None
    span_id: Optional[str] = None
    parent_span_id: Optional[str] = None
    idempotency_key: Optional[str] = None
    failure_reason: Optional[str] = None
    failure_class: Optional[str] = None
    payload: Optional[Any] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)
