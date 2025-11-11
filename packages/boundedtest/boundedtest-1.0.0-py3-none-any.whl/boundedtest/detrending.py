"""
Detrending Module for Bounded Unit Root Tests

Implements OLS and GLS detrending procedures with bound-specific 
non-centrality parameter estimation.

References:
-----------
- Elliott, Rothenberg, and Stock (1996) for GLS detrending
- Carrion-i-Silvestre and Gadea (2013) for bound-specific modifications
"""

import numpy as np
from typing import Tuple, Optional
from .noncentrality import get_kappa


def ols_detrend(
    x: np.ndarray,
    deterministics: str = 'constant'
) -> Tuple[np.ndarray, np.ndarray, float]:
    """
    OLS detrending of the time series.
    
    Parameters:
    -----------
    x : np.ndarray
        Time series data (T x 1)
    deterministics : str, default='constant'
        Type of deterministic components ('constant', 'trend', or 'both')
        
    Returns:
    --------
    Tuple containing:
        - y_tilde : np.ndarray - Detrended series
        - z : np.ndarray - Design matrix of deterministics
        - mu_hat : float or np.ndarray - Estimated deterministic parameters
    """
    T = len(x)
    x = x.flatten()
    
    # Build design matrix
    if deterministics == 'constant':
        z = np.ones((T, 1))
    elif deterministics == 'trend':
        z = np.arange(1, T+1).reshape(-1, 1)
    elif deterministics == 'both':
        z = np.column_stack([np.ones(T), np.arange(1, T+1)])
    else:
        raise ValueError(f"Unknown deterministics: {deterministics}")
    
    # OLS estimation
    mu_hat = np.linalg.lstsq(z, x, rcond=None)[0]
    y_tilde = x - z @ mu_hat
    
    return y_tilde, z, mu_hat


def quasi_difference(
    x: np.ndarray,
    alpha_bar: float
) -> np.ndarray:
    """
    Compute quasi-differenced series: x_t - α̅ * x_{t-1}.
    
    Parameters:
    -----------
    x : np.ndarray
        Time series data (T x 1)
    alpha_bar : float
        Quasi-differencing parameter
        
    Returns:
    --------
    np.ndarray : Quasi-differenced series
    """
    x = x.flatten()
    T = len(x)
    x_alpha = np.zeros(T)
    
    # First observation: x₁
    x_alpha[0] = x[0]
    
    # Remaining observations: (1 - α̅L)xₜ = xₜ - α̅xₜ₋₁
    x_alpha[1:] = x[1:] - alpha_bar * x[:-1]
    
    return x_alpha


def gls_detrend(
    x: np.ndarray,
    c_lower: float,
    c_upper: float,
    deterministics: str = 'constant',
    kappa: Optional[float] = None
) -> Tuple[np.ndarray, float, float]:
    """
    GLS detrending with bound-specific non-centrality parameter.
    
    Implements the quasi-GLS detrending procedure described in the paper.
    
    Parameters:
    -----------
    x : np.ndarray
        Time series data (T x 1)
    c_lower : float
        Lower bound parameter (c_)
    c_upper : float
        Upper bound parameter (c̄)
    deterministics : str, default='constant'
        Type of deterministic components
    kappa : float, optional
        Non-centrality parameter. If None, determined from bounds.
        
    Returns:
    --------
    Tuple containing:
        - y_tilde : np.ndarray - GLS-detrended series
        - alpha_bar : float - Quasi-differencing parameter used
        - kappa : float - Non-centrality parameter used
    """
    T = len(x)
    x = x.flatten()
    
    # Get non-centrality parameter if not provided
    if kappa is None:
        kappa = get_kappa(c_lower, c_upper)
    
    # Compute α̅ = 1 + κ̅/T
    alpha_bar = 1 + kappa / T
    
    # Quasi-difference the data
    x_alpha = quasi_difference(x, alpha_bar)
    
    # Build quasi-differenced design matrix
    if deterministics == 'constant':
        z = np.ones(T)
        z_alpha = quasi_difference(z, alpha_bar)
    elif deterministics == 'trend':
        z = np.arange(1, T+1)
        z_alpha = quasi_difference(z, alpha_bar)
    elif deterministics == 'both':
        z_const = np.ones(T)
        z_trend = np.arange(1, T+1)
        z_alpha = np.column_stack([
            quasi_difference(z_const, alpha_bar),
            quasi_difference(z_trend, alpha_bar)
        ])
    else:
        raise ValueError(f"Unknown deterministics: {deterministics}")
    
    # GLS estimation
    if z_alpha.ndim == 1:
        z_alpha = z_alpha.reshape(-1, 1)
    
    mu_gls = np.linalg.lstsq(z_alpha, x_alpha, rcond=None)[0]
    
    # Reconstruct deterministics
    if deterministics == 'constant':
        z_full = np.ones(T).reshape(-1, 1)
    elif deterministics == 'trend':
        z_full = np.arange(1, T+1).reshape(-1, 1)
    elif deterministics == 'both':
        z_full = np.column_stack([np.ones(T), np.arange(1, T+1)])
    
    # GLS-detrended series
    y_tilde = x - z_full @ mu_gls
    
    return y_tilde, alpha_bar, kappa


