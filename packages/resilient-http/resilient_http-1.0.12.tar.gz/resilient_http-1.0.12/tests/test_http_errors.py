from resilient_http.retry_policy import RetryPolicy


def test_http_error_status_behavior():
    policy = RetryPolicy(max_attempts=3)

    # 429 should be retried
    assert policy.should_retry("GET", 0, status=429)
    # 400/404 should NOT be retried
    for status in [400, 401, 403, 404]:
        assert not policy.should_retry("GET", 0, status=status)
