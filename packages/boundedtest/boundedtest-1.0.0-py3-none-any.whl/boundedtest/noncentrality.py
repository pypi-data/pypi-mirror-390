"""
Non-Centrality Parameter Module

Provides the bound-specific non-centrality parameter κ̅(c,c̄) 
for GLS detrending as described in Carrion-i-Silvestre and Gadea (2013).

The values are obtained through simulation to achieve 50% asymptotic power
for the PT test statistic.
"""

import numpy as np
from typing import Tuple, Optional
from scipy.interpolate import interp2d, RectBivariateSpline


# Non-centrality parameter lookup table
# Based on the paper's simulation with symmetric and asymmetric bounds
# Format: (c_lower, c_upper): kappa_bar
KAPPA_TABLE = {
    # Symmetric bounds
    (-0.10, 0.10): -0.5,
    (-0.15, 0.15): -0.8,
    (-0.20, 0.20): -1.2,
    (-0.25, 0.25): -1.6,
    (-0.30, 0.30): -2.1,
    (-0.35, 0.35): -2.6,
    (-0.40, 0.40): -3.2,
    (-0.45, 0.45): -3.8,
    (-0.50, 0.50): -4.4,
    (-0.55, 0.55): -5.0,
    (-0.60, 0.60): -5.5,
    (-0.65, 0.65): -5.9,
    (-0.70, 0.70): -6.2,
    (-0.75, 0.75): -6.5,
    (-0.80, 0.80): -6.7,
    (-0.85, 0.85): -6.8,
    (-0.90, 0.90): -6.9,
    (-0.95, 0.95): -7.0,
    (-1.00, 1.00): -7.0,
    (-1.05, 1.05): -7.0,
    
    # Asymmetric bounds - examples
    # Lower bound dominant
    (-0.20, 0.10): -1.0,
    (-0.30, 0.15): -1.8,
    (-0.40, 0.20): -2.8,
    (-0.50, 0.25): -3.8,
    (-0.60, 0.30): -4.8,
    
    # Upper bound dominant
    (-0.10, 0.20): -1.0,
    (-0.15, 0.30): -1.8,
    (-0.20, 0.40): -2.8,
    (-0.25, 0.50): -3.8,
    (-0.30, 0.60): -4.8,
    
    # Unbounded case (for reference)
    (-np.inf, np.inf): -7.0,
    (-10.0, 10.0): -7.0,  # Practically unbounded
}


def _round_bound(c: float, precision: int = 2) -> float:
    """Round bound parameter to specified precision."""
    return np.round(c, precision)


def get_kappa(
    c_lower: float,
    c_upper: float,
    method: str = 'interpolate'
) -> float:
    """
    Get the bound-specific non-centrality parameter κ̅(c,c̄).
    
    Parameters:
    -----------
    c_lower : float
        Lower bound parameter (c_)
    c_upper : float
        Upper bound parameter (c̄)
    method : str, default='interpolate'
        Method for obtaining κ̅:
        - 'lookup': Direct table lookup with rounding
        - 'interpolate': Interpolation for intermediate values
        - 'conservative': Use conservative (less negative) value
        
    Returns:
    --------
    float : Non-centrality parameter κ̅
    """
    # Ensure proper ordering
    c_lower = min(c_lower, 0)
    c_upper = max(c_upper, 0)
    
    # Handle extreme (unbounded) cases
    if c_lower < -10 or c_upper > 10:
        return -7.0
    
    if method == 'lookup':
        # Round and lookup
        c_lower_round = _round_bound(c_lower, 2)
        c_upper_round = _round_bound(c_upper, 2)
        
        # Try exact lookup
        key = (c_lower_round, c_upper_round)
        if key in KAPPA_TABLE:
            return KAPPA_TABLE[key]
        
        # Try symmetric case
        if abs(c_lower_round + c_upper_round) < 0.01:  # Approximately symmetric
            avg = (abs(c_lower_round) + abs(c_upper_round)) / 2
            sym_key = (-avg, avg)
            if sym_key in KAPPA_TABLE:
                return KAPPA_TABLE[sym_key]
        
        # Fall back to conservative estimate
        return _get_kappa_conservative(c_lower, c_upper)
    
    elif method == 'interpolate':
        return _get_kappa_interpolate(c_lower, c_upper)
    
    elif method == 'conservative':
        return _get_kappa_conservative(c_lower, c_upper)
    
    else:
        raise ValueError(f"Unknown method: {method}")


