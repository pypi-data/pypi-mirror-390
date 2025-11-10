"""
Fourier ADF Unit Root Test
Based on: Enders, W., and Lee, J. (2012)
"The flexible Fourier form and Dickey-Fuller type unit root test"
Economics Letters, 117, (2012), 196-199.

Author: Dr. Merwan Roudane
Email: merwanroudane920@gmail.com
GitHub: https://github.com/merwanroudane/funitroot
"""

import numpy as np
import pandas as pd
from scipy import stats
from scipy.optimize import minimize_scalar
from typing import Tuple, Optional, Union, Dict, List
import warnings


class FourierADF:
    """
    Fourier ADF unit root test with flexible Fourier form.
    
    This test allows for smooth structural breaks of unknown number and form
    using Fourier approximations.
    
    Parameters
    ----------
    data : array-like
        Time series data to test
    model : str, default='c'
        Deterministic terms: 'c' for constant, 'ct' for constant and trend
    max_lag : int, optional
        Maximum lag length for augmentation. Default is 8.
    max_freq : int, default=5
        Maximum frequency to search (upper bound is 5)
    ic : str, default='aic'
        Information criterion for lag selection: 'aic', 'bic', or 'tstat'
    trimm : float, default=0.1
        Trimming parameter for frequency search
        
    Attributes
    ----------
    statistic : float
        The test statistic value
    pvalue : float
        The p-value (based on critical values)
    optimal_frequency : int
        The selected optimal frequency
    optimal_lag : int
        The selected optimal lag
    critical_values : dict
        Critical values at 1%, 5%, and 10% levels
    reject_null : bool
        Whether to reject the null hypothesis of unit root
        
    References
    ----------
    Enders, W., and Lee, J. (2012). "The flexible Fourier form and 
    Dickey-Fuller type unit root tests," Economics Letters, 117, 196-199.
    """
    
    def __init__(
        self,
        data: Union[np.ndarray, pd.Series, list],
        model: str = 'c',
        max_lag: Optional[int] = None,
        max_freq: int = 5,
        ic: str = 'aic',
        trimm: float = 0.1
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
        self.ic = ic.lower()
        self.trimm = trimm
        
        # Set default max_lag if not provided
        if max_lag is None:
            self.max_lag = int(12 * (self.T / 100) ** (1/4))
        else:
            self.max_lag = max_lag
            
        # Validate inputs
        if self.model not in ['c', 'ct']:
            raise ValueError("model must be 'c' or 'ct'")
        if self.ic not in ['aic', 'bic', 'tstat']:
            raise ValueError("ic must be 'aic', 'bic', or 'tstat'")
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
            # Model with constant only
            Z = np.column_stack([const, sin_k, cos_k])
        else:  # model == 'ct'
            # Model with constant and trend
            Z = np.column_stack([const, t, sin_k, cos_k])
            
        return Z
    
    def _ols_regression(
        self,
        y: np.ndarray,
        X: np.ndarray
    ) -> Tuple[np.ndarray, np.ndarray, float]:
        """Perform OLS regression."""
        # Add small regularization to avoid singular matrix
        XtX = X.T @ X
        XtX += np.eye(XtX.shape[0]) * 1e-10
        
        beta = np.linalg.solve(XtX, X.T @ y)
        residuals = y - X @ beta
        sse = np.sum(residuals ** 2)
        
        return beta, residuals, sse
    
    def _compute_aic_bic(
        self,
        sse: float,
        n_obs: int,
        n_params: int
    ) -> Tuple[float, float]:
        """Compute AIC and BIC."""
        log_sse = np.log(sse / n_obs)
        aic = log_sse + 2 * n_params / n_obs
        bic = log_sse + n_params * np.log(n_obs) / n_obs
        return aic, bic
    
    def _select_lag(
        self,
        y_lag: np.ndarray,
        Z: np.ndarray,
        dy: np.ndarray
    ) -> Tuple[int, float]:
        """Select optimal lag length."""
        aic_values = []
        bic_values = []
        tstat_values = []
        
        for p in range(self.max_lag + 1):
            # Prepare lagged differences
            if p > 0:
                dy_lags = np.column_stack([
                    np.roll(dy, i+1)[p:] for i in range(p)
                ])
                X = np.column_stack([
                    y_lag[p:],
                    Z[p:],
                    dy_lags
                ])
                y_dep = dy[p:]
            else:
                X = np.column_stack([y_lag, Z])
                y_dep = dy
            
            # OLS regression
            beta, resid, sse = self._ols_regression(y_dep, X)
            n_obs = len(y_dep)
            n_params = X.shape[1]
            
            # Compute information criteria
            aic, bic = self._compute_aic_bic(sse, n_obs, n_params)
            aic_values.append(aic)
            bic_values.append(bic)
            
            # Compute t-statistic for last lag (if p > 0)
            if p > 0:
                # Standard error of last coefficient
                sigma2 = sse / (n_obs - n_params)
                XtX_inv = np.linalg.inv(X.T @ X + np.eye(n_params) * 1e-10)
                se = np.sqrt(sigma2 * np.diag(XtX_inv))
                t_stat = np.abs(beta[-1] / se[-1])
                tstat_values.append(t_stat)
            else:
                tstat_values.append(0)
        
        # Select lag based on criterion
        if self.ic == 'aic':
            opt_lag = np.argmin(aic_values)
        elif self.ic == 'bic':
            opt_lag = np.argmin(bic_values)
        else:  # tstat
            # Find first lag where t-stat is insignificant
            opt_lag = self.max_lag
            for p in range(self.max_lag, 0, -1):
                if tstat_values[p] > 1.645:  # 10% significance
                    opt_lag = p
                    break
        
        # Get test statistic for optimal lag
        if opt_lag > 0:
            dy_lags = np.column_stack([
                np.roll(dy, i+1)[opt_lag:] for i in range(opt_lag)
            ])
            X = np.column_stack([
                y_lag[opt_lag:],
                Z[opt_lag:],
                dy_lags
            ])
            y_dep = dy[opt_lag:]
        else:
            X = np.column_stack([y_lag, Z])
            y_dep = dy
        
        beta, resid, sse = self._ols_regression(y_dep, X)
        n_obs = len(y_dep)
        n_params = X.shape[1]
        
        # Compute t-statistic for lagged level
        sigma2 = sse / (n_obs - n_params)
        XtX_inv = np.linalg.inv(X.T @ X + np.eye(n_params) * 1e-10)
        se = np.sqrt(sigma2 * np.diag(XtX_inv))
        t_stat = beta[0] / se[0]
        
        return opt_lag, t_stat
    
    def _test_at_frequency(self, k: int) -> Tuple[int, float]:
        """Perform test at given frequency."""
        # Create deterministic terms
        Z = self._create_deterministic_terms(k)
        
        # Create lagged level and differences
        y_lag = self.data[:-1]
        dy = np.diff(self.data)
        Z = Z[1:]  # Align with differences
        
        # Select lag and get test statistic
        opt_lag, t_stat = self._select_lag(y_lag, Z, dy)
        
        return opt_lag, t_stat
    
    def _run_test(self):
        """Run the complete Fourier ADF test."""
        # Search over frequencies
        min_stat = np.inf
        opt_freq = 1
        opt_lag = 0
        
        for k in range(1, self.max_freq + 1):
            lag, stat = self._test_at_frequency(k)
            
            # We want the minimum (most negative) statistic
            if stat < min_stat:
                min_stat = stat
                opt_freq = k
                opt_lag = lag
        
        self.statistic = min_stat
        self.optimal_frequency = opt_freq
        self.optimal_lag = opt_lag
        
        # Get critical values
        self.critical_values = self._get_critical_values()
        
        # Determine if we reject null hypothesis
        self.reject_null = self.statistic < self.critical_values['5%']
        
        # Approximate p-value
        self.pvalue = self._approximate_pvalue()
    
    def _get_critical_values(self) -> Dict[str, float]:
        """
        Get critical values from Enders & Lee (2012) Table 1.
        
        Critical values depend on:
        - Sample size T
        - Model specification (constant vs. constant + trend)
        - Optimal frequency k
        
        Note: This matches the GAUSS implementation exactly.
        """
        k = self.optimal_frequency
        T = self.T
        
        # Critical values from original GAUSS code
        if self.model == 'c':
            if T <= 150:
                crit_table = [
                    [-4.42, -3.81, -3.49],  # k=1
                    [-3.97, -3.27, -2.91],  # k=2
                    [-3.77, -3.07, -2.71],  # k=3
                    [-3.64, -2.97, -2.64],  # k=4
                    [-3.58, -2.93, -2.60]   # k=5
                ]
            elif 151 <= T <= 349:
                crit_table = [
                    [-4.37, -3.78, -3.47],
                    [-3.93, -3.26, -2.92],
                    [-3.74, -3.06, -2.72],
                    [-3.62, -2.98, -2.65],
                    [-3.55, -2.94, -2.62]
                ]
            elif 350 <= T <= 500:
                crit_table = [
                    [-4.35, -3.76, -3.46],
                    [-3.91, -3.26, -2.91],
                    [-3.70, -3.06, -2.72],
                    [-3.62, -2.97, -2.66],
                    [-3.56, -2.94, -2.62]
                ]
            else:  # T > 500
                crit_table = [
                    [-4.31, -3.75, -3.45],
                    [-3.89, -3.25, -2.90],
                    [-3.69, -3.05, -2.71],
                    [-3.61, -2.96, -2.64],
                    [-3.53, -2.93, -2.61]
                ]
        else:  # model == 'ct'
            if T <= 150:
                crit_table = [
                    [-4.95, -4.35, -4.05],  # k=1
                    [-4.69, -4.05, -3.71],  # k=2
                    [-4.45, -3.78, -3.44],  # k=3
                    [-4.29, -3.65, -3.29],  # k=4
                    [-4.20, -3.56, -3.22]   # k=5
                ]
            elif 151 <= T <= 349:
                crit_table = [
                    [-4.87, -4.31, -4.02],
                    [-4.62, -4.01, -3.69],
                    [-4.38, -3.77, -3.43],
                    [-4.27, -3.63, -3.31],
                    [-4.18, -3.56, -3.24]
                ]
            elif 350 <= T <= 500:
                crit_table = [
                    [-4.81, -4.29, -4.01],
                    [-4.57, -3.99, -3.67],
                    [-4.38, -3.76, -3.43],
                    [-4.25, -3.64, -3.31],
                    [-4.18, -3.56, -3.25]
                ]
            else:  # T > 500
                crit_table = [
                    [-4.80, -4.27, -4.00],
                    [-4.58, -3.98, -3.67],
                    [-4.38, -3.75, -3.43],
                    [-4.24, -3.63, -3.30],
                    [-4.16, -3.55, -3.24]
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
        
        if self.statistic < cv['1%']:
            return 0.01
        elif self.statistic < cv['5%']:
            # Interpolate between 1% and 5%
            slope = (0.05 - 0.01) / (cv['5%'] - cv['1%'])
            return 0.01 + slope * (self.statistic - cv['1%'])
        elif self.statistic < cv['10%']:
            # Interpolate between 5% and 10%
            slope = (0.10 - 0.05) / (cv['10%'] - cv['5%'])
            return 0.05 + slope * (self.statistic - cv['5%'])
        else:
            return 0.10
    
    def summary(self) -> str:
        """Return a formatted summary of test results."""
        summary = []
        summary.append("=" * 60)
        summary.append("Fourier ADF Unit Root Test Results")
        summary.append("=" * 60)
        summary.append(f"Model: {'Constant' if self.model == 'c' else 'Constant + Trend'}")
        summary.append(f"Sample size: {self.T}")
        summary.append(f"Maximum lag tested: {self.max_lag}")
        summary.append(f"Lag selection criterion: {self.ic.upper()}")
        summary.append("-" * 60)
        summary.append(f"Optimal frequency (k): {self.optimal_frequency}")
        summary.append(f"Optimal lag (p): {self.optimal_lag}")
        summary.append(f"Test statistic: {self.statistic:.4f}")
        summary.append(f"Approximate p-value: {self.pvalue:.4f}")
        summary.append("-" * 60)
        summary.append("Critical values:")
        for level, value in self.critical_values.items():
            summary.append(f"  {level:>3s} : {value:7.4f}")
        summary.append("-" * 60)
        summary.append(f"Conclusion: {'Reject' if self.reject_null else 'Fail to reject'} null hypothesis of unit root")
        summary.append(f"            at 5% significance level")
        summary.append("=" * 60)
        
        return '\n'.join(summary)
    
    def __repr__(self) -> str:
        return (f"FourierADF(statistic={self.statistic:.4f}, "
                f"optimal_frequency={self.optimal_frequency}, "
                f"optimal_lag={self.optimal_lag}, "
                f"reject_null={self.reject_null})")


def fourier_adf_test(
    data: Union[np.ndarray, pd.Series, list],
    model: str = 'c',
    max_lag: Optional[int] = None,
    max_freq: int = 5,
    ic: str = 'aic',
    trimm: float = 0.1
) -> FourierADF:
    """
    Convenience function for Fourier ADF test.
    
    Parameters
    ----------
    data : array-like
        Time series data to test
    model : str, default='c'
        Deterministic terms: 'c' for constant, 'ct' for constant and trend
    max_lag : int, optional
        Maximum lag length for augmentation
    max_freq : int, default=5
        Maximum frequency to search (upper bound is 5)
    ic : str, default='aic'
        Information criterion for lag selection: 'aic', 'bic', or 'tstat'
    trimm : float, default=0.1
        Trimming parameter for frequency search
        
    Returns
    -------
    FourierADF
        Test results object
        
    Examples
    --------
    >>> import numpy as np
    >>> from funitroot import fourier_adf_test
    >>> 
    >>> # Generate data with structural break
    >>> np.random.seed(42)
    >>> T = 200
    >>> t = np.arange(T)
    >>> break_point = 100
    >>> y = np.zeros(T)
    >>> y[:break_point] = 5 + 0.5 * np.sin(2 * np.pi * t[:break_point] / 50) + np.random.randn(break_point) * 0.5
    >>> y[break_point:] = 8 + 0.5 * np.sin(2 * np.pi * t[break_point:] / 50) + np.random.randn(T - break_point) * 0.5
    >>> 
    >>> # Perform test
    >>> result = fourier_adf_test(y, model='c', max_freq=3)
    >>> print(result.summary())
    >>> print(f"Reject null: {result.reject_null}")
    """
    return FourierADF(
        data=data,
        model=model,
        max_lag=max_lag,
        max_freq=max_freq,
        ic=ic,
        trimm=trimm
    )
