from functools import lru_cache
from typing import Iterable

import numpy as np

from brtp.compat import numba
from brtp.misc.argument_handling import count_not_none


# =================================================================================================
#  Regular mean
# =================================================================================================
def mean(values: Iterable[int | float]) -> float:
    """compute arithmetic mean of provided values"""
    values = list(values)
    if len(values) == 0:
        return 0.0
    else:
        return float(np.mean(values))


def weighted_mean(values: Iterable[int | float], weights: Iterable[int | float]) -> float:
    """compute weighted arithmetic mean of provided values"""
    values = list(values)
    weights = list(weights)
    if len(values) == 0:
        return 0.0
    else:
        v = np.array(values)
        w = np.array(weights)
        return float(np.sum(w * v) / np.sum(w))


def ordered_weighted_mean(values: Iterable[int | float], c: float | None = None, q: float | None = None) -> float:
    """
    Compute Ordered Weighted Average (OWA) of provided values using exponential weights:

        w_i ~ e^(c*(i/(n-1))),  with i the index into the sorted array & n the array size

    Procedure:
     - sort all values in ascending order  (i=0 --> smallest value, i=n-1 --> largest value)
     - compute weights according to the exponential function with parameter 'c'
     - compute the weighted average of the sorted values with these weights

    Depending on the c-parameter, we tend to prioritize smaller values (c < 0) or larger values (c > 0), to compute
    the aggregation.  A characterization of this effect is given by the 'orness' measure, which is defined as:

        orness = 1/(n-1) * sum_{i=0...n-1} (i * w_i )     (assuming values are sorted ascendingly)

    A value of 1 corresponds to taking the maximum value, a value of 0 corresponds to taking the minimum value.

    Note that 'orness' (OR-ness) originates from decision theory, where aggregation represents taking a decision based
    on multiple criteria.  If we take the maximum of all criteria, it means we decide positively if at least one
    criterion is positive (OR logic).  Hence, taking the maximum of all values corresponds to an OR-ness of 1.

    An alternative interpretation of 'orness' is that it represents the quantile of the values that is favored in the
    aggregation:

        orness = 0.1  --> we emphasize values around the 10%-quantile when aggregating.
        orness = 0.5  --> no bias, corresponds to regular mean.
        orness = 0.7  --> we emphasize values around the 70%-quantile when aggregating.

    The concept of OWA operators was introduced by Yager [1], and the method to obtain the weights
    using the exponential function was proposed by Filev & Yager [2].

    Important to note is that exponential weights correspond to the maximum-entropy solution under the constraint of
    a given orness [2].  Maximum-entropy in this case can also be interpreted loosely as 'as close to uniform weights
    as possible'.  Hence, exponential weighting tries to take as many values into account while achieving the requested
    orness (or target quantile).

    This specific implementation allows to specify the averaging bias in two ways:
      - directly via the 'c' parameter
      - indirectly via the target quantile 'q' (or orness = q), from which the corresponding 'c' parameter is computed.

    The correspondence looks roughly like this (relation is point-symmetric around c=0, q=0.5):

           c       q
          0.0     0.50
          1.0    ~0.58
          5.0    ~0.80
         10.0    ~0.90

    References:
        [1] Yager, R. R. (1988). "On ordered weighted averaging aggregation operators in multicriteria decision-making."
            IEEE Transactions on Systems, Man, and Cybernetics, 18(1), 183-190.
        [2] Filev, D., & Yager, R.R. (1998). "On the issue of obtaining OWA operator weights."
            Fuzzy Sets and Systems, 94(1), 157-169
    """

    # --- argument handling -------------------------------
    if count_not_none(c, q) != 1:
        raise ValueError("Exactly one of the parameters 'c' or 'q' must be provided (the other set to None).")
    if c is None:
        c = _compute_c_for_target_quantile(q)

    # --- actual computation ------------------------------
    if c == 0:
        return mean(values)
    else:
        sorted_values = sorted(values)
        return weighted_mean(
            values=sorted_values,
            weights=_exponential_weights(c, len(sorted_values)),
        )


# =================================================================================================
#  Geometric mean
# =================================================================================================
def geo_mean(values: Iterable[int | float]) -> float:
    """compute geometric mean of provided values"""
    values = list(values)
    if len(values) == 0:
        return 1.0
    if any(v == 0 for v in values):
        return 0.0
    else:
        return float(np.exp(np.mean(np.log(np.array(values)))))


def weighted_geo_mean(values: Iterable[int | float], weights: Iterable[int | float]) -> float:
    """compute weighted geometric mean of provided values"""
    values = list(values)
    weights = list(weights)
    if len(values) == 0:
        return 1.0
    if any((v == 0) and (w > 0) for w, v in zip(weights, values)):
        return 0.0
    else:
        # convert to numpy arrays
        v = np.array(values)
        w = np.array(weights) / sum(weights)  # normalized array of weights
        # prune v,w to only positive weights
        v = v[w != 0]
        w = w[w != 0]
        # compute weighted geometric mean
        return float(np.exp(np.sum(w * np.log(v))))


