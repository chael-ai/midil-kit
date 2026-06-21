from typing import Any
from fastapi import FastAPI
from pymidil.web.exceptions import register_jsonapi_exception_handlers
from pymidil.web.responses import JSONAPIResponse
from pymidil.exceptions import CursorError, InvalidCursorError, ExpiredCursorError


class MidilAPI(FastAPI):
    """
    FastAPI subclass with midil conventions pre-wired.

    Differences from plain FastAPI:
    - Default response class is JSONAPIResponse (sets JSON:API content-type)
    - JSON:API exception handlers are registered automatically

    Usage:
        app = MidilAPI(title="My Service", version="1.0.0")
    """

    def __init__(self, **kwargs: Any) -> None:
        kwargs.setdefault("default_response_class", JSONAPIResponse)
        super().__init__(**kwargs)
        register_jsonapi_exception_handlers(self)


__all__ = [
    "MidilAPI",
    "register_jsonapi_exception_handlers",
    "JSONAPIResponse",
    "CursorError",
    "InvalidCursorError",
    "ExpiredCursorError",
]
