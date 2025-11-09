"""
Exemple 5: Workflow complet

Workflow complet de A à Z :
1. Chargement de données
2. Analyse exploratoire
3. Optimisation de portefeuille
4. Analyse de risque
5. Backtesting
6. Reporting
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime

from quantfinance.utils.data import DataLoader, DataCleaner
from quantfinance.portfolio.optimization import PortfolioOptimizer
from quantfinance.risk.var import VaRCalculator
from quantfinance.risk.metrics import PerformanceAnalyzer
from quantfinance.utils.plotting import Plotter


def main():
    print("=" * 80)
    print("EXEMPLE 5: WORKFLOW COMPLET D'ANALYSE QUANTITATIVE")
    print("=" * 80)
    print(f"\nDate: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # ÉTAPE 1: Chargement des données
    print("\n" + "=" * 80)
    print("ÉTAPE 1: CHARGEMENT DES DONNÉES")
    print("=" * 80)
    
    print("\nGénération de données synthétiques...")
    prices = DataLoader.generate_synthetic_prices(
        n_assets=4,
        n_days=252 * 3,
        initial_price=100,
        mu=0.0004,
        sigma=0.018,
        correlation=0.35,
        random_seed=42
    )
    
    prices.columns = ['US_Equities', 'EU_Equities', 'Bonds', 'Commodities']
    
    print(f"✓ Données chargées: {len(prices)} jours, {len(prices.columns)} actifs")
    print(f"  Période: {prices.index[0].date()} à {prices.index[-1].date()}")
    
    # ÉTAPE 2: Nettoyage et préparation
    print("\n" + "=" * 80)
    print("ÉTAPE 2: NETTOYAGE ET PRÉPARATION")
    print("=" * 80)
    
    returns = DataCleaner.calculate_returns(prices, method='simple')
    returns = DataCleaner.handle_missing_values(returns, method='ffill')
    
    print(f"✓ Rendements calculés: {len(returns)} observations")
    print(f"✓ Valeurs manquantes traitées")
    
    # ÉTAPE 3: Analyse exploratoire
    print("\n" + "=" * 80)
    print("ÉTAPE 3: ANALYSE EXPLORATOIRE")
    print("=" * 80)
    
    print("\nStatistiques descriptives:")
    stats = pd.DataFrame({
        'Rendement moyen (quotidien)': returns.mean(),
        'Rendement annualisé': returns.mean() * 252,
        'Volatilité annualisée': returns.std() * np.sqrt(252),
        'Skewness': returns.apply(lambda x: x.skew()),
        'Kurtosis': returns.apply(lambda x: x.kurtosis())
    })
    print("\n" + stats.to_string())
    
    print("\nMatrice de corrélation:")
    print(returns.corr().round(3).to_string())
    
    # ÉTAPE 4: Optimisation de portefeuille
    print("\n" + "=" * 80)
    print("ÉTAPE 4: OPTIMISATION DE PORTEFEUILLE")
    print("=" * 80)
    
    optimizer = PortfolioOptimizer(returns, risk_free_rate=0.02)
    
    # Différentes stratégies
    strategies = {}
    
    print("\nCalcul des allocations optimales...")
    
    strategies['Equal Weight'] = optimizer.equal_weight()
    strategies['Min Volatility'] = optimizer.minimize_volatility()
    strategies['Max Sharpe'] = optimizer.maximize_sharpe()
    strategies['Risk Parity'] = optimizer.risk_parity()
    
    print("\nRésumé des stratégies:")
    summary = pd.DataFrame({
        name: {
            'Rendement': f"{s['return']:.2%}",
            'Volatilité': f"{s['volatility']:.2%}",
            'Sharpe': f"{s['sharpe_ratio']:.3f}"
        }
        for name, s in strategies.items()
    }).T
    print("\n" + summary.to_string())
    
    # Sélectionner la stratégie Max Sharpe pour la suite
    selected_strategy = 'Max Sharpe'
    selected_weights = strategies[selected_strategy]['weights']
    
    print(f"\n✓ Stratégie sélectionnée: {selected_strategy}")
    print("\nAllocation:")
    for asset, weight in selected_weights.items():
        print(f"  {asset:15s}: {weight:7.2%}")
    
    # ÉTAPE 5: Analyse de risque
    print("\n" + "=" * 80)
    print("ÉTAPE 5: ANALYSE DE RISQUE")
    print("=" * 80)
    
    portfolio_returns = returns.dot(selected_weights)
    
    print("\nValue at Risk:")
    for cl in [0.95, 0.99]:
        var_hist = VaRCalculator.historical_var(portfolio_returns, cl)
        es_hist = VaRCalculator.expected_shortfall(portfolio_returns, cl)
        print(f"  Niveau {cl:.0%}:")
        print(f"    VaR:  {var_hist:.4f} ({var_hist:.2%})")
        print(f"    CVaR: {es_hist:.4f} ({es_hist:.2%})")
    
    from quantfinance.risk.metrics import RiskMetrics
    
    print("\nMétriques de risque:")
    print(f"  Max Drawdown: {RiskMetrics.max_drawdown(portfolio_returns):.2%}")
    print(f"  Sharpe Ratio: {RiskMetrics.sharpe_ratio(portfolio_returns, 0.02):.3f}")
    print(f"  Sortino Ratio: {RiskMetrics.sortino_ratio(portfolio_returns, 0.02):.3f}")
    
    # ÉTAPE 6: Performance Analysis
    print("\n" + "=" * 80)
    print("ÉTAPE 6: ANALYSE DE PERFORMANCE")
    print("=" * 80)
    
    analyzer = PerformanceAnalyzer(portfolio_returns, risk_free_rate=0.02)
    full_stats = analyzer.summary_statistics()
    
    print("\nRapport complet:")
    print(full_stats.to_string())
    
    # ÉTAPE 7: Génération de rapports visuels
    print("\n" + "=" * 80)
    print("ÉTAPE 7: GÉNÉRATION DE RAPPORTS VISUELS")
    print("=" * 80)
    
    fig = plt.figure(figsize=(20, 12))
    
    # 1. Prix normalisés
    plt.subplot(3, 3, 1)
    (prices / prices.iloc[0] * 100).plot(ax=plt.gca(), linewidth=2)
    plt.title('Prix Normalisés (Base 100)', fontweight='bold')
    plt.ylabel('Valeur')
    plt.legend(loc='best')
    plt.grid(True, alpha=0.3)
    
    # 2. Allocation du portefeuille
    plt.subplot(3, 3, 2)
    selected_weights.plot(kind='bar', color='skyblue', edgecolor='black')
    plt.title(f'Allocation - {selected_strategy}', fontweight='bold')
    plt.ylabel('Poids')
    plt.xticks(rotation=45, ha='right')
    plt.grid(True, alpha=0.3, axis='y')
    
    # 3. Performance cumulée
    plt.subplot(3, 3, 3)
    cumulative = (1 + portfolio_returns).cumprod()
    plt.plot(cumulative.index, cumulative.values, linewidth=2, color='green')
    plt.title('Performance Cumulée du Portefeuille', fontweight='bold')
    plt.ylabel('Valeur (base 1)')
    plt.grid(True, alpha=0.3)
    
    # 4. Matrice de corrélation
    plt.subplot(3, 3, 4)
    import seaborn as sns
    sns.heatmap(returns.corr(), annot=True, fmt='.2f', cmap='coolwarm',
                center=0, vmin=-1, vmax=1, square=True, cbar_kws={"shrink": 0.8})
    plt.title('Matrice de Corrélation', fontweight='bold')
    
    # 5. Distribution des rendements
    plt.subplot(3, 3, 5)
    plt.hist(portfolio_returns, bins=50, alpha=0.7, edgecolor='black', density=True)
    mu, sigma = portfolio_returns.mean(), portfolio_returns.std()
    x = np.linspace(portfolio_returns.min(), portfolio_returns.max(), 100)
    plt.plot(x, 1/(sigma * np.sqrt(2 * np.pi)) * np.exp(-0.5 * ((x - mu) / sigma)**2),
            'r-', linewidth=2, label='Normale')
    plt.title('Distribution des Rendements', fontweight='bold')
    plt.xlabel('Rendement')
    plt.ylabel('Densité')
    plt.legend()
    plt.grid(True, alpha=0.3)
    
    # 6. Drawdown
    plt.subplot(3, 3, 6)
    dd = RiskMetrics.drawdown_series(portfolio_returns)
    plt.fill_between(dd.index, dd.values, 0, color='red', alpha=0.5)
    plt.title('Drawdown', fontweight='bold')
    plt.ylabel('Drawdown')
    plt.grid(True, alpha=0.3)
    
    # 7. Rolling Sharpe
    plt.subplot(3, 3, 7)
    rolling_sharpe = portfolio_returns.rolling(60).apply(
        lambda x: RiskMetrics.sharpe_ratio(x, 0.02), raw=True
    )
    plt.plot(rolling_sharpe.index, rolling_sharpe.values, linewidth=2)
    plt.axhline(0, color='red', linestyle='--', alpha=0.5)
    plt.title('Sharpe Ratio Roulant (60j)', fontweight='bold')
    plt.ylabel('Sharpe Ratio')
    plt.grid(True, alpha=0.3)
    
    # 8. Rolling Volatilité
    plt.subplot(3, 3, 8)
    rolling_vol = portfolio_returns.rolling(60).std() * np.sqrt(252)
    plt.plot(rolling_vol.index, rolling_vol.values, linewidth=2, color='orange')
    plt.title('Volatilité Roulante (60j, annualisée)', fontweight='bold')
    plt.ylabel('Volatilité')
    plt.grid(True, alpha=0.3)
    
    # 9. Rendements mensuels
    plt.subplot(3, 3, 9)
    monthly_returns = portfolio_returns.resample('M').apply(lambda x: (1 + x).prod() - 1)
    colors = ['green' if x > 0 else 'red' for x in monthly_returns]
    plt.bar(range(len(monthly_returns)), monthly_returns.values, color=colors, alpha=0.7)
    plt.title('Rendements Mensuels', fontweight='bold')
    plt.ylabel('Rendement')
    plt.axhline(0, color='black', linewidth=0.5)
    plt.grid(True, alpha=0.3, axis='y')
    
    plt.tight_layout()
    plt.savefig('complete_workflow_report.png', dpi=300, bbox_inches='tight')
    print("\n✓ Rapport visuel sauvegardé: complete_workflow_report.png")
    
    # ÉTAPE 8: Export des résultats
    print("\n" + "=" * 80)
    print("ÉTAPE 8: EXPORT DES RÉSULTATS")
    print("=" * 80)
    
    # Créer un rapport Excel
    with pd.ExcelWriter('portfolio_report.xlsx', engine='openpyxl') as writer:
        # Feuille 1: Statistiques des actifs
        stats.to_excel(writer, sheet_name='Asset Statistics')
        
        # Feuille 2: Allocations
        allocations = pd.DataFrame({
            name: s['weights'] for name, s in strategies.items()
        })
        allocations.to_excel(writer, sheet_name='Allocations')
        
        # Feuille 3: Performance des stratégies
        summary.to_excel(writer, sheet_name='Strategy Performance')
        
        # Feuille 4: Analyse de risque
        full_stats.to_excel(writer, sheet_name='Risk Analysis')
    
    print("✓ Rapport Excel sauvegardé: portfolio_report.xlsx")
    
    # Résumé final
    print("\n" + "=" * 80)
    print("RÉSUMÉ FINAL")
    print("=" * 80)
    
    print(f"\nPortefeuille optimisé ({selected_strategy}):")
    print(f"  Rendement annuel espéré:  {strategies[selected_strategy]['return']:.2%}")
    print(f"  Volatilité annuelle:      {strategies[selected_strategy]['volatility']:.2%}")
    print(f"  Ratio de Sharpe:          {strategies[selected_strategy]['sharpe_ratio']:.3f}")
    print(f"  VaR 95% (quotidienne):    {VaRCalculator.historical_var(portfolio_returns, 0.95):.2%}")
    print(f"  Max Drawdown:             {RiskMetrics.max_drawdown(portfolio_returns):.2%}")
    
    print("\n" + "=" * 80)
    print("WORKFLOW COMPLET TERMINÉ AVEC SUCCÈS!")
    print("=" * 80)
    
    print("\nFichiers générés:")
    print("  • complete_workflow_report.png")
    print("  • portfolio_report.xlsx")


if __name__ == "__main__":
    main()