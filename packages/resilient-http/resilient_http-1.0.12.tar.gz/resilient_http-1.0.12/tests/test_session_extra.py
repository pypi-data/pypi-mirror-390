import requests
from resilient_http.resilient_session import ResilientRequestsSession
from resilient_http.retry_policy import RetryPolicy
from resilient_http.circuit_breaker import CircuitBreaker


def test_sync_retry_then_success(monkeypatch):
    retry_policy = RetryPolicy(max_attempts=2)
    cb = CircuitBreaker()

    responses = [
        requests.ConnectionError("fail"),
        type("R", (), {"status_code": 200})(),
    ]
    session = ResilientRequestsSession(retry_policy=retry_policy, circuit_breaker=cb)

    def fake_request(method, url, **kw):
        result = responses.pop(0)
        if isinstance(result, Exception):
            raise result
        return result

    session.session.request = fake_request

    resp = session.get("http://ok.test")
    assert resp.status_code == 200
