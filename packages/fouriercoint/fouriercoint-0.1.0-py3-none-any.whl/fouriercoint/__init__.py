"""
Fourier Cointegration Test Package
====================================

Implementation of Tsong et al. (2016) Fourier approximation test for cointegration.

Author: Dr. Merwan Roudane
Email: merwanroudane920@gmail.com
GitHub: https://github.com/merwanroudane/fouriercoint

Reference:
----------
Tsong, C.C., Lee, C.F., Tsai, L.J., & Hu, T.C. (2016).
The Fourier approximation and testing for the null of cointegration.
Empirical Economics, 51(3), 1085-1113.
DOI: 10.1007/s00181-015-1028-6
"""

__version__ = "1.0.0"
__author__ = "Dr. Merwan Roudane"
__email__ = "merwanroudane920@gmail.com"

from .core import (
    fourier_cointegration_test,
    fourier_cointegration_ols,
    fourier_cointegration_dols,
    get_critical_values,
    select_optimal_frequency
)

from .utils import (
    calculate_long_run_variance,
    create_fourier_terms,
    bartlett_kernel,
    qs_kernel
)

__all__ = [
    'fourier_cointegration_test',
    'fourier_cointegration_ols',
    'fourier_cointegration_dols',
    'get_critical_values',
    'select_optimal_frequency',
    'calculate_long_run_variance',
    'create_fourier_terms',
    'bartlett_kernel',
    'qs_kernel'
]
