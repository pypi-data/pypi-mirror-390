"""
Core Fourier Cointegration Test Implementation
================================================

Main functions implementing Tsong et al. (2016) methodology.

Author: Dr. Merwan Roudane
Email: merwanroudane920@gmail.com

Reference:
----------
Tsong, C.C., Lee, C.F., Tsai, L.J., & Hu, T.C. (2016).
The Fourier approximation and testing for the null of cointegration.
Empirical Economics, 51(3), 1085-1113.
DOI: 10.1007/s00181-015-1028-6
"""

import numpy as np
import warnings
from typing import Dict, Optional, Tuple, Union
from .utils import (
    create_deterministic_terms,
    create_dols_regressors,
    calculate_long_run_variance,
    partial_sum_process,
    calculate_sse
)
from .critical_values import (
    get_critical_value,
    get_f_critical_value,
    get_all_critical_values
)


def fourier_cointegration_ols(
    y: np.ndarray,
    x: np.ndarray,
    m: int = 1,
    k: int = 1,
    kernel: str = 'bartlett',
    bandwidth: Optional[int] = None
) -> Dict:
    """
    Fourier cointegration test using OLS estimation (CI^m_f test).
    
    Tests H0: cointegration with structural breaks vs H1: no cointegration
    
    Parameters
    ----------
    y : np.ndarray
        Dependent variable (T x 1)
    x : np.ndarray
        Independent variable(s) (T x p)
    m : int, default=1
        Model specification:
        - 0: constant + Fourier (level shifts)
        - 1: constant + trend + Fourier (level and trend shifts)
    k : int, default=1
        Fourier frequency (recommended: 1, 2, or 3)
    kernel : str, default='bartlett'
        Kernel for long-run variance: 'bartlett' or 'qs'
    bandwidth : int, optional
        Bandwidth for kernel. If None, uses automatic selection
    
    Returns
    -------
    dict
        Results dictionary containing:
        - 'statistic': Test statistic CI^m_f
        - 'residuals': OLS residuals
        - 'beta': Estimated cointegrating vector
        - 'lrv': Long-run variance estimate
        - 'partial_sums': Partial sum process S_t
        - 'm': Model specification
        - 'k': Fourier frequency
        - 'p': Dimension of x
        - 'T': Sample size
        
    Reference
    ---------
    Equation (9) in Tsong et al. (2016)
    CI^m_f = T^{-2} ω̂^{-2}_1 Σ_{t=1}^T S^2_t
    """
    # Input validation and preparation
    y = np.asarray(y)
    if y.ndim == 1:
        y = y.reshape(-1, 1)
    elif y.ndim > 2:
        raise ValueError(f"y must be 1D or 2D array, got shape {y.shape}")
    
    x = np.asarray(x)
    if x.ndim == 1:
        x = x.reshape(-1, 1)
    elif x.ndim > 2:
        raise ValueError(f"x must be 1D or 2D array, got shape {x.shape}")
    
    T_y, _ = y.shape
    T, p = x.shape
    
    if T != T_y:
        raise ValueError(f"y and x must have same length. Got y: {T_y}, x: {T}")
    
    if m not in [0, 1]:
        raise ValueError("m must be 0 (constant) or 1 (constant + trend)")
    
    if k < 1:
        raise ValueError("k must be >= 1")
    
    # Create deterministic terms: constant, trend (if m=1), and Fourier terms
    det_terms = create_deterministic_terms(T, m, k)
    
    # Create full regressor matrix: [det_terms, x]
    Z = np.hstack([det_terms, x])
    
    # OLS estimation
    # Solve: β̂ = (Z'Z)^{-1} Z'y
    try:
        beta_hat = np.linalg.lstsq(Z, y, rcond=None)[0]
    except np.linalg.LinAlgError:
        raise ValueError("Singular matrix in OLS estimation")
    
    # Calculate residuals
    residuals = y - Z @ beta_hat
    
    # Extract cointegrating vector (coefficients on x)
    coint_vector = beta_hat[det_terms.shape[1]:, :]
    
    # Calculate partial sum process: S_t = Σ_{i=1}^t ε̂_i
    S_t = partial_sum_process(residuals)
    
    # Calculate long-run variance ω̂^2_1
    lrv = calculate_long_run_variance(residuals, kernel=kernel, bandwidth=bandwidth)
    
    # Safeguard against numerical issues
    if lrv < 1e-10 or not np.isfinite(lrv):
        warnings.warn(f"Long-run variance is very small ({lrv}), using residual variance instead")
        lrv = np.var(residuals) if np.var(residuals) > 1e-10 else 1e-10
    
    # Calculate test statistic: CI^m_f = T^{-2} ω̂^{-2}_1 Σ S^2_t
    statistic = np.sum(S_t ** 2) / (T ** 2 * lrv)
    
    return {
        'statistic': float(statistic),
        'residuals': residuals,
        'beta': coint_vector,
        'lrv': lrv,
        'partial_sums': S_t,
        'm': m,
        'k': k,
        'p': p,
        'T': T,
        'det_terms': det_terms,
        'Z': Z
    }


