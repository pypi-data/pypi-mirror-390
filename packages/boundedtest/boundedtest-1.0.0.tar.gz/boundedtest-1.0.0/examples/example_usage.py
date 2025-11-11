"""
Example Script: Bounded Unit Root Tests

This script demonstrates how to use the boundedtest package
for testing unit roots in bounded time series.

Author: Merwan Roudane
Email: merwanroudane920@gmail.com
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from boundedtest import bounded_unit_root_test
from boundedtest.regulated_ou import generate_bounded_ar1


def example_1_basic_usage():
    """Example 1: Basic usage with simulated data."""
    print("=" * 70)
    print("EXAMPLE 1: Basic Usage")
    print("=" * 70)
    
    # Generate bounded unit root process
    np.random.seed(42)
    data = generate_bounded_ar1(
        T=200,
        bounds=(-10, 10),
        rho=1.0,  # Unit root
        sigma=1.0,
        burnin=100
    )
    
    print(f"\nGenerated data:")
    print(f"  Sample size: {len(data)}")
    print(f"  Mean: {np.mean(data):.4f}")
    print(f"  Std: {np.std(data):.4f}")
    print(f"  Min: {np.min(data):.4f}")
    print(f"  Max: {np.max(data):.4f}")
    
    # Run test with GLS-BOUNDS (recommended)
    print("\n" + "-" * 70)
    print("Running bounded unit root test (GLS-BOUNDS)...")
    print("-" * 70)
    
    result = bounded_unit_root_test(
        data=data,
        bounds=(-10, 10),
        statistic='mz_alpha',
        detrending='gls_bounds',
        lrv_method='np'
    )
    
    print(result)


def example_2_all_statistics():
    """Example 2: Compute all test statistics."""
    print("\n" + "=" * 70)
    print("EXAMPLE 2: All Test Statistics")
    print("=" * 70)
    
    # Generate stationary bounded process
    np.random.seed(123)
    data = generate_bounded_ar1(
        T=200,
        bounds=(-5, 5),
        rho=0.9,  # Stationary
        sigma=1.0,
        burnin=100
    )
    
    print(f"\nGenerated stationary data (ρ=0.9):")
    print(f"  Sample size: {len(data)}")
    
    # Compute all statistics
    results = bounded_unit_root_test(
        data=data,
        bounds=(-5, 5),
        statistic='all',
        detrending='gls_bounds',
        lrv_method='np'
    )
    
    print("\n" + "-" * 70)
    print("Test Results Summary:")
    print("-" * 70)
    
    for stat_name, result in results.items():
        print(f"\n{stat_name}:")
        print(f"  Statistic: {result.statistic:.4f}")
        print(f"  Critical Value (5%): {result.critical_values['5%']:.4f}")
        print(f"  Reject H0: {result.reject_5pct}")


def example_3_compare_detrending():
    """Example 3: Compare detrending methods."""
    print("\n" + "=" * 70)
    print("EXAMPLE 3: Compare Detrending Methods")
    print("=" * 70)
    
    # Generate bounded data
    np.random.seed(456)
    data = generate_bounded_ar1(
        T=200,
        bounds=(-8, 8),
        rho=1.0,
        sigma=1.0,
        burnin=100
    )
    
    methods = {
        'ols': 'OLS Detrending',
        'gls_ers': 'GLS-ERS (κ=-7)',
        'gls_bounds': 'GLS-BOUNDS (κ̅ bound-specific)'
    }
    
    print("\nComparing detrending methods on same data:")
    print("-" * 70)
    
    for method_key, method_name in methods.items():
        result = bounded_unit_root_test(
            data=data,
            bounds=(-8, 8),
            statistic='mz_alpha',
            detrending=method_key,
            lrv_method='np'
        )
        
        print(f"\n{method_name}:")
        print(f"  MZα = {result.statistic:.4f}")
        print(f"  Critical (5%) = {result.critical_values['5%']:.4f}")
        print(f"  Reject H0 = {result.reject_5pct}")
        if result.kappa is not None:
            print(f"  κ = {result.kappa:.4f}")


def example_4_lrv_comparison():
    """Example 4: Compare LRV estimation methods."""
    print("\n" + "=" * 70)
    print("EXAMPLE 4: Compare LRV Estimation Methods")
    print("=" * 70)
    
    np.random.seed(789)
    data = generate_bounded_ar1(
        T=200,
        bounds=(-6, 6),
        rho=1.0,
        sigma=1.0,
        burnin=100
    )
    
    lrv_methods = {
        'np': 'Non-parametric (Newey-West)',
        'ar': 'Parametric (AR-based)'
    }
    
    print("\nComparing LRV estimation methods:")
    print("-" * 70)
    
    for lrv_key, lrv_name in lrv_methods.items():
        result = bounded_unit_root_test(
            data=data,
            bounds=(-6, 6),
            statistic='mz_alpha',
            detrending='gls_bounds',
            lrv_method=lrv_key
        )
        
        print(f"\n{lrv_name}:")
        print(f"  MZα = {result.statistic:.4f}")
        print(f"  LRV estimate = {result.lrv_estimate:.4f}")
        print(f"  Reject H0 = {result.reject_5pct}")


def example_5_with_pandas():
    """Example 5: Using with pandas DataFrame."""
    print("\n" + "=" * 70)
    print("EXAMPLE 5: Using with Pandas DataFrame")
    print("=" * 70)
    
    # Create DataFrame
    np.random.seed(101112)
    dates = pd.date_range('2020-01-01', periods=200, freq='D')
    data = generate_bounded_ar1(
        T=200,
        bounds=(-10, 10),
        rho=1.0,
        sigma=1.0,
        burnin=100
    )
    
    df = pd.DataFrame({
        'date': dates,
        'value': data
    })
    
    print("\nDataFrame info:")
    print(df.head())
    print(f"\nShape: {df.shape}")
    
    # Run test on Series
    result = bounded_unit_root_test(
        data=df['value'],
        bounds=(-10, 10),
        detrending='gls_bounds'
    )
    
    print("\n" + "-" * 70)
    print("Test Results:")
    print("-" * 70)
    print(result)


def example_6_monte_carlo():
    """Example 6: Simple Monte Carlo simulation."""
    print("\n" + "=" * 70)
    print("EXAMPLE 6: Monte Carlo Simulation (Small Scale)")
    print("=" * 70)
    
    print("\nSimulating power under H1 (ρ=0.95)...")
    
    n_sim = 100  # Small number for demonstration
    rejections = 0
    
    for i in range(n_sim):
        # Generate stationary data
        data = generate_bounded_ar1(
            T=200,
            bounds=(-5, 5),
            rho=0.95,
            sigma=1.0,
            burnin=100,
            seed=i
        )
        
        # Test
        result = bounded_unit_root_test(
            data=data,
            bounds=(-5, 5),
            statistic='mz_alpha',
            detrending='gls_bounds',
            lrv_method='np'
        )
        
        if result.reject_5pct:
            rejections += 1
        
        if (i + 1) % 25 == 0:
            print(f"  Completed {i+1}/{n_sim} replications...")
    
    power = rejections / n_sim
    print(f"\nEmpirical power (5% level): {power:.3f}")
    print(f"Rejections: {rejections}/{n_sim}")


def example_7_different_bounds():
    """Example 7: Testing with different bound widths."""
    print("\n" + "=" * 70)
    print("EXAMPLE 7: Effect of Bound Width")
    print("=" * 70)
    
    # Generate base series
    np.random.seed(202122)
    base_data = np.cumsum(np.random.randn(200))
    
    bound_widths = [
        (2, 4),
        (5, 10),
        (10, 20),
    ]
    
    print("\nTesting same series with different bound widths:")
    print("-" * 70)
    
    for (half_width, full_width) in bound_widths:
        # Clip data to bounds
        data = np.clip(base_data, -half_width, half_width)
        
        result = bounded_unit_root_test(
            data=data,
            bounds=(-half_width, half_width),
            statistic='mz_alpha',
            detrending='gls_bounds',
            lrv_method='np'
        )
        
        print(f"\nBounds: [{-half_width}, {half_width}] (width={full_width}):")
        print(f"  c-parameters: [{result.c_parameters[0]:.4f}, {result.c_parameters[1]:.4f}]")
        print(f"  κ̅ = {result.kappa:.4f}")
        print(f"  MZα = {result.statistic:.4f}")
        print(f"  Critical (5%) = {result.critical_values['5%']:.4f}")
        print(f"  Reject H0 = {result.reject_5pct}")


def main():
    """Run all examples."""
    print("\n")
    print("*" * 70)
    print("*" + " " * 68 + "*")
    print("*" + "  BOUNDED UNIT ROOT TEST - EXAMPLES".center(68) + "*")
    print("*" + " " * 68 + "*")
    print("*" * 70)
    
    try:
        example_1_basic_usage()
        example_2_all_statistics()
        example_3_compare_detrending()
        example_4_lrv_comparison()
        example_5_with_pandas()
        example_6_monte_carlo()
        example_7_different_bounds()
        
        print("\n" + "=" * 70)
        print("All examples completed successfully!")
        print("=" * 70 + "\n")
        
    except Exception as e:
        print(f"\n\nError occurred: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
