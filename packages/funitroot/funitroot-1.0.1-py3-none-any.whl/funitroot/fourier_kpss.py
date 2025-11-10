"""
Fourier KPSS Stationarity Test
Based on: Becker, R., Enders, W., and Lee, J. (2006)
"A stationarity test in the presence of an unknown number of smooth breaks"
Journal of Time Series Analysis, 27(3), 381-409.

Author: Dr. Merwan Roudane
Email: merwanroudane920@gmail.com
GitHub: https://github.com/merwanroudane/funitroot
"""

import numpy as np
import pandas as pd
from scipy import stats
from typing import Tuple, Optional, Union, Dict
import warnings


class FourierKPSS:
    """
    Fourier KPSS stationarity test with flexible Fourier form.
    
    This test allows for smooth structural breaks of unknown number and form
    using Fourier approximations. Unlike standard KPSS, null hypothesis is
    stationarity around Fourier components.
    
    Parameters
    ----------
    data : array-like
        Time series data to test
    model : str, default='c'
        Deterministic terms: 'c' for level stationarity, 'ct' for trend stationarity
    max_freq : int, default=5
        Maximum frequency to search (upper bound is 5)
    lags : str or int, default='auto'
        Number of lags for Newey-West HAC estimator. 
        If 'auto', uses int(4*(T/100)^(2/9))
        
    Attributes
    ----------
    statistic : float
        The test statistic value (minimum over frequencies)
    pvalue : float
        The approximate p-value
    optimal_frequency : int
        The selected optimal frequency
    critical_values : dict
        Critical values at 1%, 5%, and 10% levels
    reject_null : bool
        Whether to reject the null hypothesis of stationarity
    tau_statistic : float
        The Fourier KPSS τ statistic
        
    References
    ----------
    Becker, R., Enders, W., and Lee, J. (2006). "A stationarity test in the 
    presence of an unknown number of smooth breaks," Journal of Time Series 
    Analysis, 27(3), 381-409.
    """
    
    def __init__(
        self,
        data: Union[np.ndarray, pd.Series, list],
        model: str = 'c',
        max_freq: int = 5,
        lags: Union[str, int] = 'auto'
    ):
        # Convert data to numpy array
        if isinstance(data, (pd.Series, pd.DataFrame)):
            self.data = data.values.flatten()
        else:
            self.data = np.array(data).flatten()
            
        # Remove NaN values
        self.data = self.data[~np.isnan(self.data)]
        
        self.T = len(self.data)
        self.model = model.lower()
        self.max_freq = min(max_freq, 5)  # Upper bound is 5
        
        # Set number of lags for Newey-West estimator
        if lags == 'auto':
            self.lags = int(4 * (self.T / 100) ** (2/9))
        else:
            self.lags = int(lags)
            
        # Validate inputs
        if self.model not in ['c', 'ct']:
            raise ValueError("model must be 'c' or 'ct'")
        if self.max_freq < 1 or self.max_freq > 5:
            raise ValueError("max_freq must be between 1 and 5")
            
        # Run the test
        self._run_test()
        
    def _create_fourier_terms(self, k: int) -> Tuple[np.ndarray, np.ndarray]:
        """Create Fourier trigonometric terms."""
        t = np.arange(1, self.T + 1)
        sin_term = np.sin(2 * np.pi * k * t / self.T)
        cos_term = np.cos(2 * np.pi * k * t / self.T)
        return sin_term, cos_term
    
    def _create_deterministic_terms(self, k: int) -> np.ndarray:
        """Create deterministic regressors including Fourier terms."""
        t = np.arange(1, self.T + 1)
        
        # Constant
        const = np.ones(self.T)
        
        # Get Fourier terms
        sin_k, cos_k = self._create_fourier_terms(k)
        
        if self.model == 'c':
            # Model with constant and Fourier terms (level stationarity)
            Z = np.column_stack([const, sin_k, cos_k])
        else:  # model == 'ct'
            # Model with constant, trend, and Fourier terms (trend stationarity)
            Z = np.column_stack([const, t, sin_k, cos_k])
            
        return Z
    
    def _ols_regression(
        self,
        y: np.ndarray,
        X: np.ndarray
    ) -> Tuple[np.ndarray, np.ndarray]:
        """Perform OLS regression."""
        # Add small regularization to avoid singular matrix
        XtX = X.T @ X
        XtX += np.eye(XtX.shape[0]) * 1e-10
        
        beta = np.linalg.solve(XtX, X.T @ y)
        residuals = y - X @ beta
        
        return beta, residuals
    
    def _compute_long_run_variance(self, residuals: np.ndarray) -> float:
        """
        Compute long-run variance using Newey-West HAC estimator.
        
        Uses Bartlett kernel with automatic bandwidth selection.
        """
        T = len(residuals)
        
        # Residual variance (lag 0)
        s0 = np.sum(residuals ** 2) / T
        
        # Autocovariances
        gamma_sum = 0.0
        for lag in range(1, self.lags + 1):
            # Bartlett kernel weight
            weight = 1 - lag / (self.lags + 1)
            
            # Autocovariance at lag
            gamma_lag = np.sum(residuals[lag:] * residuals[:-lag]) / T
            
            # Add weighted autocovariance (both positive and negative lags)
            gamma_sum += 2 * weight * gamma_lag
        
        # Long-run variance
        s2_lr = s0 + gamma_sum
        
        # Ensure positive
        s2_lr = max(s2_lr, 1e-10)
        
        return s2_lr
    
    def _compute_kpss_statistic(
        self,
        residuals: np.ndarray,
        s2_lr: float
    ) -> float:
        """Compute the KPSS test statistic."""
        T = len(residuals)
        
        # Partial sum of residuals
        S = np.cumsum(residuals)
        
        # KPSS statistic
        numerator = np.sum(S ** 2) / T ** 2
        statistic = numerator / s2_lr
        
        return statistic
    
    def _test_at_frequency(self, k: int) -> Tuple[float, np.ndarray, float]:
        """Perform test at given frequency and return SSR."""
        # Create deterministic terms
        Z = self._create_deterministic_terms(k)
        
        # Detrend data using Fourier regression
        beta, residuals = self._ols_regression(self.data, Z)
        
        # Compute SSR for frequency selection (like GAUSS code)
        ssr = np.sum(residuals ** 2)
        
        # Compute long-run variance
        s2_lr = self._compute_long_run_variance(residuals)
        
        # Compute KPSS statistic
        tau_stat = self._compute_kpss_statistic(residuals, s2_lr)
        
        return tau_stat, residuals, ssr
    
    def _run_test(self):
        """Run the complete Fourier KPSS test."""
        # Search over frequencies using minimum SSR (like GAUSS code)
        min_ssr = np.inf
        opt_freq = 1
        opt_stat = np.inf
        opt_residuals = None
        
        for k in range(1, self.max_freq + 1):
            stat, residuals, ssr = self._test_at_frequency(k)
            
            # Use minimum SSR to select frequency (like GAUSS _get_fourier)
            if ssr < min_ssr:
                min_ssr = ssr
                opt_freq = k
                opt_stat = stat
                opt_residuals = residuals
        
        self.statistic = opt_stat
        self.tau_statistic = opt_stat
        self.optimal_frequency = opt_freq
        self.residuals = opt_residuals
        
        # Get critical values
        self.critical_values = self._get_critical_values()
        
        # Determine if we reject null hypothesis (stationarity)
        # If statistic > critical value, reject stationarity
        self.reject_null = self.statistic > self.critical_values['5%']
        
        # Approximate p-value
        self.pvalue = self._approximate_pvalue()
    
    def _get_critical_values(self) -> Dict[str, float]:
        """
        Get critical values from Becker, Enders, Lee (2006) Table 1.
        
        Critical values depend on:
        - Sample size T
        - Model specification (level vs. trend stationarity)
        - Optimal frequency k
        
        Note: This matches the GAUSS implementation exactly.
        """
        k = self.optimal_frequency
        T = self.T
        
        # Critical values from original GAUSS code
        if self.model == 'c':
            if T <= 250:
                crit_table = [
                    [0.2699, 0.1720, 0.1318],  # k=1
                    [0.6671, 0.4152, 0.3150],  # k=2
                    [0.7182, 0.4480, 0.3393],  # k=3
                    [0.7222, 0.4592, 0.3476],  # k=4
                    [0.7386, 0.4626, 0.3518]   # k=5
                ]
            elif 251 <= T <= 500:
                crit_table = [
                    [0.2709, 0.1696, 0.1294],
                    [0.6615, 0.4075, 0.3053],
                    [0.7046, 0.4424, 0.3309],
                    [0.7152, 0.4491, 0.3369],
                    [0.7344, 0.4571, 0.3415]
                ]
            else:  # T > 500
                crit_table = [
                    [0.2706, 0.1704, 0.1295],
                    [0.6526, 0.4047, 0.3050],
                    [0.7086, 0.4388, 0.3304],
                    [0.7163, 0.4470, 0.3355],
                    [0.7297, 0.4525, 0.3422]
                ]
        else:  # model == 'ct'
            if T <= 250:
                crit_table = [
                    [0.0716, 0.0546, 0.0471],  # k=1
                    [0.2022, 0.1321, 0.1034],  # k=2
                    [0.2103, 0.1423, 0.1141],  # k=3
                    [0.2170, 0.1478, 0.1189],  # k=4
                    [0.2177, 0.1484, 0.1201]   # k=5
                ]
            elif 251 <= T <= 500:
                crit_table = [
                    [0.0720, 0.0539, 0.0463],
                    [0.1968, 0.1278, 0.0995],
                    [0.2091, 0.1404, 0.1123],
                    [0.2111, 0.1441, 0.1155],
                    [0.2178, 0.1465, 0.1178]
                ]
            else:  # T > 500
                crit_table = [
                    [0.0718, 0.0538, 0.0461],
                    [0.1959, 0.1275, 0.0994],
                    [0.2081, 0.1398, 0.1117],
                    [0.2139, 0.1436, 0.1149],
                    [0.2153, 0.1451, 0.1163]
                ]
        
        # Get critical values for optimal frequency (k-1 for 0-indexing)
        cv_values = crit_table[k - 1]
        
        return {
            '1%': cv_values[0],
            '5%': cv_values[1],
            '10%': cv_values[2]
        }
    
    def _approximate_pvalue(self) -> float:
        """Approximate p-value based on critical values."""
        cv = self.critical_values
        
        # For KPSS, larger statistics indicate more evidence against stationarity
        if self.statistic > cv['1%']:
            return 0.01
        elif self.statistic > cv['5%']:
            # Interpolate between 1% and 5%
            slope = (0.01 - 0.05) / (cv['1%'] - cv['5%'])
            return 0.05 + slope * (self.statistic - cv['5%'])
        elif self.statistic > cv['10%']:
            # Interpolate between 5% and 10%
            slope = (0.05 - 0.10) / (cv['5%'] - cv['10%'])
            return 0.10 + slope * (self.statistic - cv['10%'])
        else:
            return 0.10
    
    def summary(self) -> str:
        """Return a formatted summary of test results."""
        summary = []
        summary.append("=" * 60)
        summary.append("Fourier KPSS Stationarity Test Results")
        summary.append("=" * 60)
        summary.append(f"Model: {'Level stationarity' if self.model == 'c' else 'Trend stationarity'}")
        summary.append(f"Sample size: {self.T}")
        summary.append(f"Newey-West lags: {self.lags}")
        summary.append(f"Null hypothesis: Stationarity around Fourier components")
        summary.append("-" * 60)
        summary.append(f"Optimal frequency (k): {self.optimal_frequency}")
        summary.append(f"τ statistic: {self.tau_statistic:.6f}")
        summary.append(f"Approximate p-value: {self.pvalue:.4f}")
        summary.append("-" * 60)
        summary.append("Critical values:")
        for level, value in self.critical_values.items():
            summary.append(f"  {level:>3s} : {value:8.6f}")
        summary.append("-" * 60)
        summary.append(f"Conclusion: {'Reject' if self.reject_null else 'Fail to reject'} null hypothesis of stationarity")
        summary.append(f"            at 5% significance level")
        if not self.reject_null:
            summary.append(f"            → Evidence for stationarity with smooth breaks")
        else:
            summary.append(f"            → Evidence against stationarity (unit root)")
        summary.append("=" * 60)
        
        return '\n'.join(summary)
    
    def __repr__(self) -> str:
        return (f"FourierKPSS(statistic={self.statistic:.6f}, "
                f"optimal_frequency={self.optimal_frequency}, "
                f"reject_null={self.reject_null})")


