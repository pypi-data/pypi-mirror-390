from dataclasses import dataclass, field
from typing import Iterable, Set, Callable, Type, Optional, Tuple
from requests import Timeout, ConnectionError as RequestsConnectionError
from httpx import ConnectError as HttpxConnectError, ReadTimeout as HttpxTimeout


@dataclass
class RetryPolicy:
    """Configurable retry strategy with backoff and status/exception rules."""

    max_attempts: int = 3
    retry_on_status: Set[int] = field(default_factory=lambda: {429, 500, 502, 503, 504})
    retry_on_exceptions: Iterable[Type[BaseException]] = (
        Timeout,
        RequestsConnectionError,
        HttpxConnectError,
        HttpxTimeout,
    )
    retry_on_methods: Set[str] = field(
        default_factory=lambda: {"GET", "HEAD", "PUT", "DELETE", "OPTIONS"}
    )
    backoff: Optional[Callable[[int], float]] = None
    give_up_on_status: Set[int] = field(default_factory=lambda: {400, 401, 403, 404})

    def __post_init__(self) -> None:
        # Import backoff lazily to avoid circular dependencies
        if self.backoff is None:
            from .backoff import full_jitter, exponential_backoff

            exp = exponential_backoff()
            self.backoff = full_jitter(exp)

        self.validate()

    # Validation
    def validate(self) -> None:
        if self.max_attempts < 1:
            raise ValueError("max_attempts must be >= 1")

        if not self.retry_on_methods:
            raise ValueError("retry_on_methods cannot be empty")

        for m in self.retry_on_methods:
            if m != m.upper():
                raise ValueError(f"HTTP method '{m}' must be uppercase")

        conflict = self.retry_on_status.intersection(self.give_up_on_status)
        if conflict:
            raise ValueError(
                f"Status codes present in both retry_on_status and give_up_on_status: {conflict}"
            )

    # Retry decision
    def should_retry(
        self,
        method: str,
        attempt: int,
        *,
        status: Optional[int] = None,
        exc: Optional[BaseException] = None,
    ) -> bool:
        """Decide whether a retry should occur for given attempt, status or exception."""
        if attempt >= self.max_attempts - 1:
            return False

        if method.upper() not in self.retry_on_methods:
            return False

        if exc is not None:
            return any(isinstance(exc, t) for t in self.retry_on_exceptions)

        if status is not None:
            if status in self.give_up_on_status:
                return False
            return status in self.retry_on_status

        return False

    # Delay computation
    def next_delay(self, attempt: int) -> float:
        """Compute backoff delay for the given retry attempt."""
        assert self.backoff is not None
        return float(self.backoff(attempt))

    # Convenience helper
    def should_retry_exception(
        self, exc: Exception, attempt: int
    ) -> Tuple[bool, float]:
        """Return (should_retry, delay) tuple for an exception."""
        if attempt >= self.max_attempts - 1:
            return False, 0.0

        retryable = any(isinstance(exc, t) for t in self.retry_on_exceptions)
        if not retryable:
            return False, 0.0

        return True, self.next_delay(attempt)
