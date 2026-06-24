"""No-op sink — disables telemetry while keeping the wiring in place."""

from __future__ import annotations

from pymidil.event.observability.envelope import TelemetryEnvelope
from pymidil.event.observability.sinks.base import TelemetrySink


class NullTelemetrySink(TelemetrySink):
    async def emit(self, envelope: TelemetryEnvelope) -> None:
        return None
