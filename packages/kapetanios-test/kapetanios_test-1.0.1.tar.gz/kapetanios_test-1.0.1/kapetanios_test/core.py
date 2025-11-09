"""
Kapetanios Unit Root Test Implementation
Based on: Kapetanios, G. (2005). Unit-root testing against the alternative 
hypothesis of up to m structural breaks. Journal of Time Series Analysis, 
26(1), 123-133.

Author: Dr. Merwan Roudane
Email: merwanroudane920@gmail.com
"""

import numpy as np
import pandas as pd
from typing import Union, Tuple, Optional, Dict, List
from dataclasses import dataclass
from scipy import stats
import warnings


@dataclass
class KapetaniosResult:
    """
    Results from Kapetanios unit root test.
    
    Attributes
    ----------
    statistic : float
        The test statistic (minimum t-statistic).
    pvalue : float
        The approximate p-value.
    critical_values : dict
        Critical values at 1%, 5%, and 10% significance levels.
    break_dates : list
        Estimated break dates (indices).
    n_breaks : int
        Number of breaks detected.
    model_type : str
        Type of model ('A', 'B', or 'C').
    lags : int
        Number of lags used.
    reject_null : bool
        Whether to reject the null hypothesis at 5% level.
    """
    statistic: float
    pvalue: Optional[float]
    critical_values: Dict[str, float]
    break_dates: List[int]
    n_breaks: int
    model_type: str
    lags: int
    reject_null: bool
    
    def __repr__(self) -> str:
        return (
            f"Kapetanios Unit Root Test Results\n"
            f"{'=' * 50}\n"
            f"Test Statistic: {self.statistic:.4f}\n"
            f"P-value: {self.pvalue if self.pvalue else 'N/A'}\n"
            f"Number of Breaks: {self.n_breaks}\n"
            f"Break Dates (indices): {self.break_dates}\n"
            f"Model Type: {self.model_type}\n"
            f"Lags: {self.lags}\n"
            f"\nCritical Values:\n"
            f"  1%:  {self.critical_values['1%']:.4f}\n"
            f"  5%:  {self.critical_values['5%']:.4f}\n"
            f"  10%: {self.critical_values['10%']:.4f}\n"
            f"\nDecision: {'Reject H0' if self.reject_null else 'Fail to reject H0'} at 5% level\n"
            f"(H0: Unit root with drift, H1: Stationary with up to {self.n_breaks} breaks)"
        )


