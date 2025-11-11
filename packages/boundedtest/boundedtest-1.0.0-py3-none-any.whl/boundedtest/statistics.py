"""
Test Statistics Module

Implements the M-type unit root test statistics (MZα, MSB, MZt)
for bounded processes as described in Ng and Perron (2001) and
adapted by Carrion-i-Silvestre and Gadea (2013).
"""

import numpy as np
from typing import Tuple


def compute_mz_alpha(
    y_tilde: np.ndarray,
    s2: float
) -> float:
    """
    Compute MZα test statistic.
    
    MZα = (T⁻¹ŷ²ₜ - T⁻¹ŷ²₀ - s²) / (2T⁻² Σŷ²ₜ₋₁)
    
    Parameters:
    -----------
    y_tilde : np.ndarray
        Detrended series (T x 1)
    s2 : float
        Long-run variance estimate
        
    Returns:
    --------
    float : MZα statistic
    """
    T = len(y_tilde)
    y_tilde = y_tilde.flatten()
    
    # Components
    y_T_sq = y_tilde[-1] ** 2
    y_0_sq = y_tilde[0] ** 2
    sum_y_sq = np.sum(y_tilde[:-1] ** 2)  # Sum of y²_{t-1}
    
    # MZα statistic
    numerator = (y_T_sq / T) - (y_0_sq / T) - s2
    denominator = 2 * sum_y_sq / (T ** 2)
    
    if abs(denominator) < 1e-10:
        return np.nan
    
    MZ_alpha = numerator / denominator
    
    return MZ_alpha


def compute_msb(
    y_tilde: np.ndarray,
    s2: float
) -> float:
    """
    Compute MSB test statistic.
    
    MSB = √(T⁻² Σŷ²ₜ₋₁ / s²)
    
    Parameters:
    -----------
    y_tilde : np.ndarray
        Detrended series (T x 1)
    s2 : float
        Long-run variance estimate
        
    Returns:
    --------
    float : MSB statistic
    """
    T = len(y_tilde)
    y_tilde = y_tilde.flatten()
    
    # Sum of squared lagged values
    sum_y_sq = np.sum(y_tilde[:-1] ** 2)
    
    if s2 <= 0:
        return np.nan
    
    # MSB statistic
    MSB = np.sqrt((sum_y_sq / (T ** 2)) / s2)
    
    return MSB


def compute_mz_t(
    y_tilde: np.ndarray,
    s2: float
) -> float:
    """
    Compute MZt test statistic.
    
    MZt = MZα * MSB
    
    Parameters:
    -----------
    y_tilde : np.ndarray
        Detrended series (T x 1)
    s2 : float
        Long-run variance estimate
        
    Returns:
    --------
    float : MZt statistic
    """
    MZ_alpha = compute_mz_alpha(y_tilde, s2)
    MSB = compute_msb(y_tilde, s2)
    
    if np.isnan(MZ_alpha) or np.isnan(MSB):
        return np.nan
    
    MZ_t = MZ_alpha * MSB
    
    return MZ_t


def compute_all_statistics(
    y_tilde: np.ndarray,
    s2: float
) -> Tuple[float, float, float]:
    """
    Compute all M-type test statistics at once.
    
    Parameters:
    -----------
    y_tilde : np.ndarray
        Detrended series (T x 1)
    s2 : float
        Long-run variance estimate
        
    Returns:
    --------
    Tuple[float, float, float] : (MZα, MSB, MZt)
    """
    MZ_alpha = compute_mz_alpha(y_tilde, s2)
    MSB = compute_msb(y_tilde, s2)
    MZ_t = compute_mz_t(y_tilde, s2)
    
    return MZ_alpha, MSB, MZ_t


def compute_ar1_residuals(
    y_tilde: np.ndarray
) -> np.ndarray:
    """
    Compute residuals from AR(1) regression for LRV estimation.
    
    Regresses ŷₜ on ŷₜ₋₁ and returns the residuals.
    
    Parameters:
    -----------
    y_tilde : np.ndarray
        Detrended series (T x 1)
        
    Returns:
    --------
    np.ndarray : AR(1) residuals
    """
    y_tilde = y_tilde.flatten()
    
    # Lagged values
    y_lag = y_tilde[:-1].reshape(-1, 1)
    y_current = y_tilde[1:].reshape(-1, 1)
    
    if len(y_lag) == 0:
        return y_tilde
    
    # OLS estimation
    if np.sum(y_lag ** 2) > 0:
        rho = np.sum(y_lag * y_current) / np.sum(y_lag ** 2)
        residuals = y_current.flatten() - rho * y_lag.flatten()
    else:
        residuals = y_current.flatten()
    
    return residuals


def compute_pt_statistic(
    x: np.ndarray,
    alpha_bar: float,
    s2: float
) -> float:
    """
    Compute PT (Point Optimal) test statistic.
    
    PT = [S(α̅) - α̅S(1)] / s²
    
    where S(α) is the sum of squared GLS residuals.
    
    Parameters:
    -----------
    x : np.ndarray
        Original series (T x 1)
    alpha_bar : float
        GLS quasi-differencing parameter
    s2 : float
        Long-run variance estimate
        
    Returns:
    --------
    float : PT statistic
    """
    from .detrending import quasi_difference
    
    T = len(x)
    x = x.flatten()
    
    # Quasi-difference with α̅
    x_alpha = quasi_difference(x, alpha_bar)
    z_alpha = quasi_difference(np.ones(T), alpha_bar)
    
    # GLS estimation
    mu_gls = np.sum(x_alpha * z_alpha) / np.sum(z_alpha ** 2)
    S_alpha = np.sum((x_alpha - mu_gls * z_alpha) ** 2)
    
    # No differencing (α = 1)
    x_1 = x - x[0]  # Remove first observation effect
    mu_ols = np.mean(x_1)
    S_1 = np.sum((x_1 - mu_ols) ** 2)
    
    # PT statistic
    if s2 <= 0:
        return np.nan
    
    PT = (S_alpha - alpha_bar * S_1) / s2
    
    return PT
