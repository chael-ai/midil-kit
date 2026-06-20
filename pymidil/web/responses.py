from fastapi.responses import JSONResponse
from pymidil.jsonapi import Document, ErrorDocument
from typing import Any
from pymidil.jsonapi.document import JSONAPI_CONTENT_TYPE


class JSONAPIResponse(JSONResponse):
    def __init__(self, document: Document[Any] | ErrorDocument, **kwargs):
        super().__init__(
            content=document.model_dump(exclude_none=True),
            media_type=JSONAPI_CONTENT_TYPE,
            **kwargs,
        )
