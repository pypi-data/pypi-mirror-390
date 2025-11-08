from resilient_http.backoff import exponential_backoff, full_jitter


def test_backoff_generators_behavior():
    backoff_fn = exponential_backoff(base=0.5, factor=2, max_delay=10)

    # simulate multiple retry attempts
    values = [backoff_fn(i) for i in range(6)]

    # all positive, capped at max_delay
    assert all(v > 0 for v in values)
    assert all(v <= 10 for v in values)
    assert values == sorted(values)


def test_full_jitter_range():
    base_backoff = exponential_backoff(base=1, factor=2)
    jittered = full_jitter(base_backoff)

    # Should produce random delay within [0, base_backoff(attempt)]
    for attempt in range(5):
        val = jittered(attempt)
        assert 0 <= val <= base_backoff(attempt)
