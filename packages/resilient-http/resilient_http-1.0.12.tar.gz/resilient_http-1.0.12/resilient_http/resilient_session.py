import logging
import time
import requests
from typing import Optional, Callable, Any
from .retry_policy import RetryPolicy
from .circuit_breaker import CircuitBreaker
from .metrics import MetricsSink


logger = logging.getLogger(__name__)
metrics: Optional[MetricsSink] = None


class ResilientRequestsSession:
    """HTTP session wrapper with retry logic, circuit breaker, and optional metrics."""

    def __init__(
        self,
        session: Optional[requests.Session] = None,
        retry_policy: Optional[RetryPolicy] = None,
        circuit_breaker: Optional[CircuitBreaker] = None,
        on_retry: Optional[Callable[[int, Any], None]] = None,
    ) -> None:
        self.session = session or requests.Session()
        self.retry_policy = retry_policy or RetryPolicy()
        self.cb = circuit_breaker or CircuitBreaker()
        self.on_retry = on_retry
        self.metrics = metrics

    def request(self, method: str, url: str, **kwargs: Any) -> requests.Response:
        """Perform an HTTP request with retries and circuit breaker handling."""
        key = f"{method.upper()} {url}"
        attempt = 0

        while True:
            if not self.cb.allow_call(key):
                raise RuntimeError(f"Circuit open for {key}")

            try:
                response = self.session.request(method, url, **kwargs)
            except Exception as exc:
                should, delay = self.retry_policy.should_retry_exception(exc, attempt)
                if not should:
                    self.cb.record_failure(key)
                    raise

                # Logging retry
                logger.debug(
                    f'event="retry" url="{url}" method="{method}" '
                    f"attempt={attempt} delay={delay:.3f}s reason={exc.__class__.__name__}"
                )

                if callable(self.on_retry):
                    self.on_retry(attempt, exc)

                time.sleep(delay)
                attempt += 1
                continue

            # Success path
            if response.status_code < 400:
                self.cb.record_success(key)
                if self.metrics:
                    self.metrics.record_request_latency(key, 0.0, True)
                return response

            # Retry path on HTTP error
            if self.retry_policy.should_retry(
                method, attempt, status=response.status_code
            ):
                delay = self.retry_policy.next_delay(attempt)

                logger.debug(
                    f'event="retry" url="{url}" method="{method}" '
                    f"attempt={attempt} delay={delay:.3f}s reason=status_{response.status_code}"
                )

                if callable(self.on_retry):
                    self.on_retry(attempt, response)

                time.sleep(delay)
                attempt += 1
                continue

            # Failure (no retry)
            if self.metrics:
                self.metrics.record_request_latency(key, 0.0, False)

            self.cb.record_failure(key)
            return response

    # Convenience wrappers
    def get(self, url: str, **kwargs: Any) -> requests.Response:
        """Wrapper for GET requests."""
        return self.request("GET", url, **kwargs)

    def post(self, url: str, **kwargs: Any) -> requests.Response:
        """Wrapper for POST requests."""
        return self.request("POST", url, **kwargs)

    def put(self, url: str, **kwargs: Any) -> requests.Response:
        """Wrapper for PUT requests."""
        return self.request("PUT", url, **kwargs)

    def delete(self, url: str, **kwargs: Any) -> requests.Response:
        """Wrapper for DELETE requests."""
        return self.request("DELETE", url, **kwargs)

    def head(self, url: str, **kwargs: Any) -> requests.Response:
        """Wrapper for HEAD requests."""
        return self.request("HEAD", url, **kwargs)
