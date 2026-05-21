from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field

from midil.utils.time import utcnow


class ConnectorStatus(str, Enum):
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    UNKNOWN = "unknown"


class ConnectorHealth(BaseModel):
    status: ConnectorStatus
    latency_ms: Optional[float] = Field(
        default=None, description="Round-trip latency in milliseconds"
    )
    last_checked: datetime = Field(default_factory=utcnow)
    error: Optional[str] = Field(default=None)

    @classmethod
    def healthy(cls, latency_ms: Optional[float] = None) -> ConnectorHealth:
        return cls(status=ConnectorStatus.HEALTHY, latency_ms=latency_ms)

    @classmethod
    def degraded(
        cls, error: str, latency_ms: Optional[float] = None
    ) -> ConnectorHealth:
        return cls(status=ConnectorStatus.DEGRADED, error=error, latency_ms=latency_ms)

    @classmethod
    def unhealthy(cls, error: str) -> ConnectorHealth:
        return cls(status=ConnectorStatus.UNHEALTHY, error=error)

    @classmethod
    def unknown(cls) -> ConnectorHealth:
        return cls(status=ConnectorStatus.UNKNOWN)

    @property
    def is_healthy(self) -> bool:
        return self.status == ConnectorStatus.HEALTHY
