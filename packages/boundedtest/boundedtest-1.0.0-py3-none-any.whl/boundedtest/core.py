"""
Core Module for Bounded Unit Root Tests

Main API for conducting GLS-based unit root tests on bounded time series.

Author: Merwan Roudane
Email: merwanroudane920@gmail.com
"""

import numpy as np
import pandas as pd
from dataclasses import dataclass
from typing import Union, Optional, Tuple, Dict
import warnings

from .detrending import ols_detrend, iterative_gls_detrend, estimate_bounds
from .lrv import estimate_lrv
from .statistics import (
    compute_mz_alpha, compute_msb, compute_mz_t,
    compute_all_statistics, compute_ar1_residuals
)
from .noncentrality import get_kappa, get_kappa_ers
from .critical_values import get_critical_values


@dataclass
class BoundedTestResult:
    """
    Results from bounded unit root test.
    
    Attributes:
    -----------
    statistic_name : str
        Name of the test statistic
    statistic : float
        Test statistic value
    pvalue : float or None
        P-value (if available)
    critical_values : dict
        Critical values at different significance levels
    detrending_method : str
        Detrending method used ('OLS' or 'GLS')
    lrv_method : str
        LRV estimation method used
    bounds : tuple
        (lower_bound, upper_bound) used
    c_parameters : tuple
        (c_lower, c_upper) estimated
    kappa : float or None
        Non-centrality parameter (for GLS)
    reject_5pct : bool
        Whether to reject at 5% significance level
    """
    statistic_name: str
    statistic: float
    pvalue: Optional[float]
    critical_values: Dict[str, float]
    detrending_method: str
    lrv_method: str
    bounds: Tuple[float, float]
    c_parameters: Tuple[float, float]
    kappa: Optional[float]
    lrv_estimate: float
    sample_size: int
    reject_5pct: bool
    
    def __repr__(self) -> str:
        """String representation of results."""
        lines = [
            f"\nBounded Unit Root Test Results",
            f"=" * 50,
            f"Test Statistic: {self.statistic_name}",
            f"Detrending Method: {self.detrending_method}",
            f"LRV Method: {self.lrv_method}",
            f"Sample Size: {self.sample_size}",
            f"",
            f"Bounds: [{self.bounds[0]:.4f}, {self.bounds[1]:.4f}]",
            f"c-parameters: [{self.c_parameters[0]:.4f}, {self.c_parameters[1]:.4f}]",
        ]
        
        if self.kappa is not None:
            lines.append(f"κ̅ (kappa-bar): {self.kappa:.4f}")
        
        lines.extend([
            f"",
            f"Test Statistic Value: {self.statistic:.4f}",
        ])
        
        if self.pvalue is not None:
            lines.append(f"P-value: {self.pvalue:.4f}")
        
        lines.extend([
            f"",
            f"Critical Values:",
            f"  10%: {self.critical_values.get('10%', np.nan):.4f}",
            f"   5%: {self.critical_values.get('5%', np.nan):.4f}",
            f"   1%: {self.critical_values.get('1%', np.nan):.4f}",
            f"",
            f"Reject H0 (5% level): {'Yes' if self.reject_5pct else 'No'}",
            f"=" * 50,
        ])
        
        return "\n".join(lines)


