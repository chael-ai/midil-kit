class CursorError(Exception):
    """Base cursor exception."""


class InvalidCursorError(CursorError):
    """Raised when cursor is malformed."""


class ExpiredCursorError(CursorError):
    """Raised when cursor is expired."""
