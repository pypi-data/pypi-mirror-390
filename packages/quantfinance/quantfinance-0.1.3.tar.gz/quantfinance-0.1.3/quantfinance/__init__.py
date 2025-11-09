"""
QuantFinance - Package Python pour la Finance Quantitative
"""

__version__ = "0.1.0"
__author__ = "Votre Nom"
__email__ = "votre.email@example.com"

# Imports pricing
from quantfinance.pricing.options import (
    BlackScholes,
    BinomialTree,
    MonteCarlo,
    ImpliedVolatility
)
from quantfinance.pricing.bonds import (
    Bond,
    ZeroCouponBond,
    YieldCurve
)

# Imports risk
from quantfinance.risk.var import VaRCalculator
from quantfinance.risk.metrics import RiskMetrics

# Imports portfolio
from quantfinance.portfolio.optimization import (
    PortfolioOptimizer,
    EfficientFrontier
)
from quantfinance.portfolio.allocation import AssetAllocator
from quantfinance.portfolio.rebalancing import Rebalancer
from quantfinance.portfolio.backtesting import (
    Backtester,
    BuyAndHoldStrategy,
    MovingAverageCrossover
)

# Imports utils (optionnels - ne pas casser si manquants)
try:
    from quantfinance.utils.data import DataLoader, DataCleaner
    from quantfinance.utils.plotting import Plotter
except ImportError:
    pass

__all__ = [
    # Pricing
    'BlackScholes',
    'BinomialTree',
    'MonteCarlo',
    'ImpliedVolatility',
    'Bond',
    'ZeroCouponBond',
    'YieldCurve',
    
    # Risk
    'VaRCalculator',
    'RiskMetrics',
    
    # Portfolio
    'PortfolioOptimizer',
    'EfficientFrontier',
    'AssetAllocator',
    'Rebalancer',
    'Backtester',
    'BuyAndHoldStrategy',
    'MovingAverageCrossover',
]


def get_version():
    """Retourne la version du package"""
    return __version__


def info():
    """Affiche les informations sur le package"""
    print(f"""
    ╔══════════════════════════════════════════╗
    ║         QuantFinance v{__version__}           ║
    ╚══════════════════════════════════════════╝
    
    Package Python pour la Finance Quantitative
    
    Modules disponibles:
    • pricing   : Pricing d'options et obligations
    • risk      : Gestion des risques
    • portfolio : Optimisation de portefeuille
    • utils     : Utilitaires et visualisation
    
    Pour plus d'informations :
    >>> import quantfinance
    >>> help(quantfinance)
    """)