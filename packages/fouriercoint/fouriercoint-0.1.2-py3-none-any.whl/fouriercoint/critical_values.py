"""
Critical Values for Fourier Cointegration Test
==============================================

Asymptotic critical values from Tsong et al. (2016), Table 1.
Simulated with T=1000 and 5000 replications (as reported in the paper).

Reference
---------
Tsong, C.C., Lee, C.F., Tsai, L.J., & Hu, T.C. (2016).
The Fourier approximation and testing for the null of cointegration.
Empirical Economics, 51(3), 1085–1113. https://doi.org/10.1007/s00181-015-1028-6
"""

from __future__ import annotations

# -----------------------------------------------------------------------------
# Critical values for CIm_f statistic
# Structure: CRITICAL_VALUES[m][k][p] = {0.01: cv_1%, 0.05: cv_5%, 0.10: cv_10%}
#   m = 0 : model with constant + Fourier terms  (often denoted "c")
#   m = 1 : model with constant + trend + Fourier terms (often denoted "ct")
#   k = 1, 2, 3  : Fourier frequency
#   p = 1, 2, 3, 4 : number of regressors in x_t (dimension)
# -----------------------------------------------------------------------------

CRITICAL_VALUES = {
    0: {  # m = 0 (constant + Fourier)
        1: {  # k = 1
            1: {0.10: 0.095, 0.05: 0.124, 0.01: 0.198},
            2: {0.10: 0.070, 0.05: 0.092, 0.01: 0.155},
            3: {0.10: 0.059, 0.05: 0.076, 0.01: 0.130},
            4: {0.10: 0.050, 0.05: 0.061, 0.01: 0.096},
        },
        2: {  # k = 2
            1: {0.10: 0.200, 0.05: 0.276, 0.01: 0.473},
            2: {0.10: 0.132, 0.05: 0.182, 0.01: 0.328},
            3: {0.10: 0.098, 0.05: 0.132, 0.01: 0.215},
            4: {0.10: 0.072, 0.05: 0.097, 0.01: 0.171},
        },
        3: {  # k = 3
            1: {0.10: 0.225, 0.05: 0.304, 0.01: 0.507},
            2: {0.10: 0.148, 0.05: 0.202, 0.01: 0.383},
            3: {0.10: 0.112, 0.05: 0.146, 0.01: 0.250},
            4: {0.10: 0.086, 0.05: 0.111, 0.01: 0.192},
        },
    },
    1: {  # m = 1 (constant + trend + Fourier)
        1: {  # k = 1
            1: {0.10: 0.042, 0.05: 0.048, 0.01: 0.063},
            2: {0.10: 0.038, 0.05: 0.045, 0.01: 0.059},
            3: {0.10: 0.036, 0.05: 0.042, 0.01: 0.055},
            4: {0.10: 0.034, 0.05: 0.038, 0.01: 0.050},
        },
        2: {  # k = 2
            1: {0.10: 0.078, 0.05: 0.099, 0.01: 0.163},
            2: {0.10: 0.063, 0.05: 0.081, 0.01: 0.127},
            3: {0.10: 0.051, 0.05: 0.066, 0.01: 0.103},
            4: {0.10: 0.044, 0.05: 0.055, 0.01: 0.086},
        },
        3: {  # k = 3
            1: {0.10: 0.090, 0.05: 0.114, 0.01: 0.170},
            2: {0.10: 0.075, 0.05: 0.094, 0.01: 0.143},
            3: {0.10: 0.061, 0.05: 0.075, 0.01: 0.116},
            4: {0.10: 0.053, 0.05: 0.065, 0.01: 0.099},
        },
    },
}

# -----------------------------------------------------------------------------
# Critical values for the F-test of Fourier significance (testing k* > 0)
# Structure: F_CRITICAL_VALUES[m] = {0.01: cv_1%, 0.05: cv_5%, 0.10: cv_10%}
# -----------------------------------------------------------------------------
F_CRITICAL_VALUES = {
    0: {0.10: 3.352, 0.05: 4.066, 0.01: 5.774},  # m = 0
    1: {0.10: 3.306, 0.05: 4.019, 0.01: 5.860},  # m = 1
}

# -----------------------------------------------------------------------------
# Utilities
# -----------------------------------------------------------------------------

def _interp(a: float, x0: float, y0: float, x1: float, y1: float) -> float:
    """Linear interpolation for a in [x0, x1]."""
    if x1 == x0:
        return y0
    t = (a - x0) / (x1 - x0)
    return y0 + t * (y1 - y0)


