"""
Exemple 3: Analyse de risque

Ce script démontre :
- Calcul de VaR et CVaR
- Métriques de performance
- Analyse de drawdown
- Stress testing
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from quantfinance.risk.var import VaRCalculator, StressTesting
from quantfinance.risk.metrics import RiskMetrics, PerformanceAnalyzer
from quantfinance.utils.data import DataLoader
from quantfinance.utils.plotting import Plotter


def main():
    print("=" * 80)
    print("EXEMPLE 3: ANALYSE DE RISQUE")
    print("=" * 80)
    
    # 1. Générer des données
    print("\n1. Génération de données...")
    
    np.random.seed(42)
    prices = DataLoader.generate_synthetic_prices(
        n_assets=3,
        n_days=252 * 2,
        mu=0.0005,
        sigma=0.02,
        correlation=0.4
    )
    
    prices.columns = ['Portfolio', 'Benchmark', 'Asset_C']
    returns = prices.pct_change().dropna()
    
    portfolio_returns = returns['Portfolio']
    benchmark_returns = returns['Benchmark']
    
    print(f"   ✓ {len(returns)} jours de rendements")
    
    # 2. Value at Risk (VaR)
    print("\n" + "-" * 80)
    print("2. VALUE AT RISK (VaR)")
    print("-" * 80)
    
    confidence_levels = [0.90, 0.95, 0.99]
    
    print("\nVaR Historique:")
    for cl in confidence_levels:
        var = VaRCalculator.historical_var(portfolio_returns, cl)
        print(f"   VaR {cl:.0%}: {var:.4f} ({var:.2%})")
    
    print("\nVaR Paramétrique (Normale):")
    for cl in confidence_levels:
        var = VaRCalculator.parametric_var(portfolio_returns, cl, distribution='normal')
        print(f"   VaR {cl:.0%}: {var:.4f} ({var:.2%})")
    
    print("\nVaR Paramétrique (Student-t):")
    for cl in confidence_levels:
        var = VaRCalculator.parametric_var(portfolio_returns, cl, distribution='student')
        print(f"   VaR {cl:.0%}: {var:.4f} ({var:.2%})")
    
    print("\nVaR EWMA (λ=0.94):")
    for cl in confidence_levels:
        var = VaRCalculator.ewma_var(portfolio_returns, cl, lambda_param=0.94)
        print(f"   VaR {cl:.0%}: {var:.4f} ({var:.2%})")
    
    print("\nVaR Monte Carlo (10,000 simulations):")
    for cl in confidence_levels:
        var = VaRCalculator.monte_carlo_var(
            portfolio_returns, cl, n_simulations=10000, random_seed=42
        )
        print(f"   VaR {cl:.0%}: {var:.4f} ({var:.2%})")
    
    # 3. Expected Shortfall (CVaR)
    print("\n" + "-" * 80)
    print("3. EXPECTED SHORTFALL (CVaR)")
    print("-" * 80)
    
    for cl in [0.95, 0.99]:
        var = VaRCalculator.historical_var(portfolio_returns, cl)
        es = VaRCalculator.expected_shortfall(portfolio_returns, cl, method='historical')
        
        print(f"\nNiveau de confiance: {cl:.0%}")
        print(f"   VaR:  {var:.4f} ({var:.2%})")
        print(f"   CVaR: {es:.4f} ({es:.2%})")
        print(f"   Ratio CVaR/VaR: {es/var:.2f}")
    
    # 4. Métriques de performance
    print("\n" + "-" * 80)
    print("4. MÉTRIQUES DE PERFORMANCE")
    print("-" * 80)
    
    print("\nRatios de performance:")
    sharpe = RiskMetrics.sharpe_ratio(portfolio_returns, risk_free_rate=0.02)
    sortino = RiskMetrics.sortino_ratio(portfolio_returns, risk_free_rate=0.02)
    calmar = RiskMetrics.calmar_ratio(portfolio_returns)
    omega = RiskMetrics.omega_ratio(portfolio_returns, threshold=0.0)
    
    print(f"   Sharpe Ratio:  {sharpe:.3f}")
    print(f"   Sortino Ratio: {sortino:.3f}")
    print(f"   Calmar Ratio:  {calmar:.3f}")
    print(f"   Omega Ratio:   {omega:.3f}")
    
    print("\nMesures de risque:")
    max_dd = RiskMetrics.max_drawdown(portfolio_returns)
    max_dd_dur = RiskMetrics.max_drawdown_duration(portfolio_returns)
    downside_dev = RiskMetrics.downside_deviation(portfolio_returns)
    
    print(f"   Max Drawdown:         {max_dd:.2%}")
    print(f"   Max DD Duration:      {max_dd_dur} jours")
    print(f"   Downside Deviation:   {downside_dev:.2%}")
    
    print("\nStatistiques de distribution:")
    skew = RiskMetrics.skewness(portfolio_returns)
    kurt = RiskMetrics.kurtosis(portfolio_returns, excess=True)
    
    print(f"   Skewness:      {skew:.3f}")
    print(f"   Excess Kurtosis: {kurt:.3f}")
    
    print("\nMétriques vs Benchmark:")
    beta = RiskMetrics.beta(portfolio_returns, benchmark_returns)
    alpha = RiskMetrics.alpha(portfolio_returns, benchmark_returns, risk_free_rate=0.02)
    info_ratio = RiskMetrics.information_ratio(portfolio_returns, benchmark_returns)
    tracking_error = RiskMetrics.tracking_error(portfolio_returns, benchmark_returns)
    
    print(f"   Beta:              {beta:.3f}")
    print(f"   Alpha (annualisé): {alpha:.2%}")
    print(f"   Information Ratio: {info_ratio:.3f}")
    print(f"   Tracking Error:    {tracking_error:.2%}")
    
    # 5. Performance Analyzer
    print("\n" + "-" * 80)
    print("5. ANALYSE COMPLÈTE DE PERFORMANCE")
    print("-" * 80)
    
    analyzer = PerformanceAnalyzer(
        portfolio_returns,
        benchmark_returns=benchmark_returns,
        risk_free_rate=0.02
    )
    
    summary = analyzer.summary_statistics()
    print("\n" + summary.to_string())
    
    # 6. Stress Testing
    print("\n" + "-" * 80)
    print("6. STRESS TESTING")
    print("-" * 80)
    
    # Scénarios de stress
    scenarios = {
        'Market Crash (-20%)': np.array([-0.20, -0.18, -0.22]),
        'Moderate Decline (-10%)': np.array([-0.10, -0.09, -0.11]),
        'Rally (+15%)': np.array([0.15, 0.14, 0.16]),
        'Tech Bubble': np.array([0.30, -0.05, 0.10])
    }
    
    weights = np.array([0.5, 0.3, 0.2])
    
    print("\nAnalyse de scénarios:")
    scenario_results = StressTesting.scenario_analysis(returns, weights, scenarios)
    print("\n" + scenario_results.to_string(index=False))
    
    # Monte Carlo stress test
    print("\nStress Test Monte Carlo (5,000 scénarios):")
    mc_stress = StressTesting.monte_carlo_stress_test(
        returns,
        weights,
        n_scenarios=5000,
        confidence_levels=[0.95, 0.99],
        random_seed=42
    )
    
    print(f"   Rendement moyen:  {mc_stress['mean']:.2%}")
    print(f"   Écart-type:       {mc_stress['std']:.2%}")
    print(f"   Pire scénario:    {mc_stress['min']:.2%}")
    print(f"   Meilleur scénario: {mc_stress['max']:.2%}")
    print(f"   VaR 95%:          {mc_stress['VaR_95']:.2%}")
    print(f"   ES 95%:           {mc_stress['ES_95']:.2%}")
    print(f"   VaR 99%:          {mc_stress['VaR_99']:.2%}")
    print(f"   ES 99%:           {mc_stress['ES_99']:.2%}")
    
    # 7. Visualisations
    print("\n" + "-" * 80)
    print("7. VISUALISATIONS")
    print("-" * 80)
    
    fig = plt.figure(figsize=(16, 12))
    
    # Subplot 1: Drawdown
    plt.subplot(3, 2, 1)
    plotter = Plotter()
    dd_fig = plotter.plot_drawdown(portfolio_returns)
    plt.close(dd_fig)
    
    cumulative = (1 + portfolio_returns).cumprod()
    plt.plot(cumulative.index, cumulative.values, linewidth=2)
    plt.title('Performance Cumulée', fontweight='bold')
    plt.ylabel('Valeur')
    plt.grid(True, alpha=0.3)
    
    # Subplot 2: Drawdown
    plt.subplot(3, 2, 2)
    dd_series = RiskMetrics.drawdown_series(portfolio_returns)
    plt.fill_between(dd_series.index, dd_series.values, 0, color='red', alpha=0.5)
    plt.title('Drawdown', fontweight='bold')
    plt.ylabel('Drawdown')
    plt.grid(True, alpha=0.3)
    
    # Subplot 3: Distribution des rendements
    plt.subplot(3, 2, 3)
    plt.hist(portfolio_returns, bins=50, alpha=0.7, edgecolor='black', density=True)
    mu, sigma = portfolio_returns.mean(), portfolio_returns.std()
    x = np.linspace(portfolio_returns.min(), portfolio_returns.max(), 100)
    plt.plot(x, 1/(sigma * np.sqrt(2 * np.pi)) * np.exp(-0.5 * ((x - mu) / sigma)**2),
            'r-', linewidth=2, label='Normale')
    
    # Marquer VaR et CVaR
    var_95 = VaRCalculator.historical_var(portfolio_returns, 0.95)
    es_95 = VaRCalculator.expected_shortfall(portfolio_returns, 0.95)
    plt.axvline(-var_95, color='orange', linestyle='--', linewidth=2, label=f'VaR 95%: {var_95:.2%}')
    plt.axvline(-es_95, color='red', linestyle='--', linewidth=2, label=f'CVaR 95%: {es_95:.2%}')
    
    plt.title('Distribution des Rendements', fontweight='bold')
    plt.xlabel('Rendement')
    plt.ylabel('Densité')
    plt.legend()
    plt.grid(True, alpha=0.3)
    
    # Subplot 4: QQ Plot
    plt.subplot(3, 2, 4)
    from scipy import stats
    stats.probplot(portfolio_returns, dist="norm", plot=plt)
    plt.title('QQ Plot (Normalité)', fontweight='bold')
    plt.grid(True, alpha=0.3)
    
    # Subplot 5: Rolling Sharpe
    plt.subplot(3, 2, 5)
    rolling_sharpe = portfolio_returns.rolling(60).apply(
        lambda x: RiskMetrics.sharpe_ratio(x, 0.02), raw=True
    )
    plt.plot(rolling_sharpe.index, rolling_sharpe.values, linewidth=2)
    plt.axhline(0, color='red', linestyle='--', alpha=0.5)
    plt.title('Sharpe Ratio Roulant (60 jours)', fontweight='bold')
    plt.ylabel('Sharpe Ratio')
    plt.grid(True, alpha=0.3)
    
    # Subplot 6: Distribution Monte Carlo
    plt.subplot(3, 2, 6)
    plt.hist(mc_stress['scenarios'], bins=50, alpha=0.7, edgecolor='black', density=True)
    plt.axvline(mc_stress['VaR_95'], color='orange', linestyle='--', linewidth=2,
                label=f"VaR 95%: {mc_stress['VaR_95']:.2%}")
    plt.axvline(mc_stress['ES_95'], color='red', linestyle='--', linewidth=2,
                label=f"ES 95%: {mc_stress['ES_95']:.2%}")
    plt.title('Distribution Monte Carlo (Stress Test)', fontweight='bold')
    plt.xlabel('Rendement')
    plt.ylabel('Densité')
    plt.legend()
    plt.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('risk_analysis.png', dpi=300, bbox_inches='tight')
    print("\n   ✓ Graphique sauvegardé: risk_analysis.png")
    
    print("\n" + "=" * 80)
    print("Exemple terminé avec succès!")
    print("=" * 80)


if __name__ == "__main__":
    main()