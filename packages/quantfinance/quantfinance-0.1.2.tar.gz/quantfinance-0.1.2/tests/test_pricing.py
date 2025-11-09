"""
Tests complets pour le module pricing
"""

import pytest
import numpy as np
import pandas as pd
from quantfinance.pricing.options import BlackScholes, BinomialTree, MonteCarlo, ImpliedVolatility
from quantfinance.pricing.bonds import Bond, ZeroCouponBond, YieldCurve, BondPortfolio


class TestBlackScholes:
    """Tests pour le modèle Black-Scholes"""
    
    def test_call_option_price(self, sample_option_params):
        """Test du pricing d'une option call"""
        bs = BlackScholes(**sample_option_params, option_type='call')
        price = bs.price()
        
        assert price > 0
        assert isinstance(price, (float, np.floating))
        assert price < sample_option_params['S']
    
    def test_put_option_price(self, sample_option_params):
        """Test du pricing d'une option put"""
        bs = BlackScholes(**sample_option_params, option_type='put')
        price = bs.price()
        
        assert price > 0
        assert isinstance(price, (float, np.floating))
    
    def test_put_call_parity(self, sample_option_params):
        """Test de la parité put-call: C - P = S - K*e^(-rT)"""
        call = BlackScholes(**sample_option_params, option_type='call').price()
        put = BlackScholes(**sample_option_params, option_type='put').price()
        
        S, K, T, r = [sample_option_params[k] for k in ['S', 'K', 'T', 'r']]
        parity_lhs = call - put
        parity_rhs = S - K * np.exp(-r * T)
        
        assert np.isclose(parity_lhs, parity_rhs, rtol=1e-10)
    
    def test_delta_bounds_call(self, sample_option_params):
        """Test que le delta d'un call est entre 0 et 1"""
        bs = BlackScholes(**sample_option_params, option_type='call')
        delta = bs.delta()
        
        assert 0 <= delta <= 1
    
    def test_delta_bounds_put(self, sample_option_params):
        """Test que le delta d'un put est entre -1 et 0"""
        bs = BlackScholes(**sample_option_params, option_type='put')
        delta = bs.delta()
        
        assert -1 <= delta <= 0
    
    def test_gamma_positive(self, sample_option_params):
        """Test que le gamma est toujours positif"""
        bs = BlackScholes(**sample_option_params)
        gamma = bs.gamma()
        
        assert gamma > 0
    
    def test_vega_positive(self, sample_option_params):
        """Test que le vega est toujours positif"""
        bs = BlackScholes(**sample_option_params)
        vega = bs.vega()
        
        assert vega > 0
    
    def test_atm_call_delta(self, sample_option_params):
        """Test que le delta d'un call ATM est approximativement 0.5"""
        bs = BlackScholes(**sample_option_params, option_type='call')
        delta = bs.delta()
        
        assert 0.55 < delta < 0.7
    
    def test_deep_itm_call_delta(self):
        """Test que le delta d'un call très ITM est proche de 1"""
        bs = BlackScholes(S=150, K=100, T=1, r=0.05, sigma=0.2, option_type='call')
        delta = bs.delta()
        
        assert delta > 0.9
    
    def test_deep_otm_call_delta(self):
        """Test que le delta d'un call très OTM est proche de 0"""
        bs = BlackScholes(S=50, K=100, T=1, r=0.05, sigma=0.2, option_type='call')
        delta = bs.delta()
        
        assert delta < 0.1
    
    def test_greeks_dict(self, sample_option_params):
        """Test que greeks() retourne toutes les grecques"""
        bs = BlackScholes(**sample_option_params)
        greeks = bs.greeks()
        
        expected_keys = ['delta', 'gamma', 'vega', 'theta', 'rho']
        assert all(key in greeks for key in expected_keys)
        assert all(isinstance(greeks[key], (float, np.floating)) for key in expected_keys)
    
    def test_invalid_option_type(self, sample_option_params):
        """Test qu'une erreur est levée pour un type invalide"""
        with pytest.raises(ValueError):
            BlackScholes(**sample_option_params, option_type='invalid')
    
    def test_invalid_maturity(self, sample_option_params):
        """Test qu'une erreur est levée pour une maturité négative"""
        params = sample_option_params.copy()
        params['T'] = -1
        
        with pytest.raises(ValueError):
            BlackScholes(**params)
    
    def test_invalid_volatility(self, sample_option_params):
        """Test qu'une erreur est levée pour une volatilité négative"""
        params = sample_option_params.copy()
        params['sigma'] = -0.2
        
        with pytest.raises(ValueError):
            BlackScholes(**params)
    
    def test_implied_volatility(self, sample_option_params):
        """Test du calcul de volatilité implicite"""
        sigma_true = 0.25
        bs = BlackScholes(**{**sample_option_params, 'sigma': sigma_true})
        market_price = bs.price()
        
        bs_iv = BlackScholes(**{**sample_option_params, 'sigma': 0.5})
        implied_vol = bs_iv.implied_volatility(market_price)
        
        assert np.isclose(implied_vol, sigma_true, rtol=1e-4)
    
    def test_with_dividends(self):
        """Test avec taux de dividende"""
        bs_no_div = BlackScholes(S=100, K=100, T=1, r=0.05, sigma=0.2, q=0.0)
        bs_div = BlackScholes(S=100, K=100, T=1, r=0.05, sigma=0.2, q=0.02)
        
        # Avec dividendes, le call devrait valoir moins
        assert bs_div.price() < bs_no_div.price()


