"""
Test suite for running all appropriate Kobayashi-McAleer tests
"""

import numpy as np
from typing import Optional

from .km_tests import km_v1_test, km_v2_test, km_u1_test, km_u2_test
from .helpers import detect_drift
from .results import KMTestSuiteResult


def km_test_suite(y: np.ndarray, 
                  has_drift: Optional[bool] = None,
                  p: Optional[int] = None,
                  max_p: int = 12,
                  alpha: float = 0.05,
                  verbose: bool = True) -> KMTestSuiteResult:
    """
    Run complete Kobayashi-McAleer test suite
    
    Automatically selects and runs appropriate tests (V1/V2 or U1/U2) based on 
    drift detection, then provides a clear recommendation.
    
    Parameters:
        y: Time series array (must be positive)
        has_drift: If True, use V tests; if False, use U tests; 
                   if None (default), automatically detect drift
        p: Number of lags (default: automatically selected)
        max_p: Maximum number of lags to consider
        alpha: Significance level for drift detection and hypothesis testing
        verbose: If True, print progress messages
        
    Returns:
        KMTestSuiteResult object with recommendation and detailed results
        
    Example:
        >>> import numpy as np
        >>> from kmtest import km_test_suite
        >>> 
        >>> # Linear process with drift
        >>> np.random.seed(123)
        >>> y_linear = np.cumsum(np.random.normal(0.5, 1, 200)) + 100
        >>> result = km_test_suite(y_linear)
        >>> print(result.recommendation)  # "LEVELS"
        >>> 
        >>> # Logarithmic process with drift
        >>> log_y = np.cumsum(np.random.normal(0.01, 0.05, 200)) + np.log(100)
        >>> y_log = np.exp(log_y)
        >>> result = km_test_suite(y_log)
        >>> print(result.recommendation)  # "LOGARITHMS"
    """
    # Input validation
    y = np.asarray(y, dtype=float)
    
    if not np.all(y > 0):
        raise ValueError("y must contain only positive values")
    if len(y) < 10:
        raise ValueError("y must have at least 10 observations")
    
    # Detect drift if not specified
    if has_drift is None:
        has_drift = detect_drift(y, alpha=alpha)
        if verbose:
            drift_msg = "WITH drift detected" if has_drift else "WITHOUT drift detected"
            print(f"\nAutomatic drift detection: {drift_msg}")
    else:
        # Ensure has_drift is a Python bool (in case user passes numpy bool)
        has_drift = bool(has_drift)
    
    # Run appropriate tests based on drift
    if has_drift:
        if verbose:
            print("Running V1 and V2 tests (with drift)...")
        
        test1_result = km_v1_test(y, p=p, max_p=max_p)
        test2_result = km_v2_test(y, p=p, max_p=max_p)
        
        # Decision logic for V tests (asymptotically normal)
        v1_reject = test1_result.reject_null
        v2_reject = test2_result.reject_null
        
        if v1_reject and not v2_reject:
            recommendation = "LOGARITHMS"
            interpretation = (
                "V1 test rejects linear model (p-value = {:.4f}), "
                "while V2 test accepts logarithmic model (p-value = {:.4f}). "
                "The logarithmic transformation is more appropriate."
            ).format(test1_result.p_value, test2_result.p_value)
        elif v2_reject and not v1_reject:
            recommendation = "LEVELS"
            interpretation = (
                "V2 test rejects logarithmic model (p-value = {:.4f}), "
                "while V1 test accepts linear model (p-value = {:.4f}). "
                "The linear (levels) specification is more appropriate."
            ).format(test2_result.p_value, test1_result.p_value)
        elif not v1_reject and not v2_reject:
            recommendation = "LEVELS"
            interpretation = (
                "Both tests accept their null hypotheses (V1 p-value = {:.4f}, "
                "V2 p-value = {:.4f}). This suggests both specifications may be "
                "reasonable. Using levels (linear) as default."
            ).format(test1_result.p_value, test2_result.p_value)
        else:  # Both reject
            recommendation = "INCONCLUSIVE"
            interpretation = (
                "Both tests reject their null hypotheses (V1 p-value = {:.4f}, "
                "V2 p-value = {:.4f}). Results are inconclusive. "
                "Consider checking data quality or trying alternative specifications."
            ).format(test1_result.p_value, test2_result.p_value)
    
    else:  # No drift
        if verbose:
            print("Running U1 and U2 tests (no drift)...")
        
        test1_result = km_u1_test(y, p=p, max_p=max_p)
        test2_result = km_u2_test(y, p=p, max_p=max_p)
        
        # Decision logic for U tests (nonstandard distribution)
        # Use 5% significance level
        u1_reject = test1_result.reject_null['0.05']
        u2_reject = test2_result.reject_null['0.05']
        
        if u1_reject and not u2_reject:
            recommendation = "LOGARITHMS"
            interpretation = (
                "U1 test rejects linear model (|statistic| = {:.4f} > {:.4f}), "
                "while U2 test accepts logarithmic model (|statistic| = {:.4f} < {:.4f}). "
                "The logarithmic transformation is more appropriate."
            ).format(abs(test1_result.statistic), test1_result.critical_values['0.05'],
                    abs(test2_result.statistic), test2_result.critical_values['0.05'])
        elif u2_reject and not u1_reject:
            recommendation = "LEVELS"
            interpretation = (
                "U2 test rejects logarithmic model (|statistic| = {:.4f} > {:.4f}), "
                "while U1 test accepts linear model (|statistic| = {:.4f} < {:.4f}). "
                "The linear (levels) specification is more appropriate."
            ).format(abs(test2_result.statistic), test2_result.critical_values['0.05'],
                    abs(test1_result.statistic), test1_result.critical_values['0.05'])
        elif not u1_reject and not u2_reject:
            recommendation = "LEVELS"
            interpretation = (
                "Both tests accept their null hypotheses (U1: |statistic| = {:.4f}, "
                "U2: |statistic| = {:.4f}, critical value = {:.4f}). "
                "Both specifications may be reasonable. Using levels (linear) as default."
            ).format(abs(test1_result.statistic), abs(test2_result.statistic),
                    test1_result.critical_values['0.05'])
        else:  # Both reject
            recommendation = "INCONCLUSIVE"
            interpretation = (
                "Both tests reject their null hypotheses (U1: |statistic| = {:.4f}, "
                "U2: |statistic| = {:.4f}, critical value = {:.4f}). "
                "Results are inconclusive. Consider checking data quality."
            ).format(abs(test1_result.statistic), abs(test2_result.statistic),
                    test1_result.critical_values['0.05'])
    
    if verbose:
        print(f"\nRecommendation: Model data in {recommendation}")
    
    return KMTestSuiteResult(
        recommendation=recommendation,
        test1_result=test1_result,
        test2_result=test2_result,
        has_drift=has_drift,
        interpretation=interpretation
    )
