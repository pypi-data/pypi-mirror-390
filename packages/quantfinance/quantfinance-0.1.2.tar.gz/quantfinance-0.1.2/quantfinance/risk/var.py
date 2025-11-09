"""
Calcul de Value at Risk (VaR) et Expected Shortfall (CVaR)

Méthodes implémentées :
- VaR historique
- VaR paramétrique (normale, Student-t)
- VaR avec EWMA (Exponentially Weighted Moving Average)
- VaR Monte Carlo
- Expected Shortfall (CVaR)
- VaR de portefeuille
- VaR componentielle
"""

import numpy as np
import pandas as pd
from scipy.stats import norm, t as student_t
from scipy.optimize import minimize
from typing import Union, Literal, Optional, Dict, Tuple
import warnings


class VaRCalculator:
    """Calculateur de Value at Risk"""
    
    @staticmethod
    def historical_var(
        returns: Union[np.ndarray, pd.Series],
        confidence_level: float = 0.95
    ) -> float:
        """
        Calcule la VaR historique (non-paramétrique)
        
        Paramètres:
        -----------
        returns : array-like
            Série de rendements historiques
        confidence_level : float
            Niveau de confiance (ex: 0.95 pour 95%)
        
        Retourne:
        ---------
        float : VaR (valeur positive représentant une perte)
        """
        if isinstance(returns, pd.Series):
            returns = returns.values
        
        # Éliminer les NaN
        returns = returns[~np.isnan(returns)]
        
        if len(returns) == 0:
            raise ValueError("Pas de données valides dans returns")
        
        # VaR = négatif du percentile
        var = -np.percentile(returns, (1 - confidence_level) * 100)
        
        return var
    
    @staticmethod
    def parametric_var(
        returns: Union[np.ndarray, pd.Series],
        confidence_level: float = 0.95,
        distribution: Literal['normal', 'student'] = 'normal',
        df: Optional[int] = None
    ) -> float:
        """
        Calcule la VaR paramétrique
        
        Paramètres:
        -----------
        returns : array-like
            Série de rendements
        confidence_level : float
            Niveau de confiance
        distribution : str
            Distribution assumée ('normal' ou 'student')
        df : int, optional
            Degrés de liberté pour Student-t (défaut: estimé des données)
        
        Retourne:
        ---------
        float : VaR paramétrique
        """
        if isinstance(returns, pd.Series):
            returns = returns.values
        
        returns = returns[~np.isnan(returns)]
        
        mu = np.mean(returns)
        sigma = np.std(returns, ddof=1)
        
        if distribution == 'normal':
            z_score = norm.ppf(1 - confidence_level)
            var = -(mu + sigma * z_score)
        
        elif distribution == 'student':
            if df is None:
                # Estimer les degrés de liberté
                from scipy.stats import kurtosis
                kurt = kurtosis(returns, fisher=False)
                if kurt > 3:
                    df = 4 + (6 / (kurt - 3))
                else:
                    df = 10
            
            df = max(df, 2.1)  # Éviter df trop petit
            t_score = student_t.ppf(1 - confidence_level, df)
            var = -(mu + sigma * t_score)
        
        else:
            raise ValueError("distribution doit être 'normal' ou 'student'")
        
        return var
    
    @staticmethod
    def ewma_var(
        returns: Union[np.ndarray, pd.Series],
        confidence_level: float = 0.95,
        lambda_param: float = 0.94
    ) -> float:
        """
        VaR avec volatilité EWMA (RiskMetrics)
        
        Paramètres:
        -----------
        returns : array-like
            Série de rendements
        confidence_level : float
            Niveau de confiance
        lambda_param : float
            Paramètre de décroissance (typiquement 0.94 pour données quotidiennes)
        
        Retourne:
        ---------
        float : VaR EWMA
        """
        if isinstance(returns, pd.Series):
            returns = returns.values
        
        returns = returns[~np.isnan(returns)]
        
        # Calculer la variance EWMA
        n = len(returns)
        weights = np.array([lambda_param**i for i in range(n)])[::-1]
        weights = weights / weights.sum()
        
        # Variance EWMA
        squared_returns = returns**2
        ewma_variance = np.sum(weights * squared_returns)
        ewma_vol = np.sqrt(ewma_variance)
        
        # VaR avec moyenne des rendements récents
        mu = np.mean(returns[-min(30, n):])  # Moyenne sur 30 derniers jours
        
        z_score = norm.ppf(1 - confidence_level)
        var = -(mu + ewma_vol * z_score)
        
        return var
    
    @staticmethod
    def monte_carlo_var(
        returns: Union[np.ndarray, pd.Series],
        confidence_level: float = 0.95,
        n_simulations: int = 10000,
        horizon: int = 1,
        method: Literal['bootstrap', 'parametric'] = 'parametric',
        random_seed: Optional[int] = None
    ) -> float:
        """
        VaR par simulation Monte Carlo
        
        Paramètres:
        -----------
        returns : array-like
            Rendements historiques
        confidence_level : float
            Niveau de confiance
        n_simulations : int
            Nombre de simulations
        horizon : int
            Horizon temporel (en périodes)
        method : str
            'bootstrap' (resampling) ou 'parametric' (normale)
        random_seed : int, optional
            Graine aléatoire
        
        Retourne:
        ---------
        float : VaR Monte Carlo
        """
        if random_seed is not None:
            np.random.seed(random_seed)
        
        if isinstance(returns, pd.Series):
            returns = returns.values
        
        returns = returns[~np.isnan(returns)]
        
        if method == 'bootstrap':
            # Resampling bootstrap
            simulated_returns = np.random.choice(returns, size=(n_simulations, horizon))
            horizon_returns = np.sum(simulated_returns, axis=1)
        
        elif method == 'parametric':
            # Simulation paramétrique
            mu = np.mean(returns)
            sigma = np.std(returns, ddof=1)
            
            simulated_returns = np.random.normal(
                mu * horizon,
                sigma * np.sqrt(horizon),
                n_simulations
            )
            horizon_returns = simulated_returns
        
        else:
            raise ValueError("method doit être 'bootstrap' ou 'parametric'")
        
        var = -np.percentile(horizon_returns, (1 - confidence_level) * 100)
        
        return var
    
    @staticmethod
    def expected_shortfall(
        returns: Union[np.ndarray, pd.Series],
        confidence_level: float = 0.95,
        method: Literal['historical', 'parametric'] = 'historical'
    ) -> float:
        """
        Calcule l'Expected Shortfall (ES) / Conditional VaR (CVaR)
        ES = perte moyenne au-delà de la VaR
        
        Paramètres:
        -----------
        returns : array-like
            Série de rendements
        confidence_level : float
            Niveau de confiance
        method : str
            'historical' ou 'parametric'
        
        Retourne:
        ---------
        float : Expected Shortfall
        """
        if isinstance(returns, pd.Series):
            returns = returns.values
        
        returns = returns[~np.isnan(returns)]
        
        if method == 'historical':
            var = VaRCalculator.historical_var(returns, confidence_level)
            # ES = moyenne des rendements inférieurs à -VaR
            tail_returns = returns[returns <= -var]
            
            if len(tail_returns) == 0:
                return var
            
            es = -np.mean(tail_returns)
        
        elif method == 'parametric':
            mu = np.mean(returns)
            sigma = np.std(returns, ddof=1)
            
            z_alpha = norm.ppf(1 - confidence_level)
            
            # ES pour distribution normale
            es = -(mu - sigma * norm.pdf(z_alpha) / (1 - confidence_level))
        
        else:
            raise ValueError("method doit être 'historical' ou 'parametric'")
        
        return es
    
    @staticmethod
    def portfolio_var(
        returns_matrix: pd.DataFrame,
        weights: np.ndarray,
        confidence_level: float = 0.95,
        method: Literal['historical', 'parametric', 'monte_carlo'] = 'parametric'
    ) -> float:
        """
        VaR d'un portefeuille
        
        Paramètres:
        -----------
        returns_matrix : DataFrame
            Matrice des rendements (colonnes = actifs)
        weights : array
            Poids du portefeuille (doivent sommer à 1)
        confidence_level : float
            Niveau de confiance
        method : str
            Méthode de calcul
        
        Retourne:
        ---------
        float : VaR du portefeuille
        """
        # Normaliser les poids
        weights = weights / np.sum(weights)
        
        # Rendements du portefeuille
        portfolio_returns = returns_matrix.dot(weights)
        
        if method == 'historical':
            return VaRCalculator.historical_var(portfolio_returns, confidence_level)
        elif method == 'parametric':
            return VaRCalculator.parametric_var(portfolio_returns, confidence_level)
        elif method == 'monte_carlo':
            return VaRCalculator.monte_carlo_var(portfolio_returns, confidence_level)
        else:
            raise ValueError(f"Méthode inconnue: {method}")
    
    @staticmethod
    def component_var(
        returns_matrix: pd.DataFrame,
        weights: np.ndarray,
        confidence_level: float = 0.95
    ) -> pd.Series:
        """
        VaR componentielle (contribution de chaque actif à la VaR totale)
        
        Paramètres:
        -----------
        returns_matrix : DataFrame
            Rendements des actifs
        weights : array
            Poids du portefeuille
        confidence_level : float
            Niveau de confiance
        
        Retourne:
        ---------
        Series : Contribution de chaque actif à la VaR
        """
        # Normaliser les poids
        weights = weights / np.sum(weights)
        
        # Rendements et VaR du portefeuille
        portfolio_returns = returns_matrix.dot(weights)
        portfolio_var = VaRCalculator.parametric_var(portfolio_returns, confidence_level)
        
        # Covariance matrix
        cov_matrix = returns_matrix.cov()
        portfolio_variance = weights.T @ cov_matrix @ weights
        portfolio_std = np.sqrt(portfolio_variance)
        
        # VaR marginale = (Cov @ w) / σ_p * VaR / σ_p
        marginal_var = (cov_matrix @ weights) / portfolio_std * (portfolio_var / portfolio_std)
        
        # Component VaR = w * MVaR
        component_var = weights * marginal_var
        
        return pd.Series(component_var, index=returns_matrix.columns)
    
    @staticmethod
    def marginal_var(
        returns_matrix: pd.DataFrame,
        weights: np.ndarray,
        confidence_level: float = 0.95
    ) -> pd.Series:
        """
        VaR marginale (changement de VaR pour une petite augmentation de poids)
        
        Retourne:
        ---------
        Series : VaR marginale de chaque actif
        """
        weights = weights / np.sum(weights)
        
        portfolio_returns = returns_matrix.dot(weights)
        portfolio_var = VaRCalculator.parametric_var(portfolio_returns, confidence_level)
        
        cov_matrix = returns_matrix.cov()
        portfolio_variance = weights.T @ cov_matrix @ weights
        portfolio_std = np.sqrt(portfolio_variance)
        
        # Marginal VaR
        marginal_var = (cov_matrix @ weights) / portfolio_std * (portfolio_var / portfolio_std)
        
        return pd.Series(marginal_var, index=returns_matrix.columns)


