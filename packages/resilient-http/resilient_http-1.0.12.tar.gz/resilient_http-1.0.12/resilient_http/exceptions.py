class ResilientHTTPError(Exception):
    """Base exception for resilient HTTP errors."""


class CircuitOpenError(ResilientHTTPError):
    """Kept for backward compatibility (old name)."""


class CircuitBreakerOpenError(ResilientHTTPError):
    """Circuit breaker is open and request is blocked."""


class RetryError(ResilientHTTPError):
    """Raised when a retryable response or exception triggers a retry."""
