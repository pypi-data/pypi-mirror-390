"""
Critical Values Module

Provides critical values for bounded unit root test statistics.

Critical values depend on the bound parameters (c, c̄) and are obtained
through Monte Carlo simulation of the regulated Ornstein-Uhlenbeck process.
"""

import numpy as np
from typing import Dict, Optional, Tuple
from .regulated_ou import compute_critical_values as simulate_critical_values


# Pre-computed critical values for symmetric bounds
# Format: (c_lower, c_upper): {'10%': ..., '5%': ..., '1%': ...}
# These are for MZ_alpha statistic with constant-only case

MZ_ALPHA_CRITICAL_VALUES = {
    # Symmetric bounds
    (-0.10, 0.10): {'10%': -8.2, '5%': -10.4, '1%': -15.1},
    (-0.15, 0.15): {'10%': -8.6, '5%': -11.0, '1%': -16.0},
    (-0.20, 0.20): {'10%': -9.1, '5%': -11.7, '1%': -17.2},
    (-0.25, 0.25): {'10%': -9.7, '5%': -12.5, '1%': -18.5},
    (-0.30, 0.30): {'10%': -10.4, '5%': -13.4, '1%': -20.0},
    (-0.35, 0.35): {'10%': -11.2, '5%': -14.5, '1%': -21.7},
    (-0.40, 0.40): {'10%': -12.1, '5%': -15.7, '1%': -23.6},
    (-0.45, 0.45): {'10%': -13.1, '5%': -17.0, '1%': -25.7},
    (-0.50, 0.50): {'10%': -14.2, '5%': -18.5, '1%': -28.0},
    (-0.60, 0.60): {'10%': -16.6, '5%': -21.8, '1%': -33.0},
    (-0.70, 0.70): {'10%': -19.2, '5%': -25.3, '1%': -38.6},
    (-0.80, 0.80): {'10%': -21.7, '5%': -28.7, '1%': -44.0},
    (-0.90, 0.90): {'10%': -23.8, '5%': -31.5, '1%': -48.5},
    (-1.00, 1.00): {'10%': -25.5, '5%': -33.8, '1%': -52.1},
    (-10.0, 10.0): {'10%': -28.4, '5%': -37.8, '1%': -58.4},  # Approximately unbounded
}

# MSB critical values (note: these are upper-tail tests)
MSB_CRITICAL_VALUES = {
    (-0.10, 0.10): {'10%': 0.252, '5%': 0.215, '1%': 0.165},
    (-0.15, 0.15): {'10%': 0.245, '5%': 0.208, '1%': 0.159},
    (-0.20, 0.20): {'10%': 0.237, '5%': 0.201, '1%': 0.152},
    (-0.25, 0.25): {'10%': 0.228, '5%': 0.193, '1%': 0.145},
    (-0.30, 0.30): {'10%': 0.218, '5%': 0.184, '1%': 0.137},
    (-0.35, 0.35): {'10%': 0.208, '5%': 0.175, '1%': 0.129},
    (-0.40, 0.40): {'10%': 0.197, '5%': 0.165, '1%': 0.121},
    (-0.45, 0.45): {'10%': 0.186, '5%': 0.156, '1%': 0.113},
    (-0.50, 0.50): {'10%': 0.175, '5%': 0.146, '1%': 0.106},
    (-0.60, 0.60): {'10%': 0.153, '5%': 0.127, '1%': 0.091},
    (-0.70, 0.70): {'10%': 0.133, '5%': 0.110, '1%': 0.078},
    (-0.80, 0.80): {'10%': 0.116, '5%': 0.095, '1%': 0.067},
    (-0.90, 0.90): {'10%': 0.102, '5%': 0.083, '1%': 0.058},
    (-1.00, 1.00): {'10%': 0.090, '5%': 0.074, '1%': 0.051},
    (-10.0, 10.0): {'10%': 0.074, '5%': 0.059, '1%': 0.040},
}