class StressTesting:
    """Stress testing et analyse de scénarios"""
    
    @staticmethod
    def scenario_analysis(
        returns_matrix: pd.DataFrame,
        weights: np.ndarray,
        scenarios: Dict[str, np.ndarray]
    ) -> pd.DataFrame:
        """
        Analyse de scénarios de stress
        
        Paramètres:
        -----------
        returns_matrix : DataFrame
            Rendements historiques
        weights : array
            Poids du portefeuille
        scenarios : dict
            Dictionnaire {nom_scenario: array_de_chocs}
        
        Retourne:
        ---------
        DataFrame : Impact de chaque scénario
        """
        results = []
        
        current_value = 100  # Valeur normalisée
        
        for scenario_name, shocks in scenarios.items():
            # Appliquer les chocs
            shocked_returns = shocks
            portfolio_return = np.dot(weights, shocked_returns)
            new_value = current_value * (1 + portfolio_return)
            pnl = new_value - current_value
            pnl_pct = portfolio_return
            
            results.append({
                'Scenario': scenario_name,
                'Portfolio Return': pnl_pct,
                'P&L': pnl,
                'New Value': new_value
            })
        
        return pd.DataFrame(results)
    
    @staticmethod
    def historical_stress_test(
        returns_matrix: pd.DataFrame,
        weights: np.ndarray,
        stress_periods: Dict[str, Tuple[str, str]]
    ) -> pd.DataFrame:
        """
        Stress test basé sur des périodes historiques
        
        Paramètres:
        -----------
        returns_matrix : DataFrame
            Rendements avec index temporel
        weights : array
            Poids du portefeuille
        stress_periods : dict
            {nom: (date_debut, date_fin)}
        
        Retourne:
        ---------
        DataFrame : Performance durant les périodes de stress
        """
        results = []
        
        for period_name, (start_date, end_date) in stress_periods.items():
            period_returns = returns_matrix.loc[start_date:end_date]
            
            if len(period_returns) == 0:
                continue
            
            portfolio_returns = period_returns.dot(weights)
            
            cumulative_return = (1 + portfolio_returns).prod() - 1
            max_drawdown = (portfolio_returns + 1).cumprod()
            max_dd = ((max_drawdown.cummax() - max_drawdown) / max_drawdown.cummax()).max()
            
            results.append({
                'Period': period_name,
                'Start': start_date,
                'End': end_date,
                'Cumulative Return': cumulative_return,
                'Max Drawdown': max_dd,
                'Worst Day': portfolio_returns.min(),
                'Best Day': portfolio_returns.max(),
                'Volatility': portfolio_returns.std() * np.sqrt(252)
            })
        
        return pd.DataFrame(results)
    
    @staticmethod
    def monte_carlo_stress_test(
        returns_matrix: pd.DataFrame,
        weights: np.ndarray,
        n_scenarios: int = 1000,
        confidence_levels: list = [0.95, 0.99],
        horizon: int = 1,
        random_seed: Optional[int] = None
    ) -> Dict:
        """
        Stress test Monte Carlo
        
        Paramètres:
        -----------
        returns_matrix : DataFrame
            Rendements historiques
        weights : array
            Poids
        n_scenarios : int
            Nombre de scénarios
        confidence_levels : list
            Niveaux de confiance à reporter
        horizon : int
            Horizon (en jours)
        
        Retourne:
        ---------
        dict : Résultats des simulations
        """
        if random_seed is not None:
            np.random.seed(random_seed)
        
        # Estimer la distribution
        portfolio_returns = returns_matrix.dot(weights)
        mu = portfolio_returns.mean()
        sigma = portfolio_returns.std()
        
        # Simuler
        scenarios = np.random.normal(mu * horizon, sigma * np.sqrt(horizon), n_scenarios)
        
        results = {
            'scenarios': scenarios,
            'mean': scenarios.mean(),
            'std': scenarios.std(),
            'min': scenarios.min(),
            'max': scenarios.max(),
        }
        
        for cl in confidence_levels:
            var = -np.percentile(scenarios, (1-cl)*100)
            es = -scenarios[scenarios <= -var].mean()
            results[f'VaR_{int(cl*100)}'] = var
            results[f'ES_{int(cl*100)}'] = es
        
        return results