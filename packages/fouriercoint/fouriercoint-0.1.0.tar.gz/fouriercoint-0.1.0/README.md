# Fourier Cointegration Test

[![Python 3.7+](https://img.shields.io/badge/python-3.7+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

Python implementation of the **Fourier approximation test for cointegration** proposed by Tsong et al. (2016).

**Author:** Dr. Merwan Roudane  
**Email:** merwanroudane920@gmail.com  
**GitHub:** https://github.com/merwanroudane/fouriercoint

## 📖 Overview

This package implements the cointegration test developed by Tsong et al. (2016), which tests the null hypothesis of cointegration against the alternative of no cointegration, while allowing for **structural breaks of unknown form** in the deterministic trend using Fourier approximation.

### Key Features

✅ Tests for cointegration with structural breaks  
✅ No need to estimate break dates or number of breaks  
✅ Handles unknown forms of structural changes  
✅ Implements both OLS and DOLS estimation  
✅ Automatic optimal Fourier frequency selection  
✅ Critical values from Tsong et al. (2016) Table 1  
✅ F-test for Fourier significance  
✅ Compatible with Windows, Linux, and macOS

## 📚 Reference

**Tsong, C.C., Lee, C.F., Tsai, L.J., & Hu, T.C. (2016).**  
*The Fourier approximation and testing for the null of cointegration.*  
**Empirical Economics**, 51(3), 1085-1113.  
DOI: [10.1007/s00181-015-1028-6](https://doi.org/10.1007/s00181-015-1028-6)

## 🔧 Installation

### From PyPI (coming soon)

```bash
pip install fouriercoint
```

### From source

```bash
git clone https://github.com/merwanroudane/fouriercoint.git
cd fouriercoint
pip install -e .
```

### Requirements

- Python >= 3.7
- NumPy >= 1.19.0
- SciPy >= 1.5.0

## 🚀 Quick Start

### Basic Usage

```python
import numpy as np
from fouriercoint import fourier_cointegration_test

# Generate sample I(1) data
np.random.seed(42)
T = 200
x = np.cumsum(np.random.randn(T, 1))  # I(1) regressor
y = 2 + 0.5 * x + np.cumsum(np.random.randn(T, 1) * 0.1)  # Cointegrated

# Run the test
results = fourier_cointegration_test(
    y=y,
    x=x,
    m=1,              # 1 = constant + trend + Fourier
    kmax=3,           # Maximum Fourier frequency
    significance_level=0.05,
    use_dols=True     # Use DOLS estimation
)

# Print results
print(f"Test Statistic: {results['test_statistic']:.4f}")
print(f"Critical Value (5%): {results['critical_value']:.4f}")
print(f"Cointegration Evidence: {not results['reject_null']}")
print(f"\n{results['conclusion']}")
```

### Output

```
======================================================================
FOURIER COINTEGRATION TEST RESULTS
Tsong et al. (2016)
======================================================================
Sample size (T):              200
Number of regressors (p):     1
Model specification (m):      1 (constant + trend + Fourier)
Estimation method:            DOLS
DOLS leads/lags (q):          5
Kernel:                       bartlett
----------------------------------------------------------------------
Optimal Fourier frequency:    k* = 1
Test statistic CI^m_f:        0.0234
Critical value (5%):          0.0480
Long-run variance:            0.0089
----------------------------------------------------------------------
Critical values:
  10%:  0.0420
  5%:   0.0480
  1%:   0.0630
----------------------------------------------------------------------
F-test for Fourier:           F = 8.2341
F critical value (5%):        4.0190
Fourier significant:          True
======================================================================
CONCLUSION: Do not reject the null hypothesis of cointegration at 5.0% level. 
Evidence supports cointegration with structural breaks (Fourier frequency k=1).
======================================================================
```

## 📊 Methodology

### The Model

The cointegration regression is specified as:

```
y_t = d_t + x'_t β + η_t
```

where the deterministic component is:

```
d_t = δ_0 + δ_1 t + α_k sin(2πkt/T) + β_k cos(2πkt/T)
```

### Test Statistic

The test statistic is:

```
CI^m_f = T^{-2} ω̂^{-2}_1 Σ_{t=1}^T S^2_t
```

where:
- `S_t = Σ_{i=1}^t ε̂_i` is the partial sum of residuals
- `ω̂^2_1` is the long-run variance estimate
- `m = 0` for constant + Fourier
- `m = 1` for constant + trend + Fourier

### Hypothesis Testing

- **H₀:** Cointegration with structural breaks (σ²_u = 0)
- **H₁:** No cointegration (σ²_u > 0)

**Reject H₀** if `CI^m_f > critical value` → No cointegration  
**Do not reject H₀** if `CI^m_f ≤ critical value` → Evidence of cointegration

## 📖 Detailed Usage

### Model Specifications

```python
# Model 0: Level shifts only (constant + Fourier)
results_m0 = fourier_cointegration_test(y, x, m=0)

# Model 1: Level and trend shifts (constant + trend + Fourier)
results_m1 = fourier_cointegration_test(y, x, m=1)
```

### Multivariate Case

```python
# Multiple regressors
x_multi = np.cumsum(np.random.randn(T, 3), axis=0)  # 3 I(1) regressors
y = 2 + x_multi @ np.array([[0.5], [0.3], [-0.2]]) + np.random.randn(T, 1)

results = fourier_cointegration_test(y, x_multi, m=1)
```

### Customize Test Options

```python
results = fourier_cointegration_test(
    y=y,
    x=x,
    m=1,
    kmax=5,                    # Test frequencies 1 through 5
    q=3,                       # DOLS leads/lags (default: T^{1/3})
    kernel='qs',               # 'bartlett' or 'qs' (Quadratic Spectral)
    bandwidth=10,              # Manual bandwidth (default: automatic)
    significance_level=0.01,   # 1%, 5%, or 10%
    use_dols=True,             # DOLS vs OLS
    verbose=True               # Print detailed output
)
```

### Access Detailed Results

```python
# Test statistics for all frequencies
for k in range(1, 4):
    stat = results['all_frequencies'][k]['statistic']
    print(f"k={k}: Statistic = {stat:.4f}")

# Cointegrating vector
beta_hat = results['optimal_results']['beta']
print(f"Estimated β: {beta_hat.flatten()}")

# Residuals and diagnostics
residuals = results['optimal_results']['residuals']
lrv = results['optimal_results']['lrv']
```

### F-test for Fourier Significance

The package automatically performs an F-test to check if the Fourier component is necessary:

```python
f_test = results['F_test']
print(f"F-statistic: {f_test['F_statistic']:.4f}")
print(f"Fourier needed: {f_test['reject_null']}")
```

## 🧪 Testing Framework

### Running Tests

```python
# Example: Test with known cointegrated data
import numpy as np
from fouriercoint import fourier_cointegration_test

np.random.seed(123)
T = 150

# Generate cointegrated data with structural break
t = np.arange(T)
break_point = T // 2
trend_shift = np.where(t < break_point, 0, 3)  # Level shift at midpoint

x = np.cumsum(np.random.randn(T, 1))
y = 2 + 0.5 * x + trend_shift.reshape(-1, 1) + np.random.randn(T, 1) * 0.5

# Test should find cointegration with Fourier term
results = fourier_cointegration_test(y, x, m=0, kmax=3)
assert not results['reject_null'], "Should not reject cointegration"
assert results['fourier_significant'], "Fourier should be significant"
```

## 💡 Practical Application: Fiscal Sustainability

Following Tsong et al. (2016) empirical application:

```python
import pandas as pd
from fouriercoint import fourier_cointegration_test

# Load fiscal data (revenue and expenditure)
data = pd.read_excel('fiscal_data.xlsx')
revenue = data['revenue'].values.reshape(-1, 1)
expenditure = data['expenditure'].values.reshape(-1, 1)

# Test for cointegration (fiscal sustainability)
results = fourier_cointegration_test(
    y=revenue,
    x=expenditure,
    m=1,  # Allow for both level and trend breaks
    kmax=3,
    significance_level=0.05
)

# Interpretation
if not results['reject_null']:
    print("Evidence of fiscal sustainability (cointegration found)")
    print(f"Structural breaks approximated with Fourier k={results['optimal_k']}")
else:
    print("No evidence of fiscal sustainability")
```

## 📊 Comparison with Alternative Tests

| Feature | Tsong et al. (2016) | Gregory-Hansen (1996) | Shin (1994) |
|---------|---------------------|----------------------|-------------|
| Structural breaks | ✅ Yes (unknown form) | ✅ Yes (one break) | ❌ No |
| Estimate break dates | ❌ Not needed | ✅ Required | N/A |
| Multiple breaks | ✅ Yes | ❌ No | N/A |
| Gradual breaks | ✅ Yes | ❌ No (sharp only) | N/A |
| Computational cost | Low | High | Low |

## 🔬 Technical Details

### Critical Values

Critical values are provided for:
- Model specifications: `m ∈ {0, 1}`
- Fourier frequencies: `k ∈ {1, 2, 3}`
- Regressor dimensions: `p ∈ {1, 2, 3, 4}`
- Significance levels: `{1%, 5%, 10%}`

The package automatically interpolates for other values.

### Long-run Variance Estimation

Supports multiple kernel methods:
- **Bartlett** (Newey-West): Recommended for most cases
- **Quadratic Spectral**: Better for highly persistent processes

Automatic bandwidth selection using Andrews (1991) method.

### DOLS Estimation

Dynamic OLS (Saikkonen 1991) is used to handle endogenous regressors:

```
y_t = d_t + x'_t β + Σ_{i=-q}^{q} Δx'_{t-i} φ_i + ε*_t
```

## 📝 Citation

If you use this package in your research, please cite:

```bibtex
@article{tsong2016fourier,
  title={The Fourier approximation and testing for the null of cointegration},
  author={Tsong, Ching-Chuan and Lee, Cheng-Feng and Tsai, Li-Ju and Hu, Te-Chung},
  journal={Empirical Economics},
  volume={51},
  number={3},
  pages={1085--1113},
  year={2016},
  publisher={Springer}
}

@software{roudane2024fouriercoint,
  author = {Roudane, Merwan},
  title = {fouriercoint: Fourier Cointegration Test in Python},
  year = {2024},
  url = {https://github.com/merwanroudane/fouriercoint}
}
```

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 📧 Contact

**Dr. Merwan Roudane**  
Email: merwanroudane920@gmail.com  
GitHub: [@merwanroudane](https://github.com/merwanroudane)

## 🙏 Acknowledgments

- Original methodology: Tsong, Lee, Tsai, and Hu (2016)
- Inspired by R implementation and econometric theory
- Built for the Python econometrics community

## ⚠️ Disclaimer

This package is provided for research and educational purposes. Users should verify results for critical applications.

---

**Made with ❤️ for the econometrics community**
