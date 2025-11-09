"""
Métriques de risque et de performance

Implémente :
- Ratios de performance (Sharpe, Sortino, Calmar, Omega, etc.)
- Analyse de drawdown
- Mesures de risque (Beta, Alpha, Tracking Error, etc.)
- Statistiques de distribution
"""

import numpy as np
import pandas as pd
from typing import Union, Optional, Tuple, Dict
from scipy import stats
import warnings


class RiskMetrics:
    """Calculateur de métriques de risque"""
    
    @staticmethod
    def sharpe_ratio(
        returns: Union[np.ndarray, pd.Series],
        risk_free_rate: float = 0.0,
        periods_per_year: int = 252
    ) -> float:
        """
        Calcule le ratio de Sharpe annualisé
        
        Sharpe = (E[R] - Rf) / σ[R]
        
        Paramètres:
        -----------
        returns : array-like
            Rendements de la stratégie
        risk_free_rate : float
            Taux sans risque annualisé
        periods_per_year : int
            Nombre de périodes par an (252 pour jours, 12 pour mois, 52 pour semaines)
        
        Retourne:
        ---------
        float : Ratio de Sharpe annualisé
        """
        if isinstance(returns, pd.Series):
            returns = returns.values
        
        returns = returns[~np.isnan(returns)]
        
        if len(returns) == 0:
            return np.nan
        
        excess_returns = returns - risk_free_rate / periods_per_year
        
        if np.std(excess_returns, ddof=1) == 0:
            return 0.0
        
        sharpe = np.mean(excess_returns) / np.std(excess_returns, ddof=1)
        
        # Annualiser
        return sharpe * np.sqrt(periods_per_year)
    
    @staticmethod
    def sortino_ratio(
        returns: Union[np.ndarray, pd.Series],
        risk_free_rate: float = 0.0,
        target_return: Optional[float] = None,
        periods_per_year: int = 252
    ) -> float:
        """
        Calcule le ratio de Sortino (pénalise seulement la volatilité à la baisse)
        
        Sortino = (E[R] - Rf) / σ_downside
        
        Paramètres:
        -----------
        returns : array-like
            Rendements
        risk_free_rate : float
            Taux sans risque
        target_return : float, optional
            Rendement cible (défaut: risk_free_rate)
        periods_per_year : int
            Périodes par an
        
        Retourne:
        ---------
        float : Ratio de Sortino annualisé
        """
        if isinstance(returns, pd.Series):
            returns = returns.values
        
        returns = returns[~np.isnan(returns)]
        
        if target_return is None:
            target_return = risk_free_rate / periods_per_year
        else:
            target_return = target_return / periods_per_year
        
        excess_returns = returns - risk_free_rate / periods_per_year
        downside_returns = returns[returns < target_return] - target_return
        
        if len(downside_returns) == 0:
            return np.inf
        
        downside_std = np.sqrt(np.mean(downside_returns**2))
        
        if downside_std == 0:
            return np.inf
        
        sortino = np.mean(excess_returns) / downside_std
        
        return sortino * np.sqrt(periods_per_year)
    
    @staticmethod
    def calmar_ratio(
        returns: Union[np.ndarray, pd.Series],
        periods_per_year: int = 252
    ) -> float:
        """
        Calcule le ratio de Calmar
        
        Calmar = Rendement annualisé / |Drawdown maximum|
        
        Paramètres:
        -----------
        returns : array-like
            Rendements
        periods_per_year : int
            Périodes par an
        
        Retourne:
        ---------
        float : Ratio de Calmar
        """
        if isinstance(returns, pd.Series):
            returns_array = returns.values
        else:
            returns_array = returns
        
        returns_array = returns_array[~np.isnan(returns_array)]
        
        annual_return = np.mean(returns_array) * periods_per_year
        max_dd = RiskMetrics.max_drawdown(returns_array)
        
        if max_dd == 0:
            return np.inf
        
        return annual_return / abs(max_dd)
    
    @staticmethod
    def omega_ratio(
        returns: Union[np.ndarray, pd.Series],
        threshold: float = 0.0
    ) -> float:
        """
        Calcule le ratio Omega
        
        Omega = Somme(gains au-dessus du seuil) / Somme(pertes en-dessous du seuil)
        
        Paramètres:
        -----------
        returns : array-like
            Rendements
        threshold : float
            Seuil de rendement minimal acceptable
        
        Retourne:
        ---------
        float : Ratio Omega
        """
        if isinstance(returns, pd.Series):
            returns = returns.values
        
        returns = returns[~np.isnan(returns)]
        
        gains = returns[returns > threshold] - threshold
        losses = threshold - returns[returns < threshold]
        
        if len(losses) == 0 or np.sum(losses) == 0:
            return np.inf
        
        if len(gains) == 0:
            return 0.0
        
        return np.sum(gains) / np.sum(losses)
    
    @staticmethod
    def max_drawdown(returns: Union[np.ndarray, pd.Series]) -> float:
        """
        Calcule le drawdown maximum
        
        Paramètres:
        -----------
        returns : array-like
            Rendements
        
        Retourne:
        ---------
        float : Drawdown maximum (valeur négative)
        """
        if isinstance(returns, pd.Series):
            returns = returns.values
        
        returns = returns[~np.isnan(returns)]
        
        if len(returns) == 0:
            return 0.0
        
        cumulative = np.cumprod(1 + returns)
        running_max = np.maximum.accumulate(cumulative)
        drawdown = (cumulative - running_max) / running_max
        
        return np.min(drawdown)
    
    @staticmethod
    def drawdown_series(returns: Union[np.ndarray, pd.Series]) -> Union[np.ndarray, pd.Series]:
        """
        Calcule la série complète de drawdowns
        
        Paramètres:
        -----------
        returns : array-like
            Rendements
        
        Retourne:
        ---------
        array-like : Série de drawdowns
        """
        is_series = isinstance(returns, pd.Series)
        index = returns.index if is_series else None
        
        if is_series:
            returns_array = returns.values
        else:
            returns_array = returns
        
        returns_array = np.where(np.isnan(returns_array), 0, returns_array)
        
        cumulative = np.cumprod(1 + returns_array)
        running_max = np.maximum.accumulate(cumulative)
        drawdown = (cumulative - running_max) / running_max
        
        if is_series:
            return pd.Series(drawdown, index=index)
        return drawdown
    
    @staticmethod
    def max_drawdown_duration(returns: Union[np.ndarray, pd.Series]) -> int:
        """
        Calcule la durée maximale du drawdown (en nombre de périodes)
        
        Paramètres:
        -----------
        returns : array-like
            Rendements
        
        Retourne:
        ---------
        int : Durée maximale du drawdown
        """
        drawdowns = RiskMetrics.drawdown_series(returns)
        
        if isinstance(drawdowns, pd.Series):
            drawdowns = drawdowns.values
        
        is_dd = drawdowns < 0
        
        if not np.any(is_dd):
            return 0
        
        # Trouver les périodes de drawdown
        dd_periods = []
        current_duration = 0
        
        for dd in is_dd:
            if dd:
                current_duration += 1
            else:
                if current_duration > 0:
                    dd_periods.append(current_duration)
                current_duration = 0
        
        if current_duration > 0:
            dd_periods.append(current_duration)
        
        return max(dd_periods) if dd_periods else 0
    
    @staticmethod
    def information_ratio(
        returns: Union[np.ndarray, pd.Series],
        benchmark_returns: Union[np.ndarray, pd.Series],
        periods_per_year: int = 252
    ) -> float:
        """
        Calcule le ratio d'information
        
        IR = E[R - R_benchmark] / σ[R - R_benchmark]
        
        Paramètres:
        -----------
        returns : array-like
            Rendements du portefeuille
        benchmark_returns : array-like
            Rendements du benchmark
        periods_per_year : int
            Périodes par an
        
        Retourne:
        ---------
        float : Ratio d'information annualisé
        """
        if isinstance(returns, pd.Series):
            returns = returns.values
        if isinstance(benchmark_returns, pd.Series):
            benchmark_returns = benchmark_returns.values
        
        active_returns = returns - benchmark_returns
        active_returns = active_returns[~np.isnan(active_returns)]
        
        if len(active_returns) == 0:
            return np.nan
        
        tracking_error = np.std(active_returns, ddof=1)
        
        if tracking_error == 0:
            return 0.0
        
        ir = np.mean(active_returns) / tracking_error
        
        return ir * np.sqrt(periods_per_year)
    
    @staticmethod
    def beta(
        returns: Union[np.ndarray, pd.Series],
        market_returns: Union[np.ndarray, pd.Series]
    ) -> float:
        """
        Calcule le beta (sensibilité au marché)
        
        β = Cov(R, R_market) / Var(R_market)
        
        Paramètres:
        -----------
        returns : array-like
            Rendements de l'actif
        market_returns : array-like
            Rendements du marché
        
        Retourne:
        ---------
        float : Beta
        """
        if isinstance(returns, pd.Series):
            returns = returns.values
        if isinstance(market_returns, pd.Series):
            market_returns = market_returns.values
        
        # Aligner et nettoyer
        valid_idx = ~(np.isnan(returns) | np.isnan(market_returns))
        returns = returns[valid_idx]
        market_returns = market_returns[valid_idx]
        
        if len(returns) < 2:
            return np.nan
        
        covariance = np.cov(returns, market_returns)[0, 1]
        market_variance = np.var(market_returns, ddof=1)
        
        if market_variance == 0:
            return 0.0
        
        return covariance / market_variance
    
    @staticmethod
    def alpha(
        returns: Union[np.ndarray, pd.Series],
        market_returns: Union[np.ndarray, pd.Series],
        risk_free_rate: float = 0.0,
        periods_per_year: int = 252
    ) -> float:
        """
        Calcule l'alpha (Jensen's alpha) annualisé
        
        α = E[R] - (Rf + β * (E[R_market] - Rf))
        
        Paramètres:
        -----------
        returns : array-like
            Rendements de l'actif
        market_returns : array-like
            Rendements du marché
        risk_free_rate : float
            Taux sans risque annualisé
        periods_per_year : int
            Périodes par an
        
        Retourne:
        ---------
        float : Alpha annualisé
        """
        beta = RiskMetrics.beta(returns, market_returns)
        
        if isinstance(returns, pd.Series):
            returns = returns.values
        if isinstance(market_returns, pd.Series):
            market_returns = market_returns.values
        
        # Nettoyer
        valid_idx = ~(np.isnan(returns) | np.isnan(market_returns))
        returns = returns[valid_idx]
        market_returns = market_returns[valid_idx]
        
        rf_per_period = risk_free_rate / periods_per_year
        
        avg_return = np.mean(returns)
        avg_market_return = np.mean(market_returns)
        
        # Alpha par période
        alpha_per_period = avg_return - (rf_per_period + beta * (avg_market_return - rf_per_period))
        
        # Annualiser
        return alpha_per_period * periods_per_year
    
    @staticmethod
    def tracking_error(
        returns: Union[np.ndarray, pd.Series],
        benchmark_returns: Union[np.ndarray, pd.Series],
        periods_per_year: int = 252
    ) -> float:
        """
        Calcule la tracking error annualisée
        
        TE = σ[R - R_benchmark]
        
        Paramètres:
        -----------
        returns : array-like
            Rendements du portefeuille
        benchmark_returns : array-like
            Rendements du benchmark
        periods_per_year : int
            Périodes par an
        
        Retourne:
        ---------
        float : Tracking error annualisée
        """
        if isinstance(returns, pd.Series):
            returns = returns.values
        if isinstance(benchmark_returns, pd.Series):
            benchmark_returns = benchmark_returns.values
        
        active_returns = returns - benchmark_returns
        active_returns = active_returns[~np.isnan(active_returns)]
        
        te = np.std(active_returns, ddof=1) * np.sqrt(periods_per_year)
        
        return te
    
    @staticmethod
    def downside_deviation(
        returns: Union[np.ndarray, pd.Series],
        target_return: float = 0.0,
        periods_per_year: int = 252
    ) -> float:
        """
        Calcule la déviation à la baisse (downside deviation)
        
        Paramètres:
        -----------
        returns : array-like
            Rendements
        target_return : float
            Rendement cible
        periods_per_year : int
            Périodes par an
        
        Retourne:
        ---------
        float : Downside deviation annualisée
        """
        if isinstance(returns, pd.Series):
            returns = returns.values
        
        returns = returns[~np.isnan(returns)]
        
        downside_returns = returns[returns < target_return] - target_return
        
        if len(downside_returns) == 0:
            return 0.0
        
        downside_dev = np.sqrt(np.mean(downside_returns**2))
        
        return downside_dev * np.sqrt(periods_per_year)
    
    @staticmethod
    def value_at_risk_ratio(
        returns: Union[np.ndarray, pd.Series],
        confidence_level: float = 0.95
    ) -> float:
        """
        Ratio rendement moyen / VaR
        
        Paramètres:
        -----------
        returns : array-like
            Rendements
        confidence_level : float
            Niveau de confiance pour la VaR
        
        Retourne:
        ---------
        float : Ratio VaR
        """
        from quantfinance.risk.var import VaRCalculator
        
        avg_return = np.mean(returns)
        var = VaRCalculator.historical_var(returns, confidence_level)
        
        if var == 0:
            return np.inf
        
        return avg_return / var
    
    @staticmethod
    def skewness(returns: Union[np.ndarray, pd.Series]) -> float:
        """
        Calcule l'asymétrie (skewness) de la distribution
        
        Paramètres:
        -----------
        returns : array-like
            Rendements
        
        Retourne:
        ---------
        float : Skewness (>0 = asymétrie positive, <0 = négative)
        """
        if isinstance(returns, pd.Series):
            returns = returns.values
        
        returns = returns[~np.isnan(returns)]
        
        return stats.skew(returns)
    
    @staticmethod
    def kurtosis(returns: Union[np.ndarray, pd.Series], excess: bool = True) -> float:
        """
        Calcule le kurtosis (aplatissement) de la distribution
        
        Paramètres:
        -----------
        returns : array-like
            Rendements
        excess : bool
            Si True, retourne l'excess kurtosis (Kurt - 3)
        
        Retourne:
        ---------
        float : Kurtosis
        """
        if isinstance(returns, pd.Series):
            returns = returns.values
        
        returns = returns[~np.isnan(returns)]
        
        return stats.kurtosis(returns, fisher=excess)
    
    @staticmethod
    def var_ratio(returns: Union[np.ndarray, pd.Series], q: int = 2) -> float:
        """
        Calcule le variance ratio pour tester la random walk hypothesis
        
        VR(q) = Var(R_t + ... + R_{t+q-1}) / (q * Var(R_t))
        
        Paramètres:
        -----------
        returns : array-like
            Rendements
        q : int
            Période d'agrégation
        
        Retourne:
        ---------
        float : Variance ratio
        """
        if isinstance(returns, pd.Series):
            returns = returns.values
        
        returns = returns[~np.isnan(returns)]
        
        n = len(returns)
        
        # Variance des rendements individuels
        var_1 = np.var(returns, ddof=1)
        
        # Variance des rendements sur q périodes
        returns_q = np.array([returns[i:i+q].sum() for i in range(n-q+1)])
        var_q = np.var(returns_q, ddof=1)
        
        if var_1 == 0:
            return np.nan
        
        return var_q / (q * var_1)