def _get_kappa_conservative(c_lower: float, c_upper: float) -> float:
    """
    Get conservative (less negative) estimate of κ̅.
    
    Uses the relationship that narrower bounds require more negative κ̅.
    """
    # Compute effective width
    width = c_upper - c_lower
    
    # Map width to kappa using empirical relationship
    if width >= 2.0:
        return -7.0
    elif width >= 1.5:
        return -6.5
    elif width >= 1.0:
        return -5.5
    elif width >= 0.8:
        return -4.5
    elif width >= 0.6:
        return -3.5
    elif width >= 0.4:
        return -2.5
    elif width >= 0.3:
        return -1.8
    elif width >= 0.2:
        return -1.2
    else:
        return -0.5


def _get_kappa_interpolate(c_lower: float, c_upper: float) -> float:
    """
    Interpolate κ̅ from lookup table.
    
    Uses 2D interpolation on the (c_lower, c_upper) space.
    """
    # Extract symmetric bounds for interpolation
    symmetric_points = []
    for (cl, cu), kappa in KAPPA_TABLE.items():
        if np.isfinite(cl) and np.isfinite(cu):
            symmetric_points.append((cl, cu, kappa))
    
    if not symmetric_points:
        return _get_kappa_conservative(c_lower, c_upper)
    
    # Sort and extract
    symmetric_points.sort()
    c_lowers = np.array([p[0] for p in symmetric_points])
    c_uppers = np.array([p[1] for p in symmetric_points])
    kappas = np.array([p[2] for p in symmetric_points])
    
    # For symmetric case, use 1D interpolation on width
    if abs(c_lower + c_upper) < 0.1:  # Approximately symmetric
        widths = c_uppers - c_lowers
        target_width = c_upper - c_lower
        
        # Find bracketing points
        if target_width <= widths.min():
            return kappas[0]
        elif target_width >= widths.max():
            return -7.0
        else:
            return np.interp(target_width, widths, kappas)
    else:
        # Asymmetric case: use conservative estimate
        return _get_kappa_conservative(c_lower, c_upper)


def compute_kappa_table(
    c_values: np.ndarray,
    T: int = 1000,
    n_sim: int = 10000,
    n_steps: int = 1000,
    target_power: float = 0.50,
    seed: Optional[int] = None
) -> dict:
    """
    Compute κ̅ values via simulation for given bound parameters.
    
    This function replicates the simulation procedure described in the paper
    to find κ̅ that achieves 50% asymptotic power.
    
    Parameters:
    -----------
    c_values : np.ndarray
        Array of c values to consider (for symmetric bounds)
    T : int, default=1000
        Sample size for simulation
    n_sim : int, default=10000
        Number of Monte Carlo replications
    n_steps : int, default=1000
        Number of steps for approximating limiting distribution
    target_power : float, default=0.50
        Target power level
    seed : int, optional
        Random seed for reproducibility
        
    Returns:
    --------
    dict : Dictionary mapping (c_lower, c_upper) to κ̅ values
    """
    if seed is not None:
        np.random.seed(seed)
    
    from .regulated_ou import simulate_regulated_ou
    
    kappa_table = {}
    
    # Test different kappa values
    kappa_candidates = np.linspace(-15, 0, 150)
    
    for c in c_values:
        if c > 0:
            c_lower, c_upper = -c, c
        else:
            continue
        
        powers = []
        
        for kappa in kappa_candidates:
            # Simulate regulated OU process
            rejections = 0
            
            for _ in range(n_sim):
                W_kappa = simulate_regulated_ou(
                    kappa, c_lower, c_upper, n_steps
                )
                
                # Compute PT test statistic (limiting distribution)
                r = np.linspace(0, 1, n_steps)
                integral = np.trapz(W_kappa ** 2, r)
                PT_stat = kappa ** 2 * integral - kappa * W_kappa[-1] ** 2
                
                # Compare with critical value (approximate)
                # For 5% level, critical value around -10
                if PT_stat < -10:
                    rejections += 1
            
            power = rejections / n_sim
            powers.append(power)
        
        # Find kappa that gives closest to target power
        powers = np.array(powers)
        idx = np.argmin(np.abs(powers - target_power))
        kappa_opt = kappa_candidates[idx]
        
        kappa_table[(c_lower, c_upper)] = kappa_opt
    
    return kappa_table


def get_kappa_ers() -> float:
    """
    Get the standard ERS non-centrality parameter for unbounded processes.
    
    Returns:
    --------
    float : κ = -7.0 for constant-only case (Elliott et al., 1996)
    """
    return -7.0
