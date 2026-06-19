from abc import ABC, abstractmethod
from typing import Generic, TypeVar

from pymidil.midilapi.pagination.strategies.offset.models import OffsetPage

ItemT = TypeVar("ItemT")


class OffsetPaginationStrategy(ABC, Generic[ItemT]):
    @abstractmethod
    async def paginate(self, size: int, offset: int = 0) -> OffsetPage[ItemT]:
        ...
