"""
Utility Functions for Fourier Cointegration Test
==================================================

Helper functions for long-run variance estimation and Fourier term construction.

Author: Dr. Merwan Roudane
"""

import numpy as np
from typing import Tuple, Optional


def bartlett_kernel(x: float, bandwidth: float) -> float:
    """
    Bartlett (triangular) kernel function.
    
    Parameters
    ----------
    x : float
        Input value
    bandwidth : float
        Bandwidth parameter
    
    Returns
    -------
    float
        Kernel weight
    """
    abs_x = np.abs(x)
    if abs_x <= bandwidth:
        return 1.0 - abs_x / bandwidth
    return 0.0


def qs_kernel(x: float, bandwidth: float) -> float:
    """
    Quadratic Spectral kernel function.
    
    Parameters
    ----------
    x : float
        Input value
    bandwidth : float
        Bandwidth parameter
    
    Returns
    -------
    float
        Kernel weight
    """
    z = 6.0 * np.pi * x / (5.0 * bandwidth)
    if np.abs(z) < 1e-10:
        return 1.0
    return 3.0 * (np.sin(z) / z - np.cos(z)) / (z ** 2)


def select_bandwidth(residuals: np.ndarray, kernel: str = 'bartlett') -> int:
    """
    Automatic bandwidth selection using Andrews (1991) method.
    
    Parameters
    ----------
    residuals : np.ndarray
        Residuals from regression
    kernel : str
        Kernel type: 'bartlett' or 'qs'
    
    Returns
    -------
    int
        Optimal bandwidth
    
    Reference
    ---------
    Andrews, D.W.K. (1991). Heteroskedasticity and autocorrelation 
    consistent covariance matrix estimation. Econometrica, 59(3), 817-858.
    """
    T = len(residuals)
    
    # Estimate AR(1) coefficient
    if T < 2:
        return 1
    
    y_lag = residuals[:-1]
    y = residuals[1:]
    rho_hat = np.dot(y, y_lag) / np.dot(y_lag, y_lag)
    rho_hat = min(max(rho_hat, -1), 1)  # Bound between -1 and 1
    
    # Calculate alpha coefficients for bandwidth selection
    alpha_1 = 4 * rho_hat**2 / ((1 - rho_hat)**6 * (1 + rho_hat)**2)
    alpha_2 = 4 * rho_hat**2 / ((1 - rho_hat)**8)
    
    # Bandwidth formula depends on kernel
    if kernel.lower() in ['bartlett', 'bart']:
        # Bartlett kernel
        bandwidth = 1.1447 * (alpha_2 * T)**(1/3)
    else:
        # Quadratic Spectral kernel
        bandwidth = 1.3221 * (alpha_1 * T)**(1/5)
    
    # Ensure minimum bandwidth of at least 1
    return max(int(bandwidth), 1)


def calculate_long_run_variance(
    residuals: np.ndarray,
    kernel: str = 'bartlett',
    bandwidth: Optional[int] = None,
    prewhiten: bool = False
) -> float:
    """
    Calculate long-run variance using kernel-based HAC estimator.
    
    Parameters
    ----------
    residuals : np.ndarray
        Residuals (T x 1 array)
    kernel : str
        Kernel function: 'bartlett' or 'qs' (quadratic spectral)
    bandwidth : int, optional
        Bandwidth parameter. If None, uses automatic selection
    prewhiten : bool
        Whether to use AR(1) prewhitening
    
    Returns
    -------
    float
        Long-run variance estimate
        
    Reference
    ---------
    Kwiatkowski, D., Phillips, P.C., Schmidt, P., & Shin, Y. (1992).
    Testing the null hypothesis of stationarity against the alternative 
    of a unit root. Journal of Econometrics, 54, 159-178.
    """
    residuals = np.asarray(residuals).flatten()
    T = len(residuals)
    
    if T == 0:
        return 0.0
    
    # Automatic bandwidth selection if not provided
    if bandwidth is None:
        bandwidth = select_bandwidth(residuals, kernel)
    
    # Select kernel function
    if kernel.lower() in ['bartlett', 'bart']:
        kernel_func = bartlett_kernel
    elif kernel.lower() in ['qs', 'quadratic_spectral']:
        kernel_func = qs_kernel
    else:
        raise ValueError(f"Unknown kernel: {kernel}. Use 'bartlett' or 'qs'")
    
    # Prewhitening (optional)
    if prewhiten and T > 1:
        # Estimate AR(1)
        y_lag = residuals[:-1]
        y = residuals[1:]
        rho = np.dot(y, y_lag) / np.dot(y_lag, y_lag) if np.dot(y_lag, y_lag) > 0 else 0
        rho = min(max(rho, -0.99), 0.99)  # Bound rho
        
        # Prewhiten
        residuals_pw = residuals[1:] - rho * residuals[:-1]
    else:
        residuals_pw = residuals
        rho = 0.0
    
    # Calculate variance
    gamma_0 = np.mean(residuals_pw ** 2)
    lrv = gamma_0
    
    # Add autocovariances with kernel weights
    for j in range(1, min(bandwidth + 1, len(residuals_pw))):
        gamma_j = np.mean(residuals_pw[j:] * residuals_pw[:-j])
        weight = kernel_func(j, bandwidth)
        lrv += 2 * weight * gamma_j
    
    # Recolor if prewhitened
    if prewhiten:
        lrv = lrv / ((1 - rho) ** 2)
    
    # Ensure LRV is positive and not too small
    # Minimum should be at least the sample variance / 10
    min_lrv = max(np.var(residuals) / 10, 1e-8)
    lrv = max(lrv, min_lrv)
    
    return lrv


