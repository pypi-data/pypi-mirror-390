import logging
from resilient_http.circuit_breaker import CircuitBreaker


def test_logging_cb_transitions(caplog):
    caplog.set_level(logging.INFO)

    cb = CircuitBreaker(failure_threshold=1, recovery_timeout=0.1)
    key = "GET https://api/logs"

    cb.record_failure(key)
    cb.state(key)
    cb.record_success(key)

    logs = caplog.text
    assert "cb_open" in logs
    assert "cb_closed" in logs
