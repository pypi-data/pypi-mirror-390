"""
Tests complets pour le module risk
"""

import pytest
import numpy as np
import pandas as pd
from quantfinance.risk.var import VaRCalculator, StressTesting
from quantfinance.risk.metrics import RiskMetrics, PerformanceAnalyzer


class TestVaRCalculator:
    """Tests pour VaRCalculator"""
    
    def test_historical_var(self, sample_returns):
        """Test de la VaR historique"""
        var = VaRCalculator.historical_var(sample_returns.iloc[:, 0], confidence_level=0.95)
        
        assert var > 0
        assert isinstance(var, (float, np.floating))
    
    def test_parametric_var_normal(self, sample_returns):
        """Test de la VaR paramétrique normale"""
        var = VaRCalculator.parametric_var(
            sample_returns.iloc[:, 0],
            confidence_level=0.95,
            distribution='normal'
        )
        
        assert var > 0
    
    def test_parametric_var_student(self, sample_returns):
        """Test de la VaR paramétrique Student-t"""
        var = VaRCalculator.parametric_var(
            sample_returns.iloc[:, 0],
            confidence_level=0.95,
            distribution='student'
        )
        
        assert var > 0
    
    def test_ewma_var(self, sample_returns):
        """Test de la VaR EWMA"""
        var = VaRCalculator.ewma_var(
            sample_returns.iloc[:, 0],
            confidence_level=0.95,
            lambda_param=0.94
        )
        
        assert var > 0
    
    def test_monte_carlo_var_parametric(self, sample_returns):
        """Test de la VaR Monte Carlo paramétrique"""
        var = VaRCalculator.monte_carlo_var(
            sample_returns.iloc[:, 0],
            confidence_level=0.95,
            n_simulations=1000,
            method='parametric',
            random_seed=42
        )
        
        assert var > 0
    
    def test_monte_carlo_var_bootstrap(self, sample_returns):
        """Test de la VaR Monte Carlo bootstrap"""
        var = VaRCalculator.monte_carlo_var(
            sample_returns.iloc[:, 0],
            confidence_level=0.95,
            n_simulations=1000,
            method='bootstrap',
            random_seed=42
        )
        
        assert var > 0
    
    def test_expected_shortfall_greater_than_var(self, sample_returns):
        """Test que l'ES est supérieur à la VaR"""
        var = VaRCalculator.historical_var(sample_returns.iloc[:, 0], 0.95)
        es = VaRCalculator.expected_shortfall(sample_returns.iloc[:, 0], 0.95)
        
        assert es >= var
    
    def test_portfolio_var(self, sample_returns, sample_weights):
        """Test de la VaR de portefeuille"""
        var = VaRCalculator.portfolio_var(
            sample_returns,
            sample_weights,
            confidence_level=0.95,
            method='parametric'
        )
        
        assert var > 0
    
    def test_component_var(self, sample_returns, sample_weights):
        """Test de la VaR componentielle"""
        comp_var = VaRCalculator.component_var(
            sample_returns,
            sample_weights,
            confidence_level=0.95
        )
        
        assert isinstance(comp_var, pd.Series)
        assert len(comp_var) == len(sample_weights)
        assert all(comp_var.index == sample_returns.columns)
    
    def test_marginal_var(self, sample_returns, sample_weights):
        """Test de la VaR marginale"""
        marg_var = VaRCalculator.marginal_var(
            sample_returns,
            sample_weights,
            confidence_level=0.95
        )
        
        assert isinstance(marg_var, pd.Series)
        assert len(marg_var) == len(sample_weights)
    
    def test_var_increases_with_confidence(self, sample_returns):
        """Test que la VaR augmente avec le niveau de confiance"""
        var_95 = VaRCalculator.historical_var(sample_returns.iloc[:, 0], 0.95)
        var_99 = VaRCalculator.historical_var(sample_returns.iloc[:, 0], 0.99)
        
        assert var_99 > var_95


class TestStressTesting:
    """Tests pour le stress testing"""
    
    def test_scenario_analysis(self, sample_returns, sample_weights):
        """Test de l'analyse de scénarios"""
        scenarios = {
            'Crash': np.array([-0.2, -0.15, -0.18]),
            'Rally': np.array([0.1, 0.12, 0.11])
        }
        
        results = StressTesting.scenario_analysis(
            sample_returns,
            sample_weights,
            scenarios
        )
        
        assert isinstance(results, pd.DataFrame)
        assert len(results) == 2
        assert 'Scenario' in results.columns
        assert 'Portfolio Return' in results.columns
    
    def test_historical_stress_test(self, sample_returns, sample_weights):
        """Test du stress test historique"""
        stress_periods = {
            'Period1': ('2020-01-15', '2020-02-15')
        }
        
        results = StressTesting.historical_stress_test(
            sample_returns,
            sample_weights,
            stress_periods
        )
        
        assert isinstance(results, pd.DataFrame)
        assert 'Period' in results.columns
    
    def test_monte_carlo_stress_test(self, sample_returns, sample_weights):
        """Test du stress test Monte Carlo"""
        results = StressTesting.monte_carlo_stress_test(
            sample_returns,
            sample_weights,
            n_scenarios=1000,
            random_seed=42
        )
        
        assert isinstance(results, dict)
        assert 'scenarios' in results
        assert 'VaR_95' in results
        assert 'ES_95' in results


