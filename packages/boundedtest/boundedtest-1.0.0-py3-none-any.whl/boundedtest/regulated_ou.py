"""
Regulated Ornstein-Uhlenbeck Process Module

Implements simulation of regulated Ornstein-Uhlenbeck processes
for bounded time series as described in Cavaliere (2005) and
Carrion-i-Silvestre and Gadea (2013).
"""

import numpy as np
from typing import Tuple, Optional


def simulate_regulated_ou(
    kappa: float,
    c_lower: float,
    c_upper: float,
    n_steps: int = 1000,
    seed: Optional[int] = None
) -> np.ndarray:
    """
    Simulate a regulated Ornstein-Uhlenbeck process.
    
    The process follows:
    dW_κ(r) = κ W_κ(r) dr + dB(r) + dξ⁻(r) - dξ⁺(r)
    
    where ξ⁻ and ξ⁺ are regulators keeping the process within bounds.
    
    Parameters:
    -----------
    kappa : float
        Drift parameter (κ ≤ 0 for unit root testing)
    c_lower : float
        Lower bound parameter
    c_upper : float
        Upper bound parameter
    n_steps : int, default=1000
        Number of discretization steps
    seed : int, optional
        Random seed
        
    Returns:
    --------
    np.ndarray : Simulated process values (n_steps,)
    """
    if seed is not None:
        np.random.seed(seed)
    
    dt = 1.0 / n_steps
    W = np.zeros(n_steps)
    
    for t in range(1, n_steps):
        # OU drift
        drift = kappa * W[t-1] * dt
        
        # Brownian increment
        dB = np.random.normal(0, np.sqrt(dt))
        
        # Tentative next value
        W_next = W[t-1] + drift + dB
        
        # Apply bounds with regulators
        if W_next < c_lower:
            # Lower regulator activates
            W[t] = c_lower
        elif W_next > c_upper:
            # Upper regulator activates
            W[t] = c_upper
        else:
            W[t] = W_next
    
    return W


def simulate_bounded_process(
    T: int,
    b_lower: float,
    b_upper: float,
    alpha: float = 1.0,
    mu: float = 0.0,
    sigma: float = 1.0,
    seed: Optional[int] = None
) -> np.ndarray:
    """
    Simulate bounded process following the DGP in the paper.
    
    The process is:
    x_t = μ + y_t
    y_t = α y_{t-1} + u_t
    
    where u_t contains regulators to keep x_t within bounds.
    
    Parameters:
    -----------
    T : int
        Sample size
    b_lower : float
        Lower bound on x_t
    b_upper : float
        Upper bound on x_t
    alpha : float, default=1.0
        Autoregressive parameter
    mu : float, default=0.0
        Mean parameter
    sigma : float, default=1.0
        Innovation standard deviation
    seed : int, optional
        Random seed
        
    Returns:
    --------
    np.ndarray : Simulated bounded series (T,)
    """
    if seed is not None:
        np.random.seed(seed)
    
    x = np.zeros(T)
    y = np.zeros(T)
    
    # Initialize
    x[0] = mu
    y[0] = 0
    
    for t in range(1, T):
        # Innovation
        epsilon = np.random.normal(0, sigma)
        
        # Tentative y value
        y_tent = alpha * y[t-1] + epsilon
        
        # Tentative x value
        x_tent = mu + y_tent
        
        # Apply bounds
        if x_tent < b_lower:
            # Lower bound hits: adjust with lower regulator
            xi_lower = b_lower - x_tent
            x[t] = b_lower
            y[t] = b_lower - mu
        elif x_tent > b_upper:
            # Upper bound hits: adjust with upper regulator
            xi_upper = x_tent - b_upper
            x[t] = b_upper
            y[t] = b_upper - mu
        else:
            x[t] = x_tent
            y[t] = y_tent
    
    return x