def estimate_bounds(
    x: np.ndarray,
    b_lower: float,
    b_upper: float,
    s: float,
    method: str = 'initial'
) -> Tuple[float, float]:
    """
    Estimate bound parameters c and c̄.
    
    Following the paper's specification:
    c_ = s⁻¹ T⁻¹/² (b - ŷ₁)
    c̄ = s⁻¹ T⁻¹/² (b̄ - ŷ₁)
    
    Parameters:
    -----------
    x : np.ndarray
        Time series data
    b_lower : float
        Lower bound on the series
    b_upper : float
        Upper bound on the series
    s : float
        Estimate of long-run standard deviation
    method : str, default='initial'
        Method for obtaining ŷ₁ ('initial' uses first observation,
        'detrended' uses detrended first observation)
        
    Returns:
    --------
    Tuple[float, float] : (c_lower, c_upper)
    """
    T = len(x)
    
    if method == 'initial':
        y1_hat = x[0]
    elif method == 'detrended':
        y_tilde, _, _ = ols_detrend(x)
        y1_hat = y_tilde[0]
    else:
        raise ValueError(f"Unknown method: {method}")
    
    # Compute c parameters
    c_lower = (b_lower - y1_hat) / (s * np.sqrt(T))
    c_upper = (b_upper - y1_hat) / (s * np.sqrt(T))
    
    # Ensure c_lower ≤ 0 ≤ c_upper
    c_lower = min(c_lower, 0)
    c_upper = max(c_upper, 0)
    
    return c_lower, c_upper


def iterative_gls_detrend(
    x: np.ndarray,
    b_lower: float,
    b_upper: float,
    lrv_method: str = 'np',
    deterministics: str = 'constant',
    max_iter: int = 2
) -> Tuple[np.ndarray, float, float, float, float]:
    """
    Iterative GLS detrending procedure.
    
    Implements the iterative estimation described in Section 3 of the paper:
    1. Initial σ² estimation using OLS-detrending
    2. Compute (c,c̄) and κ̅
    3. Perform GLS-detrending
    4. Re-estimate σ² and update (c,c̄) and κ̅
    5. Final GLS-detrending
    
    Parameters:
    -----------
    x : np.ndarray
        Time series data
    b_lower : float
        Lower bound
    b_upper : float
        Upper bound
    lrv_method : str, default='np'
        LRV estimation method
    deterministics : str, default='constant'
        Type of deterministic components
    max_iter : int, default=2
        Maximum iterations (paper uses 2)
        
    Returns:
    --------
    Tuple containing:
        - y_tilde : np.ndarray - Final GLS-detrended series
        - c_lower : float - Final lower bound parameter
        - c_upper : float - Final upper bound parameter
        - kappa : float - Final non-centrality parameter
        - s2 : float - Final LRV estimate
    """
    from .lrv import estimate_lrv
    
    T = len(x)
    x = x.flatten()
    
    # Step 1: Initial OLS-detrending and σ² estimation
    y_ols, _, _ = ols_detrend(x, deterministics)
    
    # Estimate AR(1) for residual calculation
    y_lag = y_ols[:-1]
    y_diff = y_ols[1:]
    
    if len(y_lag) > 0:
        rho_hat = np.sum(y_lag * y_diff) / np.sum(y_lag ** 2) if np.sum(y_lag ** 2) > 0 else 0
        residuals_ols = y_diff - rho_hat * y_lag
    else:
        residuals_ols = y_ols
    
    s2_ols = estimate_lrv(residuals_ols, method=lrv_method)
    s_ols = np.sqrt(s2_ols)
    
    # Step 2: Compute initial (c,c̄)
    c_lower, c_upper = estimate_bounds(y_ols, b_lower, b_upper, s_ols, method='initial')
    
    # Step 3: First GLS-detrending
    y_gls, alpha_bar, kappa = gls_detrend(x, c_lower, c_upper, deterministics)
    
    # Iterative refinement
    for iteration in range(max_iter - 1):
        # Re-estimate residuals
        y_lag = y_gls[:-1]
        y_diff = y_gls[1:]
        
        if len(y_lag) > 0:
            rho_hat = np.sum(y_lag * y_diff) / np.sum(y_lag ** 2) if np.sum(y_lag ** 2) > 0 else 0
            residuals_gls = y_diff - rho_hat * y_lag
        else:
            residuals_gls = y_gls
        
        # Update σ² estimate
        s2_gls = estimate_lrv(residuals_gls, method=lrv_method)
        s_gls = np.sqrt(s2_gls)
        
        # Update (c,c̄)
        c_lower, c_upper = estimate_bounds(y_gls, b_lower, b_upper, s_gls, method='initial')
        
        # Re-do GLS-detrending with updated parameters
        y_gls, alpha_bar, kappa = gls_detrend(x, c_lower, c_upper, deterministics)
    
    # Final LRV estimate
    y_lag = y_gls[:-1]
    y_diff = y_gls[1:]
    if len(y_lag) > 0:
        rho_hat = np.sum(y_lag * y_diff) / np.sum(y_lag ** 2) if np.sum(y_lag ** 2) > 0 else 0
        residuals_final = y_diff - rho_hat * y_lag
    else:
        residuals_final = y_gls
    
    s2_final = estimate_lrv(residuals_final, method=lrv_method)
    
    return y_gls, c_lower, c_upper, kappa, s2_final
