import pytest
from resilient_http.circuit_breaker import CircuitBreaker


@pytest.mark.parametrize(
    "args",
    [
        {"failure_threshold": 0},
        {"recovery_timeout": 0},
        {"half_open_max_calls": 0},
    ],
)
def test_cb_invalid_values(args):
    """Validate raises for invalid circuit breaker configs."""
    with pytest.raises(ValueError):
        CircuitBreaker(**args)
