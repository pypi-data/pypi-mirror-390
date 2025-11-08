"""
Test suite for cointhatemij package
"""

import pytest
import numpy as np
from cointhatemij import HatemiJTest, coint_hatemi_j


class TestHatemiJTest:
    """Test cases for HatemiJTest class"""
    
    def setup_method(self):
        """Set up test data"""
        np.random.seed(42)
        self.n = 100
        self.x = np.random.randn(self.n, 2)
        self.y = 0.5 + 0.3 * self.x[:, 0] + 0.2 * self.x[:, 1] + np.random.randn(self.n)
    
    def test_initialization(self):
        """Test HatemiJTest initialization"""
        test = HatemiJTest(self.y, self.x)
        assert test.n == self.n
        assert test.k == 2
        assert test.model == 3
        assert test.trimm == 0.10
        
    def test_input_validation_missing_values(self):
        """Test that missing values raise error"""
        y_nan = self.y.copy()
        y_nan[0] = np.nan
        with pytest.raises(ValueError, match="Missing values"):
            HatemiJTest(y_nan, self.x)
    
    def test_input_validation_shape_mismatch(self):
        """Test that shape mismatch raises error"""
        with pytest.raises(ValueError, match="same number of observations"):
            HatemiJTest(self.y[:50], self.x)
    
    def test_input_validation_model(self):
        """Test that invalid model raises error"""
        with pytest.raises(ValueError, match="Only Model 3"):
            HatemiJTest(self.y, self.x, model=1)
    
    def test_fit_returns_dict(self):
        """Test that fit returns a dictionary with expected keys"""
        test = HatemiJTest(self.y, self.x)
        results = test.fit()
        
        expected_keys = ['ADF_min', 'TB1_adf', 'TB2_adf', 
                        'Zt_min', 'TB1_zt', 'TB2_zt',
                        'Za_min', 'TB1_za', 'TB2_za',
                        'cv_adf_zt', 'cv_za']
        
        for key in expected_keys:
            assert key in results
    
    def test_critical_values_match_paper(self):
        """Test that critical values match Hatemi-J (2008) Table 1"""
        # k=1
        test1 = HatemiJTest(self.y, self.x[:, 0].reshape(-1, 1))
        results1 = test1.fit()
        assert results1['cv_adf_zt']['1%'] == -6.503
        assert results1['cv_adf_zt']['5%'] == -6.015
        
        # k=2
        test2 = HatemiJTest(self.y, self.x)
        results2 = test2.fit()
        assert results2['cv_adf_zt']['1%'] == -6.928


class TestCointHatemiJFunction:
    """Test cases for convenience function"""
    
    def setup_method(self):
        """Set up test data"""
        np.random.seed(42)
        self.n = 100
        self.x = np.random.randn(self.n, 2)
        self.y = 0.5 + 0.3 * self.x[:, 0] + 0.2 * self.x[:, 1] + np.random.randn(self.n)
    
    def test_function_returns_dict(self):
        """Test that function returns dictionary"""
        results = coint_hatemi_j(self.y, self.x, verbose=False)
        assert isinstance(results, dict)


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
