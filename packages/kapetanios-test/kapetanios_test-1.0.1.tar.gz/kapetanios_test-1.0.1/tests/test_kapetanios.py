"""
Unit tests for Kapetanios unit root test
"""

import pytest
import numpy as np
from kapetanios_test import KapetaniosTest, kapetanios_test, KapetaniosResult


class TestKapetaniosTest:
    """Test suite for KapetaniosTest class"""
    
    def test_initialization(self):
        """Test proper initialization"""
        test = KapetaniosTest(max_breaks=3, model='A', trimming=0.15)
        assert test.max_breaks == 3
        assert test.model == 'A'
        assert test.trimming == 0.15
    
    def test_invalid_max_breaks(self):
        """Test that invalid max_breaks raises error"""
        with pytest.raises(ValueError):
            KapetaniosTest(max_breaks=0)
        with pytest.raises(ValueError):
            KapetaniosTest(max_breaks=6)
    
    def test_invalid_model(self):
        """Test that invalid model raises error"""
        with pytest.raises(ValueError):
            KapetaniosTest(model='D')
    
    def test_invalid_trimming(self):
        """Test that invalid trimming raises error"""
        with pytest.raises(ValueError):
            KapetaniosTest(trimming=0)
        with pytest.raises(ValueError):
            KapetaniosTest(trimming=0.5)
    
    def test_random_walk(self):
        """Test on random walk (should not reject)"""
        np.random.seed(42)
        y = np.cumsum(np.random.randn(100))
        
        test = KapetaniosTest(max_breaks=2, model='C')
        result = test.fit(y)
        
        assert isinstance(result, KapetaniosResult)
        assert isinstance(result.statistic, float)
        assert isinstance(result.break_dates, list)
    
    def test_stationary_with_break(self):
        """Test on stationary series with structural break"""
        np.random.seed(123)
        T = 150
        
        # Generate AR(1) with break
        y = np.zeros(T)
        y[0] = np.random.randn()
        for t in range(1, T):
            if t < 75:
                y[t] = 0.5 + 0.7 * y[t-1] + np.random.randn()
            else:
                y[t] = 2.0 + 0.7 * y[t-1] + np.random.randn()
        
        result = kapetanios_test(y, max_breaks=2, model='A')
        
        # Should detect break around t=75
        assert len(result.break_dates) > 0
        assert any(60 < b < 90 for b in result.break_dates)
    
    def test_short_series_error(self):
        """Test that short series raises error"""
        y = np.random.randn(10)
        test = KapetaniosTest()
        
        with pytest.raises(ValueError):
            test.fit(y)
    
    def test_pandas_series_input(self):
        """Test that pandas Series input works"""
        import pandas as pd
        
        np.random.seed(42)
        y_array = np.cumsum(np.random.randn(100))
        y_series = pd.Series(y_array)
        
        result = kapetanios_test(y_series, max_breaks=2)
        assert isinstance(result, KapetaniosResult)
    
    def test_all_models(self):
        """Test all three model types"""
        np.random.seed(42)
        y = np.cumsum(np.random.randn(100))
        
        for model in ['A', 'B', 'C']:
            result = kapetanios_test(y, max_breaks=1, model=model)
            assert result.model_type == model
            assert isinstance(result.statistic, float)
    
    def test_lag_selection_methods(self):
        """Test different lag selection methods"""
        np.random.seed(42)
        y = np.cumsum(np.random.randn(100))
        
        for method in ['aic', 'bic', 't-stat']:
            result = kapetanios_test(
                y, 
                max_breaks=1, 
                lag_selection=method
            )
            assert result.lags >= 0
    
    def test_critical_values_structure(self):
        """Test that critical values have correct structure"""
        test = KapetaniosTest()
        
        for model in ['A', 'B', 'C']:
            assert model in test.CRITICAL_VALUES
            for m in range(1, 6):
                assert m in test.CRITICAL_VALUES[model]
                cv = test.CRITICAL_VALUES[model][m]
                assert 0.01 in cv
                assert 0.05 in cv
                assert 0.10 in cv
    
    def test_result_repr(self):
        """Test that result has proper string representation"""
        np.random.seed(42)
        y = np.cumsum(np.random.randn(100))
        
        result = kapetanios_test(y, max_breaks=2)
        result_str = repr(result)
        
        assert 'Kapetanios Unit Root Test Results' in result_str
        assert 'Test Statistic' in result_str
        assert 'Critical Values' in result_str
    
    def test_trimming_adjustment(self):
        """Test that max_breaks is adjusted for small samples"""
        np.random.seed(42)
        y = np.cumsum(np.random.randn(50))
        
        # With trimming=0.15 and T=50, can't fit 5 breaks
        with pytest.warns(UserWarning):
            result = kapetanios_test(y, max_breaks=5, trimming=0.15)
        
        assert result.n_breaks < 5
    
    def test_deterministic_results(self):
        """Test that results are deterministic"""
        np.random.seed(42)
        y = np.cumsum(np.random.randn(100))
        
        result1 = kapetanios_test(y, max_breaks=2)
        result2 = kapetanios_test(y, max_breaks=2)
        
        assert result1.statistic == result2.statistic
        assert result1.break_dates == result2.break_dates


