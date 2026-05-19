from typing import Generic
from midil.midilapi.pagination.models import (
    ItemT,
    Page,
)


class CursorPage(
    Page[ItemT],
    Generic[ItemT],
):
    next: str | None = None
    prev: str | None = None