def fourier_kpss_test(
    data: Union[np.ndarray, pd.Series, list],
    model: str = 'c',
    max_freq: int = 5,
    lags: Union[str, int] = 'auto'
) -> FourierKPSS:
    """
    Convenience function for Fourier KPSS stationarity test.
    
    Parameters
    ----------
    data : array-like
        Time series data to test
    model : str, default='c'
        Deterministic terms: 'c' for level stationarity, 'ct' for trend stationarity
    max_freq : int, default=5
        Maximum frequency to search (upper bound is 5)
    lags : str or int, default='auto'
        Number of lags for Newey-West HAC estimator
        
    Returns
    -------
    FourierKPSS
        Test results object
        
    Examples
    --------
    >>> import numpy as np
    >>> from funitroot import fourier_kpss_test
    >>> 
    >>> # Generate stationary data with structural break
    >>> np.random.seed(42)
    >>> T = 200
    >>> t = np.arange(T)
    >>> break_point = 100
    >>> y = np.zeros(T)
    >>> y[:break_point] = 5 + 0.5 * np.sin(2 * np.pi * t[:break_point] / 50) + np.random.randn(break_point) * 0.5
    >>> y[break_point:] = 8 + 0.5 * np.sin(2 * np.pi * t[break_point:] / 50) + np.random.randn(T - break_point) * 0.5
    >>> 
    >>> # Perform test
    >>> result = fourier_kpss_test(y, model='c', max_freq=3)
    >>> print(result.summary())
    >>> print(f"Stationary: {not result.reject_null}")
    """
    return FourierKPSS(
        data=data,
        model=model,
        max_freq=max_freq,
        lags=lags
    )
