"""
Simple Example - Fourier Cointegration Test
============================================

This is a standalone example you can run immediately after installing the package.

Author: Dr. Merwan Roudane
Email: merwanroudane920@gmail.com
"""

import numpy as np

def main():
    print("=" * 70)
    print("FOURIER COINTEGRATION TEST - SIMPLE EXAMPLE")
    print("=" * 70)
    print()
    
    # Import the package
    try:
        from fouriercoint import fourier_cointegration_test
        print("✓ Package imported successfully\n")
    except ImportError as e:
        print(f"✗ Error importing package: {e}")
        print("\nPlease install the package first:")
        print("  pip install fouriercoint")
        print("or")
        print("  pip install -e /path/to/package")
        return
    
    # Set random seed for reproducibility
    np.random.seed(123)
    
    # Generate sample data
    print("Generating sample data...")
    T = 200  # Sample size
    
    # Create I(1) process (random walk for regressor)
    x = np.cumsum(np.random.randn(T, 1))
    
    # Create cointegrated dependent variable with structural break
    # Break: Level shift at t = 100
    t = np.arange(T)
    structural_break = 3 * (t > 100)  # Level increases by 3 after t=100
    
    # Cointegrating relationship: y = 2 + 0.5*x + break + noise
    y = 2 + 0.5 * x + structural_break.reshape(-1, 1) + np.random.randn(T, 1)
    
    print(f"  Sample size: {T}")
    print(f"  True cointegrating vector: β = 0.5")
    print(f"  Structural break at t = 100 (level shift = 3)")
    print()
    
    # Run the Fourier cointegration test
    print("Running Fourier cointegration test...")
    print("-" * 70)
    
    results = fourier_cointegration_test(
        y=y,
        x=x,
        m=0,                     # Model 0: constant + Fourier (for level shifts)
        kmax=3,                  # Test frequencies k = 1, 2, 3
        significance_level=0.05, # 5% significance level
        use_dols=True,           # Use Dynamic OLS
        verbose=False            # Don't print detailed output here
    )
    
    print()
    print("=" * 70)
    print("RESULTS")
    print("=" * 70)
    print()
    print(f"Test Statistic (CI^m_f):     {results['test_statistic']:.6f}")
    print(f"Critical Value (5%):         {results['critical_value']:.6f}")
    print(f"Optimal Fourier Frequency:   k* = {results['optimal_k']}")
    print()
    print(f"Long-run Variance:           {results['optimal_results']['lrv']:.6f}")
    print(f"Estimated β:                 {results['optimal_results']['beta'][0,0]:.4f}")
    print()
    
    # F-test for Fourier significance
    print("F-Test for Structural Breaks:")
    print(f"  F-statistic:               {results['F_test']['F_statistic']:.4f}")
    print(f"  F critical value (5%):     {results['F_test']['critical_value_5pct']:.4f}")
    print(f"  Breaks significant:        {results['F_test']['reject_null']}")
    print()
    
    # Interpretation
    print("=" * 70)
    print("INTERPRETATION")
    print("=" * 70)
    print()
    
    if not results['reject_null']:
        print("✓ COINTEGRATION FOUND")
        print()
        print("  The null hypothesis of cointegration is NOT rejected at 5% level.")
        print("  Evidence suggests a long-run equilibrium relationship exists")
        print("  between the variables, even with structural breaks.")
        print()
        print(f"  The structural breaks are captured by Fourier frequency k={results['optimal_k']},")
        print("  eliminating the need to estimate specific break dates.")
    else:
        print("✗ NO COINTEGRATION")
        print()
        print("  The null hypothesis of cointegration is rejected at 5% level.")
        print("  No evidence of a long-run equilibrium relationship.")
    
    if results['F_test']['reject_null']:
        print()
        print("  The F-test confirms the presence of structural breaks,")
        print("  justifying the use of the Fourier approximation.")
    
    print()
    print("=" * 70)
    print()
    print("For more examples and options, see:")
    print("  - examples.py: Comprehensive examples")
    print("  - README.md: Full documentation")
    print("  - QUICK_START.md: Getting started guide")
    print()
    print("Questions? merwanroudane920@gmail.com")
    print("=" * 70)


if __name__ == "__main__":
    main()
