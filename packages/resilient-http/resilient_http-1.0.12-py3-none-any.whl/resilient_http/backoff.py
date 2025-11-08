import random
from typing import Callable


def exponential_backoff(
    base: float = 0.25, factor: float = 2.0, max_delay: float = 30.0
) -> Callable[[int], float]:
    """
    Classic exponential backoff formula:
        delay = base * (factor ^ attempt)
    capped at max_delay.
    """

    def _fn(attempt: int) -> float:
        delay = base * (factor**attempt)
        return min(delay, max_delay)

    return _fn


def full_jitter(backoff_fn: Callable[[int], float]) -> Callable[[int], float]:
    """
    AWS-style full jitter:
        sleep(random(0, exponential))
    """

    def _fn(attempt: int) -> float:
        return random.uniform(0, backoff_fn(attempt))

    return _fn


def equal_jitter(backoff_fn: Callable[[int], float]) -> Callable[[int], float]:
    """
    Google SRE equal jitter:
        sleep(backoff/2 + random(0, backoff/2))
    """

    def _fn(attempt: int) -> float:
        d = backoff_fn(attempt)
        return d / 2 + random.uniform(0, d / 2)

    return _fn