def create_fourier_terms(
    T: int,
    k: int
) -> Tuple[np.ndarray, np.ndarray]:
    """
    Create Fourier terms sin(2πkt/T) and cos(2πkt/T).
    
    Parameters
    ----------
    T : int
        Sample size
    k : int
        Fourier frequency
    
    Returns
    -------
    tuple of np.ndarray
        (sin_term, cos_term) both of shape (T, 1)
        
    Reference
    ---------
    Equation (3) in Tsong et al. (2016)
    """
    t = np.arange(1, T + 1).reshape(-1, 1)
    sin_term = np.sin(2 * np.pi * k * t / T)
    cos_term = np.cos(2 * np.pi * k * t / T)
    
    return sin_term, cos_term


def create_deterministic_terms(
    T: int,
    m: int,
    k: int
) -> np.ndarray:
    """
    Create deterministic terms including constant, trend (if m=1), and Fourier terms.
    
    Parameters
    ----------
    T : int
        Sample size
    k : int
        Fourier frequency
    m : int
        Model specification: 0 for constant only, 1 for constant + trend
    
    Returns
    -------
    np.ndarray
        Matrix of deterministic terms (T x (2+m))
        Columns: [constant, trend (if m=1), sin(2πkt/T), cos(2πkt/T)]
    """
    t = np.arange(1, T + 1).reshape(-1, 1)
    constant = np.ones((T, 1))
    sin_term, cos_term = create_fourier_terms(T, k)
    
    if m == 0:
        # Only constant and Fourier terms
        det_terms = np.hstack([constant, sin_term, cos_term])
    elif m == 1:
        # Constant, trend, and Fourier terms
        trend = t / T  # Normalized trend
        det_terms = np.hstack([constant, trend, sin_term, cos_term])
    else:
        raise ValueError("m must be 0 or 1")
    
    return det_terms


def create_dols_regressors(
    x: np.ndarray,
    q: int
) -> np.ndarray:
    """
    Create DOLS regressors with leads and lags.
    
    Parameters
    ----------
    x : np.ndarray
        Regressor matrix (T x p)
    q : int
        Number of leads and lags
    
    Returns
    -------
    np.ndarray
        DOLS regressor matrix (T x p*(2q+1))
        Includes Δx_{t-q}, ..., Δx_t, ..., Δx_{t+q}
    """
    x = np.atleast_2d(x)
    if x.ndim == 1:
        x = x.reshape(-1, 1)
    
    T, p = x.shape
    
    if q == 0:
        return np.zeros((T, 0))  # No leads/lags
    
    # Calculate first differences: Δx_t = x_t - x_{t-1}
    delta_x = np.diff(x, axis=0)  # Shape: (T-1, p)
    
    # Create leads and lags - all must have T rows
    dols_terms = []
    for lag in range(-q, q + 1):
        # Initialize with zeros
        term = np.zeros((T, p))
        
        if lag < 0:
            # Lags: Δx_{t-|lag|}
            # Place delta_x values starting from row |lag|
            term[-lag:T-1, :] = delta_x[:T-1+lag, :]
        elif lag > 0:
            # Leads: Δx_{t+lag}
            # Place delta_x values ending at row T-1-lag
            term[:T-1-lag, :] = delta_x[lag:, :]
        else:
            # Current: Δx_t
            # Place delta_x values from start to T-1
            term[:T-1, :] = delta_x
        
        dols_terms.append(term)
    
    return np.hstack(dols_terms)


def partial_sum_process(residuals: np.ndarray) -> np.ndarray:
    """
    Calculate partial sum process S_t = Σ_{i=1}^t ε_i.
    
    Parameters
    ----------
    residuals : np.ndarray
        Residuals (T x 1)
    
    Returns
    -------
    np.ndarray
        Partial sums (T x 1)
    """
    return np.cumsum(residuals, axis=0)


def calculate_sse(y: np.ndarray, Z: np.ndarray) -> float:
    """
    Calculate sum of squared residuals from OLS.
    
    Parameters
    ----------
    y : np.ndarray
        Dependent variable (T x 1)
    Z : np.ndarray
        Regressor matrix (T x k)
    
    Returns
    -------
    float
        Sum of squared residuals
    """
    # OLS estimation
    beta_hat = np.linalg.lstsq(Z, y, rcond=None)[0]
    residuals = y - Z @ beta_hat
    sse = np.sum(residuals ** 2)
    
    return sse
