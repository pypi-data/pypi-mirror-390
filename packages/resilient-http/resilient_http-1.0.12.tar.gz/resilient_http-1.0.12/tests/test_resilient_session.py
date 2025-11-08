import requests
from resilient_http.resilient_session import ResilientRequestsSession
from resilient_http.retry_policy import RetryPolicy


def test_sync_retry_and_cb(monkeypatch):
    calls = {"count": 0}

    def fake_request(self, method, url, **_):
        calls["count"] += 1
        if calls["count"] < 2:
            raise requests.ConnectionError("boom")
        return type("R", (), {"status_code": 200})()

    monkeypatch.setattr(requests.Session, "request", fake_request)

    sess = ResilientRequestsSession(retry_policy=RetryPolicy(max_attempts=2))
    resp = sess.get("http://x.test")

    assert resp.status_code == 200
    assert calls["count"] == 2
