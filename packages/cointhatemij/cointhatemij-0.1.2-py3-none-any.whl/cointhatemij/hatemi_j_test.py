"""
Hatemi-J Cointegration Test with Two Unknown Regime Shifts

Reference:
    Hatemi-J, A. (2008). Tests for cointegration with two unknown regime shifts
    with an application to financial market integration.
    Empirical Economics, 35, 497-505.

Author: Dr. Merwan Roudane
Email: merwanroudane920@gmail.com
GitHub: https://github.com/merwanroudane/cointhatemij
"""

import numpy as np
from scipy import stats
from typing import Tuple, Optional, Dict, Union
import warnings


class HatemiJTest:
    """
    Hatemi-J Cointegration Test with Two Unknown Regime Shifts.
    
    This class implements three residual-based test statistics for cointegration
    that take into account two possible regime shifts with unknown timing.
    
    Attributes:
        critical_values (dict): Critical values for different numbers of independent variables
    """
    
    # Critical values from Hatemi-J (2008), Table 1
    CRITICAL_VALUES = {
        1: {
            'adf_zt': {'1%': -6.503, '5%': -6.015, '10%': -5.653},
            'za': {'1%': -90.704, '5%': -76.003, '10%': -52.232}
        },
        2: {
            'adf_zt': {'1%': -6.928, '5%': -6.458, '10%': -6.224},
            'za': {'1%': -99.458, '5%': -83.644, '10%': -76.806}
        },
        3: {
            'adf_zt': {'1%': -7.833, '5%': -7.352, '10%': -7.118},
            'za': {'1%': -118.577, '5%': -104.860, '10%': -97.749}
        },
        4: {
            'adf_zt': {'1%': -8.353, '5%': -7.903, '10%': -7.705},
            'za': {'1%': -140.135, '5%': -123.870, '10%': -116.169}
        }
    }
    
    def __init__(self, y: np.ndarray, x: np.ndarray, model: int = 3,
                 bwl: Optional[int] = None, ic: int = 3, pmax: int = 8,
                 varm: int = 1, trimm: float = 0.10):
        """
        Initialize Hatemi-J cointegration test.
        
        Parameters:
        -----------
        y : np.ndarray
            Dependent variable (n x 1)
        x : np.ndarray
            Independent variables (n x k)
        model : int, default=3
            Model specification (only model 3 is available: C/S regime shift)
        bwl : int, optional
            Bandwidth for long-run variance computation.
            Default: round(4 * (n/100)^(2/9))
        ic : int, default=3
            Information criterion for ADF-based test:
            1 = Akaike (AIC)
            2 = Schwarz (BIC)
            3 = t-stat significance
        pmax : int, default=8
            Maximum number of lags for Δy in ADF test
        varm : int, default=1
            Long-run variance estimation method:
            1 = iid
            2 = Bartlett
            3 = Quadratic Spectral (QS)
        trimm : float, default=0.10
            Trimming rate for break point search
        """
        # Input validation
        self._validate_inputs(y, x, model, trimm, ic, varm)
        
        # Store parameters
        self.y = y.flatten() if y.ndim > 1 else y
        self.x = x if x.ndim > 1 else x.reshape(-1, 1)
        self.n = len(self.y)
        self.k = self.x.shape[1]
        self.model = model
        self.ic = ic
        self.pmax = pmax
        self.varm = varm
        self.trimm = trimm
        
        # Set bandwidth
        if bwl is None:
            self.bwl = int(np.round(4 * (self.n / 100) ** (2/9)))
        else:
            self.bwl = bwl
            
        # Initialize results
        self.results = None
        
    def _validate_inputs(self, y: np.ndarray, x: np.ndarray, model: int,
                        trimm: float, ic: int, varm: int):
        """Validate input parameters."""
        if np.any(np.isnan(y)) or np.any(np.isnan(x)):
            raise ValueError("Missing values found in y or x")
            
        y_len = len(y.flatten())
        x_len = x.shape[0]
        
        if y_len != x_len:
            raise ValueError("y and x must have the same number of observations")
            
        if model != 3:
            raise ValueError("Only Model 3 (C/S regime shift) is available")
            
        if not 0 < trimm < 0.5:
            raise ValueError("Trimming rate must be between 0 and 0.5")
            
        if ic not in [1, 2, 3]:
            raise ValueError("Information criterion must be 1 (AIC), 2 (BIC), or 3 (t-stat)")
            
        if varm not in range(1, 8):
            raise ValueError("Variance method must be between 1 and 7")
            
        k = x.shape[1] if x.ndim > 1 else 1
        if k > 4:
            raise ValueError("Critical values are only available for k <= 4")
    
    def _ols(self, y: np.ndarray, x: np.ndarray) -> Tuple[np.ndarray, np.ndarray, float]:
        """
        Perform OLS regression.
        
        Returns:
        --------
        b : np.ndarray
            Coefficient estimates
        e : np.ndarray
            Residuals
        sig2 : float
            Variance estimate
        """
        n, k = x.shape
        b = np.linalg.lstsq(x, y, rcond=None)[0]
        e = y - x @ b
        sig2 = float(e.T @ e / (n - k))
        return b, e, sig2
    
    def _adf_test(self, y: np.ndarray) -> Tuple[float, int]:
        """
        Augmented Dickey-Fuller test with lag selection.
        
        Parameters:
        -----------
        y : np.ndarray
            Series to test
            
        Returns:
        --------
        adf_stat : float
            ADF test statistic
        opt_lag : int
            Optimal lag length
        """
        n = len(y)
        dy = np.diff(y)
        y_lag = y[:-1]
        
        # Lag selection
        if self.ic == 1:  # AIC
            aic_vals = np.zeros(self.pmax + 1)
            for p in range(self.pmax + 1):
                if p == 0:
                    X = np.column_stack([np.ones(len(dy)), y_lag])
                    dy_temp = dy
                else:
                    dy_lags = self._create_lags(dy, p)
                    X = np.column_stack([np.ones(len(dy_lags)), 
                                        y_lag[p:],
                                        dy_lags])
                    dy_temp = dy[p:]
                    
                b = np.linalg.lstsq(X, dy_temp, rcond=None)[0]
                e = dy_temp - X @ b
                k = X.shape[1]
                aic_vals[p] = len(e) * np.log(np.sum(e**2) / len(e)) + 2 * k
                
            opt_lag = np.argmin(aic_vals)
            
        elif self.ic == 2:  # BIC
            bic_vals = np.zeros(self.pmax + 1)
            for p in range(self.pmax + 1):
                if p == 0:
                    X = np.column_stack([np.ones(len(dy)), y_lag])
                    dy_temp = dy
                else:
                    dy_lags = self._create_lags(dy, p)
                    X = np.column_stack([np.ones(len(dy_lags)), 
                                        y_lag[p:],
                                        dy_lags])
                    dy_temp = dy[p:]
                    
                b = np.linalg.lstsq(X, dy_temp, rcond=None)[0]
                e = dy_temp - X @ b
                k = X.shape[1]
                bic_vals[p] = len(e) * np.log(np.sum(e**2) / len(e)) + k * np.log(len(e))
                
            opt_lag = np.argmin(bic_vals)
            
        else:  # t-stat significance
            opt_lag = 0
            for p in range(self.pmax, 0, -1):
                dy_lags = self._create_lags(dy, p)
                X = np.column_stack([np.ones(len(dy_lags)), 
                                    y_lag[p:],
                                    dy_lags])
                dy_temp = dy[p:]
                
                b = np.linalg.lstsq(X, dy_temp, rcond=None)[0]
                e = dy_temp - X @ b
                
                # Calculate t-statistics
                var_e = np.sum(e**2) / (len(e) - X.shape[1])
                var_b = var_e * np.linalg.inv(X.T @ X)
                se_b = np.sqrt(np.diag(var_b))
                t_stats = np.abs(b / se_b)
                
                # Check if any lag (excluding constant and y_lag) is significant
                if np.any(t_stats[2:] > 1.96):
                    opt_lag = p
                    break
        
        # Final regression with optimal lag
        if opt_lag == 0:
            X = np.column_stack([np.ones(len(dy)), y_lag])
            dy_temp = dy
        else:
            dy_lags = self._create_lags(dy, opt_lag)
            X = np.column_stack([np.ones(len(dy_lags)), 
                                y_lag[opt_lag:],
                                dy_lags])
            dy_temp = dy[opt_lag:]
        
        b = np.linalg.lstsq(X, dy_temp, rcond=None)[0]
        e = dy_temp - X @ b
        
        # Calculate ADF statistic
        var_e = np.sum(e**2) / (len(e) - X.shape[1])
        var_b = var_e * np.linalg.inv(X.T @ X)
        se_b = np.sqrt(np.diag(var_b))
        adf_stat = b[1] / se_b[1]  # t-statistic for y_lag coefficient
        
        return float(adf_stat), opt_lag
    
    def _create_lags(self, y: np.ndarray, p: int) -> np.ndarray:
        """Create lagged variables."""
        n = len(y)
        lags = np.zeros((n - p, p))
        for i in range(p):
            lags[:, i] = y[p-1-i:n-1-i]
        return lags
    
    def _pp_test(self, y: np.ndarray) -> Tuple[float, float]:
        """
        Phillips-Perron test.
        
        Parameters:
        -----------
        y : np.ndarray
            Series to test
            
        Returns:
        --------
        zt : float
            Zt test statistic
        za : float
            Za test statistic
        """
        n = len(y)
        dy = np.diff(y)
        y_lag = y[:-1]
        
        # OLS regression: Δy_t = ρ * y_{t-1} + ε_t
        X = y_lag.reshape(-1, 1)
        b = np.linalg.lstsq(X, dy, rcond=None)[0]
        rho = float(b[0])
        e = dy - X @ b
        sigma2 = float(np.sum(e**2) / (n - 1))
        
        # Long-run variance estimation
        omega2 = self._long_run_variance(e, self.bwl, self.varm)
        
        # Calculate test statistics
        lambda_val = 0.5 * (omega2 - sigma2) / sigma2
        
        # Zt statistic (equation 6 in paper)
        sum_y2 = float(np.sum(y_lag**2))
        zt = (n * rho - 1) / np.sqrt(omega2 / sigma2 * sum_y2 / n**2)
        
        # Za statistic (equation 5 in paper)
        se_rho2 = sigma2 / sum_y2
        za = n * (rho - 1) - lambda_val * n**2 * se_rho2 / omega2
        
        return float(zt), float(za)
    
    def _long_run_variance(self, e: np.ndarray, bwl: int, method: int) -> float:
        """
        Estimate long-run variance.
        
        Parameters:
        -----------
        e : np.ndarray
            Residuals
        bwl : int
            Bandwidth
        method : int
            Estimation method
            
        Returns:
        --------
        omega2 : float
            Long-run variance estimate
        """
        n = len(e)
        
        # Short-run variance
        gamma0 = float(np.sum(e**2) / n)
        
        if method == 1:  # iid
            return gamma0
            
        elif method == 2:  # Bartlett kernel
            gamma = np.zeros(bwl + 1)
            gamma[0] = gamma0
            
            for j in range(1, bwl + 1):
                if j < n:
                    gamma[j] = float(np.sum(e[:-j] * e[j:]) / n)
                else:
                    gamma[j] = 0
                    
            weights = 1 - np.arange(1, bwl + 1) / (bwl + 1)
            omega2 = gamma[0] + 2 * np.sum(weights * gamma[1:])
            
            return float(omega2)
            
        elif method == 3:  # Quadratic Spectral
            # QS kernel with automatic bandwidth
            def qs_kernel(x):
                if x == 0:
                    return 1.0
                return (25 / (12 * np.pi**2 * x**2)) * \
                       (np.sin(6 * np.pi * x / 5) / (6 * np.pi * x / 5) - 
                        np.cos(6 * np.pi * x / 5))
            
            gamma = np.zeros(n)
            gamma[0] = gamma0
            
            for j in range(1, min(n, bwl + 1)):
                gamma[j] = float(np.sum(e[:-j] * e[j:]) / n)
            
            weights = np.array([qs_kernel(j / bwl) for j in range(min(n, bwl + 1))])
            omega2 = gamma[0] + 2 * np.sum(weights[1:min(n, bwl + 1)] * 
                                           gamma[1:min(n, bwl + 1)])
            
            return float(omega2)
        
        else:
            # For other methods (4-7), use Bartlett as default
            warnings.warn(f"Variance method {method} not fully implemented. Using Bartlett.")
            return self._long_run_variance(e, bwl, 2)
    
    def fit(self) -> Dict[str, Union[float, int, np.ndarray]]:
        """
        Execute Hatemi-J cointegration test.
        
        Returns:
        --------
        results : dict
            Dictionary containing test statistics and break dates
        """
        # Initialize
        TB1_adf = TB1_zt = TB1_za = 0
        TB2_adf = TB2_zt = TB2_za = 0
        ADF_min = Zt_min = Za_min = 1000.0
        
        # Loop boundaries
        T1 = int(np.round(self.trimm * self.n))
        T2 = int(np.round((1 - 2 * self.trimm) * self.n))
        T3 = int(np.round((1 - self.trimm) * self.n))
        
        # Result matrices
        DF = np.full((T2 - T1 + 1, T3 - 2 * T1 + 1), np.nan)
        Zt = np.full((T2 - T1 + 1, T3 - 2 * T1 + 1), np.nan)
        Za = np.full((T2 - T1 + 1, T3 - 2 * T1 + 1), np.nan)
        
        # Double loop for break point detection
        print("Searching for optimal break points...")
        for tb1 in range(T1, T2 + 1):
            for tb2 in range(tb1 + T1, T3 + 1):
                # Create dummy variables
                du1 = np.concatenate([np.zeros(tb1), np.ones(self.n - tb1)])
                du2 = np.concatenate([np.zeros(tb2), np.ones(self.n - tb2)])
                
                # Model 3: C/S (regime shift in intercept and slopes)
                if self.model == 3:
                    x1 = np.column_stack([
                        np.ones(self.n),
                        du1,
                        du2,
                        self.x,
                        du1.reshape(-1, 1) * self.x,
                        du2.reshape(-1, 1) * self.x
                    ])
                
                # OLS estimation
                _, e1, _ = self._ols(self.y, x1)
                
                # ADF test
                adf_stat, _ = self._adf_test(e1)
                DF[tb1 - T1, tb2 - 2 * T1] = adf_stat
                
                # PP tests
                zt_stat, za_stat = self._pp_test(e1)
                Zt[tb1 - T1, tb2 - 2 * T1] = zt_stat
                Za[tb1 - T1, tb2 - 2 * T1] = za_stat
                
                # Update minimum statistics
                if adf_stat < ADF_min:
                    TB1_adf, TB2_adf, ADF_min = tb1, tb2, adf_stat
                
                if zt_stat < Zt_min:
                    TB1_zt, TB2_zt, Zt_min = tb1, tb2, zt_stat
                
                if za_stat < Za_min:
                    TB1_za, TB2_za, Za_min = tb1, tb2, za_stat
        
        # Get critical values
        cv_adf_zt = self.CRITICAL_VALUES[self.k]['adf_zt']
        cv_za = self.CRITICAL_VALUES[self.k]['za']
        
        # Store results
        self.results = {
            'ADF_min': ADF_min,
            'TB1_adf': TB1_adf,
            'TB2_adf': TB2_adf,
            'Zt_min': Zt_min,
            'TB1_zt': TB1_zt,
            'TB2_zt': TB2_zt,
            'Za_min': Za_min,
            'TB1_za': TB1_za,
            'TB2_za': TB2_za,
            'cv_adf_zt': cv_adf_zt,
            'cv_za': cv_za,
            'n': self.n,
            'k': self.k,
            'trimm': self.trimm,
            'bwl': self.bwl,
            'ic': self.ic,
            'pmax': self.pmax,
            'varm': self.varm
        }
        
        return self.results
    
    def summary(self):
        """Print formatted test results."""
        if self.results is None:
            raise ValueError("Must run fit() before summary()")
        
        r = self.results
        
        print("\n" + "=" * 65)
        print("Hatemi-J Cointegration Test with Two Regime Shifts")
        print("=" * 65)
        print(f"Model: C/S (regime shift in intercept and slopes)")
        print(f"Number of observations: {r['n']}")
        print(f"Number of independent variables: {r['k']}")
        print(f"Trimming rate: {r['trimm']:.3f}")
        print(f"Bandwidth for long-run variance: {r['bwl']}")
        print(f"Information criterion: {r['ic']} ", end="")
        print(f"({'AIC' if r['ic'] == 1 else 'BIC' if r['ic'] == 2 else 't-stat'})")
        print(f"Maximum lags: {r['pmax']}")
        print(f"Variance estimation method: {r['varm']}")
        print("=" * 65)
        
        # Test statistics
        print("\nTest Statistics:")
        print("=" * 65)
        print(f"{'Test':<8} {'Statistic':>12} {'1%':>12} {'5%':>12} {'10%':>12}")
        print("-" * 65)
        
        cv_adf = r['cv_adf_zt']
        cv_za = r['cv_za']
        
        print(f"{'ADF':<8} {r['ADF_min']:>12.3f} {cv_adf['1%']:>12.3f} "
              f"{cv_adf['5%']:>12.3f} {cv_adf['10%']:>12.3f}")
        print(f"{'Zt':<8} {r['Zt_min']:>12.3f} {cv_adf['1%']:>12.3f} "
              f"{cv_adf['5%']:>12.3f} {cv_adf['10%']:>12.3f}")
        print(f"{'Za':<8} {r['Za_min']:>12.3f} {cv_za['1%']:>12.3f} "
              f"{cv_za['5%']:>12.3f} {cv_za['10%']:>12.3f}")
        print("=" * 65)
        
        # Break dates
        print("\nEstimated Break Dates:")
        print("=" * 65)
        print(f"ADF test:")
        print(f"  First break (TB1):  {r['TB1_adf']:>4d} ({r['TB1_adf']/r['n']:.3f})")
        print(f"  Second break (TB2): {r['TB2_adf']:>4d} ({r['TB2_adf']/r['n']:.3f})")
        print(f"\nZt test:")
        print(f"  First break (TB1):  {r['TB1_zt']:>4d} ({r['TB1_zt']/r['n']:.3f})")
        print(f"  Second break (TB2): {r['TB2_zt']:>4d} ({r['TB2_zt']/r['n']:.3f})")
        print(f"\nZa test:")
        print(f"  First break (TB1):  {r['TB1_za']:>4d} ({r['TB1_za']/r['n']:.3f})")
        print(f"  Second break (TB2): {r['TB2_za']:>4d} ({r['TB2_za']/r['n']:.3f})")
        print("=" * 65)
        
        # Conclusions
        print("\nTest Conclusions (at 10% significance level):")
        print("=" * 65)
        
        adf_reject = r['ADF_min'] < cv_adf['10%']
        zt_reject = r['Zt_min'] < cv_adf['10%']
        za_reject = r['Za_min'] < cv_za['10%']
        
        print(f"ADF test: ", end="")
        print("Reject H0 - Cointegration detected" if adf_reject 
              else "Fail to reject H0 - No cointegration")
        
        print(f"Zt test:  ", end="")
        print("Reject H0 - Cointegration detected" if zt_reject 
              else "Fail to reject H0 - No cointegration")
        
        print(f"Za test:  ", end="")
        print("Reject H0 - Cointegration detected" if za_reject 
              else "Fail to reject H0 - No cointegration")
        
        print("=" * 65)
        print("\nNote: H0 = No cointegration")
        print("=" * 65)


