"""Telemetry + trace propagation (A1 + A2).

Run: python examples/event/telemetry.py

Shows, without any broker, how:
  * a producer injects the current trace into outgoing message metadata (A1),
  * a consumer continues that trace on receive (A1),
  * the TelemetryDispatchHook emits a correlated envelope at each outcome (A2).
"""

import asyncio

from pymidil.event.consumer.strategies.base import BaseConsumerConfig, EventConsumer
from pymidil.event.message import Message
from pymidil.event.observability import StdoutTelemetrySink, TelemetryDispatchHook
from pymidil.event.subscriber.base import FunctionSubscriber
from pymidil.event.tracing import (
    TraceContext,
    current_trace,
    inject_current,
    trace_scope,
)


class InMemoryConsumer(EventConsumer):
    """A trivial consumer so the example needs no real transport."""

    async def start(self) -> None:
        ...

    async def stop(self) -> None:
        ...

    async def ack(self, message: Message) -> None:
        ...

    async def nack(self, message: Message, requeue: bool = False) -> None:
        ...


class _Config(BaseConsumerConfig):
    type: str = "memory"


async def handle(event: Message) -> None:
    trace = current_trace()
    print(
        f"  handler sees trace={trace.trace_id[:8]} span={trace.span_id[:8]} "
        f"parent={trace.parent_span_id[:8] if trace.parent_span_id else None}"
    )


async def main() -> None:
    # --- producer side: inject the active trace into outgoing metadata ---
    outgoing: dict = {"event_type": "BookingCreated"}
    with trace_scope(TraceContext.new_root()):
        sent = inject_current(outgoing)
    print(
        f"published with traceparent={outgoing['traceparent']} (trace={sent.trace_id[:8]})"
    )

    # --- consumer side: continue the trace + emit telemetry ---
    consumer = InMemoryConsumer(_Config())
    consumer.subscribe(FunctionSubscriber(handler=handle))
    consumer.add_hook(
        TelemetryDispatchHook(
            StdoutTelemetrySink(), source_service="booking-svc", broker="sqs"
        )
    )

    incoming = Message(id="EVT-1", body={"booking_id": "BK-44821"}, metadata=outgoing)
    await consumer.dispatch(
        incoming
    )  # extracts trace, runs handler, emits success envelope


if __name__ == "__main__":
    asyncio.run(main())
