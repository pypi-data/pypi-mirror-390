import threading
from typing import Protocol, Dict, Any, List


class MetricsSink(Protocol):
    """Interface for structured observability of retries and circuit breaker events."""

    def record_retry(
        self, key: str, attempt: int, reason: str, delay: float
    ) -> None: ...
    def record_circuit_state(self, key: str, state: str) -> None: ...
    def record_request_latency(
        self, key: str, latency: float, success: bool
    ) -> None: ...


class InMemoryMetricsSink:
    """Lightweight in-process metrics collector (client-grade, thread-safe)."""

    def __init__(self) -> None:
        self._lock = threading.Lock()
        self.data: Dict[str, Dict[str, Any]] = {}

    def _get_entry(self, key: str) -> Dict[str, Any]:
        with self._lock:
            if key not in self.data:
                entry: Dict[str, Any] = {
                    "retries": 0,
                    "failures": 0,
                    "successes": 0,
                    "open_events": 0,
                    "half_open_events": 0,
                    "closed_events": 0,
                    "latencies": [],
                }
                self.data[key] = entry
            return self.data[key]

    def record_retry(self, key: str, attempt: int, reason: str, delay: float) -> None:
        entry = self._get_entry(key)
        entry["retries"] += 1
        print(
            f"[metrics] RETRY key={key} attempt={attempt} delay={delay:.3f}s reason={reason}"
        )

    def record_circuit_state(self, key: str, state: str) -> None:
        entry = self._get_entry(key)
        if state == "open":
            entry["open_events"] += 1
        elif state == "half-open":
            entry["half_open_events"] += 1
        elif state == "closed":
            entry["closed_events"] += 1
        print(f"[metrics] CB key={key} state={state}")

    def record_request_latency(self, key: str, latency: float, success: bool) -> None:
        entry = self._get_entry(key)
        entry["latencies"].append(latency)
        if success:
            entry["successes"] += 1
        else:
            entry["failures"] += 1

    def summary(self) -> Dict[str, Dict[str, Any]]:
        """Return summarized view for dashboards or export."""
        return self.data

    def average_latency(self, key: str) -> float:
        entry = self.data.get(key)
        if not entry or not entry["latencies"]:
            return 0.0
        latencies: List[float] = entry["latencies"]
        return sum(latencies) / len(latencies)
