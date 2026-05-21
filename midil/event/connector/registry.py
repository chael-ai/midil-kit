from __future__ import annotations

from typing import Dict, List, Optional

from midil.event.connector.base import Connector, ConnectorDirection
from midil.event.connector.health import ConnectorHealth


class ConnectorRegistry:
    """
    Central registry for all active connectors in an EventBus.

    Connectors self-describe their direction and health. The registry
    provides discovery, directional filtering, and aggregate health
    reporting — the data layer for the future MIDIL dashboard.

    Connectors are registered by their logical name (set by the EventBus
    at configuration time) rather than their type, so multiple connectors
    of the same type (e.g. two SQS consumers) coexist without collision.
    """

    def __init__(self) -> None:
        self._connectors: Dict[str, Connector] = {}

    def register(self, connector: Connector, name: Optional[str] = None) -> None:
        key = name or connector.name
        self._connectors[key] = connector

    def unregister(self, name: str) -> None:
        self._connectors.pop(name, None)

    def get(self, name: str) -> Optional[Connector]:
        return self._connectors.get(name)

    def all(self) -> List[Connector]:
        return list(self._connectors.values())

    def by_direction(self, direction: ConnectorDirection) -> List[Connector]:
        return [
            c
            for c in self._connectors.values()
            if c.direction in (direction, ConnectorDirection.BIDIRECTIONAL)
        ]

    async def health_report(self) -> Dict[str, ConnectorHealth]:
        return {
            name: await connector.health()
            for name, connector in self._connectors.items()
        }

    def __len__(self) -> int:
        return len(self._connectors)

    def __contains__(self, name: str) -> bool:
        return name in self._connectors

    def __repr__(self) -> str:
        return f"<ConnectorRegistry connectors={list(self._connectors.keys())}>"
