# QuantFinance 

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![PyPI version](https://badge.fury.io/py/quantfinance.svg)](https://badge.fury.io/py/quantfinance)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Build Status](https://github.com/Mafoya1er/quantfinance/workflows/CI/badge.svg)](https://github.com/Mafoya1er/quantfinance/actions)
[![codecov](https://codecov.io/gh/Mafoya1er/quantfinance/branch/main/graph/badge.svg)](https://codecov.io/gh/Mafoya1er/quantfinance)
[![Documentation Status](https://readthedocs.org/projects/quantfinance/badge/?version=latest)](https://quantfinance.readthedocs.io/en/latest/?badge=latest)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

> Package Python professionnel pour la finance quantitative

[Documentation](https://quantfinance.readthedocs.io) | [PyPI](https://pypi.org/project/quantfinance/) | [GitHub](https://github.com/Mafoya1er/quantfinance)

## Fonctionnalités

### Pricing d'Instruments Financiers
- **Options** : Black-Scholes, Binomial Tree, Monte Carlo
- **Grecques** : Delta, Gamma, Vega, Theta, Rho
- **Volatilité Implicite** : Méthode de Newton-Raphson
- **Options Exotiques** : Asiatiques, Barrières
- **Obligations** : Pricing, YTM, Duration, Convexité

### Gestion des Risques
- **Value at Risk (VaR)** : Historique, Paramétrique, EWMA, Monte Carlo
- **Expected Shortfall (CVaR)**
- **Métriques** : Sharpe, Sortino, Calmar, Omega, Information Ratio
- **Drawdown** : Maximum, Duration, Série temporelle
- **Stress Testing** : Scénarios, Analyse historique, Simulation

### Optimisation de Portefeuille
- **Markowitz** : Variance minimale, Sharpe maximum, Frontière efficiente
- **Risk Parity** : Contribution égale au risque
- **Black-Litterman** : Intégration de vues d'investissement
- **Hierarchical Risk Parity (HRP)**
- **Maximum Diversification**
- **Rééquilibrage** : Périodique, Seuils, Bandes de tolérance

### Backtesting
- Framework de backtesting flexible
- Stratégies prédéfinies (MA Crossover, Momentum, etc.)
- Prise en compte des coûts de transaction
- Analyse de performance détaillée

### Utilitaires
- Chargement de données (CSV, Yahoo Finance, API)
- Génération de données synthétiques
- Nettoyage et préparation de données
- Indicateurs techniques (SMA, EMA, RSI, MACD, Bollinger Bands)
- Visualisations avancées

## Installation

### Via pip (recommandé)

```bash
pip install quantfinance
```

### Depuis les sources

```bash
git clone https://github.com/Mafoya1er/quantfinance.git
cd quantfinance
pip install -e .
```

### Avec dépendances optionnelles

```bash
# Pour l'analyse de données
pip install quantfinance[data]

# Pour le développement
pip install quantfinance[dev]

# Tout installer
pip install quantfinance[all]
```

## Démarrage Rapide

### Pricing d'Options

```python
from quantfinance.pricing.options import BlackScholes

# Option call européenne
bs = BlackScholes(S=100, K=105, T=1, r=0.05, sigma=0.25, option_type='call')

print(f"Prix: {bs.price():.2f}")
print(f"Delta: {bs.delta():.4f}")
print(f"Gamma: {bs.gamma():.6f}")
print(f"Vega: {bs.vega():.4f}")

# Volatilité implicite
market_price = 8.50
implied_vol = bs.implied_volatility(market_price)
print(f"Vol implicite: {implied_vol:.2%}")
```

### Optimisation de Portefeuille

```python
from quantfinance.portfolio.optimization import PortfolioOptimizer, EfficientFrontier
from quantfinance.utils.data import DataLoader

# Charger des données
prices = DataLoader.generate_synthetic_prices(n_assets=5, n_days=252*3)
returns = prices.pct_change().dropna()

# Optimiser
optimizer = PortfolioOptimizer(returns, risk_free_rate=0.02)

# Sharpe maximum
max_sharpe = optimizer.maximize_sharpe()
print(f"Rendement: {max_sharpe['return']:.2%}")
print(f"Sharpe: {max_sharpe['sharpe_ratio']:.3f}")
print("\nPoids:")
print(max_sharpe['weights'])

# Frontière efficiente
frontier = EfficientFrontier(optimizer)
frontier.plot()
```

### Analyse de Risque

```python
from quantfinance.risk.var import VaRCalculator
from quantfinance.risk.metrics import RiskMetrics, PerformanceAnalyzer

# VaR et CVaR
var_95 = VaRCalculator.historical_var(returns.iloc[:, 0], 0.95)
es_95 = VaRCalculator.expected_shortfall(returns.iloc[:, 0], 0.95)

print(f"VaR 95%: {var_95:.2%}")
print(f"CVaR 95%: {es_95:.2%}")

# Analyse complète
analyzer = PerformanceAnalyzer(returns.iloc[:, 0], risk_free_rate=0.02)
summary = analyzer.summary_statistics()
print(summary)
```

### Backtesting

```python
from quantfinance.portfolio.backtesting import Backtester, MovingAverageCrossover
from quantfinance.utils.data import DataLoader

# Données OHLCV
data = DataLoader.generate_ohlcv_data(n_days=500)

# Stratégie
strategy = MovingAverageCrossover(short_window=20, long_window=50)

# Backtest
backtester = Backtester(data, strategy, initial_capital=100000)
results = backtester.run()

print(f"Rendement: {results['Total Return']:.2%}")
print(f"Sharpe: {results['Sharpe Ratio']:.3f}")
print(f"Max DD: {results['Max Drawdown']:.2%}")

# Visualisation
backtester.plot_results()
```

## Documentation

Documentation complète disponible sur [ReadTheDocs](https://quantfinance.readthedocs.io).

### Guides

- [Installation](https://quantfinance.readthedocs.io/en/latest/user_guide/installation.html)
- [Démarrage Rapide](https://quantfinance.readthedocs.io/en/latest/user_guide/quickstart.html)
- [Tutoriels](https://quantfinance.readthedocs.io/en/latest/user_guide/tutorials.html)
- [Exemples](https://quantfinance.readthedocs.io/en/latest/user_guide/examples.html)

### Référence API

- [Pricing](https://quantfinance.readthedocs.io/en/latest/api/pricing.html)
- [Risk](https://quantfinance.readthedocs.io/en/latest/api/risk.html)
- [Portfolio](https://quantfinance.readthedocs.io/en/latest/api/portfolio.html)
- [Utils](https://quantfinance.readthedocs.io/en/latest/api/utils.html)

## Tests

```bash
# Lancer tous les tests
pytest

# Avec couverture
pytest --cov=quantfinance --cov-report=html

# Tests rapides seulement
pytest -m "not slow"
```

##  Contribution

Les contributions sont les bienvenues ! Consultez [CONTRIBUTING.md](CONTRIBUTING.md).

1. Fork le projet
2. Créez une branche (`git checkout -b feature/AmazingFeature`)
3. Committez (`git commit -m 'feat: Add AmazingFeature'`)
4. Push (`git push origin feature/AmazingFeature`)
5. Ouvrez une Pull Request

##  Licence

Ce projet est sous licence MIT. Voir [LICENSE](LICENSE) pour plus de détails.

## Remerciements

- [NumPy](https://numpy.org/) - Calculs numériques
- [Pandas](https://pandas.pydata.org/) - Manipulation de données
- [SciPy](https://scipy.org/) - Outils scientifiques
- [Matplotlib](https://matplotlib.org/) - Visualisations

## Contact

Marcel ALOEKPO - [LinkedIn](https://www.linkedin.com/in/marcel-aloekpo-21b42619a) -marcelaloekpo@gmail.com

Projet: [https://github.com/Mafoya1er/quantfinance](https://github.com/Mafoya1er/quantfinance)

## Support

Si vous trouvez ce projet utile, n'hésitez pas à lui donner une étoile sur [GitHub](https://github.com/Mafoya1er/quantfinance) !

##  Statistiques

![GitHub stars](https://img.shields.io/github/stars/Mafoya1er/quantfinance?style=social)
![GitHub forks](https://img.shields.io/github/forks/Mafoya1er/quantfinance?style=social)
![GitHub watchers](https://img.shields.io/github/watchers/Mafoya1er/quantfinance?style=social)
![GitHub contributors](https://img.shields.io/github/contributors/Mafoya1er/quantfinance)
![GitHub issues](https://img.shields.io/github/issues/Mafoya1er/quantfinance)
![GitHub pull requests](https://img.shields.io/github/issues-pr/Mafoya1er/quantfinance)

---

**Made with ❤️ for quantitative finance**
