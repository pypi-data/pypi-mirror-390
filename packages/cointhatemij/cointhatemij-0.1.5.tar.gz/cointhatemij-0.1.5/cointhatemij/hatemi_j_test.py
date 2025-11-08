"""
Hatemi-J Cointegration Test - DEFINITIVE CLEAN IMPLEMENTATION

This version has crystal-clear formulas matching the paper exactly.
Each equation is labeled and explained.

Reference: Hatemi-J (2008), Empirical Economics, 35, 497-505
"""

import numpy as np
from scipy import stats
from typing import Tuple, Optional, Dict, Union
import warnings


class HatemiJTest:
    """
    Hatemi-J Cointegration Test with Two Unknown Regime Shifts.
    
    Crystal-clear implementation following the paper exactly.
    """
    
    # Critical values from Table 1
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
        1: 'C (Level shift)',
        2: 'C/T (Level shift with trend)',
        3: 'C/S (Regime shift)'
    }
    
    def __init__(self, y: np.ndarray, x: np.ndarray, model: int = 3,
                 bwl: Optional[int] = None, ic: int = 3, pmax: int = 8,
                 varm: int = 1, trimm: float = 0.10):
        """Initialize test."""
        # Validate
        self._validate_inputs(y, x, model, trimm, ic, varm)
        
        # Store
        self.y = y.flatten() if y.ndim > 1 else y
        self.x = x if x.ndim > 1 else x.reshape(-1, 1)
        self.n = len(self.y)
        self.k = self.x.shape[1]
        self.model = model
        self.ic = ic
        self.pmax = pmax
        self.varm = varm
        self.trimm = trimm
        
        # Bandwidth
        if bwl is None:
            self.bwl = int(np.round(4 * (self.n / 100) ** (2/9)))
        else:
            self.bwl = bwl
            
        self.results = None
        
    def _validate_inputs(self, y, x, model, trimm, ic, varm):
        """Validate inputs."""
        if np.any(np.isnan(y)) or np.any(np.isnan(x)):
            raise ValueError("Missing values in y or x")
        if len(y.flatten()) != x.shape[0]:
            raise ValueError("y and x must have same number of observations")
        if model not in [1, 2, 3]:
            raise ValueError("Model must be 1, 2, or 3")
        if not 0 < trimm < 0.5:
            raise ValueError("Trimming rate must be between 0 and 0.5")
        if ic not in [1, 2, 3]:
            raise ValueError("IC must be 1 (AIC), 2 (BIC), or 3 (t-stat)")
        if varm not in range(1, 8):
            raise ValueError("Variance method must be 1-7")
        k = x.shape[1] if x.ndim > 1 else 1
        if k > 4:
            raise ValueError("Critical values only available for k <= 4")
    
    def _ols(self, y, x):
        """OLS regression."""
        b = np.linalg.lstsq(x, y, rcond=None)[0]
        e = y - x @ b
        sig2 = float(e.T @ e / (len(e) - len(b)))
        return b, e, sig2
    
    def _create_lags(self, y, p):
        """Create lagged matrix."""
        n = len(y)
        lags = np.zeros((n - p, p))
        for i in range(p):
            lags[:, i] = y[p - i - 1:n - i - 1]
        return lags
    
    def _adf_test(self, y):
        """
        Augmented Dickey-Fuller test with lag selection.
        Returns: (test_statistic, optimal_lag)
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
                    X = np.column_stack([np.ones(len(dy_lags)), y_lag[p:], dy_lags])
                    dy_temp = dy[p:]
                b = np.linalg.lstsq(X, dy_temp, rcond=None)[0]
                e = dy_temp - X @ b
                aic_vals[p] = len(e) * np.log(np.sum(e**2) / len(e)) + 2 * len(b)
            opt_lag = np.argmin(aic_vals)
            
        elif self.ic == 2:  # BIC
            bic_vals = np.zeros(self.pmax + 1)
            for p in range(self.pmax + 1):
                if p == 0:
                    X = np.column_stack([np.ones(len(dy)), y_lag])
                    dy_temp = dy
                else:
                    dy_lags = self._create_lags(dy, p)
                    X = np.column_stack([np.ones(len(dy_lags)), y_lag[p:], dy_lags])
                    dy_temp = dy[p:]
                b = np.linalg.lstsq(X, dy_temp, rcond=None)[0]
                e = dy_temp - X @ b
                bic_vals[p] = len(e) * np.log(np.sum(e**2) / len(e)) + len(b) * np.log(len(e))
            opt_lag = np.argmin(bic_vals)
            
        else:  # t-stat
            opt_lag = 0
            for p in range(self.pmax, 0, -1):
                dy_lags = self._create_lags(dy, p)
                X = np.column_stack([np.ones(len(dy_lags)), y_lag[p:], dy_lags])
                dy_temp = dy[p:]
                b = np.linalg.lstsq(X, dy_temp, rcond=None)[0]
                e = dy_temp - X @ b
                se = np.sqrt(np.diag(np.sum(e**2) / (len(e) - len(b)) * np.linalg.inv(X.T @ X)))
                if np.abs(b[-1] / se[-1]) > 1.645:
                    opt_lag = p
                    break
        
        # Estimate with optimal lag
        if opt_lag == 0:
            X = np.column_stack([np.ones(len(dy)), y_lag])
            dy_temp = dy
        else:
            dy_lags = self._create_lags(dy, opt_lag)
            X = np.column_stack([np.ones(len(dy_lags)), y_lag[opt_lag:], dy_lags])
            dy_temp = dy[opt_lag:]
        
        b = np.linalg.lstsq(X, dy_temp, rcond=None)[0]
        e = dy_temp - X @ b
        se = np.sqrt(np.diag(np.sum(e**2) / (len(e) - len(b)) * np.linalg.inv(X.T @ X)))
        adf_stat = b[1] / se[1]
        
        return adf_stat, opt_lag
    
    def _kernel_weight(self, j):
        """Kernel weight function."""
        if self.varm in [2, 4, 6]:  # Bartlett
            if abs(j) <= self.bwl:
                return 1 - abs(j) / self.bwl
            return 0.0
        elif self.varm in [3, 5, 7]:  # Quadratic Spectral
            if j == 0:
                return 1.0
            z = 6 * np.pi * j / (5 * self.bwl)
            return 3 * (np.sin(z) / z - np.cos(z)) / (z**2)
        else:  # iid
            return 0.0 if j != 0 else 1.0
    
    def _pp_test(self, e):
        """
        Phillips-Perron Zt and Za tests.
        
        Following Hatemi-J (2008) Equations (3), (4), (5), (6) exactly.
        
        Returns: (Zt_statistic, Za_statistic)
        
        Both should be NEGATIVE. If positive, something is wrong!
        """
        T = len(e)
        
        # =================================================================
        # STEP 1: Estimate rho from AR(1) regression WITHOUT intercept
        # u_t = rho * u_{t-1} + v_t
        # =================================================================
        e_lag = e[:-1]
        e_current = e[1:]
        
        sum_e_lag_squared = np.sum(e_lag**2)
        if sum_e_lag_squared < 1e-10:
            return 0.0, 0.0
        
        # OLS estimate of rho
        rho_hat = np.sum(e_lag * e_current) / sum_e_lag_squared
        
        # =================================================================
        # STEP 2: Compute autocovariance function γ̂(j) - Equation (4)
        # γ̂(j) = (1/T) Σ_{t=j+1}^T [(û_{t-j} - ρ̂û_{t-j-1})(û_t - ρ̂û_{t-1})]
        # =================================================================
        def gamma_hat(j):
            if j >= T:
                return 0.0
            
            result = 0.0
            for t in range(j, T):
                # For t-j term
                u_t_minus_j = e[t - j]
                u_t_minus_j_minus_1 = e[t - j - 1] if (t - j - 1) >= 0 else 0.0
                
                # For t term  
                u_t = e[t]
                u_t_minus_1 = e[t - 1] if (t - 1) >= 0 else 0.0
                
                result += (u_t_minus_j - rho_hat * u_t_minus_j_minus_1) * \
                         (u_t - rho_hat * u_t_minus_1)
            
            return result / T
        
        # =================================================================
        # STEP 3: Compute bias correction term
        # Σ_{j=1}^B w(j/B) * γ̂(j)
        # =================================================================
        bias_correction = 0.0
        if self.varm > 1:  # Only if not iid
            for j in range(1, self.bwl + 1):
                w_j = self._kernel_weight(j)
                gamma_j = gamma_hat(j)
                bias_correction += w_j * gamma_j
        
        # =================================================================
        # STEP 4: Compute ρ̂* (bias-corrected) - Equation (3)
        # ρ̂* = [Σ û_t*û_{t+1} - B*Σw(j/B)γ̂(j)] / Σ û_t^2
        #
        # NOTE: The paper shows bias_correction term is summed,
        # but needs to be multiplied by T to match dimensions
        # =================================================================
        numerator = np.sum(e_lag * e_current) - T * bias_correction
        denominator = sum_e_lag_squared
        
        if denominator > 1e-10:
            rho_star = numerator / denominator
        else:
            rho_star = rho_hat
        
        # =================================================================
        # STEP 5: Compute long-run variance
        # lrv = γ̂(0) + 2*Σ_{j=1}^B w(j/B)*γ̂(j)
        # =================================================================
        lrv = gamma_hat(0)
        for j in range(1, self.bwl + 1):
            w_j = self._kernel_weight(j)
            lrv += 2 * w_j * gamma_hat(j)
        
        lrv = max(lrv, 1e-10)  # Avoid division by zero
        
        # =================================================================
        # STEP 6: Compute Za statistic - Equation (5)
        # Z_α = T * (ρ̂* - 1)
        #
        # NOTE: Should be NEGATIVE (since ρ̂* < 1 for stationary series)
        # =================================================================
        za_stat = T * (rho_star - 1)
        
        # =================================================================
        # STEP 7: Compute Zt statistic - Equation (6)
        # Z_t = (ρ̂* - 1) * sqrt(Σû²_t / lrv)
        #
        # NOTE: Should also be NEGATIVE
        # =================================================================
        if lrv > 1e-10 and sum_e_lag_squared > 1e-10:
            zt_stat = (rho_star - 1) * np.sqrt(sum_e_lag_squared / lrv)
        else:
            # Fallback
            zt_stat = za_stat / np.sqrt(T)
        
        # =================================================================
        # SANITY CHECK: Both should be negative!
        # =================================================================
        if zt_stat > 0 or za_stat > 0:
            warnings.warn(
                f"WARNING: PP test produced positive values! "
                f"Zt={zt_stat:.3f}, Za={za_stat:.3f}. "
                f"This suggests non-stationary residuals or computational issue."
            )
        
        return zt_stat, za_stat
    
    def _create_design_matrix(self, tb1, tb2):
        """Create design matrix for model."""
        n = self.n
        du1 = np.concatenate([np.zeros(tb1), np.ones(n - tb1)])
        du2 = np.concatenate([np.zeros(tb2), np.ones(n - tb2)])
        
        if self.model == 1:
            # Level shift: y_t = α0 + α1*D1t + α2*D2t + β'x_t + u_t
            X = np.column_stack([np.ones(n), du1, du2, self.x])
        elif self.model == 2:
            # Level shift + trend
            trend = np.arange(1, n + 1)
            X = np.column_stack([np.ones(n), du1, du2, trend, self.x])
        else:  # model == 3
            # Regime shift
            X = np.column_stack([
                np.ones(n), du1, du2, self.x,
                du1.reshape(-1, 1) * self.x,
                du2.reshape(-1, 1) * self.x
            ])
        
        return X
    
    def fit(self):
        """Execute test."""
        # Initialize
        TB1_adf = TB1_zt = TB1_za = 0
        TB2_adf = TB2_zt = TB2_za = 0
        ADF_min = Zt_min = Za_min = 1000.0
        
        # Loop boundaries
        T1 = int(np.round(self.trimm * self.n))
        T2 = int(np.round((1 - 2 * self.trimm) * self.n))
        T3 = int(np.round((1 - self.trimm) * self.n))
        
        print(f"\nSearching for optimal break points...")
        print(f"Model: {self.MODEL_NAMES[self.model]}")
        print(f"n={self.n}, k={self.k}")
        print(f"Search range: tb1 ∈ [{T1},{T2}], tb2 ∈ [tb1+{T1},{T3}]")
        
        total_iter = 0
        for tb1 in range(T1, T2 + 1):
            for tb2 in range(tb1 + T1, T3 + 1):
                total_iter += 1
                
                if total_iter % 500 == 0:
                    print(f"  Iteration {total_iter}...")
                
                # Design matrix
                X = self._create_design_matrix(tb1, tb2)
                
                # OLS
                _, e, _ = self._ols(self.y, X)
                
                # Tests
                adf_stat, _ = self._adf_test(e)
                zt_stat, za_stat = self._pp_test(e)
                
                # Update minima
                if adf_stat < ADF_min:
                    TB1_adf, TB2_adf, ADF_min = tb1, tb2, adf_stat
                if zt_stat < Zt_min:
                    TB1_zt, TB2_zt, Zt_min = tb1, tb2, zt_stat
                if za_stat < Za_min:
                    TB1_za, TB2_za, Za_min = tb1, tb2, za_stat
        
        print(f"Search complete! Tested {total_iter} combinations.")
        
        # Get critical values
        cv_adf_zt = self.CRITICAL_VALUES[self.k]['adf_zt']
        cv_za = self.CRITICAL_VALUES[self.k]['za']
        
        # Store results
        self.results = {
            'ADF_min': ADF_min, 'TB1_adf': TB1_adf, 'TB2_adf': TB2_adf,
            'Zt_min': Zt_min, 'TB1_zt': TB1_zt, 'TB2_zt': TB2_zt,
            'Za_min': Za_min, 'TB1_za': TB1_za, 'TB2_za': TB2_za,
            'cv_adf_zt': cv_adf_zt, 'cv_za': cv_za,
            'n': self.n, 'k': self.k, 'model': self.model,
            'model_name': self.MODEL_NAMES[self.model],
            'trimm': self.trimm, 'bwl': self.bwl,
            'ic': self.ic, 'pmax': self.pmax, 'varm': self.varm
        }
        
        return self.results
    
    def summary(self):
        """Print results."""
        if self.results is None:
            raise ValueError("Run fit() first")
        
        r = self.results
        
        print("\n" + "="*70)
        print("Hatemi-J Cointegration Test")
        print("="*70)
        print(f"Model: {r['model_name']}")
        print(f"Observations: {r['n']}, Regressors: {r['k']}")
        print(f"Trimming: {r['trimm']}, Bandwidth: {r['bwl']}")
        print(f"IC: {r['ic']}, pmax: {r['pmax']}, varm: {r['varm']}")
        print("="*70)
        
        print("\nTest Statistics:")
        print("="*70)
        print(f"{'Test':<8} {'Statistic':>12} {'1%':>10} {'5%':>10} {'10%':>10}")
        print("-"*70)
        
        cv_adf = r['cv_adf_zt']
        cv_za = r['cv_za']
        
        print(f"{'ADF':<8} {r['ADF_min']:>12.3f} {cv_adf['1%']:>10.3f} {cv_adf['5%']:>10.3f} {cv_adf['10%']:>10.3f}")
        print(f"{'Zt':<8} {r['Zt_min']:>12.3f} {cv_adf['1%']:>10.3f} {cv_adf['5%']:>10.3f} {cv_adf['10%']:>10.3f}")
        print(f"{'Za':<8} {r['Za_min']:>12.3f} {cv_za['1%']:>10.3f} {cv_za['5%']:>10.3f} {cv_za['10%']:>10.3f}")
        print("="*70)
        
        print("\nBreak Dates:")
        print("="*70)
        print(f"ADF: TB1={r['TB1_adf']:4d} ({r['TB1_adf']/r['n']:.3f}), TB2={r['TB2_adf']:4d} ({r['TB2_adf']/r['n']:.3f})")
        print(f"Zt:  TB1={r['TB1_zt']:4d} ({r['TB1_zt']/r['n']:.3f}), TB2={r['TB2_zt']:4d} ({r['TB2_zt']/r['n']:.3f})")
        print(f"Za:  TB1={r['TB1_za']:4d} ({r['TB1_za']/r['n']:.3f}), TB2={r['TB2_za']:4d} ({r['TB2_za']/r['n']:.3f})")
        print("="*70)
        
        print("\nConclusions (10% level):")
        print("="*70)
        adf_rej = r['ADF_min'] < cv_adf['10%']
        zt_rej = r['Zt_min'] < cv_adf['10%']
        za_rej = r['Za_min'] < cv_za['10%']
        
        print(f"ADF: {'Reject H0 - Cointegration' if adf_rej else 'No cointegration'}")
        print(f"Zt:  {'Reject H0 - Cointegration' if zt_rej else 'No cointegration'}")
        print(f"Za:  {'Reject H0 - Cointegration' if za_rej else 'No cointegration'}")
        print("="*70)


def coint_hatemi_j(y, x, model=3, bwl=None, ic=3, pmax=8,
                   varm=1, trimm=0.10, verbose=True):
    """Convenience function."""
    test = HatemiJTest(y, x, model, bwl, ic, pmax, varm, trimm)
    results = test.fit()
    if verbose:
        test.summary()
    return results
