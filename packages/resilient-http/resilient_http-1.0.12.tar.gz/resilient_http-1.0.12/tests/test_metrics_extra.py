from resilient_http.metrics import MetricsSink


class DummyMetrics(MetricsSink):
    def __init__(self):
        self.events = []

    def record_retry(self, key, attempt, reason, delay):
        self.events.append(("retry", key, reason))

    def record_circuit_state(self, key, state):
        self.events.append(("state", key, state))

    def record_request_latency(self, key, latency, success):
        self.events.append(("latency", key, latency, success))


def test_metrics_callbacks():
    m = DummyMetrics()
    m.record_retry("url1", 1, "reason", 0.1)
    m.record_circuit_state("url1", "open")
    m.record_request_latency("url1", 0.25, True)

    assert len(m.events) == 3
    assert any(e[0] == "retry" for e in m.events)
