from __future__ import annotations

import asyncio
import time
from abc import abstractmethod
from threading import Lock
from typing import Annotated, Any, List, Optional, Set

from loguru import logger
from pydantic import BaseModel, Field

from midil.event.connector.base import Connector, ConnectorDirection
from midil.event.connector.health import ConnectorHealth
from midil.event.exceptions import RetryableEventError
from midil.event.message import Message
from midil.event.observability.hooks import DispatchHook
from midil.event.subscriber.base import EventSubscriber


class ConsumerMessage(Message):
    ack_handle: Optional[str] = Field(
        default=None,
        description="Token or handle required to ack/nack/delete this message",
    )


class BaseConsumerConfig(BaseModel):
    type: Annotated[
        str,
        Field(
            description="Type of the consumer configuration",
            pattern=r"^[a-zA-Z0-9_-]+$",
        ),
    ]


class EventConsumer(Connector):
    """
    Abstract base for all event consumers.

    An EventConsumer is a SOURCE Connector — it receives messages from an
    external backend and dispatches them to registered EventSubscribers.

    The dispatch lifecycle is instrumented through DispatchHooks, which
    observe each stage (receive → handled/failed/retried) without modifying
    this class — Open/Closed Principle applied. Attach hooks via add_hook()
    before calling connect().

    Subclasses implement start(), stop(), ack(), and nack().
    """

    def __init__(self, config: BaseConsumerConfig) -> None:
        self._config = config
        self._subscribers: Set[EventSubscriber] = set()
        self._subscription_lock = Lock()
        self._dispatch_hooks: List[DispatchHook] = []

    @property
    def name(self) -> str:
        return self._config.type

    @property
    def direction(self) -> ConnectorDirection:
        return ConnectorDirection.SOURCE

    async def connect(self) -> None:
        await self.start()

    async def disconnect(self) -> None:
        await self.stop()

    async def health(self) -> ConnectorHealth:
        return ConnectorHealth.unknown()

    def add_hook(self, hook: DispatchHook) -> None:
        """Attach a DispatchHook to observe this consumer's dispatch lifecycle."""
        self._dispatch_hooks.append(hook)

    def remove_hook(self, hook: DispatchHook) -> None:
        self._dispatch_hooks = [h for h in self._dispatch_hooks if h is not hook]

    def subscribe(self, subscriber: EventSubscriber) -> None:
        with self._subscription_lock:
            self._subscribers.add(subscriber)

    def unsubscribe(self, subscriber: EventSubscriber) -> None:
        """
        Discard a handler (subscriber).

        Args:
            subscriber (EventSubscriber): The subscriber to remove.
        """
        with self._subscription_lock:
            self._subscribers.discard(subscriber)

    async def dispatch(self, message: Message) -> None:
        """
        Dispatch a message to all subscribers, timing the full lifecycle
        and notifying hooks at each stage.

        Flow:
          1. on_receive hooks
          2. All subscribers gathered concurrently
          3. RetryableEventError  →  nack(requeue=True) + on_retry hooks
          4. Other exceptions     →  ack + on_failure hooks
          5. Clean run            →  ack + on_complete hooks
        """
        start = time.monotonic()

        await self._notify_hooks("on_receive", message)

        if not self._subscribers:
            logger.warning(
                f"[{self.name}] No subscribers registered, skipping event {message.id}"
            )
            return

        results = await asyncio.gather(
            *[subscriber(message) for subscriber in self._subscribers],
            return_exceptions=True,
        )

        duration_ms = (time.monotonic() - start) * 1000

        if any(isinstance(r, RetryableEventError) for r in results):
            logger.debug(f"[{self.name}] Retryable failure on {message.id}, requeuing")
            await self._notify_hooks("on_retry", message)
            return await self.nack(message, requeue=True)

        exceptions = [r for r in results if isinstance(r, Exception)]
        if exceptions:
            await self._notify_hooks("on_failure", message, error=exceptions[0])
        else:
            await self._notify_hooks("on_complete", message, duration_ms=duration_ms)

        return await self.ack(message)

    async def _notify_hooks(self, stage: str, message: Message, **kwargs: Any) -> None:
        """
        Notify all dispatch hooks of the event lifecycle stage.

        Args:
            stage: The stage of the event lifecycle.
            message: The message to notify the hooks about.
            **kwargs: Additional keyword arguments to pass to the hook.
        """
        for hook in self._dispatch_hooks:
            try:
                await getattr(hook, stage)(message, self.name, **kwargs)
            except Exception as exc:
                logger.warning(
                    f"[{self.name}] Hook {hook.__class__.__name__}.{stage} raised: {exc}"
                )

    @abstractmethod
    async def start(self) -> None:
        """
        Begin consuming events from the event source.

        This method should be implemented to start the event loop or background
        process that listens for incoming events and dispatches them to the
        registered subscribers.
        """
        ...

    @abstractmethod
    async def stop(self) -> None:
        """
        Stop consuming events and perform any necessary cleanup.

        This method should be implemented to halt event processing, release
        resources, and ensure that no further events are delivered to subscribers.
        """
        ...

    @abstractmethod
    async def ack(self, message: Message) -> None:
        """
        Acknowledge the receipt of an event.

        This method should be implemented to acknowledge the receipt of an event,
        such as confirming that the event has been processed successfully.

        Args:
            message: The message to ack.
        """
        pass

    @abstractmethod
    async def nack(self, message: Message, requeue: bool = False) -> None:
        """
        Negative acknowledge the receipt of an event.

        This method should be implemented to negatively acknowledge the receipt of an event,
        such as indicating that the event was not processed successfully. If requeue is True,
        the message will be requeued for re-processing.

        Args:
            message: The message to nack.
            requeue: Whether to requeue the message.
        """
        pass
