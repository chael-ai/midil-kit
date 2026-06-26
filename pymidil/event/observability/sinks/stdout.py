"""Stdout sink — logs envelopes as JSON. The zero-dependency default."""

from __future__ import annotations

from loguru import logger

from pymidil.event.observability.envelope import TelemetryEnvelope
from pymidil.event.observability.sinks.base import TelemetrySink


class StdoutTelemetrySink(TelemetrySink):
    async def emit(self, envelope: TelemetryEnvelope) -> None:
        logger.bind(telemetry=True).info(envelope.model_dump_json())