class TestRiskMetrics:
    """Tests pour RiskMetrics"""
    
    def test_sharpe_ratio(self, sample_returns):
        """Test du ratio de Sharpe"""
        sharpe = RiskMetrics.sharpe_ratio(
            sample_returns.iloc[:, 0],
            risk_free_rate=0.02
        )
        
        assert isinstance(sharpe, (float, np.floating))
        assert not np.isnan(sharpe)
    
    def test_sortino_ratio(self, sample_returns):
        """Test du ratio de Sortino"""
        sortino = RiskMetrics.sortino_ratio(
            sample_returns.iloc[:, 0],
            risk_free_rate=0.02
        )
        
        assert isinstance(sortino, (float, np.floating))
    
    def test_calmar_ratio(self, sample_returns):
        """Test du ratio de Calmar"""
        calmar = RiskMetrics.calmar_ratio(sample_returns.iloc[:, 0])
        
        assert isinstance(calmar, (float, np.floating))
    
    def test_omega_ratio(self, sample_returns):
        """Test du ratio Omega"""
        omega = RiskMetrics.omega_ratio(sample_returns.iloc[:, 0], threshold=0.0)
        
        assert omega > 0
    
    def test_max_drawdown_negative(self, sample_returns):
        """Test que le drawdown maximum est négatif"""
        max_dd = RiskMetrics.max_drawdown(sample_returns.iloc[:, 0])
        
        assert max_dd <= 0
    
    def test_drawdown_series_length(self, sample_returns):
        """Test que la série de drawdown a la bonne longueur"""
        dd_series = RiskMetrics.drawdown_series(sample_returns.iloc[:, 0])
        
        assert len(dd_series) == len(sample_returns)
    
    def test_beta(self, sample_returns):
        """Test du calcul du beta"""
        beta = RiskMetrics.beta(
            sample_returns.iloc[:, 0],
            sample_returns.iloc[:, 1]
        )
        
        assert isinstance(beta, (float, np.floating))
        assert not np.isnan(beta)
    
    def test_alpha(self, sample_returns):
        """Test du calcul de l'alpha"""
        alpha = RiskMetrics.alpha(
            sample_returns.iloc[:, 0],
            sample_returns.iloc[:, 1],
            risk_free_rate=0.02
        )
        
        assert isinstance(alpha, (float, np.floating))
    
    def test_information_ratio(self, sample_returns):
        """Test du ratio d'information"""
        ir = RiskMetrics.information_ratio(
            sample_returns.iloc[:, 0],
            sample_returns.iloc[:, 1]
        )
        
        assert isinstance(ir, (float, np.floating))
    
    def test_tracking_error(self, sample_returns):
        """Test de la tracking error"""
        te = RiskMetrics.tracking_error(
            sample_returns.iloc[:, 0],
            sample_returns.iloc[:, 1]
        )
        
        assert te >= 0
    
    def test_skewness(self, sample_returns):
        """Test du skewness"""
        skew = RiskMetrics.skewness(sample_returns.iloc[:, 0])
        
        assert isinstance(skew, (float, np.floating))
    
    def test_kurtosis(self, sample_returns):
        """Test du kurtosis"""
        kurt = RiskMetrics.kurtosis(sample_returns.iloc[:, 0])
        
        assert isinstance(kurt, (float, np.floating))


class TestPerformanceAnalyzer:
    """Tests pour PerformanceAnalyzer"""
    
    def test_summary_statistics(self, sample_returns):
        """Test du résumé de statistiques"""
        analyzer = PerformanceAnalyzer(
            sample_returns.iloc[:, 0],
            risk_free_rate=0.02
        )
        
        stats = analyzer.summary_statistics()
        
        assert isinstance(stats, pd.DataFrame)
        assert 'Total Return' in stats.index
        assert 'Sharpe Ratio' in stats.index
        assert 'Max Drawdown' in stats.index
    
    def test_rolling_statistics(self, sample_returns):
        """Test des statistiques roulantes"""
        analyzer = PerformanceAnalyzer(
            sample_returns.iloc[:, 0],
            risk_free_rate=0.02
        )
        
        rolling_stats = analyzer.rolling_statistics(window=60)
        
        assert isinstance(rolling_stats, pd.DataFrame)
    
    def test_monthly_returns_table(self, sample_returns):
        """Test de la table de rendements mensuels"""
        analyzer = PerformanceAnalyzer(
            sample_returns.iloc[:, 0],
            risk_free_rate=0.02
        )
        
        monthly_table = analyzer.monthly_returns_table()
        
        assert isinstance(monthly_table, pd.DataFrame)