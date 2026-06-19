from typing import Generic

from pymidil.midilapi.pagination.models import ItemT, Page


class OffsetPage(Page[ItemT], Generic[ItemT]):
    offset: int
    total: int
