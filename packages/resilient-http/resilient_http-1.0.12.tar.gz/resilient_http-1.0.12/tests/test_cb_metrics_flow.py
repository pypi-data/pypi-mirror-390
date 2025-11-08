import time
from resilient_http.circuit_breaker import CircuitBreaker
from resilient_http.metrics import InMemoryMetricsSink


def test_cb_metrics_flow():
    sink = InMemoryMetricsSink()
    events = []

    cb = CircuitBreaker(
        failure_threshold=1,
        recovery_timeout=0.1,
        metrics=sink,
        on_open=lambda k: events.append("open"),
        on_half_open=lambda k: events.append("half"),
        on_closed=lambda k: events.append("closed"),
    )

    key = "GET https://api.test"

    cb.record_failure(key)
    assert "open" in events
    assert cb.state(key) == "open"

    time.sleep(0.12)
    assert cb.state(key) == "half-open"
    assert "half" in events

    cb.record_success(key)
    assert "closed" in events

    summary = sink.summary()
    data = summary[key]
    assert data["open_events"] == 1
    assert data["half_open_events"] == 1
    assert data["closed_events"] == 1