class PerformanceAnalyzer:
    """Analyse complète de performance d'un portefeuille"""
    
    def __init__(
        self,
        returns: pd.Series,
        benchmark_returns: Optional[pd.Series] = None,
        risk_free_rate: float = 0.0,
        periods_per_year: int = 252
    ):
        """
        Paramètres:
        -----------
        returns : Series
            Rendements du portefeuille (avec index temporel)
        benchmark_returns : Series, optional
            Rendements du benchmark
        risk_free_rate : float
            Taux sans risque annualisé
        periods_per_year : int
            Périodes par an
        """
        self.returns = returns
        self.benchmark_returns = benchmark_returns
        self.risk_free_rate = risk_free_rate
        self.periods_per_year = periods_per_year
    
    def summary_statistics(self) -> pd.DataFrame:
        """
        Génère un résumé complet des statistiques
        
        Retourne:
        ---------
        DataFrame : Résumé des statistiques
        """
        stats_dict = {}
        
        # Rendements
        stats_dict['Total Return'] = (1 + self.returns).prod() - 1
        stats_dict['Annual Return'] = self.returns.mean() * self.periods_per_year
        stats_dict['Annual Volatility'] = self.returns.std() * np.sqrt(self.periods_per_year)
        
        # Ratios de performance
        stats_dict['Sharpe Ratio'] = RiskMetrics.sharpe_ratio(
            self.returns, self.risk_free_rate, self.periods_per_year
        )
        stats_dict['Sortino Ratio'] = RiskMetrics.sortino_ratio(
            self.returns, self.risk_free_rate, periods_per_year=self.periods_per_year
        )
        stats_dict['Calmar Ratio'] = RiskMetrics.calmar_ratio(
            self.returns, self.periods_per_year
        )
        
        # Risque
        stats_dict['Max Drawdown'] = RiskMetrics.max_drawdown(self.returns)
        stats_dict['Max DD Duration'] = RiskMetrics.max_drawdown_duration(self.returns)
        
        # Distribution
        stats_dict['Skewness'] = RiskMetrics.skewness(self.returns)
        stats_dict['Kurtosis'] = RiskMetrics.kurtosis(self.returns)
        
        # VaR
        from quantfinance.risk.var import VaRCalculator
        stats_dict['VaR 95%'] = VaRCalculator.historical_var(self.returns, 0.95)
        stats_dict['CVaR 95%'] = VaRCalculator.expected_shortfall(self.returns, 0.95)
        
        # Statistiques vs benchmark
        if self.benchmark_returns is not None:
            stats_dict['Beta'] = RiskMetrics.beta(self.returns, self.benchmark_returns)
            stats_dict['Alpha'] = RiskMetrics.alpha(
                self.returns, self.benchmark_returns,
                self.risk_free_rate, self.periods_per_year
            )
            stats_dict['Information Ratio'] = RiskMetrics.information_ratio(
                self.returns, self.benchmark_returns, self.periods_per_year
            )
            stats_dict['Tracking Error'] = RiskMetrics.tracking_error(
                self.returns, self.benchmark_returns, self.periods_per_year
            )
        
        # Autres
        stats_dict['Best Period'] = self.returns.max()
        stats_dict['Worst Period'] = self.returns.min()
        stats_dict['Win Rate'] = (self.returns > 0).sum() / len(self.returns)
        stats_dict['Avg Win'] = self.returns[self.returns > 0].mean()
        stats_dict['Avg Loss'] = self.returns[self.returns < 0].mean()
        
        return pd.DataFrame(stats_dict, index=['Value']).T
    
    def rolling_statistics(
        self,
        window: int = 252,
        statistics: list = None
    ) -> pd.DataFrame:
        """
        Calcule des statistiques roulantes
        
        Paramètres:
        -----------
        window : int
            Taille de la fenêtre
        statistics : list, optional
            Liste des statistiques à calculer
        
        Retourne:
        ---------
        DataFrame : Statistiques roulantes
        """
        if statistics is None:
            statistics = ['sharpe', 'volatility', 'max_dd']
        
        results = {}
        
        for stat in statistics:
            if stat == 'sharpe':
                results['Sharpe'] = self.returns.rolling(window).apply(
                    lambda x: RiskMetrics.sharpe_ratio(x, self.risk_free_rate, self.periods_per_year),
                    raw=True
                )
            elif stat == 'volatility':
                results['Volatility'] = self.returns.rolling(window).std() * np.sqrt(self.periods_per_year)
            elif stat == 'max_dd':
                results['Max DD'] = self.returns.rolling(window).apply(
                    lambda x: RiskMetrics.max_drawdown(x),
                    raw=True
                )
        
        return pd.DataFrame(results, index=self.returns.index)
    
    def monthly_returns_table(self) -> pd.DataFrame:
        """
        Génère une table des rendements mensuels
        
        Retourne:
        ---------
        DataFrame : Table des rendements mensuels (lignes=années, colonnes=mois)
        """
        if not isinstance(self.returns.index, pd.DatetimeIndex):
            raise ValueError("L'index doit être de type DatetimeIndex")
        
        monthly_returns = self.returns.resample('ME').apply(lambda x: (1 + x).prod() - 1)
        
        # Créer la table pivot
        table = pd.DataFrame(index=monthly_returns.index.year.unique())
        
        for month in range(1, 13):
            month_name = pd.Timestamp(2000, month, 1).strftime('%b')
            table[month_name] = np.nan
        
        for date, ret in monthly_returns.items():
            table.loc[date.year, date.strftime('%b')] = ret
        
        # Ajouter la colonne année
        table['Year'] = table.mean(axis=1)
        
        return table
    
    def plot_performance(self):
        """Trace les graphiques de performance"""
        import matplotlib.pyplot as plt
        
        fig, axes = plt.subplots(2, 2, figsize=(15, 10))
        
        # Courbe de performance cumulée
        cumulative = (1 + self.returns).cumprod()
        axes[0, 0].plot(cumulative.index, cumulative.values, linewidth=2)
        if self.benchmark_returns is not None:
            bench_cumulative = (1 + self.benchmark_returns).cumprod()
            axes[0, 0].plot(bench_cumulative.index, bench_cumulative.values,
                          linewidth=2, alpha=0.7, label='Benchmark')
        axes[0, 0].set_title('Cumulative Returns', fontweight='bold')
        axes[0, 0].set_ylabel('Growth of $1')
        axes[0, 0].legend()
        axes[0, 0].grid(True, alpha=0.3)
        
        # Drawdown
        dd = RiskMetrics.drawdown_series(self.returns)
        axes[0, 1].fill_between(dd.index, dd.values, 0, alpha=0.5, color='red')
        axes[0, 1].set_title('Drawdown', fontweight='bold')
        axes[0, 1].set_ylabel('Drawdown')
        axes[0, 1].grid(True, alpha=0.3)
        
        # Distribution des rendements
        axes[1, 0].hist(self.returns.dropna(), bins=50, alpha=0.7, edgecolor='black')
        axes[1, 0].axvline(self.returns.mean(), color='red', linestyle='--',
                          linewidth=2, label=f'Mean: {self.returns.mean():.4f}')
        axes[1, 0].set_title('Returns Distribution', fontweight='bold')
        axes[1, 0].set_xlabel('Return')
        axes[1, 0].set_ylabel('Frequency')
        axes[1, 0].legend()
        axes[1, 0].grid(True, alpha=0.3)
        
        # Volatilité roulante
        rolling_vol = self.returns.rolling(63).std() * np.sqrt(self.periods_per_year)
        axes[1, 1].plot(rolling_vol.index, rolling_vol.values, linewidth=2)
        axes[1, 1].set_title('Rolling Volatility (3M)', fontweight='bold')
        axes[1, 1].set_ylabel('Annualized Volatility')
        axes[1, 1].grid(True, alpha=0.3)
        
        plt.tight_layout()
        
        return fig