def coint_hatemi_j(y: np.ndarray, x: np.ndarray, model: int = 3,
                   bwl: Optional[int] = None, ic: int = 3, pmax: int = 8,
                   varm: int = 1, trimm: float = 0.10, 
                   verbose: bool = True) -> Dict[str, Union[float, int, np.ndarray]]:
    """
    Perform Hatemi-J cointegration test with two unknown regime shifts.
    
    This is a convenience function that wraps the HatemiJTest class.
    
    Parameters:
    -----------
    y : np.ndarray
        Dependent variable (n x 1)
    x : np.ndarray
        Independent variables (n x k)
    model : int, default=3
        Model specification (only model 3 available)
    bwl : int, optional
        Bandwidth for long-run variance computation
    ic : int, default=3
        Information criterion (1=AIC, 2=BIC, 3=t-stat)
    pmax : int, default=8
        Maximum number of lags for ADF test
    varm : int, default=1
        Variance estimation method
    trimm : float, default=0.10
        Trimming rate
    verbose : bool, default=True
        Print summary of results
        
    Returns:
    --------
    results : dict
        Dictionary with test statistics and break dates
        
    Example:
    --------
    >>> import numpy as np
    >>> from cointhatemij import coint_hatemi_j
    >>> 
    >>> # Generate sample data
    >>> np.random.seed(123)
    >>> n = 100
    >>> x = np.random.randn(n, 2)
    >>> y = 0.5 + 0.3 * x[:, 0] + 0.2 * x[:, 1] + np.random.randn(n)
    >>> 
    >>> # Run test
    >>> results = coint_hatemi_j(y, x)
    >>> print(f"ADF statistic: {results['ADF_min']:.3f}")
    """
    test = HatemiJTest(y, x, model, bwl, ic, pmax, varm, trimm)
    results = test.fit()
    
    if verbose:
        test.summary()
    
    return results
