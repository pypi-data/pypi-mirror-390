import time
import asyncio
import logging
import httpx
from typing import Optional, Callable, Any

from .retry_policy import RetryPolicy
from .circuit_breaker import CircuitBreaker
from .metrics import MetricsSink
from .exceptions import CircuitBreakerOpenError

logger = logging.getLogger(__name__)


class ResilientAsyncClient:
    def __init__(
        self,
        client: Optional[httpx.AsyncClient] = None,
        retry_policy: Optional[RetryPolicy] = None,
        circuit_breaker: Optional[CircuitBreaker] = None,
        metrics: Optional[MetricsSink] = None,
        on_retry: Optional[Callable[[int, Any], None]] = None,
    ):
        self.client = client or httpx.AsyncClient()
        self.retry_policy = retry_policy or RetryPolicy()
        self.circuit_breaker = circuit_breaker or CircuitBreaker(metrics=metrics)
        self.metrics = metrics
        self.on_retry = on_retry

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc, tb):
        if hasattr(self.client, "aclose"):
            await self.client.aclose()

    async def request(self, method: str, url: str, **kwargs):
        key = f"{method.upper()} {url}"

        if not self.circuit_breaker.allow_call(key):
            logger.info(f"Circuit open — skipping async call {key}")
            if self.metrics:
                self.metrics.record_circuit_state(key, "open")
            raise CircuitBreakerOpenError(f"CircuitBreaker open for {key}")

        for attempt in range(self.retry_policy.max_attempts):
            start = time.perf_counter()
            try:
                response = await self.client.request(method, url, **kwargs)
                latency = time.perf_counter() - start
                if self.metrics:
                    self.metrics.record_request_latency(key, latency, True)

                # Retry based on status code
                if response.status_code >= 400:
                    if self.retry_policy.should_retry(
                        method, attempt, status=response.status_code
                    ):
                        delay = self.retry_policy.next_delay(attempt)
                        logger.debug(
                            f"event='retry' url='{url}' attempt={attempt} delay={delay:.2f}s reason='status_{response.status_code}'"
                        )
                        if self.metrics:
                            self.metrics.record_retry(
                                key, attempt, f"status_{response.status_code}", delay
                            )
                        if callable(self.on_retry):
                            self.on_retry(attempt, response)
                        await asyncio.sleep(delay)
                        continue

                self.circuit_breaker.record_success(key)
                return response

            except Exception as exc:
                latency = time.perf_counter() - start
                if self.metrics:
                    self.metrics.record_request_latency(key, latency, False)

                should_retry, delay = self.retry_policy.should_retry_exception(
                    exc, attempt
                )
                if not should_retry:
                    self.circuit_breaker.record_failure(key)
                    raise

                logger.debug(
                    f"event='retry' url='{url}' attempt={attempt} delay={delay:.2f}s reason='{exc.__class__.__name__}'"
                )
                if self.metrics:
                    self.metrics.record_retry(
                        key, attempt, exc.__class__.__name__, delay
                    )
                if callable(self.on_retry):
                    self.on_retry(attempt, exc)
                await asyncio.sleep(delay)

        self.circuit_breaker.record_failure(key)
        raise RuntimeError(f"All async retry attempts failed for {key}")

    async def get(self, url: str, **kwargs) -> httpx.Response:
        return await self.request("GET", url, **kwargs)

    async def post(self, url: str, **kwargs) -> httpx.Response:
        return await self.request("POST", url, **kwargs)

    async def close(self):
        await self.client.aclose()
