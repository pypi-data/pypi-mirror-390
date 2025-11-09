Démarrage rapide
================

Ce guide vous aidera à démarrer rapidement avec QuantFinance.

Premier exemple : Pricing d'option
-----------------------------------

.. code-block:: python

   from quantfinance.pricing.options import BlackScholes

   # Créer une option call européenne
   option = BlackScholes(
       S=100,      # Prix spot du sous-jacent
       K=105,      # Prix d'exercice (strike)
       T=1,        # Temps jusqu'à maturité (années)
       r=0.05,     # Taux sans risque
       sigma=0.25, # Volatilité implicite
       option_type='call'
   )

   # Calculer le prix
   price = option.price()
   print(f"Prix de l'option: {price:.2f}")

   # Calculer les grecques
   greeks = option.greeks()
   for name, value in greeks.items():
       print(f"{name}: {value:.4f}")

Optimisation de portefeuille
-----------------------------

.. code-block:: python

   from quantfinance.portfolio.optimization import PortfolioOptimizer
   from quantfinance.utils.data import DataLoader
   import pandas as pd

   # Générer des données synthétiques
   prices = DataLoader.generate_synthetic_prices(
       n_assets=4,
       n_days=252,
       random_seed=42
   )

   # Calculer les rendements
   returns = prices.pct_change().dropna()

   # Créer l'optimiseur
   optimizer = PortfolioOptimizer(returns, risk_free_rate=0.02)

   # Trouver le portefeuille à Sharpe maximum
   result = optimizer.maximize_sharpe()

   print(f"Rendement annuel: {result['return']:.2%}")
   print(f"Volatilité: {result['volatility']:.2%}")
   print(f"Sharpe Ratio: {result['sharpe_ratio']:.3f}")

   print("\nAllocation:")
   for asset, weight in result['weights'].items():
       print(f"  {asset}: {weight:.2%}")

Calcul de risque
----------------

.. code-block:: python

   from quantfinance.risk.var import VaRCalculator
   from quantfinance.risk.metrics import RiskMetrics

   # VaR à 95%
   var_95 = VaRCalculator.historical_var(
       returns.iloc[:, 0],
       confidence_level=0.95
   )
   print(f"VaR 95%: {var_95:.2%}")

   # Expected Shortfall
   es_95 = VaRCalculator.expected_shortfall(
       returns.iloc[:, 0],
       confidence_level=0.95
   )
   print(f"CVaR 95%: {es_95:.2%}")

   # Sharpe Ratio
   sharpe = RiskMetrics.sharpe_ratio(
       returns.iloc[:, 0],
       risk_free_rate=0.02
   )
   print(f"Sharpe Ratio: {sharpe:.3f}")

Backtesting d'une stratégie
----------------------------

.. code-block:: python

   from quantfinance.portfolio.backtesting import (
       Backtester,
       MovingAverageCrossover
   )
   from quantfinance.utils.data import DataLoader

   # Générer des données OHLCV
   data = DataLoader.generate_ohlcv_data(n_days=500, random_seed=42)

   # Créer une stratégie
   strategy = MovingAverageCrossover(short_window=20, long_window=50)

   # Backtester
   backtester = Backtester(
       data,
       strategy,
       initial_capital=100000,
       commission=0.001
   )

   # Exécuter
   results = backtester.run()

   print(f"Rendement total: {results['Total Return']:.2%}")
   print(f"Sharpe Ratio: {results['Sharpe Ratio']:.3f}")
   print(f"Max Drawdown: {results['Max Drawdown']:.2%}")
   print(f"Nombre de trades: {results['Number of Trades']}")

Prochaines étapes
-----------------

* Consultez les :doc:`tutorials` pour des exemples plus détaillés
* Explorez la :doc:`../api/pricing` pour toutes les fonctionnalités
* Visitez le `GitHub <https://github.com/Mafoya1er/quantfinance>`_ pour contribuer
