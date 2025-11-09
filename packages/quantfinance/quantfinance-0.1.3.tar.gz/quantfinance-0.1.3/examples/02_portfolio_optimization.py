"""
Exemple 2: Optimisation de portefeuille

Ce script démontre :
- Optimisation de Markowitz
- Frontière efficiente
- Different stratégies d'allocation
- Analyse de risque
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from quantfinance.portfolio.optimization import PortfolioOptimizer, EfficientFrontier
from quantfinance.portfolio.allocation import AssetAllocator
from quantfinance.utils.data import DataLoader
from quantfinance.utils.plotting import Plotter


def main():
    print("=" * 80)
    print("EXEMPLE 2: OPTIMISATION DE PORTEFEUILLE")
    print("=" * 80)
    
    # 1. Générer des données synthétiques
    print("\n1. Génération de données...")
    
    np.random.seed(42)
    prices = DataLoader.generate_synthetic_prices(
        n_assets=5,
        n_days=252 * 3,  # 3 ans
        initial_price=100,
        mu=0.0003,
        sigma=0.015,
        correlation=0.3
    )
    
    prices.columns = ['Tech', 'Finance', 'Healthcare', 'Energy', 'Consumer']
    returns = prices.pct_change().dropna()
    
    print(f"   ✓ {len(prices)} jours de données pour {len(prices.columns)} actifs")
    
    # 2. Statistiques descriptives
    print("\n" + "-" * 80)
    print("2. STATISTIQUES DES ACTIFS")
    print("-" * 80)
    
    stats = pd.DataFrame({
        'Rendement annuel': returns.mean() * 252,
        'Volatilité annuelle': returns.std() * np.sqrt(252),
        'Sharpe Ratio': (returns.mean() * 252) / (returns.std() * np.sqrt(252))
    })
    
    print("\n" + stats.to_string())
    
    # Matrice de corrélation
    print("\nMatrice de corrélation:")
    print(returns.corr().round(3).to_string())
    
    # 3. Optimisation de portefeuille
    print("\n" + "-" * 80)
    print("3. OPTIMISATION DE PORTEFEUILLE")
    print("-" * 80)
    
    optimizer = PortfolioOptimizer(returns, risk_free_rate=0.02)
    
    # a) Portefeuille équipondéré
    print("\na) Portefeuille Équipondéré (1/N)")
    equal_weight = optimizer.equal_weight()
    print(f"   Rendement annuel:    {equal_weight['return']:.2%}")
    print(f"   Volatilité annuelle: {equal_weight['volatility']:.2%}")
    print(f"   Ratio de Sharpe:     {equal_weight['sharpe_ratio']:.3f}")
    
    # b) Variance minimale
    print("\nb) Portefeuille de Variance Minimale")
    min_vol = optimizer.minimize_volatility()
    print(f"   Rendement annuel:    {min_vol['return']:.2%}")
    print(f"   Volatilité annuelle: {min_vol['volatility']:.2%}")
    print(f"   Ratio de Sharpe:     {min_vol['sharpe_ratio']:.3f}")
    print("\n   Allocation:")
    for asset, weight in min_vol['weights'].items():
        print(f"      {asset:12s}: {weight:7.2%}")
    
    # c) Sharpe maximum
    print("\nc) Portefeuille à Sharpe Maximum")
    max_sharpe = optimizer.maximize_sharpe()
    print(f"   Rendement annuel:    {max_sharpe['return']:.2%}")
    print(f"   Volatilité annuelle: {max_sharpe['volatility']:.2%}")
    print(f"   Ratio de Sharpe:     {max_sharpe['sharpe_ratio']:.3f}")
    print("\n   Allocation:")
    for asset, weight in max_sharpe['weights'].items():
        print(f"      {asset:12s}: {weight:7.2%}")
    
    # d) Risk Parity
    print("\nd) Portefeuille Risk Parity")
    risk_parity = optimizer.risk_parity()
    print(f"   Rendement annuel:    {risk_parity['return']:.2%}")
    print(f"   Volatilité annuelle: {risk_parity['volatility']:.2%}")
    print(f"   Ratio de Sharpe:     {risk_parity['sharpe_ratio']:.3f}")
    print("\n   Allocation:")
    for asset, weight in risk_parity['weights'].items():
        print(f"      {asset:12s}: {weight:7.2%}")
    print("\n   Contribution au risque:")
    for asset, contrib in risk_parity['risk_contribution'].items():
        print(f"      {asset:12s}: {contrib:7.2%}")
    
    # 4. Stratégies d'allocation avancées
    print("\n" + "-" * 80)
    print("4. STRATÉGIES D'ALLOCATION AVANCÉES")
    print("-" * 80)
    
    allocator = AssetAllocator(returns)
    
    # a) Hierarchical Risk Parity
    print("\na) Hierarchical Risk Parity (HRP)")
    hrp_weights = allocator.hierarchical_risk_parity()
    perf = optimizer.portfolio_performance(hrp_weights.values)
    print(f"   Rendement annuel:    {perf[0]:.2%}")
    print(f"   Volatilité annuelle: {perf[1]:.2%}")
    print(f"   Ratio de Sharpe:     {perf[2]:.3f}")
    print("\n   Allocation:")
    for asset, weight in hrp_weights.items():
        print(f"      {asset:12s}: {weight:7.2%}")
    
    # b) Maximum Diversification
    print("\nb) Maximum Diversification")
    max_div_weights = allocator.maximum_diversification()
    perf = optimizer.portfolio_performance(max_div_weights.values)
    print(f"   Rendement annuel:    {perf[0]:.2%}")
    print(f"   Volatilité annuelle: {perf[1]:.2%}")
    print(f"   Ratio de Sharpe:     {perf[2]:.3f}")
    print("\n   Allocation:")
    for asset, weight in max_div_weights.items():
        print(f"      {asset:12s}: {weight:7.2%}")
    
    # 5. Frontière efficiente
    print("\n" + "-" * 80)
    print("5. FRONTIÈRE EFFICIENTE")
    print("-" * 80)
    
    frontier = EfficientFrontier(optimizer)
    print("\n   Calcul de la frontière efficiente...")
    
    # 6. Visualisations
    print("\n" + "-" * 80)
    print("6. VISUALISATIONS")
    print("-" * 80)
    
    fig = plt.figure(figsize=(16, 12))
    
    # Subplot 1: Frontière efficiente
    plt.subplot(2, 2, 1)
    frontier_fig = frontier.plot_frontier(
        n_points=50,
        show_assets=True,
        show_max_sharpe=True,
        show_min_vol=True
    )
    plt.close(frontier_fig)  # On va le recréer dans notre subplot
    
    # Recréer manuellement
    plotter = Plotter()
    frontier_fig = plotter.plot_efficient_frontier(
        returns,
        n_portfolios=5000,
        show_cml=True,
        risk_free_rate=0.02
    )
    
    # Subplot 2: Allocation des différents portefeuilles
    plt.subplot(2, 2, 2)
    portfolios = pd.DataFrame({
        'Equal Weight': equal_weight['weights'],
        'Min Vol': min_vol['weights'],
        'Max Sharpe': max_sharpe['weights'],
        'Risk Parity': risk_parity['weights']
    })
    portfolios.T.plot(kind='bar', ax=plt.gca(), width=0.8)
    plt.title('Comparaison des Allocations', fontweight='bold')
    plt.ylabel('Poids')
    plt.xlabel('Stratégie')
    plt.legend(title='Actifs', bbox_to_anchor=(1.05, 1), loc='upper left')
    plt.xticks(rotation=45, ha='right')
    plt.grid(True, alpha=0.3, axis='y')
    
    # Subplot 3: Performance cumulée
    plt.subplot(2, 2, 3)
    strategies_returns = pd.DataFrame({
        'Equal Weight': returns.dot(equal_weight['weights']),
        'Min Vol': returns.dot(min_vol['weights']),
        'Max Sharpe': returns.dot(max_sharpe['weights']),
        'Risk Parity': returns.dot(risk_parity['weights'])
    })
    
    cumulative = (1 + strategies_returns).cumprod()
    cumulative.plot(ax=plt.gca(), linewidth=2)
    plt.title('Performance Cumulée', fontweight='bold')
    plt.ylabel('Valeur (base 1)')
    plt.xlabel('Date')
    plt.legend()
    plt.grid(True, alpha=0.3)
    
    # Subplot 4: Matrice de corrélation
    plt.subplot(2, 2, 4)
    import seaborn as sns
    sns.heatmap(returns.corr(), annot=True, fmt='.2f', cmap='RdBu_r',
                center=0, vmin=-1, vmax=1, square=True,
                cbar_kws={"shrink": 0.8})
    plt.title('Matrice de Corrélation', fontweight='bold')
    
    plt.tight_layout()
    plt.savefig('portfolio_optimization.png', dpi=300, bbox_inches='tight')
    print("\n   ✓ Graphique sauvegardé: portfolio_optimization.png")
    
    # 7. Tableau récapitulatif
    print("\n" + "-" * 80)
    print("7. TABLEAU RÉCAPITULATIF")
    print("-" * 80)
    
    summary = pd.DataFrame({
        'Equal Weight': [equal_weight['return'], equal_weight['volatility'], equal_weight['sharpe_ratio']],
        'Min Vol': [min_vol['return'], min_vol['volatility'], min_vol['sharpe_ratio']],
        'Max Sharpe': [max_sharpe['return'], max_sharpe['volatility'], max_sharpe['sharpe_ratio']],
        'Risk Parity': [risk_parity['return'], risk_parity['volatility'], risk_parity['sharpe_ratio']]
    }, index=['Rendement annuel', 'Volatilité annuelle', 'Sharpe Ratio'])
    
    print("\n" + summary.to_string())
    
    print("\n" + "=" * 80)
    print("Exemple terminé avec succès!")
    print("=" * 80)


if __name__ == "__main__":
    main()