def fourier_cointegration_dols(
    y: np.ndarray,
    x: np.ndarray,
    m: int = 1,
    k: int = 1,
    q: Optional[int] = None,
    kernel: str = 'bartlett',
    bandwidth: Optional[int] = None
) -> Dict:
    """
    Fourier cointegration test using DOLS estimation (CI^m*_f test).
    
    Handles endogenous regressors using Saikkonen (1991) DOLS approach.
    
    Parameters
    ----------
    y : np.ndarray
        Dependent variable (T x 1)
    x : np.ndarray
        Independent variable(s) (T x p)
    m : int, default=1
        Model specification (0 or 1)
    k : int, default=1
        Fourier frequency
    q : int, optional
        Number of leads and lags for DOLS. If None, uses q = int(T^{1/3})
    kernel : str, default='bartlett'
        Kernel for long-run variance
    bandwidth : int, optional
        Bandwidth for kernel
    
    Returns
    -------
    dict
        Results dictionary (same as OLS version plus 'q')
        
    Reference
    ---------
    Equation (12) in Tsong et al. (2016)
    Saikkonen, P. (1991). Asymptotically efficient estimation of 
    cointegration regressions. Econometric Theory, 7(1), 1-21.
    """
    y = np.asarray(y)
    if y.ndim == 1:
        y = y.reshape(-1, 1)
    elif y.ndim > 2:
        raise ValueError(f"y must be 1D or 2D array")
    
    x = np.asarray(x)
    if x.ndim == 1:
        x = x.reshape(-1, 1)
    elif x.ndim > 2:
        raise ValueError(f"x must be 1D or 2D array")
    
    T_y, _ = y.shape
    T, p = x.shape
    
    if T != T_y:
        raise ValueError(f"y and x must have same length")
    
    # Automatic selection of q if not provided (Andrews 1991)
    if q is None:
        q = max(1, int(T ** (1/3)))
    
    # Create deterministic terms
    det_terms = create_deterministic_terms(T, m, k)
    
    # Create DOLS leads and lags of Δx
    dols_terms = create_dols_regressors(x, q)
    
    # Create full DOLS regressor matrix: [det_terms, x, DOLS_terms]
    Z_dols = np.hstack([det_terms, x, dols_terms])
    
    # DOLS estimation
    try:
        beta_hat = np.linalg.lstsq(Z_dols, y, rcond=None)[0]
    except np.linalg.LinAlgError:
        raise ValueError("Singular matrix in DOLS estimation")
    
    # Calculate residuals
    residuals = y - Z_dols @ beta_hat
    
    # Extract cointegrating vector
    coint_vector = beta_hat[det_terms.shape[1]:det_terms.shape[1]+p, :]
    
    # Calculate partial sum process
    S_t = partial_sum_process(residuals)
    
    # Calculate long-run variance
    lrv = calculate_long_run_variance(residuals, kernel=kernel, bandwidth=bandwidth)
    
    # Safeguard against numerical issues
    if lrv < 1e-10 or not np.isfinite(lrv):
        warnings.warn(f"Long-run variance is very small ({lrv}), using residual variance instead")
        lrv = np.var(residuals) if np.var(residuals) > 1e-10 else 1e-10
    
    # Calculate test statistic
    statistic = np.sum(S_t ** 2) / (T ** 2 * lrv)
    
    return {
        'statistic': float(statistic),
        'residuals': residuals,
        'beta': coint_vector,
        'lrv': lrv,
        'partial_sums': S_t,
        'm': m,
        'k': k,
        'q': q,
        'p': p,
        'T': T,
        'det_terms': det_terms,
        'Z': Z_dols
    }


