
"""
Fixtures pytest partagées pour tous les tests
"""

import pytest
import numpy as np
import pandas as pd
from datetime import datetime, timedelta


@pytest.fixture
def sample_prices():
    """Fixture de prix pour les tests"""
    np.random.seed(42)
    dates = pd.date_range('2020-01-01', periods=252, freq='B')
    n_assets = 3
    
    prices = pd.DataFrame(
        100 * np.exp(np.cumsum(np.random.normal(0.0001, 0.02, (252, n_assets)), axis=0)),
        index=dates,
        columns=['AAPL', 'MSFT', 'GOOGL']
    )
    return prices


@pytest.fixture
def sample_returns(sample_prices):
    """Fixture de rendements"""
    return sample_prices.pct_change().dropna()


@pytest.fixture
def sample_weights():
    """Fixture de poids de portefeuille"""
    return np.array([0.4, 0.3, 0.3])


@pytest.fixture
def sample_bond_params():
    """Fixture de paramètres d'obligation"""
    return {
        'face_value': 100,
        'coupon_rate': 0.05,
        'maturity': 5,
        'frequency': 2
    }


@pytest.fixture
def sample_option_params():
    """Fixture de paramètres d'option"""
    return {
        'S': 100,
        'K': 100,
        'T': 1,
        'r': 0.05,
        'sigma': 0.2
    }