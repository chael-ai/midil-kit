from __future__ import annotations

from abc import abstractmethod

from pydantic import BaseModel, Field

from midil.event.connector.base import Connector, ConnectorDirection
from midil.event.connector.health import ConnectorHealth
from midil.event.message import MessageBody


class BaseProducerConfig(BaseModel):
    type: str = Field(..., description="Type of the producer configuration")


class EventProducer(Connector):
    """
    Abstract base for all event producers.

    An EventProducer is a DESTINATION Connector — it accepts event payloads
    and routes them to an external backend (SQS, Redis, etc.).

    Subclasses must implement publish() and close(). The connect/disconnect/health
    methods have sensible defaults but can be overridden for richer lifecycle control.
    """

    def __init__(self, config: BaseProducerConfig) -> None:
        self._config = config

    @property
    def name(self) -> str:
        return self._config.type

    @property
    def direction(self) -> ConnectorDirection:
        return ConnectorDirection.DESTINATION

    async def connect(self) -> None:
        """No-op by default — producers typically connect lazily on first publish."""
        pass

    async def disconnect(self) -> None:
        await self.close()

    async def health(self) -> ConnectorHealth:
        return ConnectorHealth.unknown()

    @abstractmethod
    async def publish(self, payload: MessageBody, **kwargs) -> None:
        ...

    @abstractmethod
    async def close(self) -> None:
        ...