def select_optimal_frequency(
    y: np.ndarray,
    x: np.ndarray,
    m: int = 1,
    kmax: int = 3,
    method: str = 'sse'
) -> int:
    """
    Select optimal Fourier frequency k* by minimizing SSE.
    
    Parameters
    ----------
    y : np.ndarray
        Dependent variable
    x : np.ndarray
        Independent variables
    m : int
        Model specification
    kmax : int, default=3
        Maximum frequency to consider (paper recommends 3)
    method : str, default='sse'
        Selection criterion: 'sse', 'aic', or 'bic'
    
    Returns
    -------
    int
        Optimal frequency k*
        
    Reference
    ---------
    Section 2.2 in Tsong et al. (2016)
    k* = ArgMin_{k∈{1,2,3}} SSE(k)
    """
    y = np.asarray(y)
    if y.ndim == 1:
        y = y.reshape(-1, 1)
    
    x = np.asarray(x)
    if x.ndim == 1:
        x = x.reshape(-1, 1)
    
    T, p = x.shape
    
    criteria_values = {}
    
    for k in range(1, kmax + 1):
        det_terms = create_deterministic_terms(T, m, k)
        Z = np.hstack([det_terms, x])
        
        # Number of parameters
        n_params = Z.shape[1]
        
        # Calculate SSE
        sse = calculate_sse(y, Z)
        
        if method.lower() == 'sse':
            criteria_values[k] = sse
        elif method.lower() == 'aic':
            # AIC = ln(SSE/T) + 2k/T
            criteria_values[k] = np.log(sse / T) + 2 * n_params / T
        elif method.lower() == 'bic':
            # BIC = ln(SSE/T) + k*ln(T)/T
            criteria_values[k] = np.log(sse / T) + n_params * np.log(T) / T
        else:
            raise ValueError("method must be 'sse', 'aic', or 'bic'")
    
    # Return frequency with minimum criterion
    optimal_k = min(criteria_values, key=criteria_values.get)
    
    return optimal_k


def f_test_fourier_significance(
    y: np.ndarray,
    x: np.ndarray,
    m: int = 1,
    k: int = 1
) -> Dict:
    """
    F-test for significance of Fourier component.
    
    Tests H0: α_k = β_k = 0 (linear trend) vs H1: nonlinear trend
    
    Parameters
    ----------
    y : np.ndarray
        Dependent variable
    x : np.ndarray
        Independent variables
    m : int
        Model specification
    k : int
        Fourier frequency
    
    Returns
    -------
    dict
        Results with 'F_statistic', 'p_value', and 'reject_null'
        
    Reference
    ---------
    Equation (14) in Tsong et al. (2016)
    F^m(k) = [(SSE_0 - SSE_1) / 2] / [SSE_1 / (T - q)]
    """
    y = np.asarray(y)
    if y.ndim == 1:
        y = y.reshape(-1, 1)
    
    x = np.asarray(x)
    if x.ndim == 1:
        x = x.reshape(-1, 1)
    
    T, p = x.shape
    
    # Model under H0 (no Fourier terms)
    if m == 0:
        Z_0 = np.hstack([np.ones((T, 1)), x])
    else:
        t = np.arange(1, T + 1).reshape(-1, 1) / T
        Z_0 = np.hstack([np.ones((T, 1)), t, x])
    
    sse_0 = calculate_sse(y, Z_0)
    
    # Model under H1 (with Fourier terms)
    det_terms = create_deterministic_terms(T, m, k)
    Z_1 = np.hstack([det_terms, x])
    
    sse_1 = calculate_sse(y, Z_1)
    
    # Degrees of freedom
    df1 = 2  # Two restrictions: α_k = 0 and β_k = 0
    df2 = T - Z_1.shape[1]
    
    # F-statistic
    if sse_1 == 0 or df2 <= 0:
        F_stat = np.inf
    else:
        F_stat = ((sse_0 - sse_1) / df1) / (sse_1 / df2)
    
    # Critical value at 5%
    crit_val = get_f_critical_value(m, significance_level=0.05)
    
    return {
        'F_statistic': float(F_stat),
        'critical_value_5pct': crit_val,
        'reject_null': F_stat > crit_val,
        'sse_restricted': sse_0,
        'sse_unrestricted': sse_1
    }


