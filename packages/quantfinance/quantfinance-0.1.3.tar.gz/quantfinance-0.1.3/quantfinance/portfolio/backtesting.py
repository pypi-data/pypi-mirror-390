"""
Framework de backtesting pour stratégies de trading

Implémente :
- Backtester générique
- Stratégies prédéfinies (Buy & Hold, Moving Average Crossover, etc.)
- Métriques de performance
"""

import numpy as np
import pandas as pd
from typing import Optional, Dict
from abc import ABC, abstractmethod


class Strategy(ABC):
    """
    Classe abstraite pour les stratégies de trading
    """
    
    @abstractmethod
    def generate_signals(self, data: pd.DataFrame) -> pd.Series:
        """
        Génère les signaux de trading
        
        Args:
            data: DataFrame avec les données de marché
            
        Returns:
            Series de signaux (1 = long, 0 = neutre, -1 = short)
        """
        pass


class BuyAndHoldStrategy(Strategy):
    """
    Stratégie Buy & Hold simple
    """
    
    def generate_signals(self, data: pd.DataFrame) -> pd.Series:
        """
        Achète au début et garde jusqu'à la fin
        
        Args:
            data: DataFrame avec colonne 'Close'
            
        Returns:
            Series de signaux (toujours 1)
        """
        signals = pd.Series(1, index=data.index)
        return signals


class MovingAverageCrossover(Strategy):
    """
    Stratégie de croisement de moyennes mobiles
    
    Signal d'achat quand MA courte > MA longue
    Signal de vente quand MA courte < MA longue
    """
    
    def __init__(self, short_window: int = 20, long_window: int = 50):
        """
        Args:
            short_window: Période de la moyenne mobile courte
            long_window: Période de la moyenne mobile longue
        """
        self.short_window = short_window
        self.long_window = long_window
    
    def generate_signals(self, data: pd.DataFrame) -> pd.Series:
        """
        Génère les signaux basés sur le croisement des MA
        
        Args:
            data: DataFrame avec colonne 'Close'
            
        Returns:
            Series de signaux
        """
        prices = data['Close']
        
        # Calcule les moyennes mobiles
        short_ma = prices.rolling(window=self.short_window).mean()
        long_ma = prices.rolling(window=self.long_window).mean()
        
        # Génère les signaux
        signals = pd.Series(0, index=data.index)
        signals[short_ma > long_ma] = 1  # Long
        signals[short_ma < long_ma] = -1  # Short ou sortie
        
        return signals


