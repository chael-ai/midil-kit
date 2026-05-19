from __future__ import annotations

from typing import Generic

from midil.midilapi.pagination.models import ItemT, Page


class OffsetPage(Page[ItemT], Generic[ItemT]):
    offset: int
    limit: int
    total: int
