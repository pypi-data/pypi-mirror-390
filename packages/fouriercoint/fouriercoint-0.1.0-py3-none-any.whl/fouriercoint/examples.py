"""
Examples for Fourier Cointegration Test Package
=================================================

Demonstrates various use cases and applications of the fouriercoint package.

Author: Dr. Merwan Roudane
"""

import numpy as np


def example_basic():
    """
    Basic example: Simple cointegration test
    """
    print("\n" + "="*70)
    print("EXAMPLE 1: Basic Cointegration Test")
    print("="*70)
    
    from fouriercoint import fourier_cointegration_test
    
    # Set seed for reproducibility
    np.random.seed(42)
    
    # Generate I(1) processes
    T = 200
    x = np.cumsum(np.random.randn(T, 1))
    
    # Generate cointegrated y (with structural break)
    t = np.arange(T)
    break_component = 3 * (t > T//2)  # Level shift at midpoint
    y = 2 + 0.5 * x + break_component.reshape(-1, 1) + np.random.randn(T, 1) * 0.5
    
    # Run test
    results = fourier_cointegration_test(
        y=y,
        x=x,
        m=0,  # Level shifts only
        kmax=3,
        verbose=True
    )
    
    print(f"\n✓ Cointegration found: {not results['reject_null']}")
    print(f"✓ Optimal frequency: k={results['optimal_k']}")
    print(f"✓ Estimated β: {results['optimal_results']['beta'][0,0]:.4f}")


def example_multivariate():
    """
    Multivariate example: Multiple regressors
    """
    print("\n" + "="*70)
    print("EXAMPLE 2: Multivariate Cointegration")
    print("="*70)
    
    from fouriercoint import fourier_cointegration_test
    
    np.random.seed(123)
    T = 150
    
    # Generate 3 I(1) regressors
    x = np.cumsum(np.random.randn(T, 3), axis=0)
    
    # True cointegrating vector
    beta_true = np.array([[0.5], [0.3], [-0.2]])
    
    # Generate cointegrated y with trend break
    t = np.arange(T) / T
    trend_break = 2 * np.where(t < 0.5, t, 0.5)
    y = 2 + x @ beta_true + trend_break.reshape(-1, 1) + np.random.randn(T, 1) * 0.3
    
    # Run test
    results = fourier_cointegration_test(
        y=y,
        x=x,
        m=1,  # Allow trend breaks
        kmax=3,
        significance_level=0.05,
        verbose=True
    )
    
    print(f"\n✓ True β: {beta_true.flatten()}")
    print(f"✓ Estimated β: {results['optimal_results']['beta'].flatten()}")
    print(f"✓ Cointegration evidence: {not results['reject_null']}")


def example_fiscal_sustainability():
    """
    Application: Fiscal sustainability analysis
    Following Tsong et al. (2016) Section 4
    """
    print("\n" + "="*70)
    print("EXAMPLE 3: Fiscal Sustainability Analysis")
    print("="*70)
    
    from fouriercoint import fourier_cointegration_test
    
    np.random.seed(456)
    T = 100
    
    # Simulate government revenue and expenditure
    # Both are I(1) processes
    shocks = np.random.randn(T, 2)
    revenue = np.cumsum(shocks[:, 0]) + 50
    expenditure = np.cumsum(shocks[:, 1]) + 48
    
    # Add fiscal policy regime change (structural break)
    regime_change = T // 3
    expenditure[regime_change:] += 5  # Fiscal expansion
    
    # Reshape for test
    revenue = revenue.reshape(-1, 1)
    expenditure = expenditure.reshape(-1, 1)
    
    print(f"Testing cointegration between revenue and expenditure")
    print(f"Sample period: {T} observations")
    print(f"Potential policy regime change at t={regime_change}")
    
    # Test for cointegration (fiscal sustainability)
    results = fourier_cointegration_test(
        y=revenue,
        x=expenditure,
        m=1,  # Allow for both level and trend breaks
        kmax=3,
        use_dols=True,
        verbose=True
    )
    
    if not results['reject_null']:
        print("\n✓ CONCLUSION: Evidence of fiscal sustainability")
        print(f"  Revenue and expenditure are cointegrated")
        print(f"  Structural breaks captured by Fourier k={results['optimal_k']}")
    else:
        print("\n✗ CONCLUSION: No evidence of fiscal sustainability")
        print(f"  Revenue and expenditure are not cointegrated")


def example_ols_vs_dols():
    """
    Comparison: OLS vs DOLS estimation
    """
    print("\n" + "="*70)
    print("EXAMPLE 4: OLS vs DOLS Comparison")
    print("="*70)
    
    from fouriercoint import fourier_cointegration_test
    
    np.random.seed(789)
    T = 150
    
    # Generate I(1) processes with endogeneity
    errors = np.random.randn(T, 2)
    errors[:, 0] += 0.5 * errors[:, 1]  # Create correlation
    
    x = np.cumsum(errors[:, 1]).reshape(-1, 1)
    y = 2 + 0.5 * x + np.cumsum(errors[:, 0]).reshape(-1, 1) * 0.1
    
    print("Testing with potentially endogenous regressor...\n")
    
    # Test with OLS
    print("-" * 70)
    print("OLS Estimation:")
    print("-" * 70)
    results_ols = fourier_cointegration_test(
        y=y, x=x, m=1, use_dols=False, verbose=False
    )
    print(f"Test statistic: {results_ols['test_statistic']:.6f}")
    print(f"Critical value: {results_ols['critical_value']:.6f}")
    print(f"Reject H0: {results_ols['reject_null']}")
    
    # Test with DOLS
    print("\n" + "-" * 70)
    print("DOLS Estimation:")
    print("-" * 70)
    results_dols = fourier_cointegration_test(
        y=y, x=x, m=1, use_dols=True, verbose=False
    )
    print(f"Test statistic: {results_dols['test_statistic']:.6f}")
    print(f"Critical value: {results_dols['critical_value']:.6f}")
    print(f"Reject H0: {results_dols['reject_null']}")
    print(f"DOLS leads/lags: q={results_dols['optimal_results']['q']}")
    
    print("\n✓ DOLS should be more reliable with endogenous regressors")


def example_frequency_selection():
    """
    Demonstrate automatic frequency selection
    """
    print("\n" + "="*70)
    print("EXAMPLE 5: Automatic Frequency Selection")
    print("="*70)
    
    from fouriercoint import fourier_cointegration_test
    
    np.random.seed(321)
    T = 200
    t = np.arange(T)
    
    # Generate different types of breaks for different frequencies
    x = np.cumsum(np.random.randn(T, 1))
    
    # Complex break pattern (requires higher frequency)
    break_pattern = 2 * np.sin(2 * np.pi * 2 * t / T)  # Frequency 2 pattern
    y = 1 + 0.5 * x + break_pattern.reshape(-1, 1) + np.random.randn(T, 1) * 0.3
    
    print("Testing data with sinusoidal structural break pattern...\n")
    
    # Test with different kmax values
    for kmax in [1, 3, 5]:
        print(f"\nTesting with kmax={kmax}:")
        results = fourier_cointegration_test(
            y=y, x=x, m=0, kmax=kmax, verbose=False
        )
        print(f"  Optimal k*: {results['optimal_k']}")
        print(f"  Test statistic: {results['test_statistic']:.6f}")
        print(f"  Evidence of cointegration: {not results['reject_null']}")
        
        # Show statistics for all frequencies
        print(f"  Statistics by frequency:")
        for k in range(1, min(kmax+1, 6)):
            if k in results['all_frequencies']:
                stat = results['all_frequencies'][k]['statistic']
                print(f"    k={k}: {stat:.6f}")


def example_critical_values():
    """
    Demonstrate critical value access
    """
    print("\n" + "="*70)
    print("EXAMPLE 6: Accessing Critical Values")
    print("="*70)
    
    from fouriercoint import get_critical_values
    
    print("\nCritical values for different configurations:\n")
    
    # Model 0: Constant + Fourier
    print("Model m=0 (Constant + Fourier):")
    for k in [1, 2, 3]:
        cv = get_critical_values(m=0, k=k, p=1)
        print(f"  k={k}, p=1: 10%={cv[0.10]:.4f}, 5%={cv[0.05]:.4f}, 1%={cv[0.01]:.4f}")
    
    # Model 1: Constant + Trend + Fourier
    print("\nModel m=1 (Constant + Trend + Fourier):")
    for k in [1, 2, 3]:
        cv = get_critical_values(m=1, k=k, p=1)
        print(f"  k={k}, p=1: 10%={cv[0.10]:.4f}, 5%={cv[0.05]:.4f}, 1%={cv[0.01]:.4f}")
    
    # Different dimensions
    print("\nCritical values for different p (at m=1, k=1):")
    for p in [1, 2, 3, 4]:
        cv = get_critical_values(m=1, k=1, p=p)
        print(f"  p={p}: 5% critical value = {cv[0.05]:.4f}")


def example_monte_carlo():
    """
    Monte Carlo simulation to verify size and power
    """
    print("\n" + "="*70)
    print("EXAMPLE 7: Monte Carlo Simulation (Size and Power)")
    print("="*70)
    
    from fouriercoint import fourier_cointegration_test
    
    print("\nRunning Monte Carlo simulation with 100 replications...")
    print("(For publication, use 1000+ replications)\n")
    
    n_replications = 100
    T = 150
    np.random.seed(2024)
    
    # Test size (under H0: cointegration)
    print("Testing SIZE (H0 true: cointegration exists):")
    rejections_h0 = 0
    
    for i in range(n_replications):
        # Generate cointegrated data
        x = np.cumsum(np.random.randn(T, 1))
        y = 2 + 0.5 * x + np.random.randn(T, 1) * 0.5  # Cointegrated
        
        results = fourier_cointegration_test(
            y=y, x=x, m=1, significance_level=0.05, verbose=False
        )
        
        if results['reject_null']:
            rejections_h0 += 1
    
    size = rejections_h0 / n_replications
    print(f"  Rejection rate: {size:.3f} (should be ≈ 0.05)")
    
    # Test power (under H1: no cointegration)
    print("\nTesting POWER (H1 true: no cointegration):")
    rejections_h1 = 0
    
    for i in range(n_replications):
        # Generate non-cointegrated data
        x = np.cumsum(np.random.randn(T, 1))
        y = 2 + np.cumsum(np.random.randn(T, 1))  # NOT cointegrated
        
        results = fourier_cointegration_test(
            y=y, x=x, m=1, significance_level=0.05, verbose=False
        )
        
        if results['reject_null']:
            rejections_h1 += 1
    
    power = rejections_h1 / n_replications
    print(f"  Rejection rate: {power:.3f} (should be high, ideally > 0.80)")
    
    print(f"\n✓ Simulation complete")
    print(f"  Size: {size:.3f} (nominal: 0.05)")
    print(f"  Power: {power:.3f}")


def run_all_examples():
    """
    Run all examples
    """
    examples = [
        example_basic,
        example_multivariate,
        example_fiscal_sustainability,
        example_ols_vs_dols,
        example_frequency_selection,
        example_critical_values,
        example_monte_carlo
    ]
    
    for example in examples:
        try:
            example()
        except Exception as e:
            print(f"\n✗ Error in {example.__name__}: {e}")
    
    print("\n" + "="*70)
    print("ALL EXAMPLES COMPLETED")
    print("="*70)


if __name__ == "__main__":
    run_all_examples()
