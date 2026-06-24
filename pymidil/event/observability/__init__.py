from pymidil.event.observability.config import (
    TelemetrySettings,
    attach_telemetry,
    create_sink,
    create_telemetry_hook,
)
from pymidil.event.observability.emitter import TelemetryDispatchHook
from pymidil.event.observability.envelope import EventStatus, TelemetryEnvelope
from pymidil.event.observability.hooks import DispatchHook
from pymidil.event.observability.protocols import MessageProtocol
from pymidil.event.observability.sinks import (
    NullTelemetrySink,
    StdoutTelemetrySink,
    TelemetrySink,
)

__all__ = [
    # extension points
    "DispatchHook",
    "MessageProtocol",
    # telemetry contract
    "TelemetryEnvelope",
    "EventStatus",
    # emitter (A2)
    "TelemetryDispatchHook",
    # sinks
    "TelemetrySink",
    "StdoutTelemetrySink",
    "NullTelemetrySink",
    # config / wiring
    "TelemetrySettings",
    "create_sink",
    "create_telemetry_hook",
    "attach_telemetry",
]
