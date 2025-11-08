import pytest
from resilient_http.retry_policy import RetryPolicy


def test_retry_validation_rules():
    # Valid case
    RetryPolicy(max_attempts=3).validate()

    # Invalid attempts
    with pytest.raises(ValueError):
        RetryPolicy(max_attempts=0).validate()

    # Empty methods
    with pytest.raises(ValueError):
        RetryPolicy(max_attempts=3, retry_on_methods=set()).validate()

    # Lowercase method
    with pytest.raises(ValueError):
        RetryPolicy(retry_on_methods={"get"}).validate()
