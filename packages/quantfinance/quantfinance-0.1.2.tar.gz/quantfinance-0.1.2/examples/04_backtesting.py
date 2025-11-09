"""
Exemple 4: Backtesting de stratégies

Ce script démontre :
- Création de stratégies de trading
- Backtesting
- Analyse de performance
- Comparaison de stratégies
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from quantfinance.portfolio.backtesting import (
    Backtester,
    Strategy,
    BuyAndHoldStrategy,
    MovingAverageCrossover
)
from quantfinance.utils.data import DataLoader


class MomentumStrategy(Strategy):
    """Stratégie de momentum simple"""
    
    def __init__(self, lookback=20, threshold=0.02):
        self.lookback = lookback
        self.threshold = threshold
    
    def generate_signals(self, data):
        """Générer des signaux basés sur le momentum"""
        price_col = 'Close' if 'Close' in data.columns else 'Price'
        prices = data[price_col]
        
        # Calcul du momentum
        momentum = prices.pct_change(self.lookback)
        
        # Signaux
        signals = pd.Series(0, index=data.index)
        signals[momentum > self.threshold] = 1
        signals[momentum < -self.threshold] = -1
        
        return signals


def main():
    print("=" * 80)
    print("EXEMPLE 4: BACKTESTING DE STRATÉGIES")
    print("=" * 80)
    
    # 1. Générer des données
    print("\n1. Génération de données...")
    
    np.random.seed(42)
    data = DataLoader.generate_ohlcv_data(
        n_days=252 * 2,  # 2 ans
        initial_price=100,
        volatility=0.02,
        random_seed=42
    )
    
    print(f"   ✓ {len(data)} jours de données OHLCV")
    
    # 2. Définir les stratégies
    print("\n" + "-" * 80)
    print("2. DÉFINITION DES STRATÉGIES")
    print("-" * 80)
    
    strategies = {
        'Buy & Hold': BuyAndHoldStrategy(),
        'MA Cross (20/50)': MovingAverageCrossover(short_window=20, long_window=50),
        'MA Cross (50/200)': MovingAverageCrossover(short_window=50, long_window=200),
        'Momentum (20d)': MomentumStrategy(lookback=20, threshold=0.02)
    }
    
    print("\nStratégies à tester:")
    for name in strategies.keys():
        print(f"   • {name}")
    
    # 3. Backtesting
    print("\n" + "-" * 80)
    print("3. BACKTESTING")
    print("-" * 80)
    
    results = {}
    
    for name, strategy in strategies.items():
        print(f"\nBacktest: {name}")
        
        backtester = Backtester(
            data,
            strategy,
            initial_capital=100000,
            commission=0.001,
            slippage=0.0005
        )
        
        stats = backtester.run()
        results[name] = {
            'stats': stats,
            'backtester': backtester
        }
        
        print(f"   Rendement total:    {stats['Total Return']:.2%}")
        print(f"   Rendement annuel:   {stats['Annual Return']:.2%}")
        print(f"   Volatilité:         {stats['Annual Volatility']:.2%}")
        print(f"   Sharpe Ratio:       {stats['Sharpe Ratio']:.3f}")
        print(f"   Max Drawdown:       {stats['Max Drawdown']:.2%}")
        print(f"   Nombre de trades:   {stats['Number of Trades']}")
        print(f"   Win Rate:           {stats['Win Rate']:.2%}")
    
    # 4. Tableau comparatif
    print("\n" + "-" * 80)
    print("4. TABLEAU COMPARATIF")
    print("-" * 80)
    
    comparison = pd.DataFrame({
        name: {
            'Rendement Total': f"{res['stats']['Total Return']:.2%}",
            'Rendement Annuel': f"{res['stats']['Annual Return']:.2%}",
            'Volatilité': f"{res['stats']['Annual Volatility']:.2%}",
            'Sharpe': f"{res['stats']['Sharpe Ratio']:.3f}",
            'Sortino': f"{res['stats']['Sortino Ratio']:.3f}",
            'Calmar': f"{res['stats']['Calmar Ratio']:.3f}",
            'Max DD': f"{res['stats']['Max Drawdown']:.2%}",
            'Trades': res['stats']['Number of Trades'],
            'Win Rate': f"{res['stats']['Win Rate']:.2%}"
        }
        for name, res in results.items()
    })
    
    print("\n" + comparison.T.to_string())
    
    # 5. Visualisations
    print("\n" + "-" * 80)
    print("5. VISUALISATIONS")
    print("-" * 80)
    
    fig = plt.figure(figsize=(16, 12))
    
    # Subplot 1: Performance cumulée
    plt.subplot(3, 2, 1)
    for name, res in results.items():
        portfolio_value = res['backtester'].results['portfolio_value']
        plt.plot(portfolio_value.index, portfolio_value.values, 
                linewidth=2, label=name, alpha=0.8)
    
    plt.title('Performance Cumulée des Stratégies', fontweight='bold', fontsize=12)
    plt.ylabel('Valeur du Portefeuille ($)')
    plt.legend()
    plt.grid(True, alpha=0.3)
    
    # Subplot 2: Drawdown (MA Cross 20/50)
    plt.subplot(3, 2, 2)
    from mon_package.risk.metrics import RiskMetrics
    strategy_name = 'MA Cross (20/50)'
    returns = results[strategy_name]['backtester'].results['returns']
    dd = RiskMetrics.drawdown_series(returns)
    plt.fill_between(dd.index, dd.values, 0, color='red', alpha=0.5)
    plt.title(f'Drawdown - {strategy_name}', fontweight='bold', fontsize=12)
    plt.ylabel('Drawdown')
    plt.grid(True, alpha=0.3)
    
    # Subplot 3: Distribution des rendements quotidiens
    plt.subplot(3, 2, 3)
    for name, res in results.items():
        returns = res['backtester'].results['returns'].dropna()
        plt.hist(returns, bins=30, alpha=0.5, label=name)
    
    plt.title('Distribution des Rendements Quotidiens', fontweight='bold', fontsize=12)
    plt.xlabel('Rendement')
    plt.ylabel('Fréquence')
    plt.legend()
    plt.grid(True, alpha=0.3)
    
    # Subplot 4: Prix avec signaux (MA Cross)
    plt.subplot(3, 2, 4)
    strategy_name = 'MA Cross (20/50)'
    backtester = results[strategy_name]['backtester']
    
    plt.plot(data.index, data['Close'], linewidth=1, color='black', 
            alpha=0.5, label='Prix')
    
    # Achats et ventes
    trades = backtester.trades
    buys = trades[trades['signal'] > 0]
    sells = trades[trades['signal'] < 0]
    
    plt.scatter(buys['date'], buys['price'], color='green', marker='^', 
               s=100, label='Achat', zorder=5)
    plt.scatter(sells['date'], sells['price'], color='red', marker='v', 
               s=100, label='Vente', zorder=5)
    
    plt.title(f'Signaux de Trading - {strategy_name}', fontweight='bold', fontsize=12)
    plt.ylabel('Prix')
    plt.legend()
    plt.grid(True, alpha=0.3)
    
    # Subplot 5: Sharpe Ratio comparaison
    plt.subplot(3, 2, 5)
    sharpe_ratios = [res['stats']['Sharpe Ratio'] for res in results.values()]
    plt.bar(range(len(strategies)), sharpe_ratios, color='skyblue', edgecolor='black')
    plt.xticks(range(len(strategies)), strategies.keys(), rotation=45, ha='right')
    plt.ylabel('Sharpe Ratio')
    plt.title('Comparaison des Sharpe Ratios', fontweight='bold', fontsize=12)
    plt.axhline(0, color='red', linestyle='--', linewidth=1)
    plt.grid(True, alpha=0.3, axis='y')
    
    # Subplot 6: Rendement vs Risque
    plt.subplot(3, 2, 6)
    for name, res in results.items():
        ret = res['stats']['Annual Return']
        vol = res['stats']['Annual Volatility']
        plt.scatter(vol, ret, s=200, alpha=0.7, edgecolors='black')
        plt.annotate(name, (vol, ret), xytext=(5, 5), 
                    textcoords='offset points', fontsize=9)
    
    plt.xlabel('Volatilité Annuelle')
    plt.ylabel('Rendement Annuel')
    plt.title('Rendement vs Risque', fontweight='bold', fontsize=12)
    plt.grid(True, alpha=0.3)
    plt.axhline(0, color='red', linestyle='--', linewidth=1, alpha=0.5)
    plt.axvline(0, color='red', linestyle='--', linewidth=1, alpha=0.5)
    
    plt.tight_layout()
    plt.savefig('backtesting_analysis.png', dpi=300, bbox_inches='tight')
    print("\n   ✓ Graphique sauvegardé: backtesting_analysis.png")
    
    # 6. Meilleure stratégie
    print("\n" + "-" * 80)
    print("6. MEILLEURE STRATÉGIE")
    print("-" * 80)
    
    best_strategy = max(results.items(), 
                       key=lambda x: x[1]['stats']['Sharpe Ratio'])
    
    print(f"\nMeilleure stratégie (Sharpe Ratio): {best_strategy[0]}")
    print(f"   Sharpe Ratio: {best_strategy[1]['stats']['Sharpe Ratio']:.3f}")
    print(f"   Rendement:    {best_strategy[1]['stats']['Total Return']:.2%}")
    print(f"   Max DD:       {best_strategy[1]['stats']['Max Drawdown']:.2%}")
    
    print("\n" + "=" * 80)
    print("Exemple terminé avec succès!")
    print("=" * 80)


if __name__ == "__main__":
    main()