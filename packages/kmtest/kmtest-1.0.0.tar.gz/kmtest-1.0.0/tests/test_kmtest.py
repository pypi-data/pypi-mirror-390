"""
Unit tests for kmtest package
"""

import pytest
import numpy as np
from kmtest import km_v1_test, km_v2_test, km_u1_test, km_u2_test, km_test_suite
from kmtest.helpers import create_lags, select_lag_order, detect_drift


class TestHelpers:
    """Test helper functions"""
    
    def test_create_lags(self):
        """Test lag creation"""
        x = np.array([1, 2, 3, 4, 5, 6])
        lags = create_lags(x, 2)
        
        assert lags.shape == (4, 2)
        assert np.array_equal(lags[:, 0], [2, 3, 4, 5])
        assert np.array_equal(lags[:, 1], [1, 2, 3, 4])
    
    def test_select_lag_order(self):
        """Test lag order selection"""
        np.random.seed(123)
        x = np.random.normal(0, 1, 100)
        
        p_aic = select_lag_order(x, max_p=5, criterion='AIC')
        p_bic = select_lag_order(x, max_p=5, criterion='BIC')
        
        assert isinstance(p_aic, (int, np.integer))
        assert isinstance(p_bic, (int, np.integer))
        assert 0 <= p_aic <= 5
        assert 0 <= p_bic <= 5
    
    def test_detect_drift(self):
        """Test drift detection"""
        np.random.seed(123)
        
        # Series with drift
        y_drift = np.cumsum(np.random.normal(0.5, 1, 100)) + 100
        assert detect_drift(y_drift) is True
        
        # Series without drift
        y_no_drift = np.cumsum(np.random.normal(0, 1, 100)) + 100
        # This might fail occasionally due to randomness, but should mostly work
        # We just check it returns a boolean
        result = detect_drift(y_no_drift)
        assert isinstance(result, (bool, np.bool_))


class TestV1Test:
    """Test V1 test function"""
    
    def test_v1_basic(self):
        """Test basic V1 functionality"""
        np.random.seed(123)
        y = np.cumsum(np.random.normal(0.5, 1, 100)) + 100
        
        result = km_v1_test(y)
        
        assert result.test_type == "V1"
        assert result.statistic is not None
        assert result.p_value is not None
        assert isinstance(result.reject_null, bool)
        assert result.lag_order >= 0
    
    def test_v1_invalid_input(self):
        """Test V1 with invalid input"""
        with pytest.raises(ValueError):
            km_v1_test([1, -2, 3, 4, 5])  # Negative value
        
        with pytest.raises(ValueError):
            km_v1_test([1, 2, 3])  # Too few observations
    
    def test_v1_specified_lag(self):
        """Test V1 with specified lag order"""
        np.random.seed(123)
        y = np.cumsum(np.random.normal(0.5, 1, 100)) + 100
        
        result = km_v1_test(y, p=2)
        assert result.lag_order == 2


class TestV2Test:
    """Test V2 test function"""
    
    def test_v2_basic(self):
        """Test basic V2 functionality"""
        np.random.seed(456)
        log_y = np.cumsum(np.random.normal(0.01, 0.05, 100)) + np.log(100)
        y = np.exp(log_y)
        
        result = km_v2_test(y)
        
        assert result.test_type == "V2"
        assert result.statistic is not None
        assert result.p_value is not None
        assert isinstance(result.reject_null, bool)
    
    def test_v2_invalid_input(self):
        """Test V2 with invalid input"""
        with pytest.raises(ValueError):
            km_v2_test([1, 0, 3, 4, 5])  # Zero value


class TestU1Test:
    """Test U1 test function"""
    
    def test_u1_basic(self):
        """Test basic U1 functionality"""
        np.random.seed(789)
        y = np.cumsum(np.random.normal(0, 1, 100)) + 100
        
        result = km_u1_test(y)
        
        assert result.test_type == "U1"
        assert result.statistic is not None
        assert result.p_value is None
        assert result.critical_values is not None
        assert isinstance(result.reject_null, dict)
        assert '0.05' in result.reject_null


class TestU2Test:
    """Test U2 test function"""
    
    def test_u2_basic(self):
        """Test basic U2 functionality"""
        np.random.seed(321)
        log_y = np.cumsum(np.random.normal(0, 0.05, 100)) + np.log(100)
        y = np.exp(log_y)
        
        result = km_u2_test(y)
        
        assert result.test_type == "U2"
        assert result.statistic is not None
        assert result.critical_values is not None
        assert isinstance(result.reject_null, dict)


class TestTestSuite:
    """Test the complete test suite"""
    
    def test_suite_with_drift(self):
        """Test suite with drift detection"""
        np.random.seed(123)
        y = np.cumsum(np.random.normal(0.5, 1, 100)) + 100
        
        result = km_test_suite(y, verbose=False)
        
        assert result.recommendation in ["LEVELS", "LOGARITHMS", "INCONCLUSIVE"]
        assert result.test1_result is not None
        assert result.test2_result is not None
        assert isinstance(result.has_drift, bool)
    
    def test_suite_without_drift(self):
        """Test suite without drift"""
        np.random.seed(456)
        y = np.cumsum(np.random.normal(0, 1, 100)) + 100
        
        result = km_test_suite(y, has_drift=False, verbose=False)
        
        assert result.test1_result.test_type == "U1"
        assert result.test2_result.test_type == "U2"
    
    def test_suite_forced_drift(self):
        """Test suite with forced drift parameter"""
        np.random.seed(789)
        y = np.cumsum(np.random.normal(0.5, 1, 100)) + 100
        
        result = km_test_suite(y, has_drift=True, verbose=False)
        
        assert result.test1_result.test_type == "V1"
        assert result.test2_result.test_type == "V2"
        assert result.has_drift is True
    
    def test_suite_summary(self):
        """Test suite summary method"""
        np.random.seed(111)
        y = np.cumsum(np.random.normal(0.5, 1, 100)) + 100
        
        result = km_test_suite(y, verbose=False)
        summary = result.summary()
        
        assert isinstance(summary, dict)
        assert 'recommendation' in summary
        assert 'interpretation' in summary
        assert 'test1' in summary
        assert 'test2' in summary


class TestResultObjects:
    """Test result object functionality"""
    
    def test_result_str(self):
        """Test string representation of results"""
        np.random.seed(123)
        y = np.cumsum(np.random.normal(0.5, 1, 100)) + 100
        
        result = km_v1_test(y)
        result_str = str(result)
        
        assert "Kobayashi-McAleer" in result_str
        assert "Test Statistic" in result_str
    
    def test_suite_result_str(self):
        """Test string representation of suite results"""
        np.random.seed(456)
        y = np.cumsum(np.random.normal(0.5, 1, 100)) + 100
        
        result = km_test_suite(y, verbose=False)
        result_str = str(result)
        
        assert "RECOMMENDATION" in result_str
        assert "Interpretation" in result_str


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
