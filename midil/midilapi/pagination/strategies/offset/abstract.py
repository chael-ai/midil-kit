from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Generic, TypeVar

from midil.midilapi.pagination.strategies.offset.models import OffsetPage

ItemT = TypeVar("ItemT")


class OffsetPaginationStrategy(ABC, Generic[ItemT]):
    @abstractmethod
    async def paginate(self, *, offset: int = 0, limit: int) -> OffsetPage[ItemT]:
        ...