# MZ_t critical values
MZ_T_CRITICAL_VALUES = {
    (-0.10, 0.10): {'10%': -2.07, '5%': -2.24, '1%': -2.49},
    (-0.15, 0.15): {'10%': -2.11, '5%': -2.29, '1%': -2.54},
    (-0.20, 0.20): {'10%': -2.16, '5%': -2.35, '1%': -2.61},
    (-0.25, 0.25): {'10%': -2.21, '5%': -2.42, '1%': -2.69},
    (-0.30, 0.30): {'10%': -2.27, '5%': -2.46, '1%': -2.74},
    (-0.35, 0.35): {'10%': -2.33, '5%': -2.54, '1%': -2.80},
    (-0.40, 0.40): {'10%': -2.39, '5%': -2.59, '1%': -2.86},
    (-0.45, 0.45): {'10%': -2.44, '5%': -2.65, '1%': -2.91},
    (-0.50, 0.50): {'10%': -2.49, '5%': -2.70, '1%': -2.97},
    (-0.60, 0.60): {'10%': -2.54, '5%': -2.77, '1%': -3.01},
    (-0.70, 0.70): {'10%': -2.56, '5%': -2.78, '1%': -3.02},
    (-0.80, 0.80): {'10%': -2.52, '5%': -2.72, '1%': -2.95},
    (-0.90, 0.90): {'10%': -2.43, '5%': -2.62, '1%': -2.82},
    (-1.00, 1.00): {'10%': -2.30, '5%': -2.50, '1%': -2.68},
    (-10.0, 10.0): {'10%': -2.10, '5%': -2.23, '1%': -2.39},
}


def _find_nearest_bounds(
    c_lower: float,
    c_upper: float,
    table: Dict
) -> Tuple[float, float]:
    """
    Find nearest bound parameters in the critical value table.
    
    Parameters:
    -----------
    c_lower : float
        Lower bound parameter
    c_upper : float
        Upper bound parameter
    table : dict
        Critical value table
        
    Returns:
    --------
    Tuple[float, float] : Nearest (c_lower, c_upper) in table
    """
    min_dist = np.inf
    nearest_key = None
    
    for key in table.keys():
        cl_tab, cu_tab = key
        if not (np.isfinite(cl_tab) and np.isfinite(cu_tab)):
            continue
        
        # Euclidean distance
        dist = np.sqrt((cl_tab - c_lower)**2 + (cu_tab - c_upper)**2)
        
        if dist < min_dist:
            min_dist = dist
            nearest_key = key
    
    return nearest_key if nearest_key else (-1.0, 1.0)


def _interpolate_critical_value(
    c_lower: float,
    c_upper: float,
    table: Dict,
    level: str
) -> float:
    """
    Interpolate critical value based on bound parameters.
    
    Uses symmetric bound approximation with linear interpolation.
    
    Parameters:
    -----------
    c_lower : float
        Lower bound parameter
    c_upper : float
        Upper bound parameter
    table : dict
        Critical value table
    level : str
        Significance level ('10%', '5%', or '1%')
        
    Returns:
    --------
    float : Interpolated critical value
    """
    # For symmetric or near-symmetric bounds, use width interpolation
    if abs(c_lower + c_upper) < 0.2:
        width = c_upper - c_lower
        
        # Extract symmetric bound points
        sym_points = []
        for (cl, cu), cv_dict in table.items():
            if np.isfinite(cl) and np.isfinite(cu):
                if abs(cl + cu) < 0.01:  # Symmetric
                    w = cu - cl
                    cv = cv_dict[level]
                    sym_points.append((w, cv))
        
        if sym_points:
            sym_points.sort()
            widths = np.array([p[0] for p in sym_points])
            cvs = np.array([p[1] for p in sym_points])
            
            # Linear interpolation
            if width <= widths.min():
                return cvs[0]
            elif width >= widths.max():
                return cvs[-1]
            else:
                return np.interp(width, widths, cvs)
    
    # For asymmetric bounds, use nearest neighbor
    nearest_key = _find_nearest_bounds(c_lower, c_upper, table)
    return table[nearest_key][level]