def fourier_cointegration_test(
    y: np.ndarray,
    x: np.ndarray,
    m: int = 1,
    kmax: int = 3,
    q: Optional[int] = None,
    kernel: str = 'bartlett',
    bandwidth: Optional[int] = None,
    significance_level: float = 0.05,
    use_dols: bool = True,
    verbose: bool = True
) -> Dict:
    """
    Complete Fourier cointegration test with automatic frequency selection.
    
    This is the main function that users should call. It implements the full
    testing procedure from Tsong et al. (2016).
    
    Parameters
    ----------
    y : np.ndarray or array-like
        Dependent variable (must be I(1))
    x : np.ndarray or array-like
        Independent variable(s) (must be I(1))
    m : int, default=1
        Model specification:
        - 0: constant + Fourier (for level shifts)
        - 1: constant + trend + Fourier (for level and trend shifts)
    kmax : int, default=3
        Maximum Fourier frequency to consider (paper recommends 3)
    q : int, optional
        DOLS leads/lags. If None, uses q = int(T^{1/3})
    kernel : str, default='bartlett'
        Kernel for variance: 'bartlett' or 'qs'
    bandwidth : int, optional
        Bandwidth for kernel (None = automatic selection)
    significance_level : float, default=0.05
        Significance level for testing (0.01, 0.05, or 0.10)
    use_dols : bool, default=True
        Whether to use DOLS estimation (recommended for endogenous regressors)
    verbose : bool, default=True
        Whether to print results summary
    
    Returns
    -------
    dict
        Complete results dictionary containing:
        - 'optimal_k': Selected Fourier frequency
        - 'test_statistic': CI^m_f or CI^m*_f test statistic
        - 'critical_values': Dict with 1%, 5%, 10% critical values
        - 'reject_null': Boolean, whether to reject cointegration
        - 'conclusion': Text conclusion
        - 'F_test': F-test results for Fourier significance
        - 'all_frequencies': Results for all tested frequencies
        - Plus all results from the test at optimal frequency
    
    Examples
    --------
    >>> import numpy as np
    >>> from fouriercoint import fourier_cointegration_test
    >>> 
    >>> # Generate sample data
    >>> T = 100
    >>> x = np.cumsum(np.random.randn(T, 1))  # I(1) process
    >>> y = 2 + 0.5 * x + np.random.randn(T, 1)  # Cointegrated
    >>> 
    >>> # Run test
    >>> results = fourier_cointegration_test(y, x, m=1)
    >>> 
    >>> print(f"Test Statistic: {results['test_statistic']:.4f}")
    >>> print(f"Cointegration: {not results['reject_null']}")
    
    Reference
    ---------
    Tsong, C.C., Lee, C.F., Tsai, L.J., & Hu, T.C. (2016).
    The Fourier approximation and testing for the null of cointegration.
    Empirical Economics, 51(3), 1085-1113.
    """
    # Input validation
    y = np.asarray(y)
    if y.ndim == 1:
        y = y.reshape(-1, 1)
    elif y.ndim > 2:
        raise ValueError("y must be 1D or 2D array")
    
    x = np.asarray(x)
    if x.ndim == 1:
        x = x.reshape(-1, 1)
    elif x.ndim > 2:
        raise ValueError("x must be 1D or 2D array")
    
    T, p = x.shape
    
    # Step 1: Select optimal frequency
    optimal_k = select_optimal_frequency(y, x, m=m, kmax=kmax)
    
    # Step 2: Run test at each frequency
    results_by_k = {}
    for k in range(1, kmax + 1):
        if use_dols:
            result_k = fourier_cointegration_dols(
                y, x, m=m, k=k, q=q, kernel=kernel, bandwidth=bandwidth
            )
        else:
            result_k = fourier_cointegration_ols(
                y, x, m=m, k=k, kernel=kernel, bandwidth=bandwidth
            )
        results_by_k[k] = result_k
    
    # Results at optimal frequency
    optimal_results = results_by_k[optimal_k]
    test_stat = optimal_results['statistic']
    
    # Step 3: Get critical values
    critical_values = get_all_critical_values(m, optimal_k, p)
    crit_val = critical_values[significance_level]
    
    # Step 4: F-test for Fourier significance
    f_test_results = f_test_fourier_significance(y, x, m=m, k=optimal_k)
    
    # Step 5: Determine conclusion
    reject_null = test_stat > crit_val
    
    if reject_null:
        conclusion = (
            f"Reject the null hypothesis of cointegration at {significance_level*100}% level. "
            f"No evidence of cointegration with structural breaks."
        )
    else:
        conclusion = (
            f"Do not reject the null hypothesis of cointegration at {significance_level*100}% level. "
            f"Evidence supports cointegration with structural breaks "
            f"(Fourier frequency k={optimal_k})."
        )
    
    # Compile complete results
    complete_results = {
        'optimal_k': optimal_k,
        'test_statistic': test_stat,
        'critical_value': crit_val,
        'critical_values': critical_values,
        'reject_null': reject_null,
        'conclusion': conclusion,
        'F_test': f_test_results,
        'fourier_significant': f_test_results['reject_null'],
        'all_frequencies': results_by_k,
        'optimal_results': optimal_results,
        'm': m,
        'p': p,
        'T': T,
        'method': 'DOLS' if use_dols else 'OLS',
        'significance_level': significance_level
    }
    
    # Print summary if verbose
    if verbose:
        print("=" * 70)
        print("FOURIER COINTEGRATION TEST RESULTS")
        print("Tsong et al. (2016)")
        print("=" * 70)
        print(f"Sample size (T):              {T}")
        print(f"Number of regressors (p):     {p}")
        print(f"Model specification (m):      {m} " + 
              ("(constant + trend + Fourier)" if m == 1 else "(constant + Fourier)"))
        print(f"Estimation method:            {complete_results['method']}")
        if use_dols:
            print(f"DOLS leads/lags (q):          {optimal_results.get('q', 'N/A')}")
        print(f"Kernel:                       {kernel}")
        print("-" * 70)
        print(f"Optimal Fourier frequency:    k* = {optimal_k}")
        print(f"Test statistic CI^m_f:        {test_stat:.6f}")
        print(f"Critical value ({significance_level*100}%):        {crit_val:.6f}")
        print(f"Long-run variance:            {optimal_results['lrv']:.6f}")
        print("-" * 70)
        print(f"Critical values:")
        print(f"  10%:  {critical_values[0.10]:.6f}")
        print(f"  5%:   {critical_values[0.05]:.6f}")
        print(f"  1%:   {critical_values[0.01]:.6f}")
        print("-" * 70)
        print(f"F-test for Fourier:           F = {f_test_results['F_statistic']:.4f}")
        print(f"F critical value (5%):        {f_test_results['critical_value_5pct']:.4f}")
        print(f"Fourier significant:          {f_test_results['reject_null']}")
        print("=" * 70)
        print(f"CONCLUSION: {conclusion}")
        print("=" * 70)
    
    return complete_results


# Convenience function
def get_critical_values(m: int, k: int, p: int) -> Dict[float, float]:
    """
    Get critical values for given test configuration.
    
    Parameters
    ----------
    m : int
        Model specification (0 or 1)
    k : int
        Fourier frequency (1, 2, or 3)
    p : int
        Dimension of regressor
    
    Returns
    -------
    dict
        Critical values at 1%, 5%, and 10% levels
    """
    return get_all_critical_values(m, k, p)