def generate_bounded_ar1(
    T: int,
    bounds: Tuple[float, float],
    rho: float = 1.0,
    sigma: float = 1.0,
    mu: float = None,
    burnin: int = 100,
    seed: Optional[int] = None
) -> np.ndarray:
    """
    Generate bounded AR(1) process using Cavaliere's (2005) algorithm.
    
    This is the algorithm referenced in the paper for generating
    bounded processes in the Monte Carlo experiments.
    
    Parameters:
    -----------
    T : int
        Desired sample size
    bounds : Tuple[float, float]
        (lower_bound, upper_bound) for the process
    rho : float, default=1.0
        AR(1) coefficient (use 1.0 for unit root)
    sigma : float, default=1.0
        Innovation standard deviation
    mu : float, optional
        Mean of the process. If None, set to midpoint of bounds.
    burnin : int, default=100
        Number of burn-in observations
    seed : int, optional
        Random seed
        
    Returns:
    --------
    np.ndarray : Bounded AR(1) series (T,)
    """
    if seed is not None:
        np.random.seed(seed)
    
    b_lower, b_upper = bounds
    
    if mu is None:
        mu = (b_lower + b_upper) / 2
    
    # Total length including burnin
    total_T = T + burnin
    
    # Generate series
    x = np.zeros(total_T)
    
    # Start at mean
    x[0] = mu
    
    for t in range(1, total_T):
        # Generate innovation
        eps = np.random.normal(0, sigma)
        
        # AR(1) evolution (on demeaned series)
        y_tm1 = x[t-1] - mu
        y_t = rho * y_tm1 + eps
        x_prop = mu + y_t
        
        # Reflect at boundaries
        while x_prop < b_lower or x_prop > b_upper:
            if x_prop < b_lower:
                # Reflect off lower bound
                x_prop = 2 * b_lower - x_prop
            elif x_prop > b_upper:
                # Reflect off upper bound
                x_prop = 2 * b_upper - x_prop
        
        x[t] = x_prop
    
    # Return post-burnin sample
    return x[burnin:]


def compute_critical_values(
    c_lower: float,
    c_upper: float,
    kappa: float = 0,
    n_sim: int = 10000,
    n_steps: int = 1000,
    alpha: float = 0.05,
    seed: Optional[int] = None
) -> dict:
    """
    Compute critical values for M-type test statistics.
    
    Uses Monte Carlo simulation of the regulated OU process to obtain
    the limiting distribution under the null.
    
    Parameters:
    -----------
    c_lower : float
        Lower bound parameter
    c_upper : float
        Upper bound parameter
    kappa : float, default=0
        Non-centrality parameter (0 for null hypothesis)
    n_sim : int, default=10000
        Number of Monte Carlo replications
    n_steps : int, default=1000
        Number of steps for continuous approximation
    alpha : float, default=0.05
        Significance level
    seed : int, optional
        Random seed
        
    Returns:
    --------
    dict : Dictionary with critical values for MZα, MSB, MZt
    """
    if seed is not None:
        np.random.seed(seed)
    
    mz_alpha_stats = []
    msb_stats = []
    mz_t_stats = []
    
    for _ in range(n_sim):
        # Simulate regulated OU
        W_kappa = simulate_regulated_ou(kappa, c_lower, c_upper, n_steps)
        
        # Compute limiting statistics
        r = np.linspace(0, 1, n_steps)
        dr = r[1] - r[0]
        
        # Integral of W²
        int_W2 = np.sum(W_kappa[:-1] ** 2) * dr
        
        # Final value
        W_1 = W_kappa[-1]
        
        if int_W2 > 0:
            # MZα statistic
            MZ_alpha = (W_1 ** 2 - 1) / (2 * int_W2)
            mz_alpha_stats.append(MZ_alpha)
            
            # MSB statistic
            MSB = np.sqrt(int_W2)
            msb_stats.append(MSB)
            
            # MZt statistic
            MZ_t = MZ_alpha * MSB
            mz_t_stats.append(MZ_t)
    
    # Compute quantiles
    mz_alpha_stats = np.array(mz_alpha_stats)
    msb_stats = np.array(msb_stats)
    mz_t_stats = np.array(mz_t_stats)
    
    critical_values = {
        'MZ_alpha': np.percentile(mz_alpha_stats, alpha * 100),
        'MSB': np.percentile(msb_stats, 100 - alpha * 100),  # Upper tail
        'MZ_t': np.percentile(mz_t_stats, alpha * 100),
    }
    
    return critical_values
