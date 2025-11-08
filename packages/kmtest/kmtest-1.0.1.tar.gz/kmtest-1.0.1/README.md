# kmtest: Kobayashi-McAleer Tests for Python

[![PyPI version](https://badge.fury.io/py/kmtest.svg)](https://badge.fury.io/py/kmtest)
[![Python 3.7+](https://img.shields.io/badge/python-3.7+-blue.svg)](https://www.python.org/downloads/)
[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)

Python implementation of the **Kobayashi-McAleer (1999) tests** for choosing between linear and logarithmic transformations of integrated time series processes.

**Author:** Dr. Merwan Roudane ([merwanroudane920@gmail.com](mailto:merwanroudane920@gmail.com))

## 📚 Reference

Based on:

> **Kobayashi, M. and McAleer, M. (1999)**  
> Tests of Linear and Logarithmic Transformations for Integrated Processes.  
> *Journal of the American Statistical Association*, 94(447), 860-868.  
> DOI: [10.1080/01621459.1999.10474191](https://doi.org/10.1080/01621459.1999.10474191)

## 🎯 What Does This Package Do?

When working with time series data, a fundamental question is: **Should I model my data in levels or logarithms?**

This package provides **rigorous statistical tests** to answer this question for integrated (I(1)) processes:

- ✅ **V1 Test**: Tests linear (with drift) vs logarithmic transformation
- ✅ **V2 Test**: Tests logarithmic (with drift) vs linear transformation  
- ✅ **U1 Test**: Tests linear (no drift) vs logarithmic transformation
- ✅ **U2 Test**: Tests logarithmic (no drift) vs linear transformation
- ✅ **Test Suite**: Automatically runs appropriate tests and provides clear recommendations

## 📦 Installation

### From PyPI (recommended)

```bash
pip install kmtest
```

### From source

```bash
git clone https://github.com/merwanroudane/kmtest.git
cd kmtest
pip install -e .
```

## 🚀 Quick Start

### Example 1: Using the Test Suite (Easiest)

```python
import numpy as np
from kmtest import km_test_suite

# Simulate a linear integrated process with drift
np.random.seed(123)
y_linear = np.cumsum(np.random.normal(0.5, 1, 200)) + 100

# Run the full test suite
result = km_test_suite(y_linear)
print(result)
# Output: "RECOMMENDATION: Model data in LEVELS"
```

### Example 2: Logarithmic Process

```python
# Simulate a logarithmic integrated process
np.random.seed(456)
log_y = np.cumsum(np.random.normal(0.01, 0.05, 200)) + np.log(100)
y_log = np.exp(log_y)

result = km_test_suite(y_log)
print(result)
# Output: "RECOMMENDATION: Model data in LOGARITHMS"
```

### Example 3: Individual Tests

```python
from kmtest import km_v1_test, km_v2_test

# Test linear vs logarithmic (with drift)
v1_result = km_v1_test(y_linear)
print(v1_result)

# Test logarithmic vs linear (with drift)
v2_result = km_v2_test(y_linear)
print(v2_result)
```

### Example 4: Process Without Drift

```python
from kmtest import km_u1_test, km_u2_test

# Random walk without drift
y_no_drift = np.cumsum(np.random.normal(0, 1, 200)) + 100

# Use U tests for processes without drift
u1_result = km_u1_test(y_no_drift)
u2_result = km_u2_test(y_no_drift)
```

## 📖 Documentation

### Main Functions

#### `km_test_suite(y, has_drift=None, p=None, max_p=12, alpha=0.05, verbose=True)`

Runs the complete test suite and provides a clear recommendation.

**Parameters:**
- `y` (array-like): Time series data (must be positive)
- `has_drift` (bool, optional): If True, use V tests; if False, use U tests; if None (default), automatically detect drift
- `p` (int, optional): Number of lags for AR process (automatically selected by AIC if None)
- `max_p` (int): Maximum number of lags to consider (default: 12)
- `alpha` (float): Significance level for testing (default: 0.05)
- `verbose` (bool): Print progress messages (default: True)

**Returns:**
- `KMTestSuiteResult`: Object containing recommendation and detailed results

---

#### `km_v1_test(y, p=None, max_p=12)`

Tests the null hypothesis of a linear integrated process (with drift) against a logarithmic alternative.

**Test Statistic:** Under the null hypothesis, V1 ~ N(0,1) asymptotically.

---

#### `km_v2_test(y, p=None, max_p=12)`

Tests the null hypothesis of a logarithmic integrated process (with drift) against a linear alternative.

**Test Statistic:** Under the null hypothesis, V2 ~ N(0,1) asymptotically.

---

#### `km_u1_test(y, p=None, max_p=12)`

Tests the null hypothesis of a linear integrated process (no drift) against a logarithmic alternative.

**Test Statistic:** U1 has a nonstandard asymptotic distribution. Critical values from simulation.

---

#### `km_u2_test(y, p=None, max_p=12)`

Tests the null hypothesis of a logarithmic integrated process (no drift) against a linear alternative.

**Test Statistic:** U2 has a nonstandard asymptotic distribution. Critical values from simulation.

---

### Result Objects

#### `KMTestResult`

Object returned by individual tests containing:
- `statistic`: Test statistic value
- `p_value`: P-value (for V tests) or None
- `critical_values`: Dictionary of critical values (for U tests) or None
- `reject_null`: Boolean or dictionary indicating rejection
- `null_hypothesis`: Description of null hypothesis
- `alternative`: Description of alternative hypothesis
- `lag_order`: Selected lag order
- `drift_estimate`: Estimated drift parameter (if applicable)
- `variance_estimate`: Estimated innovation variance
- `test_type`: Type of test ('V1', 'V2', 'U1', 'U2')

#### `KMTestSuiteResult`

Object returned by test suite containing:
- `recommendation`: "LEVELS", "LOGARITHMS", or "INCONCLUSIVE"
- `test1_result`: First test result (V1 or U1)
- `test2_result`: Second test result (V2 or U2)
- `has_drift`: Whether drift was detected
- `interpretation`: Detailed interpretation text

## 🔬 Methodology

### The Problem

For an integrated time series Y_t, should we model:
1. **Linear model**: Y_t - Y_{t-1} = μ + Σ a_j (Y_{t-j} - Y_{t-j-1}) + ε_t
2. **Logarithmic model**: log(Y_t) - log(Y_{t-1}) = η + Σ b_j (log(Y_{t-j}) - log(Y_{t-j-1})) + u_t

### The Tests

**V Tests (With Drift):**
- Uses asymptotic normality under null hypothesis
- Appropriate when series has positive drift
- Tests heteroscedasticity pattern in misspecified model

**U Tests (Without Drift):**
- Uses nonstandard asymptotic distribution
- Appropriate when series has no drift (random walk)
- Critical values from Monte Carlo simulation

### Decision Logic

The test suite automatically:
1. Detects presence of drift
2. Runs appropriate pair of tests (V1/V2 or U1/U2)
3. Interprets results using nonnested testing framework
4. Provides clear recommendation: LEVELS or LOGARITHMS

## 📊 Critical Values

For U tests (without drift), critical values from Kobayashi & McAleer (1999):

| Significance Level | Critical Value |
|-------------------|----------------|
| 10%               | 0.477          |
| 5%                | 0.664          |
| 1%                | 1.116          |

*Note: Due to symmetry, U1 and U2 have identical critical values.*

## 💡 When to Use Each Test

| Your Data Characteristics | Use This Test |
|--------------------------|---------------|
| Integrated process with positive trend | V1 and V2 tests |
| Random walk without trend | U1 and U2 tests |
| Unsure about drift | `km_test_suite()` with automatic detection |

## 🔧 Advanced Usage

### Custom Lag Selection

```python
# Specify lag order manually
result = km_v1_test(y, p=2)

# Adjust maximum lag for automatic selection
result = km_v1_test(y, max_p=8)
```

### Controlling Verbosity

```python
# Silent mode
result = km_test_suite(y, verbose=False)

# Access results programmatically
if result.recommendation == "LOGARITHMS":
    y_transformed = np.log(y)
else:
    y_transformed = y
```

### Extracting Detailed Information

```python
result = km_test_suite(y)

# Get summary as dictionary
summary = result.summary()

# Access individual test results
v1_result = result.test1_result
v2_result = result.test2_result

# Check specific test statistics
print(f"V1 statistic: {v1_result.statistic:.4f}")
print(f"V1 p-value: {v1_result.p_value:.4f}")
print(f"Lag order: {v1_result.lag_order}")
```

## 🧪 Testing

Run the test suite:

```bash
pytest tests/
```

With coverage:

```bash
pytest --cov=kmtest tests/
```

## 📝 Examples

See the `examples/` directory for:
- Basic usage examples
- Comparison with R implementation
- Monte Carlo simulations
- Real economic data applications

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📄 License

This project is licensed under the GNU General Public License v3.0 or later - see the [LICENSE](LICENSE) file for details.

## 📧 Contact

**Dr. Merwan Roudane**  
Email: [merwanroudane920@gmail.com](mailto:merwanroudane920@gmail.com)  
GitHub: [@merwanroudane](https://github.com/merwanroudane)

## 🙏 Acknowledgments

- Original methodology by Masahito Kobayashi and Michael McAleer (1999)
- R implementation available at: [https://github.com/merwanroudane/kmtest](https://github.com/merwanroudane/kmtest)

## 📚 Citation

If you use this package in your research, please cite:

```bibtex
@software{roudane2024kmtest,
  author = {Roudane, Merwan},
  title = {kmtest: Kobayashi-McAleer Tests for Python},
  year = {2024},
  url = {https://github.com/merwanroudane/kmtest}
}

@article{kobayashi1999tests,
  title={Tests of linear and logarithmic transformations for integrated processes},
  author={Kobayashi, Masahito and McAleer, Michael},
  journal={Journal of the American Statistical Association},
  volume={94},
  number={447},
  pages={860--868},
  year={1999},
  publisher={Taylor \& Francis},
  doi={10.1080/01621459.1999.10474191}
}
```

## 🗺️ Roadmap

- [ ] Add plotting functions for diagnostic visualization
- [ ] Implement bootstrap versions of U tests
- [ ] Add support for multivariate extensions
- [ ] Create interactive Jupyter notebook tutorials
- [ ] Add more real-world example datasets

---

**Happy testing!** 📈✨
