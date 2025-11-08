import time
import logging
from dataclasses import dataclass, field
from typing import Dict, Callable, Optional, Set
from .metrics import MetricsSink

logger = logging.getLogger(__name__)


@dataclass
class CircuitBreaker:
    """Lightweight circuit breaker with metrics and structured logging."""

    failure_threshold: int = 5
    recovery_timeout: float = 30.0
    half_open_max_calls: int = 1

    metrics: Optional[MetricsSink] = None

    on_open: Optional[Callable[[str], None]] = None
    on_half_open: Optional[Callable[[str], None]] = None
    on_closed: Optional[Callable[[str], None]] = None

    _failures: Dict[str, int] = field(default_factory=dict)
    _open_until: Dict[str, float] = field(default_factory=dict)
    _half_open_calls: Dict[str, int] = field(default_factory=dict)
    _half_open_notified: Set[str] = field(default_factory=set)

    def __post_init__(self) -> None:
        self._failures = {}
        self._open_until = {}
        self._half_open_calls = {}
        self._half_open_notified = set()
        self.validate()

    def validate(self) -> None:
        if self.failure_threshold < 1:
            raise ValueError("failure_threshold must be >= 1")
        if self.recovery_timeout <= 0:
            raise ValueError("recovery_timeout must be > 0")
        if self.half_open_max_calls < 1:
            raise ValueError("half_open_max_calls must be >= 1")

    def state(self, key: str) -> str:
        """Return current state: closed / open / half-open"""
        now = time.time()
        if key in self._open_until:
            if now >= self._open_until[key]:
                if key not in self._half_open_notified:
                    self._half_open_notified.add(key)
                    if callable(self.on_half_open):
                        self.on_half_open(key)
                    logger.info(f'event="cb_half_open" key="{key}"')
                    if self.metrics:
                        self.metrics.record_circuit_state(key, "half-open")
                return "half-open"
            return "open"
        return "closed"

    def record_success(self, key: str) -> None:
        """Mark a successful call and possibly close the circuit."""
        self._failures[key] = 0
        was_open = key in self._open_until
        self._open_until.pop(key, None)
        self._half_open_calls.pop(key, None)
        self._half_open_notified.discard(key)
        if was_open:
            if callable(self.on_closed):
                self.on_closed(key)
            logger.info(f'event="cb_closed" key="{key}"')
            if self.metrics:
                self.metrics.record_circuit_state(key, "closed")

    def record_failure(self, key: str) -> None:
        self._failures[key] = self._failures.get(key, 0) + 1
        if self._failures[key] >= self.failure_threshold:
            already_open = key in self._open_until
            self._open_until[key] = time.time() + self.recovery_timeout
            if not already_open:
                logger.info(
                    f'event="cb_open" key="{key}" failures={self._failures.get(key, 0)}'
                )
                if self.metrics:
                    self.metrics.record_circuit_state(key, "open")
                if callable(self.on_open):
                    self.on_open(key)

    def allow_call(self, key: str) -> bool:
        """Check if a request is allowed under current state."""
        state = self.state(key)
        if state == "closed":
            return True
        if state == "open":
            return False
        calls = self._half_open_calls.get(key, 0)
        if calls < self.half_open_max_calls:
            self._half_open_calls[key] = calls + 1
            return True
        return False