class TestBinomialTree:
    """Tests pour le modèle binomial"""
    
    def test_european_call_convergence(self, sample_option_params):
        """Test que le binomial converge vers Black-Scholes"""
        bs_price = BlackScholes(**sample_option_params, option_type='call').price()
        binomial_price = BinomialTree(
            **sample_option_params,
            N=500,
            option_type='call',
            exercise_type='european'
        ).price()
        
        assert np.isclose(bs_price, binomial_price, rtol=0.01)
    
    def test_european_put_convergence(self, sample_option_params):
        """Test pour les puts européens"""
        bs_price = BlackScholes(**sample_option_params, option_type='put').price()
        binomial_price = BinomialTree(
            **sample_option_params,
            N=500,
            option_type='put',
            exercise_type='european'
        ).price()
        
        assert np.isclose(bs_price, binomial_price, rtol=0.01)
    
    def test_american_put_higher_than_european(self):
        """Test qu'une option américaine vaut au moins autant qu'une européenne"""
        params = {'S': 100, 'K': 110, 'T': 1, 'r': 0.05, 'sigma': 0.2, 'N': 100}
        
        european_price = BinomialTree(
            **params,
            option_type='put',
            exercise_type='european'
        ).price()
        
        american_price = BinomialTree(
            **params,
            option_type='put',
            exercise_type='american'
        ).price()
        
        assert american_price >= european_price
    
    def test_delta_calculation(self, sample_option_params):
        """Test du calcul du delta par différences finies"""
        binomial = BinomialTree(**sample_option_params, N=100)
        delta = binomial.delta()
        
        assert isinstance(delta, (float, np.floating))
        assert -1 <= delta <= 1
    
    def test_gamma_calculation(self, sample_option_params):
        """Test du calcul du gamma"""
        binomial = BinomialTree(**sample_option_params, N=100)
        gamma = binomial.gamma()
        
        assert isinstance(gamma, (float, np.floating))
        assert gamma >= 0


