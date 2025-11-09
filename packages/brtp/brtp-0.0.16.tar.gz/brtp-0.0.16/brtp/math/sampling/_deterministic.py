"""A set of functions for generating deterministic samples in a given range."""

import math


def linspace(min_value: float, max_value: float, n: int, inclusive: bool = True) -> list[float]:
    """Generate n linearly spaced samples in [min_value, max_value]."""
    if inclusive:
        dv = (max_value - min_value) / (n - 1)
        v0 = min_value
    else:
        dv = (max_value - min_value) / n
        v0 = min_value + (0.5 * dv)

    return [v0 + i * dv for i in range(n)]


def logspace(min_value: float, max_value: float, n: int, inclusive: bool = True) -> list[float]:
    """Generate n logarithmically spaced samples in [min_value, max_value]."""
    return [math.exp(v) for v in linspace(math.log(min_value), math.log(max_value), n, inclusive)]
