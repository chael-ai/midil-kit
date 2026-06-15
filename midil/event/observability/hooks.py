from __future__ import annotations

from midil.event.message import Message


class DispatchHook:
    """
    Extension point for observing the full event dispatch lifecycle.

    Attach hooks to an EventConsumer via add_hook() to instrument
    message flow without modifying consumer or subscriber code —
    a clean application of the Open/Closed Principle.

    All methods are no-ops by default. Override only the stages you care
    about. Multiple hooks may be attached; they are called in order.
    """

    async def on_receive(self, message: Message) -> None:
        """Called immediately when a message arrives at the consumer."""
        pass

    async def on_complete(
        self,
        message: Message,
        duration_ms: float,
    ) -> None:
        """Called after all subscribers handled the message without error."""
        pass

    async def on_failure(
        self,
        message: Message,
        error: Exception,
    ) -> None:
        """Called when one or more subscribers raised a non-retryable error."""
        pass

    async def on_retry(self, message: Message) -> None:
        """Called when the message is being requeued due to a RetryableEventError."""
        pass
