"""
Critical Values for Fourier Cointegration Test
================================================

Asymptotic critical values from Tsong et al. (2016), Table 1.
Calculated with T=1000 and 5000 replications.

Reference:
----------
Tsong, C.C., Lee, C.F., Tsai, L.J., & Hu, T.C. (2016).
The Fourier approximation and testing for the null of cointegration.
Empirical Economics, 51(3), 1085-1113.
"""

import numpy as np

# Critical values for CIm_f test
# Structure: CRITICAL_VALUES[m][k][p] = {0.01: cv_1%, 0.05: cv_5%, 0.10: cv_10%}
# m = 0: constant + Fourier
# m = 1: constant + trend + Fourier
# k = 1, 2, 3: Fourier frequency
# p = 1, 2, 3, 4: dimension of regressor x_t

CRITICAL_VALUES = {
    0: {  # m = 0: Model with constant and Fourier component
        1: {  # Frequency k = 1
            1: {0.10: 0.095, 0.05: 0.124, 0.01: 0.198},
            2: {0.10: 0.070, 0.05: 0.092, 0.01: 0.155},
            3: {0.10: 0.059, 0.05: 0.076, 0.01: 0.130},
            4: {0.10: 0.050, 0.05: 0.061, 0.01: 0.096}
        },
        2: {  # Frequency k = 2
            1: {0.10: 0.200, 0.05: 0.276, 0.01: 0.473},
            2: {0.10: 0.132, 0.05: 0.182, 0.01: 0.328},
            3: {0.10: 0.098, 0.05: 0.132, 0.01: 0.215},
            4: {0.10: 0.072, 0.05: 0.097, 0.01: 0.171}
        },
        3: {  # Frequency k = 3
            1: {0.10: 0.225, 0.05: 0.304, 0.01: 0.507},
            2: {0.10: 0.148, 0.05: 0.202, 0.01: 0.383},
            3: {0.10: 0.112, 0.05: 0.146, 0.01: 0.250},
            4: {0.10: 0.086, 0.05: 0.111, 0.01: 0.192}
        }
    },
    1: {  # m = 1: Model with constant, trend, and Fourier component
        1: {  # Frequency k = 1
            1: {0.10: 0.042, 0.05: 0.048, 0.01: 0.063},
            2: {0.10: 0.038, 0.05: 0.045, 0.01: 0.059},
            3: {0.10: 0.036, 0.05: 0.042, 0.01: 0.055},
            4: {0.10: 0.034, 0.05: 0.038, 0.01: 0.050}
        },
        2: {  # Frequency k = 2
            1: {0.10: 0.078, 0.05: 0.099, 0.01: 0.163},
            2: {0.10: 0.063, 0.05: 0.081, 0.01: 0.127},
            3: {0.10: 0.051, 0.05: 0.066, 0.01: 0.103},
            4: {0.10: 0.044, 0.05: 0.055, 0.01: 0.086}
        },
        3: {  # Frequency k = 3
            1: {0.10: 0.090, 0.05: 0.114, 0.01: 0.170},
            2: {0.10: 0.075, 0.05: 0.094, 0.01: 0.143},
            3: {0.10: 0.061, 0.05: 0.075, 0.01: 0.116},
            4: {0.10: 0.053, 0.05: 0.065, 0.01: 0.099}
        }
    }
}

# Critical values for F_m(k*) test (testing for Fourier significance)
# Structure: F_CRITICAL_VALUES[m] = {0.01: cv_1%, 0.05: cv_5%, 0.10: cv_10%}
F_CRITICAL_VALUES = {
    0: {0.10: 3.352, 0.05: 4.066, 0.01: 5.774},  # m = 0
    1: {0.10: 3.306, 0.05: 4.019, 0.01: 5.860}   # m = 1
}


