"""
Main test functions for Kobayashi-McAleer tests
"""

import numpy as np
from scipy import stats
from typing import Optional

from .helpers import (
    create_lags,
    select_lag_order,
    estimate_ar_model,
    get_u1_critical_values,
    get_u2_critical_values
)
from .results import KMTestResult


def km_v1_test(y: np.ndarray, p: Optional[int] = None, max_p: int = 12) -> KMTestResult:
    """
    Kobayashi-McAleer V1 Test
    
    Tests the null hypothesis of a linear integrated process with positive drift
    against the alternative of a logarithmic integrated process.
    Based on Kobayashi & McAleer (1999) JASA.
    
    Parameters:
        y: Time series array (must be positive)
        p: Number of lags for AR process (default: automatically selected by AIC)
        max_p: Maximum number of lags to consider for automatic selection
        
    Returns:
        KMTestResult object containing test statistics and results
        
    Reference:
        Kobayashi, M. and McAleer, M. (1999). Tests of Linear and Logarithmic
        Transformations for Integrated Processes. Journal of the American
        Statistical Association, 94(447), 860-868.
    """
    # Input validation
    y = np.asarray(y, dtype=float)
    
    if not np.all(y > 0):
        raise ValueError("y must contain only positive values")
    if len(y) < 10:
        raise ValueError("y must have at least 10 observations")
    
    n = len(y)
    delta_y = np.diff(y)
    
    # Select optimal lag if not specified
    if p is None:
        p = select_lag_order(delta_y, max_p, criterion='AIC')
    
    # Estimate the linear model
    if p > 0:
        X_lags = create_lags(delta_y, p)
        X = np.column_stack([np.ones(len(X_lags)), X_lags])
        y_reg = delta_y[p:]
        
        # OLS estimation
        beta = np.linalg.lstsq(X, y_reg, rcond=None)[0]
        z_t = y_reg - X @ beta
        
        a_sum = np.sum(beta[1:])
        mu_hat = beta[0] / (1 - a_sum)
    else:
        mu_hat = np.mean(delta_y)
        z_t = delta_y - mu_hat
    
    s_squared = np.mean(z_t**2)
    y_lagged = y[p:(n-1)]
    
    # Calculate V1 statistic
    numerator = np.sum(y_lagged * (z_t**2 - s_squared))
    denominator = np.sqrt(s_squared**2 * mu_hat**2 / 6)
    V1 = numerator / (n**(3/2) * denominator)
    
    # P-value under asymptotic normality
    p_value = 2 * (1 - stats.norm.cdf(abs(V1)))
    reject = bool(abs(V1) > stats.norm.ppf(0.975))
    
    return KMTestResult(
        statistic=V1,
        p_value=p_value,
        critical_values=None,
        reject_null=reject,
        null_hypothesis="Linear integrated process (with drift)",
        alternative="Logarithmic integrated process",
        lag_order=p,
        drift_estimate=mu_hat,
        variance_estimate=s_squared,
        test_type="V1"
    )


def km_u1_test(y: np.ndarray, p: Optional[int] = None, max_p: int = 12) -> KMTestResult:
    """
    Kobayashi-McAleer U1 Test
    
    Tests the null hypothesis of a linear integrated process without drift
    against the alternative of a logarithmic integrated process.
    
    Parameters:
        y: Time series array (must be positive)
        p: Number of lags for AR process (default: automatically selected)
        max_p: Maximum number of lags to consider
        
    Returns:
        KMTestResult object containing test statistics and results
        
    Note:
        The U1 test is designed for integrated processes without drift. Unlike V1, 
        this test has a nonstandard asymptotic distribution. Critical values are 
        based on simulations from Kobayashi & McAleer (1999).
    """
    # Input validation
    y = np.asarray(y, dtype=float)
    
    if not np.all(y > 0):
        raise ValueError("y must contain only positive values")
    if len(y) < 10:
        raise ValueError("y must have at least 10 observations")
    
    n = len(y)
    delta_y = np.diff(y)
    
    if p is None:
        p = select_lag_order(delta_y, max_p, criterion='AIC')
    
    # Estimate AR model without constant
    if p > 0:
        X_lags = create_lags(delta_y, p)
        y_reg = delta_y[p:]
        
        # OLS estimation without intercept
        beta = np.linalg.lstsq(X_lags, y_reg, rcond=None)[0]
        z_t = y_reg - X_lags @ beta
        alpha_1 = 1 - np.sum(beta)
    else:
        z_t = delta_y
        alpha_1 = 1.0
    
    s_squared = np.mean(z_t**2)
    y_lagged = y[p:(n-1)]
    
    # Calculate U1 statistic
    numerator = np.sum(y_lagged * (z_t**2 - s_squared))
    denominator = np.sqrt(2 * s_squared**3 / alpha_1)
    U1 = numerator / (n * denominator)
    
    critical_values = get_u1_critical_values()
    reject_dict = {
        '0.10': bool(abs(U1) > critical_values['0.10']),
        '0.05': bool(abs(U1) > critical_values['0.05']),
        '0.01': bool(abs(U1) > critical_values['0.01'])
    }
    
    return KMTestResult(
        statistic=U1,
        p_value=None,
        critical_values=critical_values,
        reject_null=reject_dict,
        null_hypothesis="Linear integrated process (no drift)",
        alternative="Logarithmic integrated process",
        lag_order=p,
        drift_estimate=None,
        variance_estimate=s_squared,
        test_type="U1"
    )


