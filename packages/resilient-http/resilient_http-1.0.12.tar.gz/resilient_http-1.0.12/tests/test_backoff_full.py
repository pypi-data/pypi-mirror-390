from resilient_http.backoff import exponential_backoff, full_jitter


def test_exponential_backoff_and_jitter_limits():
    exp = exponential_backoff(base=2, factor=1, max_delay=8)
    values = [exp(i) for i in range(6)]
    assert all(0 <= v <= 8 for v in values)

    # Pass a backoff function, not an int
    jitter_fn = full_jitter(exponential_backoff(base=2, factor=1, max_delay=5))
    for i in range(10):
        j = jitter_fn(i)
        assert 0 <= j <= 5
