"""
Unit Tests for BoundedTest Package

Basic tests to verify functionality.
"""

import numpy as np
import pytest
from boundedtest import bounded_unit_root_test
from boundedtest.regulated_ou import generate_bounded_ar1
from boundedtest.detrending import ols_detrend, gls_detrend
from boundedtest.lrv import estimate_lrv_np, estimate_lrv_ar
from boundedtest.statistics import compute_mz_alpha, compute_msb, compute_mz_t
from boundedtest.noncentrality import get_kappa


class TestBasicFunctionality:
    """Test basic functionality of the package."""
    
    def test_data_generation(self):
        """Test bounded AR(1) data generation."""
        data = generate_bounded_ar1(
            T=100,
            bounds=(-5, 5),
            rho=1.0,
            sigma=1.0,
            seed=42
        )
        
        assert len(data) == 100
        assert np.min(data) >= -5
        assert np.max(data) <= 5
    
    def test_ols_detrend(self):
        """Test OLS detrending."""
        np.random.seed(42)
        x = np.random.randn(100)
        
        y_tilde, z, mu = ols_detrend(x, deterministics='constant')
        
        assert len(y_tilde) == 100
        assert np.abs(np.mean(y_tilde)) < 1e-10  # Should be demeaned
    
    def test_gls_detrend(self):
        """Test GLS detrending."""
        np.random.seed(42)
        x = np.random.randn(100)
        
        y_tilde, alpha_bar, kappa = gls_detrend(
            x, c_lower=-0.5, c_upper=0.5,
            deterministics='constant'
        )
        
        assert len(y_tilde) == 100
        assert alpha_bar < 1.0  # Should be less than 1
        assert kappa < 0  # Should be negative
    
    def test_lrv_estimation(self):
        """Test LRV estimation methods."""
        np.random.seed(42)
        residuals = np.random.randn(100)
        
        # Non-parametric
        s2_np = estimate_lrv_np(residuals)
        assert s2_np > 0
        
        # Parametric
        s2_ar, lag = estimate_lrv_ar(residuals)
        assert s2_ar > 0
        assert lag >= 0
    
    def test_statistics_computation(self):
        """Test computation of test statistics."""
        np.random.seed(42)
        y_tilde = np.random.randn(100)
        s2 = 1.0
        
        mz_alpha = compute_mz_alpha(y_tilde, s2)
        msb = compute_msb(y_tilde, s2)
        mz_t = compute_mz_t(y_tilde, s2)
        
        assert not np.isnan(mz_alpha)
        assert not np.isnan(msb)
        assert not np.isnan(mz_t)
        assert msb > 0
    
    def test_kappa_retrieval(self):
        """Test non-centrality parameter retrieval."""
        kappa = get_kappa(-0.5, 0.5, method='lookup')
        
        assert kappa < 0
        assert kappa > -10  # Reasonable range


class TestBoundedUnitRootTest:
    """Test the main testing function."""
    
    def test_basic_test(self):
        """Test basic unit root test."""
        np.random.seed(42)
        data = generate_bounded_ar1(
            T=100,
            bounds=(-5, 5),
            rho=1.0,
            sigma=1.0
        )
        
        result = bounded_unit_root_test(
            data=data,
            bounds=(-5, 5),
            statistic='mz_alpha',
            detrending='gls_bounds',
            lrv_method='np'
        )
        
        assert result is not None
        assert hasattr(result, 'statistic')
        assert hasattr(result, 'critical_values')
        assert hasattr(result, 'reject_5pct')
    
    def test_all_statistics(self):
        """Test computation of all statistics."""
        np.random.seed(42)
        data = generate_bounded_ar1(
            T=100,
            bounds=(-5, 5),
            rho=1.0,
            sigma=1.0
        )
        
        results = bounded_unit_root_test(
            data=data,
            bounds=(-5, 5),
            statistic='all',
            detrending='gls_bounds',
            lrv_method='np'
        )
        
        assert isinstance(results, dict)
        assert 'MZ_alpha' in results
        assert 'MSB' in results
        assert 'MZ_t' in results
    
    def test_different_detrending_methods(self):
        """Test different detrending methods."""
        np.random.seed(42)
        data = generate_bounded_ar1(
            T=100,
            bounds=(-5, 5),
            rho=1.0,
            sigma=1.0
        )
        
        for method in ['ols', 'gls_ers', 'gls_bounds']:
            result = bounded_unit_root_test(
                data=data,
                bounds=(-5, 5),
                statistic='mz_alpha',
                detrending=method,
                lrv_method='np'
            )
            
            assert result is not None
            assert not np.isnan(result.statistic)
    
    def test_different_lrv_methods(self):
        """Test different LRV estimation methods."""
        np.random.seed(42)
        data = generate_bounded_ar1(
            T=100,
            bounds=(-5, 5),
            rho=1.0,
            sigma=1.0
        )
        
        for lrv_method in ['np', 'ar']:
            result = bounded_unit_root_test(
                data=data,
                bounds=(-5, 5),
                statistic='mz_alpha',
                detrending='gls_bounds',
                lrv_method=lrv_method
            )
            
            assert result is not None
            assert result.lrv_estimate > 0
    
    def test_with_list_input(self):
        """Test with list input."""
        np.random.seed(42)
        data = generate_bounded_ar1(
            T=100,
            bounds=(-5, 5),
            rho=1.0,
            sigma=1.0
        ).tolist()
        
        result = bounded_unit_root_test(
            data=data,
            bounds=(-5, 5),
            detrending='gls_bounds'
        )
        
        assert result is not None
    
    def test_invalid_bounds(self):
        """Test error handling for invalid bounds."""
        data = np.random.randn(100)
        
        with pytest.raises(ValueError):
            bounded_unit_root_test(
                data=data,
                bounds=(5, -5),  # Invalid: lower > upper
                detrending='gls_bounds'
            )


def test_reproducibility():
    """Test that results are reproducible with same seed."""
    data = generate_bounded_ar1(
        T=100,
        bounds=(-5, 5),
        rho=1.0,
        sigma=1.0,
        seed=12345
    )
    
    result1 = bounded_unit_root_test(
        data=data,
        bounds=(-5, 5),
        detrending='gls_bounds',
        lrv_method='np'
    )
    
    result2 = bounded_unit_root_test(
        data=data,
        bounds=(-5, 5),
        detrending='gls_bounds',
        lrv_method='np'
    )
    
    assert result1.statistic == result2.statistic
    assert result1.c_parameters == result2.c_parameters


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
