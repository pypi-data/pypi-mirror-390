import pytest
import httpx

from resilient_http.resilient_async_client import ResilientAsyncClient
from resilient_http.retry_policy import RetryPolicy
from resilient_http.circuit_breaker import CircuitBreaker
from resilient_http.exceptions import CircuitBreakerOpenError


@pytest.mark.asyncio
async def test_retry_and_success():
    call_count = {"n": 0}

    async def handler(request):
        call_count["n"] += 1
        if call_count["n"] == 1:
            return httpx.Response(503)
        return httpx.Response(200, text="OK")

    transport = httpx.MockTransport(handler)
    inner_client = httpx.AsyncClient(transport=transport)

    retry_policy = RetryPolicy(max_attempts=2)

    async with ResilientAsyncClient(
        client=inner_client, retry_policy=retry_policy
    ) as client:
        response = await client.get("http://test.local/resource")
        assert response.status_code == 200
        assert response.text == "OK"


@pytest.mark.asyncio
async def test_circuit_breaker_blocks():
    breaker = CircuitBreaker(failure_threshold=1, recovery_timeout=999)
    async with ResilientAsyncClient(circuit_breaker=breaker) as client:
        # Симулираме failure — circuit се отваря
        breaker.record_failure("GET http://mock")

        with pytest.raises(CircuitBreakerOpenError):
            await client.get("http://mock")