class KapetaniosTest:
    """
    Kapetanios (2005) unit root test with up to m structural breaks.
    
    This test allows for up to m structural breaks in the intercept and/or trend
    under the alternative hypothesis of stationarity. Break dates are estimated
    endogenously using a sequential procedure.
    
    Parameters
    ----------
    max_breaks : int, default=5
        Maximum number of breaks to test for (1 to 5).
    model : str, default='C'
        Type of model:
        - 'A': breaks in intercept only
        - 'B': breaks in trend only
        - 'C': breaks in both intercept and trend
    trimming : float, default=0.15
        Trimming parameter (proportion of sample size).
    max_lags : int, optional
        Maximum number of lags to consider. If None, uses int(12*(T/100)^(1/4)).
    lag_selection : str, default='aic'
        Method for lag selection: 'aic', 'bic', or 't-stat'.
    
    References
    ----------
    Kapetanios, G. (2005). Unit-root testing against the alternative hypothesis
    of up to m structural breaks. Journal of Time Series Analysis, 26(1), 123-133.
    """
    
    # Critical values from Table I in Kapetanios (2005)
    CRITICAL_VALUES = {
        'A': {
            1: {0.10: -4.661, 0.05: -4.930, 0.025: -5.173, 0.01: -5.338},
            2: {0.10: -5.467, 0.05: -5.685, 0.025: -5.965, 0.01: -6.162},
            3: {0.10: -6.265, 0.05: -6.529, 0.025: -6.757, 0.01: -6.991},
            4: {0.10: -6.832, 0.05: -7.104, 0.025: -7.361, 0.01: -7.560},
            5: {0.10: -7.398, 0.05: -7.636, 0.025: -7.963, 0.01: -8.248},
        },
        'B': {
            1: {0.10: -4.144, 0.05: -4.495, 0.025: -4.696, 0.01: -5.014},
            2: {0.10: -4.784, 0.05: -5.096, 0.025: -5.333, 0.01: -5.616},
            3: {0.10: -5.429, 0.05: -5.726, 0.025: -6.010, 0.01: -6.286},
            4: {0.10: -5.999, 0.05: -6.305, 0.025: -6.497, 0.01: -6.856},
            5: {0.10: -6.417, 0.05: -6.717, 0.025: -6.998, 0.01: -7.395},
        },
        'C': {
            1: {0.10: -4.820, 0.05: -5.081, 0.025: -5.297, 0.01: -5.704},
            2: {0.10: -5.847, 0.05: -6.113, 0.025: -6.344, 0.01: -6.587},
            3: {0.10: -6.686, 0.05: -7.006, 0.025: -7.216, 0.01: -7.401},
            4: {0.10: -7.426, 0.05: -7.736, 0.025: -7.998, 0.01: -8.243},
            5: {0.10: -8.016, 0.05: -8.343, 0.025: -8.593, 0.01: -9.039},
        }
    }
    
    def __init__(
        self,
        max_breaks: int = 5,
        model: str = 'C',
        trimming: float = 0.15,
        max_lags: Optional[int] = None,
        lag_selection: str = 'aic'
    ):
        if max_breaks < 1 or max_breaks > 5:
            raise ValueError("max_breaks must be between 1 and 5")
        if model not in ['A', 'B', 'C']:
            raise ValueError("model must be 'A', 'B', or 'C'")
        if trimming <= 0 or trimming >= 0.5:
            raise ValueError("trimming must be between 0 and 0.5")
        if lag_selection not in ['aic', 'bic', 't-stat']:
            raise ValueError("lag_selection must be 'aic', 'bic', or 't-stat'")
            
        self.max_breaks = max_breaks
        self.model = model
        self.trimming = trimming
        self.max_lags = max_lags
        self.lag_selection = lag_selection
    
    def fit(self, y: Union[np.ndarray, pd.Series]) -> KapetaniosResult:
        """
        Perform the Kapetanios unit root test.
        
        Parameters
        ----------
        y : array-like
            Time series data to test.
            
        Returns
        -------
        KapetaniosResult
            Test results including statistic, critical values, and break dates.
        """
        # Convert to numpy array
        if isinstance(y, pd.Series):
            y = y.values
        y = np.asarray(y).flatten()
        
        if len(y) < 20:
            raise ValueError("Time series too short (minimum 20 observations)")
        
        T = len(y)
        
        # Determine maximum lags if not specified
        if self.max_lags is None:
            k_max = int(12 * (T / 100) ** 0.25)
        else:
            k_max = self.max_lags
        
        # Adjust max_breaks if necessary given trimming and sample size
        min_segment = int(T * self.trimming)
        max_feasible_breaks = (T - 2 * min_segment) // min_segment
        actual_max_breaks = min(self.max_breaks, max_feasible_breaks)
        
        if actual_max_breaks < self.max_breaks:
            warnings.warn(
                f"Reduced max_breaks from {self.max_breaks} to {actual_max_breaks} "
                f"due to trimming constraints"
            )
        
        # Sequential search for breaks
        all_t_stats = []
        all_break_dates = []
        
        for m in range(1, actual_max_breaks + 1):
            t_stats_m, break_dates_m = self._search_breaks(y, m, k_max)
            all_t_stats.extend(t_stats_m)
            all_break_dates.extend(break_dates_m)
        
        # Find minimum t-statistic
        min_idx = np.argmin(all_t_stats)
        min_t_stat = all_t_stats[min_idx]
        optimal_breaks = all_break_dates[min_idx]
        
        # Get critical values
        critical_vals = {
            '1%': self.CRITICAL_VALUES[self.model][actual_max_breaks][0.01],
            '5%': self.CRITICAL_VALUES[self.model][actual_max_breaks][0.05],
            '10%': self.CRITICAL_VALUES[self.model][actual_max_breaks][0.10],
        }
        
        # Determine rejection
        reject = min_t_stat < critical_vals['5%']
        
        # Approximate p-value
        pval = self._approximate_pvalue(min_t_stat, actual_max_breaks)
        
        return KapetaniosResult(
            statistic=min_t_stat,
            pvalue=pval,
            critical_values=critical_vals,
            break_dates=sorted(optimal_breaks),
            n_breaks=len(optimal_breaks),
            model_type=self.model,
            lags=self._select_lags(y, optimal_breaks, k_max),
            reject_null=reject
        )
    
    def _search_breaks(
        self, 
        y: np.ndarray, 
        m: int, 
        k_max: int
    ) -> Tuple[List[float], List[List[int]]]:
        """
        Sequential search for m breaks.
        
        Following Bai & Perron (1998) sequential procedure.
        """
        T = len(y)
        min_segment = int(T * self.trimming)
        
        t_stats = []
        break_configs = []
        
        # Start with empty break set
        current_breaks = []
        
        for i in range(m):
            # Search for next break
            best_ssr = np.inf
            best_break = None
            best_t_stat = 0
            
            # Define search regions based on existing breaks
            if len(current_breaks) == 0:
                search_regions = [(min_segment, T - min_segment)]
            else:
                search_regions = []
                sorted_breaks = sorted(current_breaks)
                
                # Region before first break
                if sorted_breaks[0] - min_segment > min_segment:
                    search_regions.append((min_segment, sorted_breaks[0] - min_segment))
                
                # Regions between breaks
                for j in range(len(sorted_breaks) - 1):
                    start = sorted_breaks[j] + min_segment
                    end = sorted_breaks[j + 1] - min_segment
                    if end - start > min_segment:
                        search_regions.append((start, end))
                
                # Region after last break
                if T - sorted_breaks[-1] - min_segment > min_segment:
                    search_regions.append((sorted_breaks[-1] + min_segment, T - min_segment))
            
            # Search all regions
            for start, end in search_regions:
                for tb in range(start, end):
                    # Estimate model with this break configuration
                    test_breaks = current_breaks + [tb]
                    
                    # First select optimal lags for this break configuration
                    k_opt = self._select_lags(y, test_breaks, k_max)
                    
                    # Then estimate model with selected lags
                    ssr, t_stat, _ = self._estimate_model(y, test_breaks, k_opt)
                    
                    t_stats.append(t_stat)
                    break_configs.append(test_breaks.copy())
                    
                    if ssr < best_ssr:
                        best_ssr = ssr
                        best_break = tb
                        best_t_stat = t_stat
            
            if best_break is not None:
                current_breaks.append(best_break)
        
        return t_stats, break_configs
    
    def _estimate_model(
        self, 
        y: np.ndarray, 
        break_dates: List[int], 
        k: int
    ) -> Tuple[float, float, int]:
        """
        Estimate augmented Dickey-Fuller model with breaks.
        
        Model: Δy_t = μ_0 + μ_1*t + α*y_{t-1} + Σc_i*Δy_{t-i} + 
                      Σφ_i*DU_{i,t} + Σψ_i*DT_{i,t} + ε_t
        """
        T = len(y)
        
        # Use provided lag length
        k_opt = k
        
        # Construct regressors
        dy = np.diff(y)
        y_lag = y[:-1]
        t_trend = np.arange(1, T)
        
        # Start building X matrix
        X = np.column_stack([np.ones(T - 1), t_trend, y_lag])
        
        # Add break dummies
        for tb in break_dates:
            if self.model in ['A', 'C']:  # Intercept break
                du = np.zeros(T - 1)
                du[tb:] = 1
                X = np.column_stack([X, du])
            
            if self.model in ['B', 'C']:  # Trend break
                dt = np.zeros(T - 1)
                dt[tb:] = np.arange(0, T - 1 - tb)
                X = np.column_stack([X, dt])
        
        # Add lagged differences
        if k_opt > 0:
            # Need to drop first k_opt observations due to lags
            # Create lagged difference matrix
            dy_lags = []
            for i in range(1, k_opt + 1):
                dy_lag_i = dy[k_opt - i: -i] if i < k_opt else dy[:-i] if i > 0 else dy
                dy_lags.append(dy_lag_i)
            
            # Stack all lags horizontally
            dy_lags = np.column_stack(dy_lags)
            
            # Adjust all matrices to have consistent length
            # Remove first k_opt observations from X and dy
            X = X[k_opt:]
            dy_adj = dy[k_opt:]
            X = np.column_stack([X, dy_lags])
        else:
            dy_adj = dy
        
        # Final check for dimension consistency
        min_len = min(len(X), len(dy_adj))
        X = X[:min_len]
        dy_adj = dy_adj[:min_len]
        
        # OLS estimation
        try:
            beta = np.linalg.lstsq(X, dy_adj, rcond=None)[0]
            resid = dy_adj - X @ beta
            ssr = np.sum(resid ** 2)
            
            # Calculate t-statistic for α (coefficient on y_{t-1})
            # α is the 3rd coefficient (index 2)
            sigma2 = ssr / (len(dy_adj) - X.shape[1])
            var_beta = sigma2 * np.linalg.inv(X.T @ X)
            se_alpha = np.sqrt(var_beta[2, 2])
            t_stat = beta[2] / se_alpha
            
        except np.linalg.LinAlgError:
            # Singular matrix - return large SSR and t-stat
            ssr = np.inf
            t_stat = 0
        
        return ssr, t_stat, k_opt
    
    def _select_lags(
        self, 
        y: np.ndarray, 
        break_dates: List[int], 
        k_max: int
    ) -> int:
        """
        Select optimal number of lags using specified criterion.
        """
        if k_max == 0:
            return 0
        
        T = len(y)
        dy = np.diff(y)
        
        if self.lag_selection == 't-stat':
            # Perron's backward sequential t-statistic method
            # Start from k_max and work backwards
            for k in range(k_max, 0, -1):
                # Directly estimate model with k lags to get SSR
                ssr, _, _ = self._estimate_model(y, break_dates, k)
                
                # Now we need t-stat of last lag coefficient
                # Rebuild X matrix to extract it
                dy = np.diff(y)
                y_lag = y[:-1]
                t_trend = np.arange(1, T)
                X = np.column_stack([np.ones(T - 1), t_trend, y_lag])
                
                # Add break dummies
                for tb in break_dates:
                    if self.model in ['A', 'C']:
                        du = np.zeros(T - 1)
                        du[tb:] = 1
                        X = np.column_stack([X, du])
                    if self.model in ['B', 'C']:
                        dt = np.zeros(T - 1)
                        dt[tb:] = np.arange(0, T - 1 - tb)
                        X = np.column_stack([X, dt])
                
                # Add lagged differences
                if k > 0:
                    dy_lags = []
                    for i in range(1, k + 1):
                        dy_lag_i = dy[k - i: -i] if i < k else dy[:-i] if i > 0 else dy
                        dy_lags.append(dy_lag_i)
                    
                    dy_lags = np.column_stack(dy_lags)
                    X = X[k:]
                    dy_adj = dy[k:]
                    X = np.column_stack([X, dy_lags])
                else:
                    dy_adj = dy
                
                # Ensure consistent dimensions
                min_len = min(len(X), len(dy_adj))
                X = X[:min_len]
                dy_adj = dy_adj[:min_len]
                
                try:
                    beta = np.linalg.lstsq(X, dy_adj, rcond=None)[0]
                    resid = dy_adj - X @ beta
                    ssr_calc = np.sum(resid ** 2)
                    sigma2 = ssr_calc / (len(dy_adj) - X.shape[1])
                    var_beta = sigma2 * np.linalg.inv(X.T @ X)
                    
                    # t-stat of last lag coefficient (last column in X)
                    last_coef_idx = X.shape[1] - 1
                    se_last = np.sqrt(var_beta[last_coef_idx, last_coef_idx])
                    t_stat_last = beta[last_coef_idx] / se_last
                    
                    if abs(t_stat_last) > 1.96:  # 5% critical value
                        return k
                except np.linalg.LinAlgError:
                    continue
                    
            return 0
        
        else:
            # Information criteria (AIC or BIC)
            best_ic = np.inf
            best_k = 0
            
            for k in range(0, k_max + 1):
                ssr, _, _ = self._estimate_model(y, break_dates, k)
                n_params = 3 + 2 * len(break_dates) + k
                
                if self.lag_selection == 'aic':
                    ic = np.log(ssr / T) + 2 * n_params / T
                else:  # bic
                    ic = np.log(ssr / T) + n_params * np.log(T) / T
                
                if ic < best_ic:
                    best_ic = ic
                    best_k = k
            
            return best_k
    
    def _approximate_pvalue(self, t_stat: float, m: int) -> Optional[float]:
        """
        Approximate p-value using critical values.
        """
        cv = self.CRITICAL_VALUES[self.model][m]
        
        if t_stat > cv[0.10]:
            return 1.0 - 0.10 * (t_stat - cv[0.10]) / (0 - cv[0.10])
        elif t_stat > cv[0.05]:
            return 0.10 - 0.05 * (t_stat - cv[0.05]) / (cv[0.10] - cv[0.05])
        elif t_stat > cv[0.01]:
            return 0.05 - 0.04 * (t_stat - cv[0.01]) / (cv[0.05] - cv[0.01])
        else:
            return 0.01 * np.exp((t_stat - cv[0.01]) / abs(cv[0.01]))


