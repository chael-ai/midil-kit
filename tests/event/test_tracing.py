import pytest

from pymidil.event.tracing import (
    CORRELATION_ID_HEADER,
    TRACEPARENT_HEADER,
    TraceContext,
    TraceContextPropagator,
    continue_trace,
    current_trace,
    inject_current,
    trace_scope,
)


def test_new_root_has_no_parent_and_valid_ids():
    tc = TraceContext.new_root()
    assert tc.parent_span_id is None
    assert len(tc.trace_id) == 32
    assert len(tc.span_id) == 16


def test_child_keeps_trace_and_links_parent():
    root = TraceContext.new_root()
    child = root.child()
    assert child.trace_id == root.trace_id
    assert child.parent_span_id == root.span_id
    assert child.span_id != root.span_id


def test_traceparent_roundtrip():
    tc = TraceContext.new_root()
    parsed = TraceContext.from_traceparent(tc.to_traceparent())
    assert parsed is not None
    assert parsed.trace_id == tc.trace_id
    assert parsed.span_id == tc.span_id


@pytest.mark.parametrize(
    "bad",
    [
        "",
        "garbage",
        "00-xyz-abc-01",
        "00-" + "0" * 32 + "-" + "0" * 16 + "-01",  # all-zero ids
        "ff-" + "a" * 32 + "-" + "b" * 16 + "-01",  # invalid version
        "00-" + "a" * 31 + "-" + "b" * 16 + "-01",  # wrong trace length
    ],
)
def test_from_traceparent_rejects_malformed(bad):
    assert TraceContext.from_traceparent(bad) is None


def test_propagator_inject_then_extract_flat():
    propagator = TraceContextPropagator()
    tc = TraceContext.new_root()
    carrier: dict = {}
    propagator.inject(tc, carrier)
    assert carrier[TRACEPARENT_HEADER] == tc.to_traceparent()
    assert carrier[CORRELATION_ID_HEADER] == tc.trace_id
    extracted = propagator.extract(carrier)
    assert extracted is not None
    assert extracted.span_id == tc.span_id


def test_propagator_extracts_sqs_attribute_shape():
    propagator = TraceContextPropagator()
    tc = TraceContext.new_root()
    carrier = {
        "traceparent": {"DataType": "String", "StringValue": tc.to_traceparent()}
    }
    extracted = propagator.extract(carrier)
    assert extracted is not None
    assert extracted.span_id == tc.span_id


def test_continue_trace_starts_root_when_absent():
    ctx = continue_trace({})
    assert ctx.parent_span_id is None


def test_continue_trace_childs_incoming():
    parent = TraceContext.new_root()
    ctx = continue_trace({"traceparent": parent.to_traceparent()})
    assert ctx.trace_id == parent.trace_id
    assert ctx.parent_span_id == parent.span_id


def test_trace_scope_binds_and_resets():
    assert current_trace() is None
    tc = TraceContext.new_root()
    with trace_scope(tc):
        assert current_trace() is tc
    assert current_trace() is None


def test_inject_current_uses_active_trace():
    tc = TraceContext.new_root()
    carrier: dict = {}
    with trace_scope(tc):
        inject_current(carrier)
    assert carrier[TRACEPARENT_HEADER] == tc.to_traceparent()


def test_inject_current_starts_root_when_no_trace():
    carrier: dict = {}
    ctx = inject_current(carrier)
    assert ctx is not None
    assert TRACEPARENT_HEADER in carrier


def test_inject_current_can_skip_when_missing():
    carrier: dict = {}
    ctx = inject_current(carrier, start_if_missing=False)
    assert ctx is None
    assert carrier == {}
