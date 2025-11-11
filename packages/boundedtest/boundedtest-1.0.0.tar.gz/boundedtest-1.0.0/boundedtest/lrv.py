"""
Long-Run Variance (LRV) Estimation Module

Implements both parametric (AR-based) and non-parametric (kernel-based) 
long-run variance estimators as used in the paper.

References:
-----------
- Newey and West (1994) for non-parametric estimation
- Ng and Perron (2001) for parametric AR-based estimation
"""

import numpy as np
from scipy import stats
from typing import Optional, Tuple


def bartlett_kernel(x: float) -> float:
    """
    Bartlett (triangular) kernel function.
    
    Parameters:
    -----------
    x : float
        Input value
        
    Returns:
    --------
    float : Kernel weight
    """
    abs_x = np.abs(x)
    return np.where(abs_x <= 1, 1 - abs_x, 0)


def quadratic_spectral_kernel(x: float) -> float:
    """
    Quadratic Spectral kernel function.
    
    Parameters:
    -----------
    x : float
        Input value
        
    Returns:
    --------
    float : Kernel weight
    """
    x = np.where(x == 0, 1e-10, x)  # Avoid division by zero
    z = 6 * np.pi * x / 5
    sin_z = np.sin(z)
    cos_z = np.cos(z)
    result = 3 * (sin_z / z - cos_z) / (z ** 2)
    return result


def estimate_lrv_np(
    residuals: np.ndarray,
    kernel: str = 'quadratic_spectral',
    bandwidth: Optional[int] = None
) -> float:
    """
    Non-parametric long-run variance estimation using kernel methods.
    
    Following Newey and West (1994) with automatic bandwidth selection.
    
    Parameters:
    -----------
    residuals : np.ndarray
        Residuals from the regression (T x 1)
    kernel : str, default='quadratic_spectral'
        Kernel function to use ('bartlett' or 'quadratic_spectral')
    bandwidth : int, optional
        Bandwidth parameter. If None, automatically selected.
        
    Returns:
    --------
    float : Long-run variance estimate
    """
    T = len(residuals)
    residuals = residuals.flatten()
    
    # Automatic bandwidth selection (Newey-West)
    if bandwidth is None:
        bandwidth = int(4 * (T / 100) ** (2/25))
    
    # Select kernel function
    if kernel == 'bartlett':
        kernel_func = bartlett_kernel
    elif kernel == 'quadratic_spectral':
        kernel_func = quadratic_spectral_kernel
    else:
        raise ValueError(f"Unknown kernel: {kernel}")
    
    # Compute variance
    s2 = np.sum(residuals ** 2) / T
    
    # Compute autocovariances with kernel weights
    for j in range(1, bandwidth + 1):
        weight = kernel_func(j / bandwidth)
        gamma_j = np.sum(residuals[j:] * residuals[:-j]) / T
        s2 += 2 * weight * gamma_j
    
    return max(s2, 1e-10)  # Ensure positivity


def compute_maic(residuals: np.ndarray, max_lag: int) -> int:
    """
    Compute Modified AIC (MAIC) for lag selection.
    
    Following Ng and Perron (2001) and Perron and Qu (2007).
    
    Parameters:
    -----------
    residuals : np.ndarray
        Residuals from the regression
    max_lag : int
        Maximum lag to consider
        
    Returns:
    --------
    int : Optimal lag length
    """
    T = len(residuals)
    residuals = residuals.flatten()
    
    aic_values = np.zeros(max_lag + 1)
    
    for k in range(max_lag + 1):
        if k == 0:
            # AR(0) model
            sigma2 = np.sum(residuals ** 2) / T
            aic_values[k] = np.log(sigma2)
        else:
            # AR(k) model - need at least k+1 observations
            if T <= k:
                aic_values[k] = np.inf
                continue
                
            # Build lagged design matrix
            X_list = []
            for j in range(1, k+1):
                if j < len(residuals):
                    X_list.append(residuals[k-j:len(residuals)-j])
                else:
                    break
            
            if len(X_list) != k:
                aic_values[k] = np.inf
                continue
            
            X = np.column_stack(X_list)
            y = residuals[k:]
            
            # Ensure dimensions match
            if len(y) != len(X):
                aic_values[k] = np.inf
                continue
            
            if len(y) > k and len(X) > k:
                try:
                    # OLS estimation
                    beta = np.linalg.lstsq(X, y, rcond=None)[0]
                    fitted = X @ beta
                    resid = y - fitted
                    sigma2 = np.sum(resid ** 2) / len(resid)
                    
                    # MAIC criterion
                    tau = np.sum(beta ** 2 * np.sum(X ** 2, axis=0)) / sigma2
                    aic_values[k] = np.log(sigma2) + 2 * (tau + k) / T
                except np.linalg.LinAlgError:
                    aic_values[k] = np.inf
            else:
                aic_values[k] = np.inf
    
    return int(np.argmin(aic_values))


