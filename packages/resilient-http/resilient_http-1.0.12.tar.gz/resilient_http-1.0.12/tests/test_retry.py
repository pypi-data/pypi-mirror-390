import pytest
from resilient_http.retry_policy import RetryPolicy
from requests import Timeout


def test_retry_should_retry_status_and_methods():
    policy = RetryPolicy(max_attempts=3)

    # Retry on 503
    assert policy.should_retry("GET", 0, status=503)
    # Should not retry 404
    assert not policy.should_retry("GET", 0, status=404)
    # Should not retry POST if not configured
    assert not policy.should_retry("POST", 0, status=503)

    # Adding POST explicitly
    policy.retry_on_methods.add("POST")
    assert policy.should_retry("POST", 0, status=503)


def test_retry_should_retry_exception():
    policy = RetryPolicy(max_attempts=3)
    exc = Timeout()
    should, delay = policy.should_retry_exception(exc, attempt=0)
    assert should
    assert delay > 0.0


def test_retry_conflict_validation():
    # Conflicting status sets should raise ValueError
    with pytest.raises(ValueError):
        RetryPolicy(
            max_attempts=2, retry_on_status={500}, give_up_on_status={500}
        ).validate()