def km_v2_test(y: np.ndarray, p: Optional[int] = None, max_p: int = 12) -> KMTestResult:
    """
    Kobayashi-McAleer V2 Test
    
    Tests the null hypothesis of a logarithmic integrated process with drift
    against the alternative of a linear integrated process.
    
    Parameters:
        y: Time series array (must be positive)
        p: Number of lags (default: automatically selected)
        max_p: Maximum number of lags to consider
        
    Returns:
        KMTestResult object containing test statistics and results
        
    Note:
        The V2 test is designed for logarithmic integrated processes with drift.
        The test statistic is asymptotically N(0,1) under the null hypothesis.
    """
    # Input validation
    y = np.asarray(y, dtype=float)
    
    if not np.all(y > 0):
        raise ValueError("y must contain only positive values")
    if len(y) < 10:
        raise ValueError("y must have at least 10 observations")
    
    log_y = np.log(y)
    n = len(log_y)
    delta_log_y = np.diff(log_y)
    
    if p is None:
        p = select_lag_order(delta_log_y, max_p, criterion='AIC')
    
    # Estimate logarithmic model
    if p > 0:
        X_lags = create_lags(delta_log_y, p)
        X = np.column_stack([np.ones(len(X_lags)), X_lags])
        y_reg = delta_log_y[p:]
        
        # OLS estimation
        beta = np.linalg.lstsq(X, y_reg, rcond=None)[0]
        v_t = y_reg - X @ beta
        
        b_sum = np.sum(beta[1:])
        eta_hat = beta[0] / (1 - b_sum)
    else:
        eta_hat = np.mean(delta_log_y)
        v_t = delta_log_y - eta_hat
    
    w_squared = np.mean(v_t**2)
    n_eff = len(v_t)
    log_y_lagged = log_y[(p+1):(p+1+n_eff)]
    
    # Calculate V2 statistic
    numerator = np.sum((-log_y_lagged) * (v_t**2 - w_squared))
    denominator = np.sqrt(w_squared**2 * eta_hat**2 / 6)
    V2 = numerator / (n**(3/2) * denominator)
    
    p_value = 2 * (1 - stats.norm.cdf(abs(V2)))
    reject = bool(abs(V2) > stats.norm.ppf(0.975))
    
    return KMTestResult(
        statistic=V2,
        p_value=p_value,
        critical_values=None,
        reject_null=reject,
        null_hypothesis="Logarithmic integrated process (with drift)",
        alternative="Linear integrated process",
        lag_order=p,
        drift_estimate=eta_hat,
        variance_estimate=w_squared,
        test_type="V2"
    )


def km_u2_test(y: np.ndarray, p: Optional[int] = None, max_p: int = 12) -> KMTestResult:
    """
    Kobayashi-McAleer U2 Test
    
    Tests the null hypothesis of a logarithmic integrated process without drift
    against the alternative of a linear integrated process.
    
    Parameters:
        y: Time series array (must be positive)
        p: Number of lags (default: automatically selected)
        max_p: Maximum number of lags to consider
        
    Returns:
        KMTestResult object containing test statistics and results
        
    Note:
        The U2 test is for logarithmic processes without drift. Like U1, this test 
        has a nonstandard asymptotic distribution. Critical values from 
        Kobayashi & McAleer (1999).
    """
    # Input validation
    y = np.asarray(y, dtype=float)
    
    if not np.all(y > 0):
        raise ValueError("y must contain only positive values")
    if len(y) < 10:
        raise ValueError("y must have at least 10 observations")
    
    log_y = np.log(y)
    n = len(log_y)
    delta_log_y = np.diff(log_y)
    
    if p is None:
        p = select_lag_order(delta_log_y, max_p, criterion='AIC')
    
    # Estimate AR model without constant
    if p > 0:
        X_lags = create_lags(delta_log_y, p)
        y_reg = delta_log_y[p:]
        
        # OLS estimation without intercept
        beta = np.linalg.lstsq(X_lags, y_reg, rcond=None)[0]
        v_t = y_reg - X_lags @ beta
        beta_1 = 1 - np.sum(beta)
    else:
        v_t = delta_log_y
        beta_1 = 1.0
    
    w_squared = np.mean(v_t**2)
    n_eff = len(v_t)
    log_y_lagged = log_y[(p+1):(p+1+n_eff)]
    
    # Calculate U2 statistic
    numerator = np.sum((-log_y_lagged) * (v_t**2 - w_squared))
    denominator = np.sqrt(2 * w_squared**3 / beta_1)
    U2 = numerator / (n * denominator)
    
    critical_values = get_u2_critical_values()
    reject_dict = {
        '0.10': bool(abs(U2) > critical_values['0.10']),
        '0.05': bool(abs(U2) > critical_values['0.05']),
        '0.01': bool(abs(U2) > critical_values['0.01'])
    }
    
    return KMTestResult(
        statistic=U2,
        p_value=None,
        critical_values=critical_values,
        reject_null=reject_dict,
        null_hypothesis="Logarithmic integrated process (no drift)",
        alternative="Linear integrated process",
        lag_order=p,
        drift_estimate=None,
        variance_estimate=w_squared,
        test_type="U2"
    )
