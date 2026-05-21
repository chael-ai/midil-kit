from __future__ import annotations

from abc import ABC, abstractmethod
from enum import Enum

from midil.event.connector.health import ConnectorHealth


class ConnectorDirection(str, Enum):
    SOURCE = "source"  # emits events (consumer)
    DESTINATION = "destination"  # receives events (producer)
    BIDIRECTIONAL = "bidirectional"


class Connector(ABC):
    """
    The fundamental unit of the MIDIL integration platform.

    Every source of events (consumer) and every destination for events
    (producer) implements this interface, giving the platform uniform
    lifecycle management, health reporting, and registry discovery
    regardless of the underlying transport.

    Subclasses declare their direction and implement connect/disconnect/health.
    The EventBus registers and orchestrates all connectors transparently.
    """

    @property
    @abstractmethod
    def name(self) -> str:
        """Stable identifier for this connector type (e.g. 'sqs', 'redis', 'stripe_webhook')."""
        ...

    @property
    @abstractmethod
    def direction(self) -> ConnectorDirection:
        """Whether this connector is a SOURCE, DESTINATION, or BIDIRECTIONAL."""
        ...

    @abstractmethod
    async def connect(self) -> None:
        """Establish the connection and prepare for operation."""
        ...

    @abstractmethod
    async def disconnect(self) -> None:
        """Tear down the connection and release all held resources."""
        ...

    @abstractmethod
    async def health(self) -> ConnectorHealth:
        """Report the current health of this connector."""
        ...

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} name={self.name!r} direction={self.direction.value!r}>"