class TestMonteCarlo:
    """Tests pour Monte Carlo"""
    
    def test_european_call_convergence(self, sample_option_params):
        """Test que Monte Carlo converge vers Black-Scholes"""
        bs_price = BlackScholes(**sample_option_params, option_type='call').price()
        mc = MonteCarlo(
            **sample_option_params,
            option_type='call',
            n_simulations=50000,
            random_seed=42
        )
        mc_price = mc.price()
        
        # Tolérance plus large pour Monte Carlo
        assert np.isclose(bs_price, mc_price, rtol=0.05)
    
    def test_confidence_interval(self, sample_option_params):
        """Test que l'intervalle de confiance contient le vrai prix"""
        bs_price = BlackScholes(**sample_option_params, option_type='call').price()
        mc = MonteCarlo(
            **sample_option_params,
            option_type='call',
            n_simulations=10000,
            random_seed=42
        )
        mc_price, lower, upper = mc.price_with_confidence_interval(confidence_level=0.95)
        
        # Le prix BS devrait être dans l'intervalle
        assert lower <= bs_price <= upper or np.isclose(lower, bs_price, rtol=0.1)
    
    def test_asian_option(self, sample_option_params):
        """Test du pricing d'option asiatique"""
        mc = MonteCarlo(
            **sample_option_params,
            option_type='call',
            n_simulations=10000,
            random_seed=42
        )
        asian_price = mc.price_asian_option(option_type='arithmetic')
        
        assert asian_price > 0
        assert isinstance(asian_price, (float, np.floating))
    
    def test_barrier_option(self, sample_option_params):
        """Test du pricing d'option à barrière"""
        mc = MonteCarlo(
            **sample_option_params,
            option_type='call',
            n_simulations=10000,
            random_seed=42
        )
        
        barrier = 120
        barrier_price = mc.price_barrier_option(barrier, 'up-and-out')
        
        # Prix de barrière devrait être inférieur à vanille
        vanilla_price = mc.price()
        assert barrier_price <= vanilla_price
    
    def test_reproducibility(self, sample_option_params):
        """Test de la reproductibilité avec seed"""
        mc1 = MonteCarlo(**sample_option_params, n_simulations=1000, random_seed=42)
        mc2 = MonteCarlo(**sample_option_params, n_simulations=1000, random_seed=42)
        
        assert np.isclose(mc1.price(), mc2.price(), rtol=1e-1)


class TestBond:
    """Tests pour les obligations"""
    
    def test_bond_price_at_par(self, sample_bond_params):
        """Test qu'une obligation au pair a un prix de 100 quand YTM = coupon"""
        bond = Bond(**sample_bond_params)
        price = bond.price(ytm=sample_bond_params['coupon_rate'])
        
        assert np.isclose(price, 100, rtol=1e-10)
    
    def test_bond_price_premium(self, sample_bond_params):
        """Test qu'une obligation se trade à prime quand YTM < coupon"""
        bond = Bond(**sample_bond_params)
        price = bond.price(ytm=0.04)
        
        assert price > 100
    
    def test_bond_price_discount(self, sample_bond_params):
        """Test qu'une obligation se trade à décote quand YTM > coupon"""
        bond = Bond(**sample_bond_params)
        price = bond.price(ytm=0.06)
        
        assert price < 100
    
    def test_ytm_calculation(self, sample_bond_params):
        """Test du calcul du YTM"""
        bond = Bond(**sample_bond_params)
        ytm_target = 0.06
        price = bond.price(ytm=ytm_target)
        ytm_calculated = bond.ytm(price)
        
        assert np.isclose(ytm_calculated, ytm_target, rtol=1e-6)
    
    def test_duration_positive(self, sample_bond_params):
        """Test que la durée est positive"""
        bond = Bond(**sample_bond_params)
        duration = bond.duration(ytm=0.05)
        
        assert duration > 0
        assert duration <= sample_bond_params['maturity']
    
    def test_modified_duration(self, sample_bond_params):
        """Test de la relation entre durée Macaulay et modifiée"""
        bond = Bond(**sample_bond_params)
        ytm = 0.06
        
        mac_duration = bond.duration(ytm)
        mod_duration = bond.modified_duration(ytm)
        
        expected = mac_duration / (1 + ytm / bond.frequency)
        assert np.isclose(mod_duration, expected, rtol=1e-10)
    
    def test_convexity_positive(self, sample_bond_params):
        """Test que la convexité est positive"""
        bond = Bond(**sample_bond_params)
        convexity = bond.convexity(ytm=0.05)
        
        assert convexity > 0
    
    def test_dv01(self, sample_bond_params):
        """Test du calcul du DV01"""
        bond = Bond(**sample_bond_params)
        dv01 = bond.dv01(ytm=0.05)
        
        assert dv01 > 0
    
    def test_cash_flows(self, sample_bond_params):
        """Test de génération des cash flows"""
        bond = Bond(**sample_bond_params)
        cf = bond.cash_flows()
        
        assert isinstance(cf, pd.DataFrame)
        assert len(cf) == bond.n_periods
        assert 'Cash Flow' in cf.columns


