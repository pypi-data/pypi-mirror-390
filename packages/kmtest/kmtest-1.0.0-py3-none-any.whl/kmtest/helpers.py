"""
Helper functions for Kobayashi-McAleer tests
"""

import numpy as np
from typing import Tuple
from scipy import stats


def create_lags(x: np.ndarray, p: int) -> np.ndarray:
    """
    Create lagged variables matrix.
    
    Parameters:
        x: Time series array
        p: Number of lags
        
    Returns:
        Matrix of lagged variables (n-p rows, p columns)
    """
    n = len(x)
    X = np.zeros((n - p, p))
    
    for i in range(p):
        X[:, i] = x[(p - i - 1):(n - i - 1)]
    
    return X


def select_lag_order(x: np.ndarray, max_p: int, criterion: str = 'AIC') -> int:
    """
    Select optimal lag order using information criteria.
    
    Parameters:
        x: Time series array
        max_p: Maximum lag order to consider
        criterion: Information criterion ('AIC' or 'BIC'/'SIC')
        
    Returns:
        Optimal lag order
    """
    n = len(x)
    ic_values = np.zeros(max_p + 1)
    
    for p in range(max_p + 1):
        if p == 0:
            # No lags, just constant
            mean_x = np.mean(x)
            residuals = x - mean_x
            sigma2 = np.sum(residuals**2) / n
            k = 1
        else:
            # AR(p) model with constant
            X_lags = create_lags(x, p)
            X = np.column_stack([np.ones(len(X_lags)), X_lags])
            y_reg = x[p:]
            
            # OLS estimation
            beta = np.linalg.lstsq(X, y_reg, rcond=None)[0]
            residuals = y_reg - X @ beta
            sigma2 = np.sum(residuals**2) / (n - p)
            k = p + 1
        
        # Calculate information criterion
        if criterion == 'AIC':
            ic_values[p] = np.log(sigma2) + 2 * k / n
        elif criterion in ['BIC', 'SIC']:
            ic_values[p] = np.log(sigma2) + k * np.log(n) / n
        else:
            raise ValueError("criterion must be 'AIC' or 'BIC'/'SIC'")
    
    optimal_p = np.argmin(ic_values)
    return optimal_p


def estimate_ar_model(x: np.ndarray, p: int, include_constant: bool = True) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    """
    Estimate AR(p) model.
    
    Parameters:
        x: Time series array
        p: Lag order
        include_constant: Whether to include intercept
        
    Returns:
        Tuple of (coefficients, residuals, fitted_values)
    """
    if p == 0 and include_constant:
        mean_x = np.mean(x)
        residuals = x - mean_x
        return np.array([mean_x]), residuals, np.full_like(x, mean_x)
    elif p == 0 and not include_constant:
        return np.array([]), x.copy(), np.zeros_like(x)
    
    # Create lagged design matrix
    X_lags = create_lags(x, p)
    
    if include_constant:
        X = np.column_stack([np.ones(len(X_lags)), X_lags])
    else:
        X = X_lags
    
    y_reg = x[p:]
    
    # OLS estimation
    beta = np.linalg.lstsq(X, y_reg, rcond=None)[0]
    fitted = X @ beta
    residuals = y_reg - fitted
    
    return beta, residuals, fitted


def get_u1_critical_values() -> dict:
    """
    Get critical values for U1 test from Kobayashi & McAleer (1999), Table 1.
    Based on simulation with 20,000 iterations.
    
    Returns:
        Dictionary with critical values at 1%, 5%, and 10% significance levels
    """
    return {
        '0.01': 1.116,
        '0.05': 0.664,
        '0.10': 0.477
    }


def get_u2_critical_values() -> dict:
    """
    Get critical values for U2 test from Kobayashi & McAleer (1999), Table 1.
    Due to symmetry, U2 has the same critical values as U1.
    
    Returns:
        Dictionary with critical values at 1%, 5%, and 10% significance levels
    """
    return get_u1_critical_values()


def detect_drift(y: np.ndarray, alpha: float = 0.05) -> bool:
    """
    Simple test for presence of drift in differenced series.
    
    Parameters:
        y: Time series array
        alpha: Significance level
        
    Returns:
        True if drift is detected, False otherwise
    """
    delta_y = np.diff(y)
    n = len(delta_y)
    
    # t-test for non-zero mean
    mean_delta = np.mean(delta_y)
    std_delta = np.std(delta_y, ddof=1)
    t_stat = mean_delta / (std_delta / np.sqrt(n))
    p_value = 2 * (1 - stats.t.cdf(abs(t_stat), n - 1))
    
    return bool(p_value < alpha)
