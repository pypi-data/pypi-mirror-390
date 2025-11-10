"""
Unit Tests for funitroot package

Author: Dr. Merwan Roudane
"""

import unittest
import numpy as np
import sys
sys.path.insert(0, '..')

from funitroot import FourierADF, FourierKPSS, fourier_adf_test, fourier_kpss_test


class TestFourierADF(unittest.TestCase):
    """Test cases for Fourier ADF test."""
    
    def setUp(self):
        """Set up test fixtures."""
        np.random.seed(42)
        self.T = 200
        self.t = np.arange(self.T)
        
    def test_stationary_series(self):
        """Test with stationary series."""
        # Generate stationary series
        y = 5 + 0.5 * np.sin(2 * np.pi * self.t / 50) + np.random.randn(self.T) * 0.5
        
        # Run test
        result = FourierADF(y, model='c', max_freq=3)
        
        # Check attributes exist
        self.assertIsNotNone(result.statistic)
        self.assertIsNotNone(result.optimal_frequency)
        self.assertIsNotNone(result.critical_values)
        
        # Check frequency range
        self.assertGreaterEqual(result.optimal_frequency, 1)
        self.assertLessEqual(result.optimal_frequency, 3)
        
    def test_unit_root_series(self):
        """Test with unit root series."""
        # Generate random walk
        y = np.cumsum(np.random.randn(self.T) * 0.5)
        
        # Run test
        result = FourierADF(y, model='c', max_freq=3)
        
        # Check that we don't reject (likely)
        # Note: This is probabilistic, so we just check the test runs
        self.assertIsNotNone(result.statistic)
        
    def test_with_structural_break(self):
        """Test with series having structural break."""
        # Generate series with break
        y = np.zeros(self.T)
        break_point = self.T // 2
        y[:break_point] = 5 + np.random.randn(break_point) * 0.5
        y[break_point:] = 8 + np.random.randn(self.T - break_point) * 0.5
        
        # Run test
        result = FourierADF(y, model='c', max_freq=5)
        
        # Fourier terms should capture the break
        self.assertGreater(result.optimal_frequency, 0)
        
    def test_convenience_function(self):
        """Test convenience function."""
        y = 5 + np.random.randn(self.T) * 0.5
        
        result = fourier_adf_test(y, model='c', max_freq=3)
        
        self.assertIsInstance(result, FourierADF)
        
    def test_model_types(self):
        """Test different model specifications."""
        y = 5 + 0.01 * self.t + np.random.randn(self.T) * 0.5
        
        # Test with constant only
        result_c = FourierADF(y, model='c', max_freq=2)
        self.assertEqual(result_c.model, 'c')
        
        # Test with constant and trend
        result_ct = FourierADF(y, model='ct', max_freq=2)
        self.assertEqual(result_ct.model, 'ct')
        
    def test_ic_selection(self):
        """Test different information criteria."""
        y = 5 + np.random.randn(self.T) * 0.5
        
        result_aic = FourierADF(y, model='c', max_freq=2, ic='aic')
        result_bic = FourierADF(y, model='c', max_freq=2, ic='bic')
        
        self.assertEqual(result_aic.ic, 'aic')
        self.assertEqual(result_bic.ic, 'bic')
        
    def test_summary_method(self):
        """Test summary method."""
        y = 5 + np.random.randn(self.T) * 0.5
        result = FourierADF(y, model='c', max_freq=2)
        
        summary = result.summary()
        
        self.assertIsInstance(summary, str)
        self.assertIn('Test statistic', summary)
        self.assertIn('Critical values', summary)
        
    def test_repr_method(self):
        """Test __repr__ method."""
        y = 5 + np.random.randn(self.T) * 0.5
        result = FourierADF(y, model='c', max_freq=2)
        
        repr_str = repr(result)
        
        self.assertIsInstance(repr_str, str)
        self.assertIn('FourierADF', repr_str)


