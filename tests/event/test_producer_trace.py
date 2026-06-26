from pymidil.event.producer.base import EventProducer
from pymidil.event.producer.sqs import build_sqs_message_attributes
from pymidil.event.tracing import TRACEPARENT_HEADER, TraceContext, trace_scope


def test_build_sqs_message_attributes_filters_non_scalars():
    headers = {
        "traceparent": "00-abc",
        "count": 3,
        "flag": True,
        "obj": {"a": 1},
        "none": None,
    }
    attributes = build_sqs_message_attributes(headers)
    assert attributes["traceparent"] == {"DataType": "String", "StringValue": "00-abc"}
    assert attributes["count"]["StringValue"] == "3"
    assert "obj" not in attributes
    assert "none" not in attributes


def test_inject_trace_always_adds_traceparent():
    out = EventProducer._inject_trace({"k": "v"})
    assert out["k"] == "v"
    assert TRACEPARENT_HEADER in out


def test_inject_trace_uses_active_trace():
    tc = TraceContext.new_root()
    with trace_scope(tc):
        out = EventProducer._inject_trace(None)
    assert out[TRACEPARENT_HEADER] == tc.to_traceparent()
