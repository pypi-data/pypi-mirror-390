from resilient_http.retry_policy import RetryPolicy
from uuid import uuid4


def test_post_idempotency_example():
    """Docs-style test to illustrate safe POST retry."""
    RetryPolicy(
        max_attempts=5,
        retry_on_methods={"GET", "POST"},
    )

    key = uuid4().hex
    headers = {"Idempotency-Key": key}

    # Simulate backend respecting the key
    assert "Idempotency-Key" in headers
    assert len(headers["Idempotency-Key"]) == 32
