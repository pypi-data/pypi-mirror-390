"""
Module de gestion des risques

Contient :
- Calcul de Value at Risk (VaR)
- Expected Shortfall (CVaR)
- Métriques de performance (Sharpe, Sortino, etc.)
- Analyse de stress testing
"""

from quantfinance.risk.var import VaRCalculator, StressTesting
from quantfinance.risk.metrics import RiskMetrics, PerformanceAnalyzer

__all__ = [
    'VaRCalculator',
    'StressTesting',
    'RiskMetrics',
    'PerformanceAnalyzer',
]