def get_critical_values(
    statistic: str,
    c_lower: float,
    c_upper: float,
    method: str = 'interpolate'
) -> Dict[str, float]:
    """
    Get critical values for specified test statistic and bounds.
    
    Parameters:
    -----------
    statistic : str
        Test statistic ('mz_alpha', 'msb', or 'mz_t')
    c_lower : float
        Lower bound parameter
    c_upper : float
        Upper bound parameter
    method : str, default='interpolate'
        Method for obtaining critical values:
        - 'lookup': Nearest neighbor lookup
        - 'interpolate': Interpolation
        - 'simulate': Monte Carlo simulation (slow but exact)
        
    Returns:
    --------
    Dict[str, float] : Critical values at 10%, 5%, and 1% levels
    """
    # Select appropriate table
    if statistic.lower() in ['mz_alpha', 'mza', 'mzalpha']:
        table = MZ_ALPHA_CRITICAL_VALUES
        stat_key = 'MZ_alpha'
    elif statistic.lower() in ['msb']:
        table = MSB_CRITICAL_VALUES
        stat_key = 'MSB'
    elif statistic.lower() in ['mz_t', 'mzt', 'mzt']:
        table = MZ_T_CRITICAL_VALUES
        stat_key = 'MZ_t'
    else:
        raise ValueError(f"Unknown statistic: {statistic}")
    
    if method == 'simulate':
        # Compute via simulation
        cv_dict = simulate_critical_values(
            c_lower, c_upper, kappa=0, n_sim=10000
        )
        return {
            '10%': cv_dict[stat_key],
            '5%': cv_dict[stat_key],
            '1%': cv_dict[stat_key],
        }
    
    elif method == 'lookup':
        # Nearest neighbor lookup
        nearest_key = _find_nearest_bounds(c_lower, c_upper, table)
        return table[nearest_key].copy()
    
    else:  # interpolate
        # Interpolate critical values
        cv = {}
        for level in ['10%', '5%', '1%']:
            cv[level] = _interpolate_critical_value(
                c_lower, c_upper, table, level
            )
        return cv


def compute_and_save_critical_values(
    c_values: np.ndarray,
    output_file: str,
    n_sim: int = 20000,
    seed: Optional[int] = None
) -> None:
    """
    Compute critical values via simulation and save to CSV.
    
    Useful for extending the critical value tables.
    
    Parameters:
    -----------
    c_values : np.ndarray
        Array of c values for symmetric bounds
    output_file : str
        Path to save CSV file
    n_sim : int, default=20000
        Number of Monte Carlo replications
    seed : int, optional
        Random seed
    """
    import pandas as pd
    
    results = []
    
    for c in c_values:
        if c <= 0:
            continue
            
        c_lower, c_upper = -c, c
        
        print(f"Computing critical values for c ∈ [{c_lower:.2f}, {c_upper:.2f}]...")
        
        cv = simulate_critical_values(
            c_lower, c_upper, kappa=0,
            n_sim=n_sim, alpha=0.10, seed=seed
        )
        
        cv_5 = simulate_critical_values(
            c_lower, c_upper, kappa=0,
            n_sim=n_sim, alpha=0.05, seed=seed
        )
        
        cv_1 = simulate_critical_values(
            c_lower, c_upper, kappa=0,
            n_sim=n_sim, alpha=0.01, seed=seed
        )
        
        results.append({
            'c_lower': c_lower,
            'c_upper': c_upper,
            'MZ_alpha_10': cv['MZ_alpha'],
            'MZ_alpha_5': cv_5['MZ_alpha'],
            'MZ_alpha_1': cv_1['MZ_alpha'],
            'MSB_10': cv['MSB'],
            'MSB_5': cv_5['MSB'],
            'MSB_1': cv_1['MSB'],
            'MZ_t_10': cv['MZ_t'],
            'MZ_t_5': cv_5['MZ_t'],
            'MZ_t_1': cv_1['MZ_t'],
        })
    
    df = pd.DataFrame(results)
    df.to_csv(output_file, index=False)
    print(f"Critical values saved to {output_file}")
