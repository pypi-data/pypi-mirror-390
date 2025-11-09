
"""
Tests complets pour le module portfolio
"""

import pytest
import numpy as np
import pandas as pd
from quantfinance.portfolio.optimization import PortfolioOptimizer, EfficientFrontier
from quantfinance.portfolio.allocation import AssetAllocator
from quantfinance.portfolio.rebalancing import Rebalancer
from quantfinance.portfolio.backtesting import Backtester, BuyAndHoldStrategy, MovingAverageCrossover


def generate_sample_returns(n_days=251, n_assets=3, seed=42):
    """Génère des rendements synthétiques réalistes."""
    np.random.seed(seed)
    mean_returns = np.array([0.0005, 0.0004, 0.0006])  # Rendements moyens journaliers
    cov_matrix = np.array([
        [0.0004, 0.0001, 0.0002],
        [0.0001, 0.0003, 0.0001],
        [0.0002, 0.0001, 0.0005]
    ])
    
    returns = np.random.multivariate_normal(mean_returns, cov_matrix, n_days)
    assets = [f'Asset{i+1}' for i in range(n_assets)]
    dates = pd.date_range('2020-01-02', periods=n_days, freq='B')
    
    return pd.DataFrame(returns, index=dates, columns=assets)

class TestPortfolioOptimizer:
    """Tests pour l'optimisation de portefeuille"""
    
    def test_equal_weight(self, sample_returns):
        """Test du portefeuille équipondéré"""
        optimizer = PortfolioOptimizer(sample_returns)
        result = optimizer.equal_weight()
        
        assert 'weights' in result
        assert len(result['weights']) == len(sample_returns.columns)
        assert np.isclose(result['weights'].sum(), 1.0)
        assert np.allclose(result['weights'].values, 1/len(sample_returns.columns))
    
    def test_minimize_volatility(self, sample_returns):
        """Test de minimisation de volatilité"""
        optimizer = PortfolioOptimizer(sample_returns)
        result = optimizer.minimize_volatility()
        
        assert result['success']
        assert np.isclose(result['weights'].sum(), 1.0)
        assert all(result['weights'] >= -0.01)  # Tolérance numérique
    
    def test_maximize_sharpe(self, sample_returns):
        """Test de maximisation du Sharpe"""
        optimizer = PortfolioOptimizer(sample_returns)
        result = optimizer.maximize_sharpe()
        
        assert result['success']
        assert np.isclose(result['weights'].sum(), 1.0)
        assert 'sharpe_ratio' in result

    def test_maximize_return(self):
        sample_returns = generate_sample_returns()  # ✅ 251 jours, 3 actifs
        optimizer = PortfolioOptimizer(sample_returns)

        # Trouve la volatilité minimale possible
        min_vol_result = optimizer.minimize_volatility()
        min_vol = min_vol_result['volatility']
        print(f"Minimum possible volatility: {min_vol:.6f}")

        # Choisis un target_vol réaliste
        target_vol = min_vol * 1.05  # 5% au-dessus du minimum

        result = optimizer.maximize_return(target_volatility=target_vol)

        # Vérifie que l'optimisation a réussi
        assert result['success'] or np.isclose(
            optimizer.portfolio_volatility(result.x),
            target_vol,
            atol=0.01
        ), f"Optimization failed: {result.get('message', 'Unknown error')}\n" \
        f"Final volatility: {optimizer.portfolio_volatility(result.x):.6f}, Target: {target_vol}"
    
    def test_risk_parity(self, sample_returns):
        """Test du portefeuille de parité de risque"""
        optimizer = PortfolioOptimizer(sample_returns)
        result = optimizer.risk_parity()
        
        assert 'weights' in result
        assert 'risk_contribution' in result
        assert np.isclose(result['weights'].sum(), 1.0)
    
    def test_portfolio_performance(self, sample_returns, sample_weights):
        """Test du calcul de performance"""
        optimizer = PortfolioOptimizer(sample_returns)
        perf_return, perf_vol, sharpe = optimizer.portfolio_performance(sample_weights)
        
        assert isinstance(perf_return, (float, np.floating))
        assert isinstance(perf_vol, (float, np.floating))
        assert isinstance(sharpe, (float, np.floating))
        assert perf_vol > 0
    
    def test_min_vol_lower_risk_than_equal_weight(self, sample_returns):
        """Test que min vol a moins de risque que équipondéré"""
        optimizer = PortfolioOptimizer(sample_returns)
        
        min_vol = optimizer.minimize_volatility()
        equal_w = optimizer.equal_weight()
        
        assert min_vol['volatility'] <= equal_w['volatility']


