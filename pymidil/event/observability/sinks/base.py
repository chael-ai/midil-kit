"""Telemetry sink port."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Sequence

from pymidil.event.observability.envelope import TelemetryEnvelope


class TelemetrySink(ABC):
    """Destination for telemetry envelopes.

    Implementations must never raise into the caller's hot path — the dispatch
    hook guards emit() — but should fail closed (drop + log) rather than block.
    """

    @abstractmethod
    async def emit(self, envelope: TelemetryEnvelope) -> None:
        """Ship a single envelope."""

    async def emit_many(self, envelopes: Sequence[TelemetryEnvelope]) -> None:
        """Ship a batch. Default fans out to :meth:`emit`; override to batch natively."""
        for envelope in envelopes:
            await self.emit(envelope)

    async def aclose(self) -> None:
        """Release any resources held by the sink. No-op by default."""
        return None
