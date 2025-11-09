"""
Stratégies de rééquilibrage de portefeuille

Implémente :
- Rééquilibrage périodique (calendrier)
- Rééquilibrage par seuil (threshold)
- Analyse des coûts de transaction
"""

import numpy as np
import pandas as pd
from typing import Optional, Union


class Rebalancer:
    """
    Classe pour le rééquilibrage de portefeuille
    """
    
    def __init__(
        self,
        target_weights: pd.Series,
        prices: pd.DataFrame,
        initial_capital: float = 100000.0,
        transaction_cost: float = 0.001  # 0.1%
    ):
        """
        Args:
            target_weights: Poids cibles du portefeuille
            prices: DataFrame de prix historiques
            initial_capital: Capital initial
            transaction_cost: Coût de transaction (en fraction)
        """
        self.target_weights = target_weights
        self.prices = prices
        self.initial_capital = initial_capital
        self.transaction_cost = transaction_cost
        
        # Vérifie que les actifs correspondent
        if not all(asset in prices.columns for asset in target_weights.index):
            raise ValueError("Tous les actifs des poids doivent être dans les prix")
    
    def periodic_rebalancing(
        self,
        frequency: str = 'monthly'
    ) -> pd.DataFrame:
        """
        Rééquilibrage périodique (calendrier fixe)
        
        Args:
            frequency: Fréquence de rééquilibrage ('daily', 'weekly', 'monthly', 'quarterly', 'yearly')
            
        Returns:
            DataFrame avec l'historique du portefeuille
        """
        # Détermine les dates de rééquilibrage
        rebalance_dates = self._get_rebalance_dates(frequency)
        
        # Initialise le portefeuille
        cash = self.initial_capital
        holdings = pd.Series(0.0, index=self.target_weights.index)
        
        results = []
        
        for i, date in enumerate(self.prices.index):
            current_prices = self.prices.loc[date]
            
            # Rééquilibrage si nécessaire
            if date in rebalance_dates:
                # Vend toutes les positions
                cash += (holdings * current_prices).sum()
                
                # Calcul du total après frais
                portfolio_value = cash
                
                # Achète selon les poids cibles
                for asset in self.target_weights.index:
                    target_value = portfolio_value * self.target_weights[asset]
                    target_shares = target_value / current_prices[asset]
                    
                    # Coût de transaction
                    transaction_value = target_shares * current_prices[asset]
                    cost = transaction_value * self.transaction_cost
                    
                    holdings[asset] = target_shares
                    cash -= (transaction_value + cost)
            
            # Calcule la valeur du portefeuille
            holdings_value = (holdings * current_prices).sum()
            portfolio_value = holdings_value + cash
            
            # Calcule les poids actuels
            current_weights = (holdings * current_prices) / portfolio_value if portfolio_value > 0 else holdings * 0
            
            results.append({
                'date': date,
                'portfolio_value': portfolio_value,
                'cash': cash,
                'holdings_value': holdings_value,
                'is_rebalance': date in rebalance_dates,
                **{f'weight_{asset}': current_weights[asset] for asset in self.target_weights.index}
            })
        
        return pd.DataFrame(results).set_index('date')
    
    def threshold_rebalancing(
        self,
        threshold: float = 0.05
    ) -> pd.DataFrame:
        """
        Rééquilibrage par seuil (threshold-based)
        
        Rééquilibre quand un poids dévie de plus de threshold du poids cible
        
        Args:
            threshold: Seuil de déviation pour déclencher un rééquilibrage (ex: 0.05 = 5%)
            
        Returns:
            DataFrame avec l'historique du portefeuille
        """
        # Initialise le portefeuille
        cash = self.initial_capital
        holdings = pd.Series(0.0, index=self.target_weights.index)
        
        # Premier achat
        first_prices = self.prices.iloc[0]
        for asset in self.target_weights.index:
            target_value = self.initial_capital * self.target_weights[asset]
            target_shares = target_value / first_prices[asset]
            transaction_value = target_shares * first_prices[asset]
            cost = transaction_value * self.transaction_cost
            
            holdings[asset] = target_shares
            cash -= (transaction_value + cost)
        
        results = []
        rebalance_count = 0
        
        for date in self.prices.index:
            current_prices = self.prices.loc[date]
            
            # Calcule la valeur du portefeuille
            holdings_value = (holdings * current_prices).sum()
            portfolio_value = holdings_value + cash
            
            # Calcule les poids actuels
            if portfolio_value > 0:
                current_weights = (holdings * current_prices) / portfolio_value
            else:
                current_weights = holdings * 0
            
            # Vérifie si rééquilibrage nécessaire
            needs_rebalance = False
            for asset in self.target_weights.index:
                deviation = abs(current_weights[asset] - self.target_weights[asset])
                if deviation > threshold:
                    needs_rebalance = True
                    break
            
            # Rééquilibrage
            if needs_rebalance:
                rebalance_count += 1
                
                # Vend toutes les positions
                cash += (holdings * current_prices).sum()
                
                # Achète selon les poids cibles
                for asset in self.target_weights.index:
                    target_value = cash * self.target_weights[asset]
                    target_shares = target_value / current_prices[asset]
                    transaction_value = target_shares * current_prices[asset]
                    cost = transaction_value * self.transaction_cost
                    
                    holdings[asset] = target_shares
                    cash -= (transaction_value + cost)
                
                # Recalcule après rééquilibrage
                holdings_value = (holdings * current_prices).sum()
                portfolio_value = holdings_value + cash
                current_weights = (holdings * current_prices) / portfolio_value if portfolio_value > 0 else holdings * 0
            
            results.append({
                'date': date,
                'portfolio_value': portfolio_value,
                'cash': cash,
                'holdings_value': holdings_value,
                'is_rebalance': needs_rebalance,
                'rebalance_count': rebalance_count,
                **{f'weight_{asset}': current_weights[asset] for asset in self.target_weights.index}
            })
        
        return pd.DataFrame(results).set_index('date')
    
    def _get_rebalance_dates(self, frequency: str) -> pd.DatetimeIndex:
        """
        Génère les dates de rééquilibrage selon la fréquence
        
        Args:
            frequency: 'daily', 'weekly', 'monthly', 'quarterly', 'yearly'
            
        Returns:
            Index de dates
        """
        dates = self.prices.index
        
        if frequency == 'daily':
            return dates
        elif frequency == 'weekly':
            return dates[dates.to_series().dt.dayofweek == 0]  # Lundi
        elif frequency == 'monthly':
            return dates[dates.to_series().dt.is_month_end]
        elif frequency == 'quarterly':
            return dates[dates.to_series().dt.is_quarter_end]
        elif frequency == 'yearly':
            return dates[dates.to_series().dt.is_year_end]
        else:
            raise ValueError(f"Fréquence inconnue: {frequency}")