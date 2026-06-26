"""A1 + A2 together over the real dispatch path (no broker needed)."""

import pytest

from pymidil.event.consumer.strategies.base import BaseConsumerConfig, EventConsumer
from pymidil.event.message import Message
from pymidil.event.observability import EventStatus, TelemetryDispatchHook
from pymidil.event.observability.sinks.base import TelemetrySink
from pymidil.event.subscriber.base import FunctionSubscriber
from pymidil.event.tracing import TraceContext, current_trace

pytestmark = pytest.mark.anyio


@pytest.fixture
def anyio_backend() -> str:
    # dispatch() is asyncio-native (asyncio.gather/TaskGroup), so pin these
    # real-dispatch integration tests to the asyncio backend.
    return "asyncio"


class _MemConfig(BaseConsumerConfig):
    type: str = "memory"


class _MemConsumer(EventConsumer):
    async def start(self) -> None:
        ...

    async def stop(self) -> None:
        ...

    async def ack(self, message) -> None:
        ...

    async def nack(self, message, requeue: bool = False) -> None:
        ...


class ListSink(TelemetrySink):
    def __init__(self) -> None:
        self.events: list = []

    async def emit(self, envelope) -> None:
        self.events.append(envelope)


async def test_dispatch_continues_trace_and_emits_success():
    seen: dict = {}

    async def handler(event):
        seen["trace"] = current_trace()

    consumer = _MemConsumer(_MemConfig())
    consumer.subscribe(FunctionSubscriber(handler=handler))
    sink = ListSink()
    consumer.add_hook(TelemetryDispatchHook(sink, source_service="booking-svc"))

    parent = TraceContext.new_root()
    msg = Message(
        id="EVT-9",
        body={"x": 1},
        metadata={
            "traceparent": parent.to_traceparent(),
            "event_type": "BookingCreated",
        },
    )
    await consumer.dispatch(msg)

    # A1: handler observed a child of the incoming trace
    ctx = seen["trace"]
    assert ctx is not None
    assert ctx.trace_id == parent.trace_id
    assert ctx.parent_span_id == parent.span_id

    # A2: a correlated success envelope was emitted
    assert len(sink.events) == 1
    env = sink.events[0]
    assert env.status == EventStatus.SUCCESS
    assert env.event_id == "EVT-9"
    assert env.event_type == "BookingCreated"
    assert env.trace_id == parent.trace_id


async def test_dispatch_starts_root_when_no_incoming_trace():
    seen: dict = {}

    async def handler(event):
        seen["trace"] = current_trace()

    consumer = _MemConsumer(_MemConfig())
    consumer.subscribe(FunctionSubscriber(handler=handler))
    await consumer.dispatch(Message(id="m", body={}))

    assert seen["trace"] is not None
    assert seen["trace"].parent_span_id is None
