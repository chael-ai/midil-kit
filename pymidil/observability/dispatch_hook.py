from __future__ import annotations

from pymidil.observability.hooks import DispatchHook
from pymidil.observability.protocols import MessageProtocol
from pymidil.observability.store import TraceStore
from pymidil.observability.trace import EventTrace, TraceStatus


class TracingDispatchHook(DispatchHook):
    """
    DispatchHook that persists an immutable EventTrace snapshot at each
    stage of the message lifecycle.

    Each stage emits a separate trace entry to the store — query by
    event_id on the TraceStore to reconstruct the full timeline of any
    message. This append-only, immutable approach means no trace entry
    is ever mutated after it's written, making the store safe to share
    across concurrent dispatches.
    """

    def __init__(self, store: TraceStore) -> None:
        self._store = store

    async def on_receive(self, message: MessageProtocol) -> None:
        await self._store.save(
            EventTrace(
                event_id=str(message.id),
                status=TraceStatus.RECEIVED,
            )
        )

    async def on_complete(
        self,
        message: MessageProtocol,
        duration_ms: float,
    ) -> None:
        await self._store.save(
            EventTrace(
                event_id=str(message.id),
                status=TraceStatus.HANDLED,
                duration_ms=duration_ms,
            )
        )

    async def on_failure(
        self,
        message: MessageProtocol,
        error: Exception,
    ) -> None:
        await self._store.save(
            EventTrace(
                event_id=str(message.id),
                status=TraceStatus.FAILED,
                error=str(error),
            )
        )

    async def on_retry(self, message: MessageProtocol) -> None:
        await self._store.save(
            EventTrace(
                event_id=str(message.id),
                status=TraceStatus.RETRIED,
            )
        )
