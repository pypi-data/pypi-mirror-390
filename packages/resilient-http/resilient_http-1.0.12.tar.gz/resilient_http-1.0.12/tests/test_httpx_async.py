import pytest
import httpx
from resilient_http.resilient_async_client import ResilientAsyncClient
from resilient_http.retry_policy import RetryPolicy
from resilient_http.circuit_breaker import CircuitBreaker


@pytest.mark.asyncio
async def test_async_retry_and_circuitbreaker(monkeypatch):
    calls = {"n": 0}

    async def failing_handler(request):
        calls["n"] += 1
        if calls["n"] < 3:
            raise httpx.ConnectError("mock fail", request=request)
        return httpx.Response(200, json={"ok": True})

    transport = httpx.MockTransport(failing_handler)
    retry_policy = RetryPolicy(max_attempts=3)
    cb = CircuitBreaker(failure_threshold=2, recovery_timeout=0.1)

    inner_client = httpx.AsyncClient(transport=transport)
    async with ResilientAsyncClient(
        client=inner_client, retry_policy=retry_policy, circuit_breaker=cb
    ) as client:
        response = await client.get("https://test.local")
        assert response.status_code == 200
        assert calls["n"] == 3
