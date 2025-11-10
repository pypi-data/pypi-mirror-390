# funitroot: Fourier Unit Root Tests

[![Python Version](https://img.shields.io/badge/python-3.7+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

A comprehensive Python package for testing unit roots in time series with structural breaks using Fourier approximations.

## Features

- **Fourier ADF Test** (Enders & Lee, 2012): Tests for unit roots allowing for smooth structural breaks
- **Fourier KPSS Test** (Becker, Enders & Lee, 2006): Tests for stationarity with smooth breaks
- **Interactive Visualizations**: Beautiful plots using Plotly
- **Comprehensive Documentation**: Detailed examples and API reference
- **Easy to Use**: Simple and intuitive interface

## Installation

```bash
pip install funitroot
```

Or install from source:

```bash
git clone https://github.com/merwanroudane/funitroot.git
cd funitroot
pip install -e .
```

## Quick Start

### Fourier ADF Test

```python
import numpy as np
from funitroot import fourier_adf_test, plot_test_results

# Generate data with structural break
np.random.seed(42)
T = 200
t = np.arange(T)
break_point = 100

y = np.zeros(T)
y[:break_point] = 5 + 0.5 * np.sin(2 * np.pi * t[:break_point] / 50) + np.random.randn(break_point) * 0.5
y[break_point:] = 8 + 0.5 * np.sin(2 * np.pi * t[break_point:] / 50) + np.random.randn(T - break_point) * 0.5

# Perform Fourier ADF test
result = fourier_adf_test(y, model='c', max_freq=3)
print(result.summary())

# Visualize results
plot_test_results(result)
```

### Fourier KPSS Test

```python
from funitroot import fourier_kpss_test

# Perform Fourier KPSS test
result = fourier_kpss_test(y, model='c', max_freq=3)
print(result.summary())
```

### Comparative Analysis

```python
from funitroot import plot_comparative_analysis

# Compare both tests
plot_comparative_analysis(y, model='c', max_freq=5)
```

## Mathematical Background

### Fourier ADF Test

The Fourier ADF test extends the standard ADF test by incorporating Fourier terms to capture smooth structural breaks:

Δyₜ = α + βt + δyₜ₋₁ + γ₁sin(2πkt/T) + γ₂cos(2πkt/T) + Σφᵢ Δyₜ₋ᵢ + εₜ

Where:
- k is the frequency (automatically selected)
- T is the sample size
- The Fourier terms capture smooth breaks

**Null Hypothesis**: yₜ has a unit root
**Alternative**: yₜ is stationary around Fourier components

### Fourier KPSS Test

The Fourier KPSS test extends the standard KPSS test:

yₜ = α + βt + γ₁sin(2πkt/T) + γ₂cos(2πkt/T) + εₜ

**Null Hypothesis**: yₜ is stationary around Fourier components
**Alternative**: yₜ has a unit root

## API Reference

### FourierADF Class

```python
class FourierADF:
    """
    Fourier ADF unit root test.
    
    Parameters
    ----------
    data : array-like
        Time series data to test
    model : str, default='c'
        't' for constant, 'ct' for constant and trend
    max_lag : int, optional
        Maximum lag length for augmentation
    max_freq : int, default=5
        Maximum frequency to search (1-5)
    ic : str, default='aic'
        Information criterion: 'aic', 'bic', or 'tstat'
    trimm : float, default=0.1
        Trimming parameter
    
    Attributes
    ----------
    statistic : float
        Test statistic value
    pvalue : float
        Approximate p-value
    optimal_frequency : int
        Selected optimal frequency
    optimal_lag : int
        Selected optimal lag
    critical_values : dict
        Critical values at 1%, 5%, 10%
    reject_null : bool
        Whether to reject unit root hypothesis
    """
```

### FourierKPSS Class

```python
class FourierKPSS:
    """
    Fourier KPSS stationarity test.
    
    Parameters
    ----------
    data : array-like
        Time series data to test
    model : str, default='c'
        'c' for level stationarity, 'ct' for trend stationarity
    max_freq : int, default=5
        Maximum frequency to search (1-5)
    lags : str or int, default='auto'
        Number of lags for Newey-West estimator
    
    Attributes
    ----------
    statistic : float
        Test statistic value
    pvalue : float
        Approximate p-value
    optimal_frequency : int
        Selected optimal frequency
    critical_values : dict
        Critical values at 1%, 5%, 10%
    reject_null : bool
        Whether to reject stationarity hypothesis
    """
```

## Visualization Functions

### plot_series_with_fourier

```python
plot_series_with_fourier(data, optimal_frequency, model='c', show=True)
```

Plot original series with fitted Fourier components.

### plot_test_results

```python
plot_test_results(test_result, show=True)
```

Plot test statistic with critical values.

### plot_frequency_search

```python
plot_frequency_search(data, model='c', max_freq=5, test_type='adf', show=True)
```

Plot test statistics across different frequencies.

### plot_comparative_analysis

```python
plot_comparative_analysis(data, model='c', max_freq=5, show=True)
```

Compare Fourier ADF and KPSS test results.

### plot_residual_diagnostics

```python
plot_residual_diagnostics(test_result, show=True)
```

Plot residual diagnostics (ACF, histogram, Q-Q plot).

## Examples

See the `examples/` directory for complete examples:

- `example_basic.py`: Basic usage of both tests
- `example_visualization.py`: All visualization functions
- `example_real_data.py`: Analysis with real economic data
- `example_comparative.py`: Comparative analysis

## References

1. **Enders, W., and Lee, J. (2012)**  
   "The flexible Fourier form and Dickey-Fuller type unit root tests"  
   *Economics Letters*, 117, 196-199.

2. **Becker, R., Enders, W., and Lee, J. (2006)**  
   "A stationarity test in the presence of an unknown number of smooth breaks"  
   *Journal of Time Series Analysis*, 27(3), 381-409.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Author

**Dr. Merwan Roudane**
- Email: merwanroudane920@gmail.com
- GitHub: https://github.com/merwanroudane/funitroot

## Citation

If you use this package in your research, please cite:

```bibtex
@software{funitroot2024,
  author = {Roudane, Merwan},
  title = {funitroot: Fourier Unit Root Tests for Python},
  year = {2024},
  url = {https://github.com/merwanroudane/funitroot}
}
```

## Acknowledgments

This package implements the methods developed by:
- Walter Enders
- Junsoo Lee
- Ralf Becker

## Support

If you encounter any issues or have questions, please open an issue on GitHub:
https://github.com/merwanroudane/funitroot/issues
