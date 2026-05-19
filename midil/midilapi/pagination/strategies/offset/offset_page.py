from starlette.datastructures import URL

from midil.jsonapi.document import Links, MetaType
from midil.midilapi.pagination.mappers.page import PageMapper
from midil.midilapi.pagination.mappers.resource import DomainT, SchemaT
from midil.midilapi.pagination.strategies.offset.models import OffsetPage


class OffsetPageMapper(PageMapper[DomainT, SchemaT, OffsetPage[DomainT]]):
    def links(self, *, page: OffsetPage[DomainT], url: URL) -> Links:
        base = url.remove_query_params(["offset", "limit"])
        next_offset = page.offset + page.limit
        prev_offset = max(page.offset - page.limit, 0)

        return Links(
            self=str(url),
            next=(
                str(base.include_query_params(offset=next_offset, limit=page.limit))
                if next_offset < page.total
                else None
            ),
            prev=(
                str(base.include_query_params(offset=prev_offset, limit=page.limit))
                if page.offset > 0
                else None
            ),
        )

    def meta(self, *, page: OffsetPage[DomainT]) -> MetaType:
        return {
            "total": page.total,
            "limit": page.limit,
            "offset": page.offset,
        }
