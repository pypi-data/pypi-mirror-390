## Analyse du Risque (`quantfinance.risk`)

### `RiskMetrics`

Calculateur de métriques de risque.

#### Méthodes :

---

##### `sharpe_ratio(returns, risk_free_rate=0.0, periods_per_year=252) → float`

Calcule le ratio de Sharpe annualisé.

**Exemple :**
```python
sharpe = RiskMetrics.sharpe_ratio(returns, risk_free_rate=0.02)
print("Sharpe:", sharpe)
```

---

##### `sortino_ratio(returns, risk_free_rate=0.0, target_return=None, periods_per_year=252) → float`

Calcule le ratio de Sortino.

**Exemple :**
```python
sortino = RiskMetrics.sortino_ratio(returns, target_return=0.01)
print("Sortino:", sortino)
```

---

##### `calmar_ratio(returns, periods_per_year=252) → float`

Calcule le ratio de Calmar.

**Exemple :**
```python
calmar = RiskMetrics.calmar_ratio(returns)
print("Calmar:", calmar)
```

---

##### `omega_ratio(returns, threshold=0.0) → float`

Calcule le ratio Omega.

**Exemple :**
```python
omega = RiskMetrics.omega_ratio(returns, threshold=0.0)
print("Omega:", omega)
```

---

##### `max_drawdown(returns) → float`

Calcule le drawdown maximum.

**Exemple :**
```python
max_dd = RiskMetrics.max_drawdown(returns)
print("Max DD:", max_dd)
```

---

##### `drawdown_series(returns) → pd.Series`

Calcule la série complète des drawdowns.

**Exemple :**
```python
dd_series = RiskMetrics.drawdown_series(returns)
print(dd_series.head())
```

---

##### `information_ratio(returns, benchmark_returns, periods_per_year=252) → float`

Calcule le ratio d’information.

**Exemple :**
```python
ir = RiskMetrics.information_ratio(returns, benchmark_returns)
print("Information Ratio:", ir)
```

---

##### `beta(returns, market_returns) → float`

Calcule le beta.

**Exemple :**
```python
beta = RiskMetrics.beta(returns, market_returns)
print("Beta:", beta)
```

---

##### `alpha(returns, market_returns, risk_free_rate=0.0, periods_per_year=252) → float`

Calcule l’alpha (Jensen’s alpha).

**Exemple :**
```python
alpha = RiskMetrics.alpha(returns, market_returns, risk_free_rate=0.02)
print("Alpha:", alpha)
```

---

##### `tracking_error(returns, benchmark_returns, periods_per_year=252) → float`

Calcule la tracking error.

**Exemple :**
```python
te = RiskMetrics.tracking_error(returns, benchmark_returns)
print("Tracking Error:", te)
```

---

### `PerformanceAnalyzer`

Analyse complète de performance d’un portefeuille.

#### Méthodes :

---

##### `__init__(returns, benchmark_returns=None, risk_free_rate=0.0, periods_per_year=252)`

Initialise avec les rendements.

**Exemple :**
```python
analyzer = PerformanceAnalyzer(returns_df, benchmark_returns=benchmark_df)
```

---

##### `summary_statistics() → pd.DataFrame`

Génère un résumé complet des statistiques.

**Exemple :**
```python
stats = analyzer.summary_statistics()
print(stats)
```

---

##### `rolling_statistics(window=252, statistics=None) → pd.DataFrame`

Calcule des statistiques roulantes.

**Exemple :**
```python
rolling_stats = analyzer.rolling_statistics(window=63)
print(rolling_stats.head())
```

---

##### `monthly_returns_table() → pd.DataFrame`

Génère une table des rendements mensuels.

**Exemple :**
```python
monthly_table = analyzer.monthly_returns_table()
print(monthly_table)
```

---

##### `plot_performance() → Figure`

Trace les graphiques de performance.

**Exemple :**
```python
fig = analyzer.plot_performance()
plt.show()
```