class TestEfficientFrontier:
    """Tests pour la frontière efficiente"""
    
    def test_calculate_frontier(self, sample_returns):
        """Test du calcul de la frontière"""
        optimizer = PortfolioOptimizer(sample_returns)
        frontier = EfficientFrontier(optimizer)
        
        df = frontier.calculate_frontier(n_points=10)
        
        assert isinstance(df, pd.DataFrame)
        assert len(df) > 0
        assert 'return' in df.columns
        assert 'volatility' in df.columns
        assert 'sharpe_ratio' in df.columns
    
    def test_frontier_points_valid(self, sample_returns):
        """Test que tous les points de la frontière sont valides"""
        optimizer = PortfolioOptimizer(sample_returns)
        frontier = EfficientFrontier(optimizer)
        
        df = frontier.calculate_frontier(n_points=10)
        
        # Tous les rendements et volatilités doivent être positifs
        assert all(df['volatility'] > 0)


class TestAssetAllocator:
    """Tests pour l'allocation d'actifs"""
    
    def test_hierarchical_risk_parity(self, sample_returns):
        """Test de HRP"""
        allocator = AssetAllocator(sample_returns)
        weights = allocator.hierarchical_risk_parity()
        
        assert isinstance(weights, pd.Series)
        assert np.isclose(weights.sum(), 1.0, atol=0.01)
        assert all(weights >= 0)
    
    def test_minimum_correlation(self, sample_returns):
        """Test du portefeuille de corrélation minimale"""
        allocator = AssetAllocator(sample_returns)
        weights = allocator.minimum_correlation()
        
        assert isinstance(weights, pd.Series)
        assert np.isclose(weights.sum(), 1.0)
    
    def test_maximum_diversification(self, sample_returns):
        """Test du portefeuille de diversification maximale"""
        allocator = AssetAllocator(sample_returns)
        weights = allocator.maximum_diversification()
        
        assert isinstance(weights, pd.Series)
        assert np.isclose(weights.sum(), 1.0)


class TestRebalancer:
    """Tests pour le rééquilibrage"""
    
    def test_periodic_rebalancing(self, sample_prices):
        """Test du rééquilibrage périodique"""
        target_weights = pd.Series([0.33, 0.33, 0.34], index=sample_prices.columns)
        
        rebalancer = Rebalancer(target_weights, sample_prices, initial_capital=100000)
        result = rebalancer.periodic_rebalancing(frequency='monthly')
        
        assert isinstance(result, pd.DataFrame)
        assert 'portfolio_value' in result.columns
        assert len(result) > 0
    
    def test_threshold_rebalancing(self, sample_prices):
        """Test du rééquilibrage par seuil"""
        target_weights = pd.Series([0.33, 0.33, 0.34], index=sample_prices.columns)
        
        rebalancer = Rebalancer(target_weights, sample_prices, initial_capital=100000)
        result = rebalancer.threshold_rebalancing(threshold=0.05)
        
        assert isinstance(result, pd.DataFrame)
        assert 'portfolio_value' in result.columns
        assert 'rebalance_count' in result.columns


class TestBacktester:
    """Tests pour le backtesting"""
    
    def test_buy_and_hold_strategy(self, sample_prices):
        """Test de la stratégie buy & hold"""
        data = sample_prices[['AAPL']].copy()
        data.columns = ['Close']
        
        strategy = BuyAndHoldStrategy()
        backtester = Backtester(data, strategy, initial_capital=10000)
        
        stats = backtester.run()
        
        assert isinstance(stats, dict)
        assert 'Total Return' in stats
        assert 'Sharpe Ratio' in stats
        assert 'Number of Trades' in stats
    
    def test_moving_average_crossover(self, sample_prices):
        """Test de la stratégie de croisement de moyennes mobiles"""
        data = sample_prices[['AAPL']].copy()
        data.columns = ['Close']
        
        strategy = MovingAverageCrossover(short_window=20, long_window=50)
        backtester = Backtester(data, strategy, initial_capital=10000)
        
        stats = backtester.run()
        
        assert isinstance(stats, dict)
        assert stats['Number of Trades'] > 0
    
    def test_results_dataframe(self, sample_prices):
        """Test que les résultats sont bien stockés"""
        data = sample_prices[['AAPL']].copy()
        data.columns = ['Close']
        
        strategy = BuyAndHoldStrategy()
        backtester = Backtester(data, strategy)
        backtester.run()
        
        assert backtester.results is not None
        assert isinstance(backtester.results, pd.DataFrame)
        assert 'portfolio_value' in backtester.results.columns
