"""
Optimisation de portefeuille

Implémente :
- Portefeuille équipondéré
- Minimisation de volatilité
- Maximisation du Sharpe ratio
- Maximisation du rendement
- Risk Parity
- Frontière efficiente
"""

import numpy as np
import pandas as pd
from scipy.optimize import minimize
from typing import Dict, Optional, Tuple
import warnings


class PortfolioOptimizer:
    """
    Classe pour l'optimisation de portefeuille
    """
    
    def __init__(
        self,
        returns: pd.DataFrame,
        risk_free_rate: float = 0.02
    ):
        """
        Args:
            returns: DataFrame de rendements quotidiens (dates x actifs)
            risk_free_rate: Taux sans risque annualisé
        """
        self.returns = returns
        self.risk_free_rate = risk_free_rate
        
        # Calcul des statistiques annualisées
        self.mean_returns = returns.mean() * 252
        self.cov_matrix = returns.cov() * 252
        self.std_devs = returns.std() * np.sqrt(252)
        
        self.n_assets = len(returns.columns)
        self.assets = returns.columns.tolist()
    

    def expected_return(self, weights):
        """Calculate expected return of portfolio given weights."""
        return np.dot(weights, self.mean_returns)

    def portfolio_volatility(self, weights):
        """Calculate portfolio volatility (standard deviation) given weights."""
        return np.sqrt(np.dot(weights.T, np.dot(self.cov_matrix, weights)))


    def portfolio_performance(
        self,
        weights: np.ndarray
    ) -> Tuple[float, float, float]:
        """
        Calcule la performance du portefeuille
        
        Args:
            weights: Array ou Series de poids
            
        Returns:
            (rendement annualisé, volatilité annualisée, sharpe ratio)
        """
        if isinstance(weights, pd.Series):
            weights = weights.values
        
        # Rendement du portefeuille
        portfolio_return = np.dot(weights, self.mean_returns)
        
        # Volatilité du portefeuille
        portfolio_vol = np.sqrt(
            np.dot(weights.T, np.dot(self.cov_matrix, weights))
        )
        
        # Sharpe ratio
        sharpe_ratio = (portfolio_return - self.risk_free_rate) / portfolio_vol \
            if portfolio_vol > 0 else 0
        
        return portfolio_return, portfolio_vol, sharpe_ratio
    
    def equal_weight(self) -> Dict:
        """
        Crée un portefeuille équipondéré
        
        Returns:
            Dictionnaire avec weights et statistiques
        """
        weights = pd.Series(
            [1.0 / self.n_assets] * self.n_assets,
            index=self.assets
        )
        
        ret, vol, sharpe = self.portfolio_performance(weights)
        
        return {
            'weights': weights,
            'return': ret,
            'volatility': vol,
            'sharpe_ratio': sharpe,
            'success': True
        }
    
    def minimize_volatility(
        self,
        constraints: Optional[Dict] = None
    ) -> Dict:
        """
        Minimise la volatilité du portefeuille
        
        Args:
            constraints: Contraintes supplémentaires
            
        Returns:
            Dictionnaire avec résultats d'optimisation
        """
        # Fonction objectif
        def portfolio_vol(weights):
            return np.sqrt(np.dot(weights.T, np.dot(self.cov_matrix, weights)))
        
        # Contraintes
        cons = [
            {'type': 'eq', 'fun': lambda x: np.sum(x) - 1}  # Somme = 1
        ]
        
        # Bornes (pas de short selling)
        bounds = tuple((0, 1) for _ in range(self.n_assets))
        
        # Point de départ
        x0 = np.array([1.0 / self.n_assets] * self.n_assets)
        
        # Optimisation
        result = minimize(
            portfolio_vol,
            x0,
            method='SLSQP',
            bounds=bounds,
            constraints=cons,
            options={'maxiter': 1000}
        )
        
        weights = pd.Series(result.x, index=self.assets)
        ret, vol, sharpe = self.portfolio_performance(weights)
        
        return {
            'weights': weights,
            'return': ret,
            'volatility': vol,
            'sharpe_ratio': sharpe,
            'success': result.success
        }
    
    def maximize_sharpe(
        self,
        constraints: Optional[Dict] = None
    ) -> Dict:
        """
        Maximise le ratio de Sharpe
        
        Args:
            constraints: Contraintes supplémentaires
            
        Returns:
            Dictionnaire avec résultats d'optimisation
        """
        # Fonction objectif (minimiser le négatif)
        def neg_sharpe(weights):
            ret, vol, sharpe = self.portfolio_performance(weights)
            return -sharpe
        
        # Contraintes
        cons = [
            {'type': 'eq', 'fun': lambda x: np.sum(x) - 1}
        ]
        
        # Bornes
        bounds = tuple((0, 1) for _ in range(self.n_assets))
        
        # Point de départ
        x0 = np.array([1.0 / self.n_assets] * self.n_assets)
        
        # Optimisation
        result = minimize(
            neg_sharpe,
            x0,
            method='SLSQP',
            bounds=bounds,
            constraints=cons,
            options={'maxiter': 1000}
        )
        
        weights = pd.Series(result.x, index=self.assets)
        ret, vol, sharpe = self.portfolio_performance(weights)
        
        return {
            'weights': weights,
            'return': ret,
            'volatility': vol,
            'sharpe_ratio': sharpe,
            'success': result.success
        }
    
    def maximize_return(self, target_volatility):
        # Objective: maximize return → minimize negative return
        def objective(weights):
            return -self.expected_return(weights)

        # Constraints
        constraints = [
            {'type': 'eq', 'fun': lambda w: np.sum(w) - 1},  # weights sum to 1
            {'type': 'ineq', 'fun': lambda w: target_volatility + 0.02 - self.portfolio_volatility(w)}  # Allow up to 0.17
        ]

        # Bounds: weights between 0 and 1
        bounds = [(0, 1) for _ in range(len(self.assets))]

        # Initial guess: equal weights
        x0 = np.ones(len(self.assets)) / len(self.assets)

        # Try trust-constr (handles constraints better than SLSQP)
        result = minimize(
            objective,
            x0,
            method='trust-constr',
            constraints=constraints,
            bounds=bounds,
            options={'maxiter': 1000, 'disp': True}  # <-- See why it fails
        )

        if not result.success:
            print(f"Optimization failed: {result.message}")
            print(f"Final volatility: {self.portfolio_volatility(result.x):.6f}")
            print(f"Final weights: {result.x}")
            print(f"Target volatility: {target_volatility}")

        return result
    
    def risk_parity(self) -> Dict:
        """
        Crée un portefeuille de parité de risque (Risk Parity)
        
        Chaque actif contribue de manière égale au risque total
        
        Returns:
            Dictionnaire avec weights et risk_contribution
        """
        # Fonction objectif: minimiser la différence entre les contributions
        def risk_budget_objective(weights):
            portfolio_vol = np.sqrt(
                np.dot(weights.T, np.dot(self.cov_matrix, weights))
            )
            
            # Contribution marginale au risque
            marginal_contrib = np.dot(self.cov_matrix, weights)
            
            # Contribution au risque
            risk_contrib = weights * marginal_contrib / portfolio_vol
            
            # Objectif: minimiser la variance des contributions
            target_contrib = portfolio_vol / self.n_assets
            return np.sum((risk_contrib - target_contrib) ** 2)
        
        # Contraintes
        cons = [
            {'type': 'eq', 'fun': lambda x: np.sum(x) - 1}
        ]
        
        # Bornes
        bounds = tuple((0.001, 1) for _ in range(self.n_assets))
        
        # Point de départ
        x0 = np.array([1.0 / self.n_assets] * self.n_assets)
        
        # Optimisation
        result = minimize(
            risk_budget_objective,
            x0,
            method='SLSQP',
            bounds=bounds,
            constraints=cons,
            options={'maxiter': 1000}
        )
        
        weights = pd.Series(result.x, index=self.assets)
        
        # Calcul des contributions au risque
        portfolio_vol = np.sqrt(
            np.dot(weights.values.T, np.dot(self.cov_matrix, weights.values))
        )
        marginal_contrib = np.dot(self.cov_matrix, weights.values)
        risk_contrib = pd.Series(
            weights.values * marginal_contrib / portfolio_vol,
            index=self.assets
        )
        
        ret, vol, sharpe = self.portfolio_performance(weights)
        
        return {
            'weights': weights,
            'risk_contribution': risk_contrib,
            'return': ret,
            'volatility': vol,
            'sharpe_ratio': sharpe,
            'success': result.success
        }