def estimate_lrv_ar(
    residuals: np.ndarray,
    max_lag: Optional[int] = None,
    method: str = 'maic'
) -> Tuple[float, int]:
    """
    Parametric long-run variance estimation using AR model.
    
    Following Ng and Perron (2001) approach.
    
    Parameters:
    -----------
    residuals : np.ndarray
        Residuals from the regression (T x 1)
    max_lag : int, optional
        Maximum lag for AR model. If None, automatically determined.
    method : str, default='maic'
        Lag selection method ('maic', 'aic', 'bic')
        
    Returns:
    --------
    Tuple[float, int] : (Long-run variance estimate, selected lag)
    """
    T = len(residuals)
    residuals = residuals.flatten()
    
    # Set maximum lag if not provided
    if max_lag is None:
        max_lag = int(12 * (T / 100) ** (1/4))
    
    # Select optimal lag using MAIC
    if method == 'maic':
        k_opt = compute_maic(residuals, max_lag)
    else:
        raise ValueError(f"Unknown method: {method}")
    
    # Estimate AR(k) model
    if k_opt == 0:
        # No autoregressive terms
        sigma2 = np.sum(residuals ** 2) / T
        ar_sum = 0
    else:
        # Build lagged matrix - ensure correct dimensions
        X_list = []
        for j in range(1, k_opt+1):
            if j < len(residuals):
                X_list.append(residuals[k_opt-j:len(residuals)-j])
            else:
                break
        
        if len(X_list) != k_opt:
            # Fall back to AR(0)
            sigma2 = np.sum(residuals ** 2) / T
            ar_sum = 0
        else:
            X = np.column_stack(X_list)
            y = residuals[k_opt:]
            
            # Ensure dimensions match
            if len(y) != len(X):
                sigma2 = np.sum(residuals ** 2) / T
                ar_sum = 0
            else:
                try:
                    # OLS estimation
                    beta = np.linalg.lstsq(X, y, rcond=None)[0]
                    fitted = X @ beta
                    resid = y - fitted
                    sigma2 = np.sum(resid ** 2) / len(resid)
                    
                    # Compute sum of AR coefficients
                    ar_sum = np.sum(beta)
                except np.linalg.LinAlgError:
                    # Fall back to AR(0)
                    sigma2 = np.sum(residuals ** 2) / T
                    ar_sum = 0
    
    # Long-run variance formula: σ² / (1 - Σρᵢ)²
    denominator = (1 - ar_sum) ** 2
    s2_ar = sigma2 / max(denominator, 0.01)  # Prevent division by near-zero
    
    return max(s2_ar, 1e-10), k_opt


def estimate_lrv(
    residuals: np.ndarray,
    method: str = 'np',
    **kwargs
) -> float:
    """
    Unified interface for LRV estimation.
    
    Parameters:
    -----------
    residuals : np.ndarray
        Residuals from the regression
    method : str, default='np'
        Estimation method ('np' for non-parametric, 'ar' for parametric)
    **kwargs : dict
        Additional arguments passed to specific estimation functions
        
    Returns:
    --------
    float : Long-run variance estimate
    """
    if method == 'np':
        return estimate_lrv_np(residuals, **kwargs)
    elif method == 'ar':
        s2, _ = estimate_lrv_ar(residuals, **kwargs)
        return s2
    else:
        raise ValueError(f"Unknown method: {method}. Use 'np' or 'ar'.")
