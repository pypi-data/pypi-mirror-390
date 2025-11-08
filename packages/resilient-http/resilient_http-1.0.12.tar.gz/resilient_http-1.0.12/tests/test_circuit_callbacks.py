import time
from resilient_http.circuit_breaker import CircuitBreaker


def test_cb_callbacks_smoke():
    events = []

    cb = CircuitBreaker(
        failure_threshold=1,
        recovery_timeout=0.1,
        on_open=lambda k: events.append("open"),
        on_half_open=lambda k: events.append("half"),
        on_closed=lambda k: events.append("closed"),
    )

    key = "X"
    cb.record_failure(key)
    assert "open" in events
    assert cb.state(key) == "open"

    time.sleep(0.12)
    assert cb.state(key) == "half-open"
    assert "half" in events

    cb.record_success(key)
    assert "closed" in events
