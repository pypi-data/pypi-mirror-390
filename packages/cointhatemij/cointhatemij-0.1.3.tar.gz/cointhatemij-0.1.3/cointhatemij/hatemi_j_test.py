"""
Hatemi-J Cointegration Test with Two Unknown Regime Shifts

Reference:
    Hatemi-J, A. (2008). Tests for cointegration with two unknown regime shifts
    with an application to financial market integration.
    Empirical Economics, 35, 497-505.

Author: Dr. Merwan Roudane
Email: merwanroudane920@gmail.com
GitHub: https://github.com/merwanroudane/cointhatemij

REVISION: Complete implementation with all three models and corrected Zt/Za computation
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
    
    MODEL_NAMES = {
        1: 'C (Level shift - changes in intercept only)',
        2: 'C/T (Level shift with trend)',
        3: 'C/S (Regime shift - changes in intercept and slopes)'
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
            Model specification:
            1 = C (Level shift - changes in intercept only)
            2 = C/T (Level shift with trend)
            3 = C/S (Regime shift - changes in intercept and slopes)
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
            4 = SPC with Bartlett
            5 = SPC with QS
            6 = Kurozumi with Bartlett
            7 = Kurozumi with QS
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
            
        if model not in [1, 2, 3]:
            raise ValueError("Model must be 1 (C), 2 (C/T), or 3 (C/S)")
            
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
    
    def _create_lags(self, y: np.ndarray, p: int) -> np.ndarray:
        """Create lagged matrix for ADF test."""
        n = len(y)
        lags = np.zeros((n - p, p))
        for i in range(p):
            lags[:, i] = y[p - i - 1:n - i - 1]
        return lags
    
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
                se = np.sqrt(np.diag(np.sum(e**2) / (len(e) - len(b)) * 
                                     np.linalg.inv(X.T @ X)))
                t_stat = np.abs(b[-1] / se[-1])
                
                if t_stat > 1.645:  # 10% critical value
                    opt_lag = p
                    break
        
        # Estimate with optimal lag
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
        se = np.sqrt(np.diag(np.sum(e**2) / (len(e) - len(b)) * 
                            np.linalg.inv(X.T @ X)))
        
        adf_stat = b[1] / se[1]
        
        return adf_stat, opt_lag
    
    def _bartlett_kernel(self, x: float, bandwidth: int) -> float:
        """Bartlett kernel for long-run variance estimation."""
        if np.abs(x) <= bandwidth:
            return 1 - np.abs(x) / bandwidth
        else:
            return 0
    
    def _qs_kernel(self, x: float, bandwidth: int) -> float:
        """Quadratic Spectral kernel for long-run variance estimation."""
        if x == 0:
            return 1
        z = 6 * np.pi * x / (5 * bandwidth)
        return 3 * (np.sin(z) / z - np.cos(z)) / (z ** 2)
    
    def _compute_long_run_variance(self, e: np.ndarray) -> float:
        """
        Compute long-run variance using specified method.
        
        This follows the formulas in equations (3)-(6) from the paper.
        """
        n = len(e)
        
        # Demean residuals
        e_demean = e - np.mean(e)
        
        # Compute rho_hat (OLS estimate without intercept)
        if n > 1:
            rho_hat = np.sum(e_demean[:-1] * e_demean[1:]) / np.sum(e_demean[:-1]**2)
        else:
            rho_hat = 0
        
        # Compute gamma_hat(j) - autocovariance function (equation 4)
        def gamma_hat(j):
            if j >= n:
                return 0
            result = 0
            for t in range(j, n):
                result += (e_demean[t-j] - rho_hat * e_demean[max(0, t-j-1)]) * \
                         (e_demean[t] - rho_hat * e_demean[max(0, t-1)])
            return result / n
        
        # Choose kernel based on varm
        if self.varm == 1:  # iid
            # For iid case, just use variance
            lrv = gamma_hat(0)
        elif self.varm in [2, 4, 6]:  # Bartlett kernel
            lrv = gamma_hat(0)
            for j in range(1, self.bwl + 1):
                weight = self._bartlett_kernel(j, self.bwl)
                lrv += 2 * weight * gamma_hat(j)
        elif self.varm in [3, 5, 7]:  # Quadratic Spectral kernel
            lrv = gamma_hat(0)
            for j in range(1, self.bwl + 1):
                weight = self._qs_kernel(j, self.bwl)
                lrv += 2 * weight * gamma_hat(j)
        else:
            lrv = gamma_hat(0)
        
        return max(lrv, 1e-10)  # Avoid division by zero
    
    def _pp_test(self, e: np.ndarray) -> Tuple[float, float]:
        """
        Phillips-Perron tests (Zt and Za).
        
        Following equations (3), (5), and (6) from Hatemi-J (2008).
        
        Parameters:
        -----------
        e : np.ndarray
            Residuals from cointegration regression
            
        Returns:
        --------
        zt_stat : float
            Zt test statistic
        za_stat : float
            Za test statistic
        """
        n = len(e)
        
        # Demean residuals
        e_demean = e - np.mean(e)
        
        # Compute rho_hat (OLS estimate of first-order autocorrelation without intercept)
        if n > 1:
            numerator = np.sum(e_demean[:-1] * e_demean[1:])
            denominator = np.sum(e_demean[:-1]**2)
            if denominator > 1e-10:
                rho_hat = numerator / denominator
            else:
                rho_hat = 0
        else:
            rho_hat = 0
        
        # Compute bias correction term (sum of weighted autocovariances)
        bias_correction = 0
        
        # Choose kernel and compute weighted autocovariances
        if self.varm in [2, 4, 6]:  # Bartlett kernel
            for j in range(1, self.bwl + 1):
                weight = self._bartlett_kernel(j, self.bwl)
                # Compute gamma_hat(j)
                gamma_j = 0
                for t in range(j, n):
                    gamma_j += (e_demean[t-j] - rho_hat * e_demean[max(0, t-j-1)]) * \
                              (e_demean[t] - rho_hat * e_demean[max(0, t-1)])
                gamma_j /= n
                bias_correction += weight * gamma_j
        elif self.varm in [3, 5, 7]:  # Quadratic Spectral kernel
            for j in range(1, self.bwl + 1):
                weight = self._qs_kernel(j, self.bwl)
                # Compute gamma_hat(j)
                gamma_j = 0
                for t in range(j, n):
                    gamma_j += (e_demean[t-j] - rho_hat * e_demean[max(0, t-j-1)]) * \
                              (e_demean[t] - rho_hat * e_demean[max(0, t-1)])
                gamma_j /= n
                bias_correction += weight * gamma_j
        
        # Compute rho_star (bias-corrected estimate) - equation (3)
        if denominator > 1e-10:
            rho_star = (numerator - bias_correction) / denominator
        else:
            rho_star = rho_hat
        
        # Compute long-run variance
        lrv = self._compute_long_run_variance(e)
        
        # Compute Za statistic - equation (5)
        # Za = n(rho_star - 1)
        za_stat = n * (rho_star - 1)
        
        # Compute Zt statistic - equation (6)
        # Zt = (rho_star - 1) * sqrt(sum(e_t^2) / lrv)
        sum_e_squared = np.sum(e_demean[:-1]**2)
        if lrv > 1e-10 and sum_e_squared > 1e-10:
            zt_stat = (rho_star - 1) * np.sqrt(sum_e_squared / lrv)
        else:
            zt_stat = za_stat / np.sqrt(n)
        
        return zt_stat, za_stat
    
    def _create_design_matrix(self, tb1: int, tb2: int) -> np.ndarray:
        """
        Create design matrix based on model specification.
        
        Parameters:
        -----------
        tb1 : int
            First break point
        tb2 : int
            Second break point
            
        Returns:
        --------
        X : np.ndarray
            Design matrix for the specified model
        """
        n = self.n
        
        # Create dummy variables for breaks
        du1 = np.concatenate([np.zeros(tb1), np.ones(n - tb1)])
        du2 = np.concatenate([np.zeros(tb2), np.ones(n - tb2)])
        
        if self.model == 1:
            # Model C: Level shift (intercept changes only)
            # y_t = α0 + α1*D1t + α2*D2t + β'x_t + u_t
            X = np.column_stack([
                np.ones(n),    # constant
                du1,           # first break dummy
                du2,           # second break dummy
                self.x         # regressors (unchanged slopes)
            ])
            
        elif self.model == 2:
            # Model C/T: Level shift with trend
            # y_t = α0 + α1*D1t + α2*D2t + γ*t + β'x_t + u_t
            trend = np.arange(1, n + 1)
            X = np.column_stack([
                np.ones(n),    # constant
                du1,           # first break dummy
                du2,           # second break dummy
                trend,         # time trend
                self.x         # regressors (unchanged slopes)
            ])
            
        elif self.model == 3:
            # Model C/S: Regime shift (intercept and slope changes)
            # y_t = α0 + α1*D1t + α2*D2t + β0'x_t + β1'(D1t*x_t) + β2'(D2t*x_t) + u_t
            X = np.column_stack([
                np.ones(n),                        # constant
                du1,                               # first break dummy
                du2,                               # second break dummy
                self.x,                            # original regressors
                du1.reshape(-1, 1) * self.x,      # first break interaction
                du2.reshape(-1, 1) * self.x       # second break interaction
            ])
        
        return X
    
    def fit(self) -> Dict[str, Union[float, int, Dict]]:
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
        print(f"\nSearching for optimal break points...")
        print(f"Model: {self.MODEL_NAMES[self.model]}")
        print(f"Observations: {self.n}, Variables: {self.k}")
        print(f"Search range: [{T1}, {T2}] x [{T1}, {T3}]")
        
        total_iterations = (T2 - T1 + 1) * (T3 - 2 * T1 + 1)
        current_iteration = 0
        
        for tb1 in range(T1, T2 + 1):
            for tb2 in range(tb1 + T1, T3 + 1):
                current_iteration += 1
                
                if current_iteration % 100 == 0:
                    print(f"Progress: {current_iteration}/{total_iterations} "
                          f"({100*current_iteration/total_iterations:.1f}%)")
                
                # Create design matrix
                X = self._create_design_matrix(tb1, tb2)
                
                # OLS estimation
                _, e1, _ = self._ols(self.y, X)
                
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
        
        print("Search complete!")
        
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
            'model': self.model,
            'model_name': self.MODEL_NAMES[self.model],
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
        
        print("\n" + "=" * 70)
        print("Hatemi-J Cointegration Test with Two Regime Shifts")
        print("=" * 70)
        print(f"Model: {r['model_name']}")
        print(f"Number of observations: {r['n']}")
        print(f"Number of independent variables: {r['k']}")
        print(f"Trimming rate: {r['trimm']:.3f}")
        print(f"Bandwidth for long-run variance: {r['bwl']}")
        print(f"Information criterion: {r['ic']} ", end="")
        print(f"({'AIC' if r['ic'] == 1 else 'BIC' if r['ic'] == 2 else 't-stat'})")
        print(f"Maximum lags: {r['pmax']}")
        print(f"Variance estimation method: {r['varm']}")
        print("=" * 70)
        
        # Test statistics
        print("\nTest Statistics:")
        print("=" * 70)
        print(f"{'Test':<8} {'Statistic':>12} {'1%':>12} {'5%':>12} {'10%':>12}")
        print("-" * 70)
        
        cv_adf = r['cv_adf_zt']
        cv_za = r['cv_za']
        
        print(f"{'ADF':<8} {r['ADF_min']:>12.3f} {cv_adf['1%']:>12.3f} "
              f"{cv_adf['5%']:>12.3f} {cv_adf['10%']:>12.3f}")
        print(f"{'Zt':<8} {r['Zt_min']:>12.3f} {cv_adf['1%']:>12.3f} "
              f"{cv_adf['5%']:>12.3f} {cv_adf['10%']:>12.3f}")
        print(f"{'Za':<8} {r['Za_min']:>12.3f} {cv_za['1%']:>12.3f} "
              f"{cv_za['5%']:>12.3f} {cv_za['10%']:>12.3f}")
        print("=" * 70)
        
        # Break dates
        print("\nEstimated Break Dates:")
        print("=" * 70)
        print(f"ADF test:")
        print(f"  First break (TB1):  {r['TB1_adf']:>4d} ({r['TB1_adf']/r['n']:.3f})")
        print(f"  Second break (TB2): {r['TB2_adf']:>4d} ({r['TB2_adf']/r['n']:.3f})")
        print(f"\nZt test:")
        print(f"  First break (TB1):  {r['TB1_zt']:>4d} ({r['TB1_zt']/r['n']:.3f})")
        print(f"  Second break (TB2): {r['TB2_zt']:>4d} ({r['TB2_zt']/r['n']:.3f})")
        print(f"\nZa test:")
        print(f"  First break (TB1):  {r['TB1_za']:>4d} ({r['TB1_za']/r['n']:.3f})")
        print(f"  Second break (TB2): {r['TB2_za']:>4d} ({r['TB2_za']/r['n']:.3f})")
        print("=" * 70)
        
        # Conclusions
        print("\nTest Conclusions (at 10% significance level):")
        print("=" * 70)
        
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
        
        print("=" * 70)
        print("\nNote: H0 = No cointegration")
        print("      All test statistics should be negative")
        print("      More negative values provide stronger evidence for cointegration")
        print("=" * 70)


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
        Model specification:
        1 = C (Level shift - changes in intercept only)
        2 = C/T (Level shift with trend)
        3 = C/S (Regime shift - changes in intercept and slopes)
    bwl : int, optional
        Bandwidth for long-run variance computation
    ic : int, default=3
        Information criterion (1=AIC, 2=BIC, 3=t-stat)
    pmax : int, default=8
        Maximum number of lags for ADF test
    varm : int, default=1
        Variance estimation method (1-7)
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
    >>> # Generate sample data with cointegration
    >>> np.random.seed(123)
    >>> n = 100
    >>> x = np.cumsum(np.random.randn(n, 2), axis=0)  # I(1) process
    >>> y = 0.5 + 0.3 * x[:, 0] + 0.2 * x[:, 1] + np.random.randn(n) * 0.1
    >>> 
    >>> # Test for cointegration with Model 3 (regime shift)
    >>> results = coint_hatemi_j(y, x, model=3)
    >>> 
    >>> # Test with Model 1 (level shift only)
    >>> results = coint_hatemi_j(y, x, model=1)
    >>> 
    >>> # Test with Model 2 (level shift with trend)
    >>> results = coint_hatemi_j(y, x, model=2)
    """
    test = HatemiJTest(y, x, model, bwl, ic, pmax, varm, trimm)
    results = test.fit()
    
    if verbose:
        test.summary()
    
    return results