def get_critical_value(m, k, p, significance_level=0.05):
    """
    Get critical value for the Fourier cointegration test.
    
    Parameters
    ----------
    m : int
        Model specification: 0 for constant, 1 for constant + trend
    k : int
        Fourier frequency (1, 2, or 3)
    p : int
        Dimension of regressor x_t (1, 2, 3, or 4)
    significance_level : float
        Significance level (0.01, 0.05, or 0.10)
    
    Returns
    -------
    float
        Critical value
        
    Raises
    ------
    ValueError
        If parameters are out of valid range
    """
    if m not in [0, 1]:
        raise ValueError("m must be 0 (constant) or 1 (constant + trend)")
    
    if k not in [1, 2, 3]:
        raise ValueError("k must be 1, 2, or 3")
    
    if p not in [1, 2, 3, 4]:
        # Interpolate for p > 4
        if p > 4:
            # Linear extrapolation based on p=3 and p=4
            cv3 = CRITICAL_VALUES[m][k][3][significance_level]
            cv4 = CRITICAL_VALUES[m][k][4][significance_level]
            slope = cv4 - cv3
            cv = cv4 + slope * (p - 4)
            return max(cv, 0.001)  # Ensure positive
        else:
            raise ValueError(f"p must be >= 1, got {p}")
    
    if significance_level not in [0.01, 0.05, 0.10]:
        # Interpolate for other significance levels
        if significance_level < 0.01:
            return CRITICAL_VALUES[m][k][p][0.01]
        elif significance_level > 0.10:
            return CRITICAL_VALUES[m][k][p][0.10]
        elif 0.01 < significance_level < 0.05:
            # Linear interpolation between 1% and 5%
            cv1 = CRITICAL_VALUES[m][k][p][0.01]
            cv5 = CRITICAL_VALUES[m][k][p][0.05]
            weight = (significance_level - 0.01) / (0.05 - 0.01)
            return cv1 + weight * (cv5 - cv1)
        else:  # 0.05 < significance_level < 0.10
            # Linear interpolation between 5% and 10%
            cv5 = CRITICAL_VALUES[m][k][p][0.05]
            cv10 = CRITICAL_VALUES[m][k][p][0.10]
            weight = (significance_level - 0.05) / (0.10 - 0.05)
            return cv5 + weight * (cv10 - cv5)
    
    return CRITICAL_VALUES[m][k][p][significance_level]


def get_f_critical_value(m, significance_level=0.05):
    """
    Get critical value for the F test of Fourier significance.
    
    Parameters
    ----------
    m : int
        Model specification: 0 for constant, 1 for constant + trend
    significance_level : float
        Significance level (0.01, 0.05, or 0.10)
    
    Returns
    -------
    float
        F-test critical value
    """
    if m not in [0, 1]:
        raise ValueError("m must be 0 (constant) or 1 (constant + trend)")
    
    if significance_level not in [0.01, 0.05, 0.10]:
        # Interpolate
        if significance_level < 0.01:
            return F_CRITICAL_VALUES[m][0.01]
        elif significance_level > 0.10:
            return F_CRITICAL_VALUES[m][0.10]
        elif 0.01 < significance_level < 0.05:
            cv1 = F_CRITICAL_VALUES[m][0.01]
            cv5 = F_CRITICAL_VALUES[m][0.05]
            weight = (significance_level - 0.01) / (0.05 - 0.01)
            return cv1 + weight * (cv5 - cv1)
        else:
            cv5 = F_CRITICAL_VALUES[m][0.05]
            cv10 = F_CRITICAL_VALUES[m][0.10]
            weight = (significance_level - 0.05) / (0.10 - 0.05)
            return cv5 + weight * (cv10 - cv5)
    
    return F_CRITICAL_VALUES[m][significance_level]


def get_all_critical_values(m, k, p):
    """
    Get all critical values (1%, 5%, 10%) for given parameters.
    
    Parameters
    ----------
    m : int
        Model specification
    k : int
        Fourier frequency
    p : int
        Dimension of regressor
    
    Returns
    -------
    dict
        Dictionary with keys 0.01, 0.05, 0.10 and critical values
    """
    return {
        0.01: get_critical_value(m, k, p, 0.01),
        0.05: get_critical_value(m, k, p, 0.05),
        0.10: get_critical_value(m, k, p, 0.10)
    }