class TestFourierKPSS(unittest.TestCase):
    """Test cases for Fourier KPSS test."""
    
    def setUp(self):
        """Set up test fixtures."""
        np.random.seed(42)
        self.T = 200
        self.t = np.arange(self.T)
        
    def test_stationary_series(self):
        """Test with stationary series."""
        # Generate stationary series
        y = 5 + 0.5 * np.sin(2 * np.pi * self.t / 50) + np.random.randn(self.T) * 0.5
        
        # Run test
        result = FourierKPSS(y, model='c', max_freq=3)
        
        # Check attributes exist
        self.assertIsNotNone(result.statistic)
        self.assertIsNotNone(result.optimal_frequency)
        self.assertIsNotNone(result.critical_values)
        
        # For stationary series, we should fail to reject (likely)
        # Note: This is probabilistic
        self.assertIsNotNone(result.reject_null)
        
    def test_unit_root_series(self):
        """Test with unit root series."""
        # Generate random walk
        y = np.cumsum(np.random.randn(self.T) * 0.5)
        
        # Run test
        result = FourierKPSS(y, model='c', max_freq=3)
        
        self.assertIsNotNone(result.statistic)
        
    def test_with_structural_break(self):
        """Test with series having structural break."""
        # Generate series with break
        y = np.zeros(self.T)
        break_point = self.T // 2
        y[:break_point] = 5 + np.random.randn(break_point) * 0.5
        y[break_point:] = 8 + np.random.randn(self.T - break_point) * 0.5
        
        # Run test
        result = FourierKPSS(y, model='c', max_freq=5)
        
        # Fourier terms should capture the break
        self.assertGreater(result.optimal_frequency, 0)
        
    def test_convenience_function(self):
        """Test convenience function."""
        y = 5 + np.random.randn(self.T) * 0.5
        
        result = fourier_kpss_test(y, model='c', max_freq=3)
        
        self.assertIsInstance(result, FourierKPSS)
        
    def test_model_types(self):
        """Test different model specifications."""
        y = 5 + 0.01 * self.t + np.random.randn(self.T) * 0.5
        
        # Test with constant only
        result_c = FourierKPSS(y, model='c', max_freq=2)
        self.assertEqual(result_c.model, 'c')
        
        # Test with constant and trend
        result_ct = FourierKPSS(y, model='ct', max_freq=2)
        self.assertEqual(result_ct.model, 'ct')
        
    def test_lag_selection(self):
        """Test lag selection."""
        y = 5 + np.random.randn(self.T) * 0.5
        
        # Auto lag selection
        result_auto = FourierKPSS(y, model='c', max_freq=2, lags='auto')
        self.assertGreater(result_auto.lags, 0)
        
        # Manual lag selection
        result_manual = FourierKPSS(y, model='c', max_freq=2, lags=10)
        self.assertEqual(result_manual.lags, 10)
        
    def test_summary_method(self):
        """Test summary method."""
        y = 5 + np.random.randn(self.T) * 0.5
        result = FourierKPSS(y, model='c', max_freq=2)
        
        summary = result.summary()
        
        self.assertIsInstance(summary, str)
        self.assertIn('statistic', summary)
        self.assertIn('Critical values', summary)
        
    def test_repr_method(self):
        """Test __repr__ method."""
        y = 5 + np.random.randn(self.T) * 0.5
        result = FourierKPSS(y, model='c', max_freq=2)
        
        repr_str = repr(result)
        
        self.assertIsInstance(repr_str, str)
        self.assertIn('FourierKPSS', repr_str)


class TestDataTypes(unittest.TestCase):
    """Test different input data types."""
    
    def setUp(self):
        """Set up test fixtures."""
        np.random.seed(42)
        self.T = 100
        
    def test_numpy_array(self):
        """Test with numpy array."""
        y = np.random.randn(self.T)
        result = FourierADF(y, model='c', max_freq=2)
        self.assertIsNotNone(result.statistic)
        
    def test_list(self):
        """Test with Python list."""
        y = list(np.random.randn(self.T))
        result = FourierADF(y, model='c', max_freq=2)
        self.assertIsNotNone(result.statistic)
        
    def test_with_nan_values(self):
        """Test handling of NaN values."""
        y = np.random.randn(self.T)
        y[10] = np.nan
        y[50] = np.nan
        
        result = FourierADF(y, model='c', max_freq=2)
        self.assertIsNotNone(result.statistic)
        self.assertEqual(result.T, self.T - 2)  # Should remove NaNs


class TestEdgeCases(unittest.TestCase):
    """Test edge cases and error handling."""
    
    def test_invalid_model(self):
        """Test invalid model specification."""
        y = np.random.randn(100)
        
        with self.assertRaises(ValueError):
            FourierADF(y, model='invalid')
            
    def test_invalid_ic(self):
        """Test invalid information criterion."""
        y = np.random.randn(100)
        
        with self.assertRaises(ValueError):
            FourierADF(y, model='c', ic='invalid')
            
    def test_invalid_frequency(self):
        """Test invalid frequency range."""
        y = np.random.randn(100)
        
        with self.assertRaises(ValueError):
            FourierADF(y, model='c', max_freq=10)  # > 5
            
    def test_short_series(self):
        """Test with very short series."""
        y = np.random.randn(20)
        
        # Should still run but may give warnings
        result = FourierADF(y, model='c', max_freq=1)
        self.assertIsNotNone(result.statistic)


if __name__ == '__main__':
    # Run tests with verbose output
    unittest.main(verbosity=2)