def _model_to_m(model: str | int) -> int:
    """
    Map model code to m:
      - 'c'  -> 0 (constant + Fourier)
      - 'ct' -> 1 (constant + trend + Fourier)
      - 0/1 accepted directly.
    """
    if isinstance(model, int):
        if model in (0, 1):
            return model
        raise ValueError("Model integer must be 0 (c) or 1 (ct).")
    model = str(model).strip().lower()
    if model in ("c", "const", "constant"):
        return 0
    if model in ("ct", "trend", "c+t", "constant+trend"):
        return 1
    raise ValueError(f"Unknown model '{model}'. Use 'c' or 'ct' (or 0/1).")

# -----------------------------------------------------------------------------
# Public API
# -----------------------------------------------------------------------------


def get_critical_value(m: int, k: int, p: int, significance_level: float = 0.05) -> float:
    """
    Scalar critical value for the CIm_f statistic.

    Parameters
    ----------
    m : int
        0 for constant+Fourier (c), 1 for constant+trend+Fourier (ct).
    k : int
        Fourier frequency (1, 2, or 3).
    p : int
        Dimension of regressor x_t (1, 2, 3, or 4). If p > 4, linear extrapolation is used.
    significance_level : float
        One of {0.01, 0.05, 0.10}. Other levels will be linearly interpolated.

    Returns
    -------
    float
    """
    if m not in (0, 1):
        raise ValueError("m must be 0 (c) or 1 (ct).")
    if k not in (1, 2, 3):
        raise ValueError("k must be in {1, 2, 3}.")

    # handle p
    if p in (1, 2, 3, 4):
        pv = CRITICAL_VALUES[m][k][p]
    elif p > 4:
        # Extrapolate from p=3 → p=4 step
        pv3 = CRITICAL_VALUES[m][k][3]
        pv4 = CRITICAL_VALUES[m][k][4]
        pv = {alpha: pv4[alpha] + (pv4[alpha] - pv3[alpha]) * (p - 4) for alpha in (0.01, 0.05, 0.10)}
        # keep non-negative
        pv = {alpha: max(val, 0.0) for alpha, val in pv.items()}
    else:
        raise ValueError("p must be >= 1.")

    # significance interpolation
    if significance_level in (0.01, 0.05, 0.10):
        return pv[significance_level]
    if significance_level < 0.01:
        return pv[0.01]
    if significance_level > 0.10:
        return pv[0.10]
    # interpolate between neighboring levels
    if 0.01 < significance_level < 0.05:
        return _interp(significance_level, 0.01, pv[0.01], 0.05, pv[0.05])
    # 0.05 < sig < 0.10
    return _interp(significance_level, 0.05, pv[0.05], 0.10, pv[0.10])


def get_all_critical_values(m: int, k: int, p: int) -> dict[float, float]:
    """
    Return dict of critical values {0.01: cv_1%, 0.05: cv_5%, 0.10: cv_10%}
    for the given (m, k, p).
    """
    return {
        0.01: get_critical_value(m, k, p, 0.01),
        0.05: get_critical_value(m, k, p, 0.05),
        0.10: get_critical_value(m, k, p, 0.10),
    }


def get_f_critical_value(m: int, significance_level: float = 0.05) -> float:
    """
    F-test critical value for testing Fourier significance (k* > 0).

    Parameters
    ----------
    m : int
        0 for constant+Fourier (c), 1 for constant+trend+Fourier (ct).
    significance_level : float
        One of {0.01, 0.05, 0.10}. Other levels linearly interpolated.

    Returns
    -------
    float
    """
    if m not in (0, 1):
        raise ValueError("m must be 0 (c) or 1 (ct).")

    table = F_CRITICAL_VALUES[m]
    if significance_level in (0.01, 0.05, 0.10):
        return table[significance_level]
    if significance_level < 0.01:
        return table[0.01]
    if significance_level > 0.10:
        return table[0.10]
    if 0.01 < significance_level < 0.05:
        return _interp(significance_level, 0.01, table[0.01], 0.05, table[0.05])
    return _interp(significance_level, 0.05, table[0.05], 0.10, table[0.10])


def get_critical_values(
    model: str | int = "c",
    k: int = 1,
    p: int = 1,
) -> dict[float, float]:
    """
    User-friendly accessor used by package root (__init__.py).

    Parameters
    ----------
    model : {'c','ct'} or {0,1}
        'c'  (or 0): constant + Fourier
        'ct' (or 1): constant + trend + Fourier
    k : int
        Fourier frequency (1, 2, or 3).
    p : int
        Dimension of regressor x_t (>=1). For p>4, linear extrapolation is used.

    Returns
    -------
    dict
        {0.01: cv_1%, 0.05: cv_5%, 0.10: cv_10%}
    """
    m = _model_to_m(model)
    return get_all_critical_values(m, k, p)


__all__ = [
    "CRITICAL_VALUES",
    "F_CRITICAL_VALUES",
    "get_critical_value",
    "get_all_critical_values",
    "get_f_critical_value",
    "get_critical_values",
]
