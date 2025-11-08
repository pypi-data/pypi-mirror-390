"""
Fourier Cointegration Test Package

Implementation of Tsong et al. (2016) Fourier approximation test for cointegration.
"""

# --- Version pulled from installed package metadata to avoid mismatches ---
try:
    from importlib.metadata import version as _pkg_version  # Python 3.8+
    __version__ = _pkg_version("fouriercoint")
except Exception:
    __version__ = "0.0.0"  # fallback during local dev or editable installs

__author__ = "Dr. Merwan Roudane"
__email__ = "merwanroudane920@gmail.com"

from .core import (
    fourier_cointegration_test,
    fourier_cointegration_ols,
    fourier_cointegration_dols,
    select_optimal_frequency,
)
from .critical_values import get_critical_values
from .utils import (
    calculate_long_run_variance,
    create_fourier_terms,
    bartlett_kernel,
    qs_kernel,
)

__all__ = [
    "fourier_cointegration_test",
    "fourier_cointegration_ols",
    "fourier_cointegration_dols",
    "get_critical_values",
    "select_optimal_frequency",
    "calculate_long_run_variance",
    "create_fourier_terms",
    "bartlett_kernel",
    "qs_kernel",
]