class TestRealWorldScenarios:
    """Test real-world scenarios"""
    
    def test_gdp_like_series(self):
        """Test on GDP-like series with trend and break"""
        np.random.seed(42)
        T = 200
        t = np.arange(T)
        
        # Simulate GDP: trend + AR(1) + structural break
        y = 100 + 0.5 * t + np.cumsum(np.random.randn(T) * 0.5)
        y[100:] += 20  # Recession
        
        result = kapetanios_test(y, max_breaks=2, model='C')
        
        assert isinstance(result.statistic, float)
        assert len(result.break_dates) >= 1
    
    def test_multiple_breaks_detection(self):
        """Test detection of multiple breaks"""
        np.random.seed(123)
        T = 300
        t = np.arange(T)
        
        # Series with 2 clear breaks
        y = np.zeros(T)
        y[0] = 0
        for i in range(1, T):
            if i < 100:
                y[i] = 1.0 + 0.7 * y[i-1] + np.random.randn()
            elif i < 200:
                y[i] = 3.0 + 0.7 * y[i-1] + np.random.randn()
            else:
                y[i] = 5.0 + 0.7 * y[i-1] + np.random.randn()
        
        result = kapetanios_test(y, max_breaks=3, model='A')
        
        # Should detect breaks around t=100 and t=200
        assert len(result.break_dates) >= 2


class TestEdgeCases:
    """Test edge cases"""
    
    def test_constant_series(self):
        """Test on constant series"""
        y = np.ones(100)
        
        # Should handle without error
        result = kapetanios_test(y, max_breaks=1)
        assert isinstance(result, KapetaniosResult)
    
    def test_linear_trend(self):
        """Test on perfect linear trend"""
        y = np.arange(100, dtype=float)
        
        result = kapetanios_test(y, max_breaks=1)
        assert isinstance(result, KapetaniosResult)
    
    def test_very_small_trimming(self):
        """Test behavior with small trimming"""
        np.random.seed(42)
        y = np.cumsum(np.random.randn(100))
        
        # Very small trimming might cause issues
        result = kapetanios_test(y, max_breaks=1, trimming=0.05)
        assert isinstance(result, KapetaniosResult)


def test_convenience_function():
    """Test the convenience function"""
    np.random.seed(42)
    y = np.cumsum(np.random.randn(100))
    
    result = kapetanios_test(y)
    
    assert isinstance(result, KapetaniosResult)
    assert hasattr(result, 'statistic')
    assert hasattr(result, 'critical_values')
    assert hasattr(result, 'break_dates')


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
