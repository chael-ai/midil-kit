"""Distributed trace context propagation (A1).

Carries a W3C `traceparent` (and a legacy `x-correlation-id`) through
``Message.metadata`` so event lineage survives broker hops. Producers inject the
current trace on publish; consumers continue it on receive (see
``EventConsumer.dispatch``). Pure stdlib — no pymidil imports — to stay a leaf
module free of cycles.

Carrier model follows the OpenTelemetry TextMap idea: a string-keyed mapping the
transport already moves (SQS message attributes, a Redis envelope, HTTP headers).
"""

from __future__ import annotations

import contextvars
import secrets
from contextlib import contextmanager
from dataclasses import dataclass
from typing import Any, Iterator, Mapping, MutableMapping, Optional

TRACEPARENT_HEADER = "traceparent"
CORRELATION_ID_HEADER = "x-correlation-id"

_VERSION = "00"
_INVALID_VERSION = "ff"
_FLAG_SAMPLED = "01"
_FLAG_UNSAMPLED = "00"
_ZERO_TRACE_ID = "0" * 32
_ZERO_SPAN_ID = "0" * 16


def _new_trace_id() -> str:
    return secrets.token_hex(16)  # 32 hex chars


def _new_span_id() -> str:
    return secrets.token_hex(8)  # 16 hex chars


@dataclass(frozen=True, slots=True)
class TraceContext:
    """An immutable point in a distributed trace."""

    trace_id: str
    span_id: str
    parent_span_id: Optional[str] = None
    sampled: bool = True

    @classmethod
    def new_root(cls) -> "TraceContext":
        """Begin a brand-new trace."""
        return cls(
            trace_id=_new_trace_id(), span_id=_new_span_id(), parent_span_id=None
        )

    def child(self) -> "TraceContext":
        """Derive a child span within the same trace (this span becomes the parent)."""
        return TraceContext(
            trace_id=self.trace_id,
            span_id=_new_span_id(),
            parent_span_id=self.span_id,
            sampled=self.sampled,
        )

    def to_traceparent(self) -> str:
        flag = _FLAG_SAMPLED if self.sampled else _FLAG_UNSAMPLED
        return f"{_VERSION}-{self.trace_id}-{self.span_id}-{flag}"

    @classmethod
    def from_traceparent(cls, value: str) -> Optional["TraceContext"]:
        """Parse a W3C traceparent. Returns None if malformed (never raises)."""
        try:
            version, trace_id, span_id, flags = value.strip().split("-")
        except (ValueError, AttributeError):
            return None
        if version == _INVALID_VERSION or len(trace_id) != 32 or len(span_id) != 16:
            return None
        if trace_id == _ZERO_TRACE_ID or span_id == _ZERO_SPAN_ID:
            return None
        try:
            int(trace_id, 16)
            int(span_id, 16)
            sampled = bool(int(flags, 16) & 0x01)
        except ValueError:
            return None
        return cls(
            trace_id=trace_id, span_id=span_id, parent_span_id=None, sampled=sampled
        )


def coerce_header_value(value: Any) -> Optional[str]:
    """Normalise a carrier value to a flat string.

    Tolerates SQS MessageAttribute shapes (``{"StringValue": "..."}``) so the same
    propagator works whether metadata is flat headers or AWS attribute dicts.
    """
    if value is None:
        return None
    if isinstance(value, Mapping):
        for key in ("StringValue", "stringValue", "Value", "value"):
            if key in value:
                return str(value[key])
        return None
    return str(value)


class TraceContextPropagator:
    """W3C Trace Context inject/extract over a string-keyed carrier."""

    def inject(self, context: TraceContext, carrier: MutableMapping[str, Any]) -> None:
        carrier[TRACEPARENT_HEADER] = context.to_traceparent()
        carrier.setdefault(CORRELATION_ID_HEADER, context.trace_id)

    def extract(self, carrier: Mapping[str, Any]) -> Optional[TraceContext]:
        raw = self._read(carrier, TRACEPARENT_HEADER)
        if raw is None:
            return None
        return TraceContext.from_traceparent(raw)

    @staticmethod
    def _read(carrier: Mapping[str, Any], key: str) -> Optional[str]:
        for candidate_key, candidate_value in carrier.items():
            if str(candidate_key).lower() == key:
                return coerce_header_value(candidate_value)
        return None


_DEFAULT_PROPAGATOR = TraceContextPropagator()

# Active trace for the current execution scope.
_current_trace: contextvars.ContextVar[TraceContext] = contextvars.ContextVar(
    "midil_trace"
)


def current_trace() -> Optional[TraceContext]:
    """The trace bound to the current scope, or None."""
    return _current_trace.get(None)


def bind_trace(context: TraceContext) -> contextvars.Token:
    return _current_trace.set(context)


def reset_trace(token: contextvars.Token) -> None:
    _current_trace.reset(token)


@contextmanager
def trace_scope(context: TraceContext) -> Iterator[TraceContext]:
    """Bind ``context`` as the current trace for the duration of the block."""
    token = _current_trace.set(context)
    try:
        yield context
    finally:
        _current_trace.reset(token)


def continue_trace(
    carrier: Mapping[str, Any],
    propagator: TraceContextPropagator = _DEFAULT_PROPAGATOR,
) -> TraceContext:
    """Resume the trace described by ``carrier`` as a child span.

    Starts a fresh root trace when the carrier has no (valid) traceparent.
    """
    incoming = propagator.extract(carrier)
    return incoming.child() if incoming is not None else TraceContext.new_root()


def inject_current(
    carrier: MutableMapping[str, Any],
    *,
    start_if_missing: bool = True,
    propagator: TraceContextPropagator = _DEFAULT_PROPAGATOR,
) -> Optional[TraceContext]:
    """Inject the current trace into ``carrier``.

    If no trace is bound and ``start_if_missing`` is True, a root trace is created
    so the outgoing message is still traceable.
    """
    context = current_trace()
    if context is None:
        if not start_if_missing:
            return None
        context = TraceContext.new_root()
    propagator.inject(context, carrier)
    return context
