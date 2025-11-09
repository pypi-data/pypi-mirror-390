## Portfolio Optimization (`quantfinance.portfolio`)

### `PortfolioOptimizer`

Classe principale pour l’optimisation de portefeuille.

#### Méthodes :

---

##### `__init__(returns, risk_free_rate=0.02)`

Initialise l’optimiseur avec les rendements et le taux sans risque.

**Exemple :**
```python
optimizer = PortfolioOptimizer(returns_df, risk_free_rate=0.03)
```

---

##### `equal_weight() → Dict`

Crée un portefeuille équipondéré (poids égaux).

**Exemple :**
```python
result = optimizer.equal_weight()
print("Poids:", result['weights'])
print("Rendement:", result['return'])
```

---

##### `minimize_volatility(constraints=None) → Dict`

Minimise la volatilité du portefeuille.

**Exemple :**
```python
result = optimizer.minimize_volatility()
print("Volatilité minimale:", result['volatility'])
```

---

##### `maximize_sharpe(constraints=None) → Dict`

Maximise le ratio de Sharpe.

**Exemple :**
```python
result = optimizer.maximize_sharpe()
print("Sharpe max:", result['sharpe_ratio'])
```

---

##### `maximize_return(target_volatility) → Result`

Maximise le rendement sous contrainte de volatilité.

**Exemple :**
```python
result = optimizer.maximize_return(target_volatility=0.18)
print("Rendement max:", result['return'])
```

---

##### `risk_parity() → Dict`

Crée un portefeuille de parité de risque (Risk Parity).

**Exemple :**
```python
result = optimizer.risk_parity()
print("Contribution au risque:", result['risk_contribution'])
```

---

### `EfficientFrontier`

Calcule et visualise la frontière efficiente.

#### Méthodes :

---

##### `__init__(optimizer)`

Initialise avec un `PortfolioOptimizer`.

**Exemple :**
```python
frontier = EfficientFrontier(optimizer)
```

---

##### `calculate_frontier(n_points=50, min_return=None, max_return=None) → pd.DataFrame`

Calcule les points de la frontière efficiente.

**Exemple :**
```python
frontier_data = frontier.calculate_frontier(n_points=50)
print(frontier_data.head())
```

---

##### `plot(show_assets=True, show_optimal=True, figsize=(12, 8)) → Figure`

Trace la frontière efficiente.

**Exemple :**
```python
fig = frontier.plot()
plt.show()
```

---

### `AssetAllocator`

Stratégies d’allocation d’actifs avancées.

#### Méthodes :

---

##### `__init__(returns)`

Initialise avec les rendements.

**Exemple :**
```python
allocator = AssetAllocator(returns_df)
```

---

##### `hierarchical_risk_parity() → pd.Series`

Allocation selon Hierarchical Risk Parity (HRP).

**Exemple :**
```python
weights = allocator.hierarchical_risk_parity()
print("Poids HRP:", weights)
```

---

##### `minimum_correlation() → pd.Series`

Minimise la corrélation moyenne du portefeuille.

**Exemple :**
```python
weights = allocator.minimum_correlation()
print("Poids min corr:", weights)
```

---

##### `maximum_diversification() → pd.Series`

Maximise le ratio de diversification.

**Exemple :**
```python
weights = allocator.maximum_diversification()
print("Poids max div:", weights)
```

---

### `Rebalancer`

Gère le rééquilibrage de portefeuille.

#### Méthodes :

---

##### `__init__(target_weights, prices, initial_capital=100000.0, transaction_cost=0.001)`

Initialise avec les poids cibles, les prix, etc.

**Exemple :**
```python
rebalancer = Rebalancer(target_weights, prices_df, initial_capital=100000)
```

---

##### `periodic_rebalancing(frequency='monthly') → pd.DataFrame`

Rééquilibre à intervalles fixes.

**Exemple :**
```python
results = rebalancer.periodic_rebalancing(frequency='quarterly')
print(results.head())
```

---

##### `threshold_rebalancing(threshold=0.05) → pd.DataFrame`

Rééquilibre quand un poids dévie de plus de `threshold`.

**Exemple :**
```python
results = rebalancer.threshold_rebalancing(threshold=0.03)
print(results.head())
```

---

### `Backtester`

Framework de backtesting.

#### Méthodes :

---

##### `__init__(data, strategy, initial_capital=10000.0, commission=0.001)`

Initialise avec les données, la stratégie, etc.

**Exemple :**
```python
backtester = Backtester(returns_df, strategy, initial_capital=10000)
```

---

##### `run_backtest() → Dict`

Exécute le backtest.

**Exemple :**
```python
results = backtester.run_backtest()
print("Rendement:", results['Return'])
```

---

##### `plot_results(figsize=(14, 10)) → Figure`

Trace les résultats du backtest.

**Exemple :**
```python
fig = backtester.plot_results()
plt.show()
```



## Backtesting (`quantfinance.portfolio.backtesting`)

### `Strategy` (Classe abstraite)

Base pour les stratégies de trading.

#### Méthode :

---

##### `generate_signals(data) → pd.Series`

Génère les signaux de trading (à implémenter dans les sous-classes).

---

### `BuyAndHoldStrategy`

Stratégie Buy & Hold simple.

#### Méthode :

---

##### `generate_signals(data) → pd.Series`

Retourne toujours 1 (long).

**Exemple :**
```python
strategy = BuyAndHoldStrategy()
signals = strategy.generate_signals(prices_df)
print(signals.head())
```

---

### `MovingAverageCrossover`

Stratégie de croisement de moyennes mobiles.

#### Méthode :

---

##### `__init__(short_window=20, long_window=50)`

Initialise avec les périodes des moyennes mobiles.

**Exemple :**
```python
strategy = MovingAverageCrossover(short_window=10, long_window=30)
```

---

##### `generate_signals(data) → pd.Series`

Génère les signaux basés sur le croisement des MA.

**Exemple :**
```python
signals = strategy.generate_signals(prices_df)
print(signals.head())
```

---

### `Backtester`

Framework de backtesting.

#### Méthodes :

---

##### `__init__(data, strategy, initial_capital=10000.0, commission=0.001)`

Initialise avec les données et la stratégie.

**Exemple :**
```python
backtester = Backtester(prices_df, strategy, initial_capital=10000, commission=0.0005)
```

---

##### `run() → Dict`

Exécute le backtest.

**Exemple :**
```python
results = backtester.run()
print("Rendement:", results['Total Return'])
```

---

##### `plot_results(figsize=(14, 10)) → Figure`

Trace les résultats du backtest.

**Exemple :**
```python
fig = backtester.plot_results()
plt.show()
```

---

---