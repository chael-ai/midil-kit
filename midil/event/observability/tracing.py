from __future__ import annotations

from midil.event.message import Message
from midil.event.observability.hooks import DispatchHook
from midil.event.observability.store import TraceStore
from midil.event.observability.trace import EventTrace, TraceStatus


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

    async def on_receive(self, message: Message) -> None:
        await self._store.save(
            EventTrace(
                event_id=str(message.id),
                status=TraceStatus.RECEIVED,
            )
        )

    async def on_complete(
        self,
        message: Message,
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
        message: Message,
        error: Exception,
    ) -> None:
        await self._store.save(
            EventTrace(
                event_id=str(message.id),
                status=TraceStatus.FAILED,
                error=str(error),
            )
        )

    async def on_retry(self, message: Message) -> None:
        await self._store.save(
            EventTrace(
                event_id=str(message.id),
                status=TraceStatus.RETRIED,
            )
        )