def bounded_unit_root_test(
    data: Union[np.ndarray, pd.Series, list],
    bounds: Tuple[float, float],
    statistic: str = 'mz_alpha',
    detrending: str = 'gls_bounds',
    lrv_method: str = 'np',
    deterministics: str = 'constant'
) -> BoundedTestResult:
    """
    Conduct GLS-based unit root test for bounded time series.
    
    This is the main function that implements the testing procedure
    described in Carrion-i-Silvestre and Gadea (2013).
    
    Parameters:
    -----------
    data : array-like
        Time series data to test
    bounds : tuple of float
        (lower_bound, upper_bound) for the series
    statistic : str, default='mz_alpha'
        Test statistic to compute:
        - 'mz_alpha': MZα statistic
        - 'msb': MSB statistic
        - 'mz_t': MZt statistic
        - 'all': Compute all statistics
    detrending : str, default='gls_bounds'
        Detrending method:
        - 'ols': OLS detrending
        - 'gls_ers': GLS with standard κ = -7
        - 'gls_bounds': GLS with bound-specific κ (recommended)
    lrv_method : str, default='np'
        Long-run variance estimation:
        - 'np': Non-parametric (Newey-West)
        - 'ar': Parametric (AR-based)
    deterministics : str, default='constant'
        Deterministic components ('constant', 'trend', or 'both')
        
    Returns:
    --------
    BoundedTestResult : Test results object
    
    Raises:
    -------
    ValueError : If inputs are invalid
    
    Examples:
    ---------
    >>> import numpy as np
    >>> from boundedtest import bounded_unit_root_test
    >>> 
    >>> # Generate bounded data
    >>> np.random.seed(42)
    >>> data = np.cumsum(np.random.randn(100))
    >>> data = np.clip(data, -5, 5)
    >>> 
    >>> # Test for unit root
    >>> result = bounded_unit_root_test(
    ...     data=data,
    ...     bounds=(-5, 5),
    ...     detrending='gls_bounds'
    ... )
    >>> print(result)
    """
    # Input validation and conversion
    if isinstance(data, pd.Series):
        x = data.values
    elif isinstance(data, list):
        x = np.array(data)
    else:
        x = np.asarray(data)
    
    if x.ndim > 1:
        x = x.flatten()
    
    T = len(x)
    b_lower, b_upper = bounds
    
    # Validate bounds
    if b_lower >= b_upper:
        raise ValueError("Lower bound must be less than upper bound")
    
    if np.any(x < b_lower) or np.any(x > b_upper):
        warnings.warn(
            "Data contains values outside specified bounds. "
            "Results may not be reliable."
        )
    
    # Validate statistic choice
    valid_statistics = ['mz_alpha', 'msb', 'mz_t', 'all']
    if statistic not in valid_statistics:
        raise ValueError(f"statistic must be one of {valid_statistics}")
    
    # Validate detrending choice
    valid_detrending = ['ols', 'gls_ers', 'gls_bounds']
    if detrending not in valid_detrending:
        raise ValueError(f"detrending must be one of {valid_detrending}")
    
    # Perform detrending and compute statistics
    if detrending == 'ols':
        # OLS detrending
        y_tilde, _, _ = ols_detrend(x, deterministics)
        
        # Compute AR(1) residuals for LRV
        residuals = compute_ar1_residuals(y_tilde)
        s2 = estimate_lrv(residuals, method=lrv_method)
        
        # Estimate c parameters
        s = np.sqrt(s2)
        c_lower, c_upper = estimate_bounds(y_tilde, b_lower, b_upper, s, method='initial')
        kappa = None
        
        detrending_label = 'OLS'
        
    elif detrending == 'gls_ers':
        # GLS with standard ERS kappa
        kappa = get_kappa_ers()
        
        # Initial estimate for bounds
        y_ols, _, _ = ols_detrend(x, deterministics)
        residuals_ols = compute_ar1_residuals(y_ols)
        s2_ols = estimate_lrv(residuals_ols, method=lrv_method)
        s_ols = np.sqrt(s2_ols)
        c_lower, c_upper = estimate_bounds(y_ols, b_lower, b_upper, s_ols, method='initial')
        
        # GLS detrending with standard kappa
        from .detrending import gls_detrend
        y_tilde, alpha_bar, _ = gls_detrend(x, c_lower, c_upper, deterministics, kappa)
        
        # LRV estimation
        residuals = compute_ar1_residuals(y_tilde)
        s2 = estimate_lrv(residuals, method=lrv_method)
        
        detrending_label = 'GLS-ERS'
        
    else:  # gls_bounds
        # Iterative GLS with bound-specific kappa
        y_tilde, c_lower, c_upper, kappa, s2 = iterative_gls_detrend(
            x, b_lower, b_upper, lrv_method, deterministics
        )
        
        detrending_label = 'GLS-BOUNDS'
    
    # Compute test statistics
    if statistic == 'all':
        MZ_alpha, MSB, MZ_t = compute_all_statistics(y_tilde, s2)
        
        # Get critical values for all statistics
        cv_alpha = get_critical_values('mz_alpha', c_lower, c_upper)
        cv_msb = get_critical_values('msb', c_lower, c_upper)
        cv_t = get_critical_values('mz_t', c_lower, c_upper)
        
        # Create multiple results
        results = {
            'MZ_alpha': BoundedTestResult(
                statistic_name='MZ_alpha',
                statistic=MZ_alpha,
                pvalue=None,
                critical_values=cv_alpha,
                detrending_method=detrending_label,
                lrv_method=lrv_method.upper(),
                bounds=(b_lower, b_upper),
                c_parameters=(c_lower, c_upper),
                kappa=kappa,
                lrv_estimate=s2,
                sample_size=T,
                reject_5pct=MZ_alpha < cv_alpha['5%']
            ),
            'MSB': BoundedTestResult(
                statistic_name='MSB',
                statistic=MSB,
                pvalue=None,
                critical_values=cv_msb,
                detrending_method=detrending_label,
                lrv_method=lrv_method.upper(),
                bounds=(b_lower, b_upper),
                c_parameters=(c_lower, c_upper),
                kappa=kappa,
                lrv_estimate=s2,
                sample_size=T,
                reject_5pct=MSB > cv_msb['5%']
            ),
            'MZ_t': BoundedTestResult(
                statistic_name='MZ_t',
                statistic=MZ_t,
                pvalue=None,
                critical_values=cv_t,
                detrending_method=detrending_label,
                lrv_method=lrv_method.upper(),
                bounds=(b_lower, b_upper),
                c_parameters=(c_lower, c_upper),
                kappa=kappa,
                lrv_estimate=s2,
                sample_size=T,
                reject_5pct=MZ_t < cv_t['5%']
            )
        }
        return results
    
    else:
        # Compute single statistic
        if statistic == 'mz_alpha':
            stat_value = compute_mz_alpha(y_tilde, s2)
            stat_name = 'MZ_alpha'
        elif statistic == 'msb':
            stat_value = compute_msb(y_tilde, s2)
            stat_name = 'MSB'
        else:  # mz_t
            stat_value = compute_mz_t(y_tilde, s2)
            stat_name = 'MZ_t'
        
        # Get critical values
        cv = get_critical_values(statistic, c_lower, c_upper)
        
        # Determine rejection
        if statistic == 'msb':
            reject = stat_value > cv['5%']  # Right-tail test
        else:
            reject = stat_value < cv['5%']  # Left-tail test
        
        result = BoundedTestResult(
            statistic_name=stat_name,
            statistic=stat_value,
            pvalue=None,
            critical_values=cv,
            detrending_method=detrending_label,
            lrv_method=lrv_method.upper(),
            bounds=(b_lower, b_upper),
            c_parameters=(c_lower, c_upper),
            kappa=kappa,
            lrv_estimate=s2,
            sample_size=T,
            reject_5pct=reject
        )
        
        return result
