"""
Tests pour le module utils
"""

import pytest
import numpy as np
import pandas as pd
from quantfinance.utils.data import DataLoader, DataCleaner, DataTransformer
from quantfinance.utils.helpers import (
    annualize_return,
    annualize_volatility,
    compound_returns
)


class TestDataLoader:
    """Tests pour DataLoader"""
    
    def test_generate_synthetic_prices(self):
        """Test de génération de prix synthétiques"""
        prices = DataLoader.generate_synthetic_prices(
            n_assets=3,
            n_days=100,
            random_seed=42
        )
        
        assert isinstance(prices, pd.DataFrame)
        assert prices.shape == (101, 3)  # +1 pour le prix initial
        assert all(prices > 0)
    
    def test_generate_ohlcv_data(self):
        """Test de génération de données OHLCV"""
        ohlcv = DataLoader.generate_ohlcv_data(n_days=100, random_seed=42)
        
        assert isinstance(ohlcv, pd.DataFrame)
        assert all(col in ohlcv.columns for col in ['Open', 'High', 'Low', 'Close', 'Volume'])
        
        # High doit être >= Open et Close
        assert all(ohlcv['High'] >= ohlcv['Open'])
        assert all(ohlcv['High'] >= ohlcv['Close'])
        
        # Low doit être <= Open et Close
        assert all(ohlcv['Low'] <= ohlcv['Open'])
        assert all(ohlcv['Low'] <= ohlcv['Close'])
    
    def test_synthetic_prices_reproducibility(self):
        """Test de la reproductibilité"""
        prices1 = DataLoader.generate_synthetic_prices(n_assets=3, n_days=100, random_seed=42)
        prices2 = DataLoader.generate_synthetic_prices(n_assets=3, n_days=100, random_seed=42)
        
        pd.testing.assert_frame_equal(prices1, prices2)


class TestDataCleaner:
    """Tests pour DataCleaner"""
    
    def test_handle_missing_values_ffill(self):
        """Test du remplissage forward"""
        data = pd.DataFrame({
            'A': [1, np.nan, 3, np.nan, 5],
            'B': [10, 20, np.nan, 40, 50]
        })
        
        cleaned = DataCleaner.handle_missing_values(data, method='ffill')
        
        assert cleaned.isna().sum().sum() == 0
        assert cleaned.loc[1, 'A'] == 1
        assert cleaned.loc[2, 'B'] == 20
    
    def test_calculate_returns_simple(self):
        """Test du calcul de rendements simples"""
        prices = pd.DataFrame({
            'A': [100, 105, 110],
            'B': [50, 52, 51]
        })
        
        returns = DataCleaner.calculate_returns(prices, method='simple')
        
        assert len(returns) == 2
        assert np.isclose(returns.loc[1, 'A'], 0.05)
    
    def test_calculate_returns_log(self):
        """Test du calcul de rendements logarithmiques"""
        prices = pd.DataFrame({
            'A': [100, 105, 110]
        })
        
        returns = DataCleaner.calculate_returns(prices, method='log')
        
        assert len(returns) == 2
        assert np.isclose(returns.loc[1, 'A'], np.log(1.05))
    
    def test_winsorize(self):
        """Test de la winsorisation"""
        data = pd.DataFrame({
            'A': [1, 2, 3, 4, 5, 100]  # 100 est un outlier
        })
        
        winsorized = DataCleaner.winsorize(data, lower_percentile=0.1, upper_percentile=0.9)
        
        # La valeur extrême devrait être plafonnée
        assert winsorized['A'].max() < 100
    
    def test_remove_outliers(self):
        """Test de suppression d'outliers"""
        data = pd.DataFrame({
            'A': [1, 2, 3, 4, 5, 100]
        })
        
        cleaned = DataCleaner.remove_outliers(data, n_std=2, method='remove')
        
        # L'outlier devrait être supprimé
        assert len(cleaned) < len(data)


class TestDataTransformer:
    """Tests pour DataTransformer"""
    
    def test_normalize_zscore(self):
        """Test de normalisation z-score"""
        data = pd.DataFrame({
            'A': [1, 2, 3, 4, 5]
        })
        
        normalized = DataTransformer.normalize(data, method='zscore')
        
        # Mean ≈ 0, std ≈ 1
        assert np.isclose(normalized['A'].mean(), 0, atol=1e-10)
        assert np.isclose(normalized['A'].std(), 1, atol=1e-10)
    
    def test_normalize_minmax(self):
        """Test de normalisation min-max"""
        data = pd.DataFrame({
            'A': [1, 2, 3, 4, 5]
        })
        
        normalized = DataTransformer.normalize(data, method='minmax')
        
        # Min = 0, Max = 1
        assert normalized['A'].min() == 0
        assert normalized['A'].max() == 1
    
    def test_add_technical_indicators(self):
        """Test d'ajout d'indicateurs techniques"""
        ohlcv = DataLoader.generate_ohlcv_data(n_days=100, random_seed=42)
        
        with_indicators = DataTransformer.add_technical_indicators(
            ohlcv,
            indicators=['SMA', 'EMA']
        )
        
        assert 'SMA_20' in with_indicators.columns
        assert 'EMA_12' in with_indicators.columns
    
    def test_create_lagged_features(self):
        """Test de création de features retardées"""
        data = pd.DataFrame({
            'A': [1, 2, 3, 4, 5]
        })
        
        lagged = DataTransformer.create_lagged_features(data, lags=[1, 2])
        
        assert 'A_lag_1' in lagged.columns
        assert 'A_lag_2' in lagged.columns


class TestHelpers:
    """Tests pour les fonctions helper"""
    
    def test_annualize_return(self):
        """Test d'annualisation de rendement"""
        daily_return = 0.001
        annual_return = annualize_return(daily_return, periods_per_year=252)
        
        assert annual_return == 0.001 * 252
    
    def test_annualize_volatility(self):
        """Test d'annualisation de volatilité"""
        daily_vol = 0.02
        annual_vol = annualize_volatility(daily_vol, periods_per_year=252)
        
        assert np.isclose(annual_vol, 0.02 * np.sqrt(252))
    
    def test_compound_returns(self):
        """Test de rendement composé"""
        returns = np.array([0.1, 0.05, -0.03])
        compound = compound_returns(returns)
        
        expected = (1.1 * 1.05 * 0.97) - 1
        assert np.isclose(compound, expected)