class EfficientFrontier:
    """
    Calcule et visualise la frontière efficiente
    """
    
    def __init__(self, optimizer: PortfolioOptimizer):
        """
        Args:
            optimizer: Instance de PortfolioOptimizer
        """
        self.optimizer = optimizer
        self.frontier_data = None
    
    def calculate_frontier(
        self,
        n_points: int = 50,
        min_return: Optional[float] = None,
        max_return: Optional[float] = None
    ) -> pd.DataFrame:
        """
        Calcule les points de la frontière efficiente
        
        Args:
            n_points: Nombre de points à calculer
            min_return: Rendement minimum (calculé automatiquement si None)
            max_return: Rendement maximum (calculé automatiquement si None)
            
        Returns:
            DataFrame avec colonnes: return, volatility, sharpe_ratio
        """
        # Trouve le portefeuille de volatilité minimale
        min_vol_result = self.optimizer.minimize_volatility()
        min_vol_return = min_vol_result['return']
        
        # Trouve le rendement maximum
        max_ret = self.optimizer.mean_returns.max()
        
        # Définit la plage de rendements
        if min_return is None:
            min_return = min_vol_return
        if max_return is None:
            max_return = max_ret
        
        # Génère les rendements cibles
        target_returns = np.linspace(min_return, max_return, n_points)
        
        frontier_points = []
        
        for target_ret in target_returns:
            try:
                # Minimise la volatilité pour ce rendement cible
                def portfolio_vol(weights):
                    return np.sqrt(
                        np.dot(weights.T, np.dot(self.optimizer.cov_matrix, weights))
                    )
                
                def return_constraint(weights):
                    return np.dot(weights, self.optimizer.mean_returns) - target_ret
                
                cons = [
                    {'type': 'eq', 'fun': lambda x: np.sum(x) - 1},
                    {'type': 'eq', 'fun': return_constraint}
                ]
                
                bounds = tuple((0, 1) for _ in range(self.optimizer.n_assets))
                x0 = np.array([1.0 / self.optimizer.n_assets] * self.optimizer.n_assets)
                
                result = minimize(
                    portfolio_vol,
                    x0,
                    method='SLSQP',
                    bounds=bounds,
                    constraints=cons,
                    options={'maxiter': 1000}
                )
                
                if result.success:
                    weights = result.x
                    ret, vol, sharpe = self.optimizer.portfolio_performance(weights)
                    
                    frontier_points.append({
                        'return': ret,
                        'volatility': vol,
                        'sharpe_ratio': sharpe
                    })
            except:
                continue
        
        self.frontier_data = pd.DataFrame(frontier_points)
        return self.frontier_data
    
    def plot(
        self,
        show_assets: bool = True,
        show_optimal: bool = True,
        figsize: Tuple[int, int] = (12, 8)
    ):
        """
        Trace la frontière efficiente
        
        Args:
            show_assets: Afficher les actifs individuels
            show_optimal: Afficher le portefeuille optimal (max Sharpe)
            figsize: Taille de la figure
            
        Returns:
            Figure matplotlib
        """
        import matplotlib.pyplot as plt
        
        if self.frontier_data is None:
            self.calculate_frontier()
        
        fig, ax = plt.subplots(figsize=figsize)
        
        # Frontière efficiente
        ax.plot(
            self.frontier_data['volatility'],
            self.frontier_data['return'],
            'b-',
            linewidth=2,
            label='Frontière Efficiente'
        )
        
        # Actifs individuels
        if show_assets:
            asset_returns = self.optimizer.mean_returns
            asset_vols = self.optimizer.std_devs
            
            ax.scatter(
                asset_vols,
                asset_returns,
                s=100,
                c='red',
                marker='o',
                alpha=0.6,
                label='Actifs individuels'
            )
            
            for i, asset in enumerate(self.optimizer.assets):
                ax.annotate(
                    asset,
                    (asset_vols[i], asset_returns[i]),
                    xytext=(10, 10),
                    textcoords='offset points',
                    fontsize=9
                )
        
        # Portefeuille optimal (max Sharpe)
        if show_optimal:
            max_sharpe_result = self.optimizer.maximize_sharpe()
            ax.scatter(
                max_sharpe_result['volatility'],
                max_sharpe_result['return'],
                s=200,
                c='gold',
                marker='*',
                edgecolors='black',
                linewidths=2,
                label='Max Sharpe Ratio',
                zorder=5
            )
        
        ax.set_xlabel('Volatilité (Risque)', fontsize=12)
        ax.set_ylabel('Rendement Espéré', fontsize=12)
        ax.set_title('Frontière Efficiente', fontsize=14, fontweight='bold')
        ax.legend(fontsize=10)
        ax.grid(True, alpha=0.3)
        
        plt.tight_layout()
        return fig