class Backtester:
    """
    Framework de backtesting pour stratégies de trading
    """
    
    def __init__(
        self,
        data: pd.DataFrame,
        strategy: Strategy,
        initial_capital: float = 10000.0,
        commission: float = 0.001
    ):
        """
        Args:
            data: DataFrame avec les données de prix (doit contenir 'Close')
            strategy: Instance de Strategy
            initial_capital: Capital initial
            commission: Commission par trade (fraction)
        """
        self.data = data
        self.strategy = strategy
        self.initial_capital = initial_capital
        self.commission = commission
        self.results = None
    
    def run(self) -> Dict:
        """
        Execute le backtest
        
        Returns:
            Dictionnaire de statistiques de performance
        """
        # Génère les signaux
        signals = self.strategy.generate_signals(self.data)
        
        # Initialise les variables
        cash = self.initial_capital
        position = 0  # Nombre d'actions détenues
        portfolio_values = []
        trades = []
        
        for i, (date, signal) in enumerate(signals.items()):
            price = self.data.loc[date, 'Close']
            
            # Détecte les changements de signal (trades)
            if i > 0:
                prev_signal = signals.iloc[i-1]
                
                # Achat
                if signal == 1 and prev_signal != 1 and cash > 0:
                    # Achète autant d'actions que possible
                    shares_to_buy = cash / (price * (1 + self.commission))
                    cost = shares_to_buy * price * (1 + self.commission)
                    
                    position += shares_to_buy
                    cash -= cost
                    
                    trades.append({
                        'date': date,
                        'type': 'BUY',
                        'price': price,
                        'shares': shares_to_buy,
                        'cost': cost
                    })
                
                # Vente
                elif signal == -1 and prev_signal != -1 and position > 0:
                    proceeds = position * price * (1 - self.commission)
                    cash += proceeds
                    
                    trades.append({
                        'date': date,
                        'type': 'SELL',
                        'price': price,
                        'shares': position,
                        'proceeds': proceeds
                    })
                    
                    position = 0
            else:
                # Premier jour - achète si signal positif
                if signal == 1:
                    shares_to_buy = cash / (price * (1 + self.commission))
                    cost = shares_to_buy * price * (1 + self.commission)
                    
                    position += shares_to_buy
                    cash -= cost
                    
                    trades.append({
                        'date': date,
                        'type': 'BUY',
                        'price': price,
                        'shares': shares_to_buy,
                        'cost': cost
                    })
            
            # Calcule la valeur du portefeuille
            portfolio_value = cash + (position * price)
            portfolio_values.append({
                'date': date,
                'portfolio_value': portfolio_value,
                'cash': cash,
                'position': position,
                'signal': signal
            })
        
        # Stocke les résultats
        self.results = pd.DataFrame(portfolio_values).set_index('date')
        
        # Calcule les statistiques
        stats = self._calculate_statistics(trades)
        
        return stats
    
    def _calculate_statistics(self, trades: list) -> Dict:
        """
        Calcule les statistiques de performance
        
        Args:
            trades: Liste des transactions
            
        Returns:
            Dictionnaire de statistiques
        """
        if self.results is None or len(self.results) == 0:
            return {}
        
        final_value = self.results['portfolio_value'].iloc[-1]
        total_return = (final_value - self.initial_capital) / self.initial_capital
        
        # Calcule les rendements quotidiens
        returns = self.results['portfolio_value'].pct_change().dropna()
        
        # Sharpe ratio (annualisé)
        if len(returns) > 0 and returns.std() > 0:
            sharpe_ratio = (returns.mean() / returns.std()) * np.sqrt(252)
        else:
            sharpe_ratio = 0.0
        
        # Maximum drawdown
        cumulative = (1 + returns).cumprod()
        running_max = cumulative.expanding().max()
        drawdown = (cumulative - running_max) / running_max
        max_drawdown = drawdown.min()
        
        # Nombre de trades
        num_trades = len(trades)
        
        # Win rate
        winning_trades = 0
        losing_trades = 0
        
        for i in range(0, len(trades)-1, 2):
            if i+1 < len(trades):
                buy_price = trades[i]['price']
                sell_price = trades[i+1]['price']
                if sell_price > buy_price:
                    winning_trades += 1
                else:
                    losing_trades += 1
        
        total_closed_trades = winning_trades + losing_trades
        win_rate = winning_trades / total_closed_trades if total_closed_trades > 0 else 0
        
        return {
            'Initial Capital': self.initial_capital,
            'Final Value': final_value,
            'Total Return': total_return,
            'Total Return %': total_return * 100,
            'Sharpe Ratio': sharpe_ratio,
            'Max Drawdown': max_drawdown,
            'Max Drawdown %': max_drawdown * 100,
            'Number of Trades': num_trades,
            'Win Rate': win_rate,
            'Win Rate %': win_rate * 100
        }
    
    def plot_results(self, figsize=(14, 10)):
        """
        Trace les résultats du backtest
        
        Args:
            figsize: Taille de la figure
            
        Returns:
            Figure matplotlib
        """
        import matplotlib.pyplot as plt
        
        if self.results is None:
            raise ValueError("Exécutez d'abord run() avant de tracer les résultats")
        
        fig, axes = plt.subplots(3, 1, figsize=figsize)
        
        # 1. Prix et signaux
        ax1 = axes[0]
        ax1.plot(self.data.index, self.data['Close'], label='Prix', linewidth=1.5)
        
        buy_signals = self.results[self.results['signal'] == 1].index
        sell_signals = self.results[self.results['signal'] == -1].index
        
        ax1.scatter(buy_signals, self.data.loc[buy_signals, 'Close'], 
                   color='green', marker='^', s=100, label='Signal Achat', zorder=5)
        ax1.scatter(sell_signals, self.data.loc[sell_signals, 'Close'],
                   color='red', marker='v', s=100, label='Signal Vente', zorder=5)
        
        ax1.set_title('Prix et Signaux de Trading', fontsize=12, fontweight='bold')
        ax1.set_ylabel('Prix')
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        
        # 2. Valeur du portefeuille
        ax2 = axes[1]
        ax2.plot(self.results.index, self.results['portfolio_value'], 
                label='Valeur du Portefeuille', linewidth=2, color='blue')
        ax2.axhline(y=self.initial_capital, color='black', linestyle='--', 
                   label='Capital Initial', alpha=0.5)
        ax2.set_title('Evolution du Portefeuille', fontsize=12, fontweight='bold')
        ax2.set_ylabel('Valeur ($)')
        ax2.legend()
        ax2.grid(True, alpha=0.3)
        
        # 3. Drawdown
        ax3 = axes[2]
        returns = self.results['portfolio_value'].pct_change()
        cumulative = (1 + returns).cumprod()
        running_max = cumulative.expanding().max()
        drawdown = (cumulative - running_max) / running_max * 100
        
        ax3.fill_between(drawdown.index, drawdown, 0, alpha=0.3, color='red')
        ax3.plot(drawdown.index, drawdown, color='red', linewidth=1)
        ax3.set_title('Drawdown', fontsize=12, fontweight='bold')
        ax3.set_ylabel('Drawdown (%)')
        ax3.set_xlabel('Date')
        ax3.grid(True, alpha=0.3)
        
        plt.tight_layout()
        return fig