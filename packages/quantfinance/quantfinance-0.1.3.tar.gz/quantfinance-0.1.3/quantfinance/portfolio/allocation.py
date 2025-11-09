"""
Stratégies d'allocation d'actifs

Implémente :
- Hierarchical Risk Parity (HRP)
- Minimum Correlation
- Maximum Diversification
"""

import numpy as np
import pandas as pd
from scipy.cluster.hierarchy import linkage, dendrogram
from scipy.spatial.distance import squareform
from scipy.optimize import minimize
from typing import Optional


class AssetAllocator:
    """
    Classe pour l'allocation d'actifs avec différentes stratégies
    """
    
    def __init__(self, returns: pd.DataFrame):
        """
        Args:
            returns: DataFrame de rendements quotidiens
        """
        self.returns = returns
        self.cov_matrix = returns.cov() * 252  # Annualisé
        self.corr_matrix = returns.corr()
        self.std_devs = returns.std() * np.sqrt(252)  # Annualisé
        self.assets = returns.columns.tolist()
        self.n_assets = len(self.assets)
    
    def hierarchical_risk_parity(self) -> pd.Series:
        """
        Allocation selon Hierarchical Risk Parity (HRP)
        
        Méthode de Lopez de Prado qui utilise le clustering hiérarchique
        pour construire un portefeuille diversifié
        
        Returns:
            Series de poids optimaux
        """
        # 1. Calcul de la matrice de distance
        # Distance = sqrt(0.5 * (1 - correlation))
        dist_matrix = np.sqrt(0.5 * (1 - self.corr_matrix))
        
        # 2. Clustering hiérarchique
        dist_condensed = squareform(dist_matrix, checks=False)
        link = linkage(dist_condensed, method='single')
        
        # 3. Quasi-diagonalisation
        sorted_indices = self._quasi_diagonalization(link)
        
        # 4. Allocation récursive
        weights = self._recursive_bisection(
            self.cov_matrix.iloc[sorted_indices, sorted_indices]
        )
        
        # Réordonne les poids selon l'ordre original
        sorted_weights = pd.Series(weights, index=self.corr_matrix.index[sorted_indices])
        original_weights = sorted_weights.reindex(self.assets)
        
        return original_weights
    
    def _quasi_diagonalization(self, link: np.ndarray) -> list:
        """
        Réorganise les actifs selon la structure du dendrogramme
        
        Args:
            link: Matrice de linkage de scipy
            
        Returns:
            Liste d'indices triés
        """
        # Parcours du dendrogramme pour obtenir l'ordre
        def _get_quasi_diag_order(link_matrix):
            n = link_matrix.shape[0] + 1
            order = []
            
            def _traverse(node_id):
                if node_id < n:
                    order.append(node_id)
                else:
                    idx = int(node_id - n)
                    left = int(link_matrix[idx, 0])
                    right = int(link_matrix[idx, 1])
                    _traverse(left)
                    _traverse(right)
            
            _traverse(2 * n - 2)
            return order
        
        return _get_quasi_diag_order(link)
    
    def _recursive_bisection(
        self,
        cov_matrix: pd.DataFrame,
        weights: Optional[pd.Series] = None
    ) -> np.ndarray:
        """
        Allocation récursive par bisection
        
        Args:
            cov_matrix: Matrice de covariance (ordonnée)
            weights: Poids initiaux (None = équipondéré)
            
        Returns:
            Array de poids optimaux
        """
        if weights is None:
            weights = pd.Series(1.0, index=cov_matrix.index)
        
        assets = cov_matrix.index.tolist()
        n = len(assets)
        
        if n == 1:
            return weights.values
        
        # Divise en deux clusters
        split = n // 2
        left_assets = assets[:split]
        right_assets = assets[split:]
        
        # Calcule la variance de chaque cluster
        left_cov = cov_matrix.loc[left_assets, left_assets]
        right_cov = cov_matrix.loc[right_assets, right_assets]
        
        left_weights = weights[left_assets]
        right_weights = weights[right_assets]
        
        left_weights = left_weights / left_weights.sum()
        right_weights = right_weights / right_weights.sum()
        
        left_var = np.dot(left_weights.values, 
                         np.dot(left_cov.values, left_weights.values))
        right_var = np.dot(right_weights.values,
                          np.dot(right_cov.values, right_weights.values))
        
        # Allocation inversement proportionnelle à la variance
        total_var = left_var + right_var
        alpha_left = 1 - left_var / total_var
        alpha_right = 1 - right_var / total_var
        
        # Normalise
        total_alpha = alpha_left + alpha_right
        alpha_left /= total_alpha
        alpha_right /= total_alpha
        
        # Applique les poids
        weights[left_assets] *= alpha_left
        weights[right_assets] *= alpha_right
        
        # Récursion
        if len(left_assets) > 1:
            weights[left_assets] = self._recursive_bisection(left_cov, weights[left_assets])
        
        if len(right_assets) > 1:
            weights[right_assets] = self._recursive_bisection(right_cov, weights[right_assets])
        
        return weights.values
    
    def minimum_correlation(self) -> pd.Series:
        """
        Portefeuille de corrélation minimale
        
        Minimise la corrélation moyenne du portefeuille
        
        Returns:
            Series de poids optimaux
        """
        # Fonction objectif: minimiser la corrélation pondérée
        def portfolio_correlation(weights):
            # Corrélation pondérée
            weighted_corr = 0
            for i in range(self.n_assets):
                for j in range(self.n_assets):
                    if i != j:
                        weighted_corr += weights[i] * weights[j] * self.corr_matrix.iloc[i, j]
            return weighted_corr
        
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
            portfolio_correlation,
            x0,
            method='SLSQP',
            bounds=bounds,
            constraints=cons,
            options={'maxiter': 1000}
        )
        
        weights = pd.Series(result.x, index=self.assets)
        return weights
    
    def maximum_diversification(self) -> pd.Series:
        """
        Portefeuille de diversification maximale
        
        Maximise le ratio: (somme des volatilités pondérées) / (volatilité du portfolio)
        
        Returns:
            Series de poids optimaux
        """
        # Fonction objectif (minimiser le négatif)
        def neg_diversification_ratio(weights):
            # Volatilité pondérée
            weighted_vol = np.dot(weights, self.std_devs)
            
            # Volatilité du portefeuille
            portfolio_vol = np.sqrt(
                np.dot(weights.T, np.dot(self.cov_matrix.values, weights))
            )
            
            # Ratio de diversification
            div_ratio = weighted_vol / portfolio_vol if portfolio_vol > 0 else 0
            
            return -div_ratio
        
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
            neg_diversification_ratio,
            x0,
            method='SLSQP',
            bounds=bounds,
            constraints=cons,
            options={'maxiter': 1000}
        )
        
        weights = pd.Series(result.x, index=self.assets)
        return weights