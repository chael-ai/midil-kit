from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict

from midil.midilapi.pagination.strategies.cursor.enums import (
    PaginationDirection,
    SortDirection,
)


class CursorPayload(BaseModel):
    model_config = ConfigDict(
        frozen=True,
        extra="forbid",
    )

    version: int = 1

    id: str
    created_at: datetime

    direction: PaginationDirection = PaginationDirection.NEXT

    sort: SortDirection = SortDirection.DESC

    expires_at: datetime | None = None
