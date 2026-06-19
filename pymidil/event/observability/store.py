from __future__ import annotations

from abc import ABC, abstractmethod
from collections import deque
from typing import Dict, List, Optional

from pymidil.event.observability.trace import EventTrace, TraceStatus


class TraceStore(ABC):
    """
    Abstract persistence layer for event traces.

    Swap implementations to back traces with Redis, PostgreSQL, or any
    other store without touching the EventBus or connector code.
    The default InMemoryTraceStore is suitable for development and
    low-traffic services.
    """

    @abstractmethod
    async def save(self, trace: EventTrace) -> None:
        ...

    @abstractmethod
    async def get(self, trace_id: str) -> Optional[EventTrace]:
        ...

    @abstractmethod
    async def by_event(self, event_id: str) -> List[EventTrace]:
        ...

    @abstractmethod
    async def by_status(self, status: TraceStatus) -> List[EventTrace]:
        ...

    @abstractmethod
    async def recent(self, limit: int = 100) -> List[EventTrace]:
        ...


class InMemoryTraceStore(TraceStore):
    """
    Bounded in-memory store backed by a deque.

    Traces are evicted oldest-first when max_size is reached.
    The secondary index (_index) allows O(1) lookup by trace_id while
    the deque provides chronological ordering and bounded memory.
    """

    def __init__(self, max_size: int = 1000) -> None:
        self._traces: deque[EventTrace] = deque(maxlen=max_size)
        self._index: Dict[str, EventTrace] = {}

    async def save(self, trace: EventTrace) -> None:
        if len(self._traces) == self._traces.maxlen:
            evicted = self._traces[0]
            self._index.pop(evicted.trace_id, None)
        self._traces.append(trace)
        self._index[trace.trace_id] = trace

    async def get(self, trace_id: str) -> Optional[EventTrace]:
        return self._index.get(trace_id)

    async def by_event(self, event_id: str) -> List[EventTrace]:
        return [t for t in self._traces if t.event_id == event_id]

    async def by_status(self, status: TraceStatus) -> List[EventTrace]:
        return [t for t in self._traces if t.status == status]

    async def recent(self, limit: int = 100) -> List[EventTrace]:
        return list(self._traces)[-limit:]

    def __len__(self) -> int:
        return len(self._traces)
