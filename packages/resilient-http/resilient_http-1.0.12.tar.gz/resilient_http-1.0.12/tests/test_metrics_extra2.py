def test_metrics_sink_methods(monkeypatch):
    called = []

    class DummyMetrics:
        def record_circuit_state(self, key, state):
            called.append(("state", key, state))

        def record_retry(self, key, attempt):
            called.append(("retry", key, attempt))

        def record_request_latency(self, key, latency, ok):
            called.append(("latency", key, latency, ok))

    metrics = DummyMetrics()
    metrics.record_circuit_state("X", "open")
    metrics.record_retry("GET http://x", 1)
    metrics.record_request_latency("GET http://x", 0.05, True)

    assert len(called) == 3