def kapetanios_test(
    y: Union[np.ndarray, pd.Series],
    max_breaks: int = 5,
    model: str = 'C',
    trimming: float = 0.15,
    max_lags: Optional[int] = None,
    lag_selection: str = 'aic'
) -> KapetaniosResult:
    """
    Convenience function for Kapetanios unit root test.
    
    Parameters
    ----------
    y : array-like
        Time series data to test.
    max_breaks : int, default=5
        Maximum number of breaks (1-5).
    model : str, default='C'
        Model type: 'A' (intercept), 'B' (trend), or 'C' (both).
    trimming : float, default=0.15
        Trimming parameter.
    max_lags : int, optional
        Maximum lags to consider.
    lag_selection : str, default='aic'
        Lag selection method: 'aic', 'bic', or 't-stat'.
        
    Returns
    -------
    KapetaniosResult
        Test results.
        
    Examples
    --------
    >>> import numpy as np
    >>> from kapetanios_test import kapetanios_test
    >>> 
    >>> # Generate random walk with break
    >>> np.random.seed(42)
    >>> y = np.cumsum(np.random.randn(100))
    >>> y[50:] += 5  # Add level break
    >>> 
    >>> # Test for unit root
    >>> result = kapetanios_test(y, max_breaks=2, model='A')
    >>> print(result)
    """
    test = KapetaniosTest(
        max_breaks=max_breaks,
        model=model,
        trimming=trimming,
        max_lags=max_lags,
        lag_selection=lag_selection
    )
    return test.fit(y)