def ordered_weighted_geo_mean(values: Iterable[int | float], c: float | None = None, q: float | None = None) -> float:
    """
    Compute Ordered Weighted Geometric Average (OWGA) of provided values.

    This is simply the geometric counterpart to the Ordered Weighted Average (OWA) implemented in ordered_weighted_mean.

    See docs there for details.
    """
    # --- argument handling -------------------------------
    if count_not_none(c, q) != 1:
        raise ValueError("Exactly one of the parameters 'c' or 'q' must be provided (the other set to None).")
    if c is None:
        c = _compute_c_for_target_quantile(q)

    # --- actual computation ------------------------------
    if c == 0:
        return geo_mean(values)
    else:
        sorted_values = sorted(values)
        return weighted_geo_mean(
            values=sorted_values,
            weights=_exponential_weights(c, len(sorted_values)),
        )


# =================================================================================================
#  Internal
# =================================================================================================
@lru_cache
def _exponential_weights(c: float, n: int) -> np.ndarray:
    return _exponential_weights_numba(float(c), int(n))


@numba.njit
def _exponential_weights_numba(c: float, n: int) -> np.ndarray:
    """
    Computes n exponential weights with parameter c to be used in weighted_(geo_)mean as follows:

      w = np.exp(c * np.linspace(0.0, 1.0, n)) / max(1, exp(c))

    We avoid computing the exponentiation n times by re-using the previous weight to compute the next one.
    Normalization is done to ensure that the maximum weight is 1.0; we prefer underflow to 0.0 over overflow to inf.
    """
    if n == 1:
        return np.ones(1)
    elif c == 0.0:
        return np.ones(n)
    else:
        factor = np.exp(-abs(c) / (n - 1))  # use -abs(c) to always generating decreasing sequence
        w = np.zeros(n)
        w_i = 1.0
        for i in range(n):
            w[i] = w_i
            w_i *= factor
        if c < 0:
            return w
        else:
            return w[::-1]  # -abs(c) flipped the sign of c, so reverse the array


@lru_cache
def _compute_c_for_target_quantile(q: float) -> float:
    """
    Compute the 'c' parameter to be used in ordered_weighted_(geo_)mean to achieve a target quantile 'q' or 'orness'.

    E.g. q = 0.8  -> we want to favor large values around 80%-quantile  ->  c ~  5.0
         q = 0.4  -> we want to favor small values around 40%-quantile  ->  c ~ -1.0

    We compute 'c' in a manner that is independent of 'n', which practically means we ignore discretization effects,
     and hence we will actually achieve a quantile / orness closer to 'q' as 'n' increases.

    Mathematically 'c' is computed by solving the equation:

        q = (integral_0^1  x * exp(c*x) dx) / (integral_0^1 exp(c*x) dx)

    NOTE: for mathematical stability, we only allow values of q in [0.01, 0.99],
    """
    if q == 0.5:
        return 0.0
    elif 0.01 <= q <= 0.99:
        return _compute_c_for_target_quantile_numba(float(q))
    else:
        raise ValueError(f"Target quantile 'q' must be in [0.01, 0.99], here q={q}")


@numba.njit
def _compute_c_for_target_quantile_numba(q: float) -> float:
    # initialize bisection
    c_min = -110.0  # coincides with q ~ 0.009, just beyond the allowed range of the q parameter
    c_max = 110.0  # coincides with q ~ 0.991, just beyond the allowed range of the q parameter

    # apply bisection
    while True:
        c_mid = 0.5 * (c_min + c_max)
        if (c_min < c_mid < c_max) and (c_max - c_min > 1e-16):
            # we can & should still reduce the interval
            q_mid = _compute_q_afo_c_numba(c_mid)
            if q_mid == q:
                return c_mid
            elif q_mid < q:
                c_min = c_mid
            else:
                c_max = c_mid
        else:
            # numerical precision limits reached
            return c_min


@numba.njit
def _compute_q_afo_c_numba(c: float) -> float:
    """
    Compute q as function of c:
        q = (integral_0^1  x * exp(c*x) dx) / (integral_0^1 exp(c*x) dx)
          = (exp(c) * (c - 1) + 1) / (c * (exp(c) - 1))

    Note that around c=0, we get q ~= 0.5, but ill-conditioned using the above formulate due to ~0/0.
    Hence, we use the Taylor expansion around c=0 to return q=0.5
    """
    if abs(c) < 1e-3:
        # taylor expansion around c=0:  f(c) = 0.5 + c/12 - c³/720 + c⁵/30240 - c⁷/1209600 + O(c⁹)
        c2 = c * c
        return 0.5 + c * (1 / 12 - c2 * (1 / 720 - c2 * (1 / 30240 - c2 * (1 / 1209600))))
    else:
        exp_c = np.exp(c)
        return (exp_c * (c - 1) + 1) / (c * (exp_c - 1))
