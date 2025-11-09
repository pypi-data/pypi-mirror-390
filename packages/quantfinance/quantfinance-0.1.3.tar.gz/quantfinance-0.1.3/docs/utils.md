## Utils (`quantfinance.utils`)

### `DataLoader`

Chargeur de données financières.

#### Méthodes :

---

##### `load_csv(filepath, date_column='Date', parse_dates=True, index_col=None) → pd.DataFrame`

Charge un fichier CSV.

**Exemple :**
```python
df = DataLoader.load_csv('prices.csv', date_column='Date', index_col='Date')
print(df.head())
```

---

##### `download_yahoo_finance(tickers, start_date, end_date=None, column='Adj Close', interval='1d') → pd.DataFrame`

Télécharge des données depuis Yahoo Finance.

**Exemple :**
```python
prices = DataLoader.download_yahoo_finance(['AAPL', 'MSFT'], '2020-01-01', '2023-12-31')
print(prices.head())
```

---

##### `download_pandas_datareader(tickers, start_date, end_date=None, source='yahoo') → pd.DataFrame`

Télécharge via pandas-datareader.

**Exemple :**
```python
data = DataLoader.download_pandas_datareader(['SPY'], '2020-01-01', source='yahoo')
print(data.head())
```

---

##### `generate_synthetic_prices(n_assets=5, n_days=252, initial_price=100, mu=0.0001, sigma=0.02, correlation=0.3, random_seed=None) → pd.DataFrame`

Génère des prix synthétiques.

**Exemple :**
```python
synthetic = DataLoader.generate_synthetic_prices(n_assets=3, n_days=100, random_seed=42)
print(synthetic.head())
```

---

##### `generate_ohlcv_data(n_days=252, initial_price=100, volatility=0.02, volume_mean=1000000, random_seed=None) → pd.DataFrame`

Génère des données OHLCV synthétiques.

**Exemple :**
```python
ohlcv = DataLoader.generate_ohlcv_data(n_days=50, random_seed=42)
print(ohlcv.head())
```

---

### `DataCleaner`

Nettoyage et préparation de données.

#### Méthodes :

---

##### `handle_missing_values(data, method='ffill', limit=None) → pd.DataFrame`

Gère les valeurs manquantes.

**Exemple :**
```python
cleaned = DataCleaner.handle_missing_values(data, method='interpolate')
print(cleaned.head())
```

---

##### `remove_outliers(data, n_std=3.0, method='clip') → pd.DataFrame`

Retire ou ajuste les valeurs aberrantes.

**Exemple :**
```python
cleaned = DataCleaner.remove_outliers(data, method='winsorize')
print(cleaned.head())
```

---

##### `winsorize(data, lower_percentile=0.05, upper_percentile=0.95) → pd.DataFrame`

Winsorise les données.

**Exemple :**
```python
winsorized = DataCleaner.winsorize(data, lower_percentile=0.01, upper_percentile=0.99)
print(winsorized.head())
```

---

##### `calculate_returns(prices, method='simple', periods=1) → pd.DataFrame`

Calcule les rendements.

**Exemple :**
```python
returns = DataCleaner.calculate_returns(prices, method='log')
print(returns.head())
```

---

##### `align_data(*dataframes, join='inner') → Tuple[pd.DataFrame, ...]`

Aligne plusieurs DataFrames sur les mêmes dates.

**Exemple :**
```python
aligned = DataCleaner.align_data(prices, volumes, join='outer')
print(aligned[0].head())
```

---

##### `resample_data(data, frequency, method='last') → pd.DataFrame`

Rééchantillonne les données.

**Exemple :**
```python
monthly = DataCleaner.resample_data(prices, 'M', method='mean')
print(monthly.head())
```

---

### `DataTransformer`

Transformations de données financières.

#### Méthodes :

---

##### `normalize(data, method='zscore') → pd.DataFrame`

Normalise les données.

**Exemple :**
```python
normalized = DataTransformer.normalize(data, method='minmax')
print(normalized.head())
```

---

##### `add_technical_indicators(data, indicators=None) → pd.DataFrame`

Ajoute des indicateurs techniques.

**Exemple :**
```python
with_indicators = DataTransformer.add_technical_indicators(data, ['SMA', 'RSI'])
print(with_indicators.head())
```

---

##### `create_lagged_features(data, lags=[1, 2, 3, 5]) → pd.DataFrame`

Crée des features retardées.

**Exemple :**
```python
lagged = DataTransformer.create_lagged_features(data, lags=[1, 5])
print(lagged.head())
```

---

##### `rolling_statistics(data, windows=[20, 60, 120]) → pd.DataFrame`

Calcule des statistiques roulantes.

**Exemple :**
```python
stats = DataTransformer.rolling_statistics(data, windows=[20, 50])
print(stats.head())
```

---

## 6. 📈 Visualisation (`quantfinance.utils.plotting`)

### `Plotter`

Visualisations financières de base.

#### Méthodes :

---

##### `plot_prices(prices, title="Prix des Actifs", figsize=(12, 6), normalize=False) → Figure`

Trace l’évolution des prix.

**Exemple :**
```python
fig = Plotter.plot_prices(prices, normalize=True)
plt.show()
```

---

##### `plot_returns(returns, title="Distribution des Rendements", figsize=(14, 8), bins=50) → Figure`

Trace les distributions de rendements.

**Exemple :**
```python
fig = Plotter.plot_returns(returns, bins=30)
plt.show()
```

---

##### `plot_correlation_matrix(returns, title="Matrice de Corrélation", figsize=(10, 8), annot=True, method='pearson') → Figure`

Trace la matrice de corrélation.

**Exemple :**
```python
fig = Plotter.plot_correlation_matrix(returns, method='spearman')
plt.show()
```

---

##### `plot_drawdown(returns, title="Analyse de Drawdown", figsize=(12, 8)) → Figure`

Trace l’analyse de drawdown.

**Exemple :**
```python
fig = Plotter.plot_drawdown(returns)
plt.show()
```

---

##### `plot_portfolio_weights(weights, title="Allocation du Portefeuille", figsize=(12, 6), kind='both') → Figure`

Trace les poids du portefeuille.

**Exemple :**
```python
fig = Plotter.plot_portfolio_weights(weights, kind='pie')
plt.show()
```

---

##### `plot_efficient_frontier(returns, n_portfolios=10000, figsize=(12, 8), show_cml=True, risk_free_rate=0.02) → Figure`

Trace la frontière efficiente avec simulation Monte Carlo.

**Exemple :**
```python
fig = Plotter.plot_efficient_frontier(returns, n_portfolios=5000)
plt.show()
```

---

### `FinancialPlotter`

Graphiques financiers avancés.

#### Méthodes :

---

##### `plot_candlestick(data, title="Graphique en Chandelier", figsize=(14, 8), volume=True) → Figure`

Trace un graphique en chandelier.

**Exemple :**
```python
fig = FinancialPlotter.plot_candlestick(ohlcv, volume=True)
plt.show()
```

---

##### `plot_risk_return_scatter(returns, figsize=(12, 8), periods_per_year=252) → Figure`

Nuage de points risque-rendement.

**Exemple :**
```python
fig = FinancialPlotter.plot_risk_return_scatter(returns)
plt.show()
```

---

##### `plot_rolling_metrics(returns, window=60, figsize=(14, 10), periods_per_year=252) → Figure`

Trace les métriques roulantes.

**Exemple :**
```python
fig = FinancialPlotter.plot_rolling_metrics(returns, window=30)
plt.show()
```

---