---

### `VaRCalculator`

Calculateur de Value at Risk (VaR) et Expected Shortfall (CVaR).

#### Méthodes :

---

##### `historical_var(returns, confidence_level=0.95) → float`

Calcule la VaR historique.

**Exemple :**
```python
var = VaRCalculator.historical_var(returns, 0.95)
print("VaR historique:", var)
```

---

##### `parametric_var(returns, confidence_level=0.95, distribution='normal', df=None) → float`

Calcule la VaR paramétrique.

**Exemple :**
```python
var = VaRCalculator.parametric_var(returns, distribution='student')
print("VaR paramétrique:", var)
```

---

##### `ewma_var(returns, confidence_level=0.95, lambda_param=0.94) → float`

Calcule la VaR avec volatilité EWMA.

**Exemple :**
```python
var = VaRCalculator.ewma_var(returns)
print("VaR EWMA:", var)
```

---

##### `monte_carlo_var(returns, confidence_level=0.95, n_simulations=10000, horizon=1, method='parametric', random_seed=None) → float`

Calcule la VaR par simulation Monte Carlo.

**Exemple :**
```python
var = VaRCalculator.monte_carlo_var(returns, method='bootstrap')
print("VaR Monte Carlo:", var)
```

---

##### `expected_shortfall(returns, confidence_level=0.95, method='historical') → float`

Calcule l’Expected Shortfall.

**Exemple :**
```python
es = VaRCalculator.expected_shortfall(returns, method='parametric')
print("Expected Shortfall:", es)
```

---

##### `portfolio_var(returns_matrix, weights, confidence_level=0.95, method='parametric') → float`

Calcule la VaR d’un portefeuille.

**Exemple :**
```python
var = VaRCalculator.portfolio_var(returns_matrix, weights)
print("VaR portefeuille:", var)
```

---

##### `component_var(returns_matrix, weights, confidence_level=0.95) → pd.Series`


Calcule la contribution de chaque actif à la VaR totale (VaR componentielle).

**Exemple :**
```python
comp_var = VaRCalculator.component_var(returns_matrix, weights)
print("Contribution VaR par actif:\n", comp_var)
```

---

##### `marginal_var(returns_matrix, weights, confidence_level=0.95) → pd.Series`

Calcule la VaR marginale (changement de VaR pour une petite augmentation de poids).

**Exemple :**
```python
marginal_var = VaRCalculator.marginal_var(returns_matrix, weights)
print("VaR marginale par actif:\n", marginal_var)
```

---

### `StressTesting`

Analyse de scénarios de stress.

#### Méthodes :

---

##### `scenario_analysis(returns_matrix, weights, scenarios) → pd.DataFrame`

Analyse des scénarios de stress.

**Exemple :**
```python
scenarios = {
    'Crash 2008': np.array([-0.1, -0.15, -0.05]),
    'Covid 2020': np.array([-0.2, -0.1, -0.08])
}
results = StressTesting.scenario_analysis(returns_matrix, weights, scenarios)
print(results)
```

---

##### `historical_stress_test(returns_matrix, weights, stress_periods) → pd.DataFrame`

Teste le portefeuille sur des périodes historiques de stress.

**Exemple :**
```python
stress_periods = {
    '2008 Financial Crisis': ('2008-01-01', '2009-06-30'),
    'Dot-com Bubble': ('2000-01-01', '2002-12-31')
}
results = StressTesting.historical_stress_test(returns_matrix, weights, stress_periods)
print(results)
```

---

##### `monte_carlo_stress_test(returns_matrix, weights, n_scenarios=1000, confidence_levels=[0.95, 0.99], horizon=1, random_seed=None) → Dict`

Stress test Monte Carlo.

**Exemple :**
```python
results = StressTesting.monte_carlo_stress_test(returns_matrix, weights, n_scenarios=5000)
print(f"VaR 95%: {results['VaR_95']:.4f}")
```
