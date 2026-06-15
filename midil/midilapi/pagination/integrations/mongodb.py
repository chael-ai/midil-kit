from __future__ import annotations

from typing import Callable, Dict, Generic, Any, TypeVar

try:
    from bson import ObjectId
    from pymongo.asynchronous.collection import AsyncCollection
except ImportError as e:
    raise ImportError(
        "MongoDB support requires the 'mongodb' extra: " "pip install midil[mongodb]"
    ) from e

from midil.midilapi.pagination.strategies.cursor.encoders.abstract import CursorEncoder
from midil.midilapi.pagination.strategies.cursor.enums import PaginationDirection
from midil.midilapi.pagination.strategies.cursor.models import CursorPayload
from midil.midilapi.pagination.strategies.cursor.page import CursorPage
from midil.midilapi.pagination.strategies.cursor.abstract import (
    CursorPaginationStrategy,
    ItemT,
)

_DocumentType = TypeVar("_DocumentType", bound=Dict[str, Any])


class AsyncMongoCursorPaginationStrategy(
    CursorPaginationStrategy[ItemT],
    Generic[ItemT],
):
    def __init__(
        self,
        *,
        collection: AsyncCollection[_DocumentType],
        encoder: CursorEncoder,
        mapper: Callable[[_DocumentType], ItemT],
        base_query: Dict[str, Any] | None = None,
    ) -> None:
        self._collection = collection
        self._encoder = encoder
        self._mapper = mapper
        self._base_query = base_query or {}

    async def paginate(
        self,
        *,
        size: int,
        cursor: str | None = None,
    ) -> CursorPage[ItemT]:
        query = dict(self._base_query)
        direction = PaginationDirection.NEXT

        if cursor:
            payload = self._encoder.decode(cursor)
            direction = payload.direction
            query.update(self._build_cursor_query(payload))

        documents = (
            await self._collection.find(query)
            .sort(self._build_sort(direction))
            .limit(size + 1)
            .to_list(length=size + 1)
        )

        has_extra = len(documents) > size
        documents = documents[:size]

        if direction == PaginationDirection.PREV:
            documents.reverse()

        items = [self._mapper(doc) for doc in documents]

        next_cursor = None
        prev_cursor = None

        if documents:
            if direction == PaginationDirection.NEXT:
                if has_extra:
                    next_cursor = self._encoder.encode(
                        self._payload(documents[-1], PaginationDirection.NEXT)
                    )
                if cursor is not None:
                    prev_cursor = self._encoder.encode(
                        self._payload(documents[0], PaginationDirection.PREV)
                    )
            else:
                if has_extra:
                    prev_cursor = self._encoder.encode(
                        self._payload(documents[0], PaginationDirection.PREV)
                    )
                next_cursor = self._encoder.encode(
                    self._payload(documents[-1], PaginationDirection.NEXT)
                )

        return CursorPage(
            items=items,
            size=size,
            next=next_cursor,
            prev=prev_cursor,
        )

    def _payload(
        self, doc: Dict[str, Any], direction: PaginationDirection
    ) -> CursorPayload:
        return CursorPayload(
            id=str(doc["_id"]),
            created_at=doc["created_at"],
            direction=direction,
        )

    def _build_cursor_query(self, payload: CursorPayload) -> Dict[str, Any]:
        op = "$lt" if payload.direction == PaginationDirection.NEXT else "$gt"
        return {
            "$or": [
                {"created_at": {op: payload.created_at}},
                {"created_at": payload.created_at, "_id": {op: ObjectId(payload.id)}},
            ]
        }

    def _build_sort(self, direction: PaginationDirection) -> list[tuple[str, int]]:
        order = -1 if direction == PaginationDirection.NEXT else 1
        return [("created_at", order), ("_id", order)]
