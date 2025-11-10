"""
funitroot: Fourier Unit Root Tests Package
===========================================

A Python package for testing unit roots in time series with structural breaks
using Fourier approximations.

Implements:
- Fourier ADF Test (Enders & Lee, 2012)
- Fourier KPSS Test (Becker, Enders & Lee, 2006)

Author: Dr. Merwan Roudane
Email: merwanroudane920@gmail.com
GitHub: https://github.com/merwanroudane/funitroot
"""

__version__ = "1.0.1"
__author__ = "Dr. Merwan Roudane"
__email__ = "merwanroudane920@gmail.com"

from .fourier_adf import FourierADF, fourier_adf_test
from .fourier_kpss import FourierKPSS, fourier_kpss_test
from .visualization import (
    plot_series_with_fourier,
    plot_test_results,
    plot_frequency_search,
    plot_comparative_analysis,
    plot_residual_diagnostics
)

__all__ = [
    'FourierADF',
    'FourierKPSS',
    'fourier_adf_test',
    'fourier_kpss_test',
    'plot_series_with_fourier',
    'plot_test_results',
    'plot_frequency_search',
    'plot_comparative_analysis',
    'plot_residual_diagnostics'
]