class TestZeroCouponBond:
    """Tests pour les obligations zéro-coupon"""
    
    def test_price(self):
        """Test du pricing"""
        zcb = ZeroCouponBond(face_value=100, maturity=5)
        price = zcb.price(ytm=0.05)
        
        expected = 100 / (1.05 ** 5)
        assert np.isclose(price, expected)
    
    def test_ytm(self):
        """Test du calcul de YTM"""
        zcb = ZeroCouponBond(face_value=100, maturity=5)
        ytm = zcb.ytm(price=78.35)
        
        assert np.isclose(ytm, 0.05, rtol=1e-3)  
    
    def test_duration_equals_maturity(self):
        """Test que la durée égale la maturité"""
        zcb = ZeroCouponBond(face_value=100, maturity=5)
        duration = zcb.duration()
        
        assert duration == 5


class TestYieldCurve:
    """Tests pour les courbes de taux"""
    
    def test_interpolation_linear(self):
        """Test de l'interpolation linéaire"""
        maturities = [1, 2, 5, 10]
        rates = [0.02, 0.025, 0.03, 0.035]
        
        curve = YieldCurve(maturities, rates)
        interpolated = curve.interpolate(3)
        
        assert rates[1] < interpolated < rates[2]
    
    def test_discount_factor(self):
        """Test du calcul du facteur d'actualisation"""
        maturities = [1, 2, 5]
        rates = [0.02, 0.03, 0.04]
        
        curve = YieldCurve(maturities, rates)
        df = curve.discount_factor(1)
        
        expected = np.exp(-rates[0] * 1)
        assert np.isclose(df, expected, rtol=1e-10)
    
    def test_forward_rate(self):
        """Test du calcul du taux forward"""
        maturities = [1, 2]
        rates = [0.02, 0.03]
        
        curve = YieldCurve(maturities, rates)
        forward = curve.forward_rate(1, 2)
        
        expected = (rates[1] * 2 - rates[0] * 1) / (2 - 1)
        assert np.isclose(forward, expected, rtol=1e-10)
    
    def test_par_rate(self):
        """Test du calcul du taux par"""
        maturities = [1, 2, 3]
        rates = [0.02, 0.025, 0.03]
        
        curve = YieldCurve(maturities, rates)
        par_rate = curve.par_rate(2)
        
        assert par_rate > 0


class TestBondPortfolio:
    """Tests pour les portefeuilles d'obligations"""
    
    def test_portfolio_price(self):
        """Test du pricing de portefeuille"""
        bond1 = Bond(100, 0.05, 5, 2)
        bond2 = Bond(100, 0.04, 3, 2)
        
        weights = np.array([0.6, 0.4])
        portfolio = BondPortfolio([bond1, bond2], weights)
        
        price = portfolio.price(0.05)
        assert price > 0
    
    def test_portfolio_duration(self):
        """Test de la durée du portefeuille"""
        bond1 = Bond(100, 0.05, 5, 2)
        bond2 = Bond(100, 0.04, 3, 2)
        
        weights = np.array([0.6, 0.4])
        portfolio = BondPortfolio([bond1, bond2], weights)
        
        duration = portfolio.duration(0.05)
        
        # Duration devrait être entre les durations individuelles
        assert bond2.duration(0.05) < duration < bond1.duration(0.05)