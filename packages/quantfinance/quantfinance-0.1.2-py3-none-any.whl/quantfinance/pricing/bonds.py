"""
Modèles de pricing d'obligations et courbes de taux

Implémente :
- Pricing d'obligations classiques et zéro-coupon
- Calcul de YTM, duration, convexité
- Courbes de taux et interpolation
- Bootstrap de courbes zéro-coupon
"""

import numpy as np
import pandas as pd
from typing import List, Union, Optional, Tuple, Dict
from scipy.optimize import brentq, minimize_scalar
from scipy.interpolate import interp1d, CubicSpline
import warnings


class Bond:
    """
    Classe pour le pricing et l'analyse d'obligations à coupon fixe
    
    Paramètres:
    -----------
    face_value : float
        Valeur nominale de l'obligation
    coupon_rate : float
        Taux du coupon annuel (ex: 0.05 pour 5%)
    maturity : float
        Maturité en années
    frequency : int
        Fréquence des paiements par an (1=annuel, 2=semestriel, 4=trimestriel, 12=mensuel)
    """
    
    def __init__(
        self,
        face_value: float,
        coupon_rate: float,
        maturity: float,
        frequency: int = 2
    ):
        self.face_value = face_value
        self.coupon_rate = coupon_rate
        self.maturity = maturity
        self.frequency = frequency
        self.coupon_payment = (face_value * coupon_rate) / frequency
        self.n_periods = int(maturity * frequency)
    
    def price(self, ytm: float) -> float:
        """
        Calcule le prix de l'obligation (clean price)
        
        Paramètres:
        -----------
        ytm : float
            Yield to maturity (rendement à l'échéance) annualisé
        
        Retourne:
        ---------
        float : Prix de l'obligation
        """
        if self.n_periods == 0:
            return self.face_value
        
        period_rate = ytm / self.frequency
        
        if abs(period_rate) < 1e-10:  # Si taux très proche de 0
            return self.coupon_payment * self.n_periods + self.face_value
        
        # Valeur présente des coupons (annuité)
        pv_coupons = self.coupon_payment * (
            (1 - (1 + period_rate)**(-self.n_periods)) / period_rate
        )
        
        # Valeur présente de la valeur nominale
        pv_face_value = self.face_value / (1 + period_rate)**self.n_periods
        
        return pv_coupons + pv_face_value
    
    def ytm(
        self,
        price: float,
        method: str = 'brent',
        initial_guess: float = 0.05
    ) -> float:
        """
        Calcule le rendement à l'échéance (YTM) pour un prix donné
        
        Paramètres:
        -----------
        price : float
            Prix de marché de l'obligation
        method : str
            Méthode de résolution ('brent' ou 'newton')
        initial_guess : float
            Estimation initiale pour Newton-Raphson
        
        Retourne:
        ---------
        float : Yield to maturity
        """
        def price_error(y):
            return self.price(y) - price
        
        if method == 'brent':
            try:
                return brentq(price_error, -0.99, 2.0)
            except ValueError:
                warnings.warn("Méthode de Brent échouée, utilisation de minimize")
                result = minimize_scalar(
                    lambda y: abs(price_error(y)),
                    bounds=(-0.5, 2.0),
                    method='bounded'
                )
                return result.x
        
        elif method == 'newton':
            ytm_guess = initial_guess
            for _ in range(100):
                price_calc = self.price(ytm_guess)
                price_diff = price_calc - price
                
                if abs(price_diff) < 1e-8:
                    return ytm_guess
                
                # Duration modifiée pour la dérivée
                duration_mod = self.modified_duration(ytm_guess)
                derivative = -price_calc * duration_mod
                
                if abs(derivative) < 1e-10:
                    break
                
                ytm_guess = ytm_guess - price_diff / derivative
            
            warnings.warn("Newton-Raphson n'a pas convergé, utilisation de Brent")
            return self.ytm(price, method='brent')
        
        else:
            raise ValueError(f"Méthode inconnue: {method}")
    
    def duration(self, ytm: float) -> float:
        """
        Calcule la durée de Macaulay
        
        Paramètres:
        -----------
        ytm : float
            Yield to maturity
        
        Retourne:
        ---------
        float : Durée de Macaulay (en années)
        """
        period_rate = ytm / self.frequency
        bond_price = self.price(ytm)
        
        if bond_price == 0:
            return 0
        
        weighted_cf = 0
        
        for t in range(1, self.n_periods + 1):
            # Flux de trésorerie
            if t < self.n_periods:
                cf = self.coupon_payment
            else:
                cf = self.coupon_payment + self.face_value
            
            # Valeur présente pondérée par le temps
            time_in_years = t / self.frequency
            pv = cf / (1 + period_rate)**t
            weighted_cf += time_in_years * pv
        
        return weighted_cf / bond_price
    
    def modified_duration(self, ytm: float) -> float:
        """
        Calcule la durée modifiée (approximation de la sensibilité au taux)
        
        Paramètres:
        -----------
        ytm : float
            Yield to maturity
        
        Retourne:
        ---------
        float : Durée modifiée
        """
        mac_duration = self.duration(ytm)
        return mac_duration / (1 + ytm / self.frequency)
    
    def convexity(self, ytm: float) -> float:
        """
        Calcule la convexité de l'obligation
        
        Paramètres:
        -----------
        ytm : float
            Yield to maturity
        
        Retourne:
        ---------
        float : Convexité
        """
        period_rate = ytm / self.frequency
        bond_price = self.price(ytm)
        
        if bond_price == 0:
            return 0
        
        convexity_sum = 0
        
        for t in range(1, self.n_periods + 1):
            if t < self.n_periods:
                cf = self.coupon_payment
            else:
                cf = self.coupon_payment + self.face_value
            
            pv = cf / (1 + period_rate)**t
            convexity_sum += pv * t * (t + 1)
        
        convexity = convexity_sum / (
            bond_price * (1 + period_rate)**2 * self.frequency**2
        )
        
        return convexity
    
    def dv01(self, ytm: float) -> float:
        """
        Calcule le DV01 (Dollar Value of a Basis Point)
        Changement de prix pour un changement de 1 bp (0.01%) du rendement
        
        Paramètres:
        -----------
        ytm : float
            Yield to maturity
        
        Retourne:
        ---------
        float : DV01
        """
        price_base = self.price(ytm)
        price_up = self.price(ytm + 0.0001)
        price_down = self.price(ytm - 0.0001)
        
        return (price_down - price_up) / 2
    
    def price_change_approximation(
        self,
        ytm: float,
        yield_change: float
    ) -> Tuple[float, float]:
        """
        Approxime le changement de prix avec duration et convexité
        
        Paramètres:
        -----------
        ytm : float
            Yield actuel
        yield_change : float
            Changement de rendement
        
        Retourne:
        ---------
        tuple : (changement avec duration seule, changement avec duration + convexité)
        """
        price = self.price(ytm)
        mod_dur = self.modified_duration(ytm)
        conv = self.convexity(ytm)
        
        # Approximation par duration
        price_change_dur = -mod_dur * yield_change * price
        
        # Approximation par duration + convexité
        price_change_full = (
            -mod_dur * yield_change * price +
            0.5 * conv * yield_change**2 * price
        )
        
        return price_change_dur, price_change_full
    
    def accrued_interest(self, days_since_last_coupon: int) -> float:
        """
        Calcule les intérêts courus
        
        Paramètres:
        -----------
        days_since_last_coupon : int
            Nombre de jours depuis le dernier paiement de coupon
        
        Retourne:
        ---------
        float : Intérêts courus
        """
        days_in_period = 365.25 / self.frequency
        return self.coupon_payment * (days_since_last_coupon / days_in_period)
    
    def dirty_price(self, ytm: float, days_since_last_coupon: int) -> float:
        """
        Calcule le prix sale (clean price + intérêts courus)
        
        Paramètres:
        -----------
        ytm : float
            Yield to maturity
        days_since_last_coupon : int
            Jours depuis dernier coupon
        
        Retourne:
        ---------
        float : Prix sale
        """
        clean_price = self.price(ytm)
        accrued = self.accrued_interest(days_since_last_coupon)
        return clean_price + accrued
    
    def cash_flows(self) -> pd.DataFrame:
        """
        Génère le calendrier des flux de trésorerie
        
        Retourne:
        ---------
        DataFrame : Calendrier des cash flows
        """
        periods = np.arange(1, self.n_periods + 1)
        times = periods / self.frequency
        
        coupons = np.full(self.n_periods, self.coupon_payment)
        coupons[-1] += self.face_value
        
        return pd.DataFrame({
            'Period': periods,
            'Time (years)': times,
            'Cash Flow': coupons
        })


class ZeroCouponBond:
    """
    Obligation zéro-coupon (ne paie que la valeur nominale à maturité)
    
    Paramètres:
    -----------
    face_value : float
        Valeur nominale
    maturity : float
        Maturité en années
    """
    
    def __init__(self, face_value: float, maturity: float):
        self.face_value = face_value
        self.maturity = maturity
    
    def price(self, ytm: float) -> float:
        """Calcule le prix de l'obligation zéro-coupon"""
        return self.face_value / (1 + ytm)**self.maturity
    
    def ytm(self, price: float) -> float:
        """Calcule le YTM à partir du prix"""
        return (self.face_value / price)**(1/self.maturity) - 1
    
    def duration(self, ytm: float = None) -> float:
        """La duration d'un zéro-coupon est égale à sa maturité"""
        return self.maturity
    
    def modified_duration(self, ytm: float) -> float:
        """Duration modifiée"""
        return self.maturity / (1 + ytm)
    
    def convexity(self, ytm: float) -> float:
        """Convexité"""
        return self.maturity * (self.maturity + 1) / (1 + ytm)**2


class YieldCurve:
    """
    Courbe de taux avec interpolation
    
    Paramètres:
    -----------
    maturities : array-like
        Liste des maturités (en années)
    rates : array-like
        Liste des taux correspondants (annualisés)
    """
    
    def __init__(
        self,
        maturities: Union[List[float], np.ndarray],
        rates: Union[List[float], np.ndarray]
    ):
        if len(maturities) != len(rates):
            raise ValueError("maturities et rates doivent avoir la même longueur")
        
        # Convertir en arrays numpy
        self.maturities = np.array(maturities)
        self.rates = np.array(rates)
        
        # Trier par maturité
        sort_idx = np.argsort(self.maturities)
        self.maturities = self.maturities[sort_idx]
        self.rates = self.rates[sort_idx]
    
    def interpolate(
        self,
        maturity: Union[float, np.ndarray],
        method: str = 'linear'
    ) -> Union[float, np.ndarray]:
        """
        Interpole le taux pour une ou plusieurs maturités
        
        Paramètres:
        -----------
        maturity : float ou array
            Maturité(s) pour laquelle on veut le taux
        method : str
            Méthode d'interpolation ('linear', 'cubic', 'quadratic')
        
        Retourne:
        ---------
        float ou array : Taux interpolé(s)
        """
        if method == 'linear':
            return np.interp(maturity, self.maturities, self.rates)
        
        elif method in ['cubic', 'quadratic']:
            if method == 'cubic':
                if len(self.maturities) < 4:
                    warnings.warn("Pas assez de points pour interpolation cubique, utilisation de linéaire")
                    return np.interp(maturity, self.maturities, self.rates)
                f = CubicSpline(self.maturities, self.rates, extrapolate=True)
            else:  # quadratic
                f = interp1d(
                    self.maturities,
                    self.rates,
                    kind='quadratic',
                    fill_value='extrapolate'
                )
            
            return f(maturity)
        
        else:
            raise ValueError(f"Méthode d'interpolation inconnue: {method}")
    
    def discount_factor(self, maturity: float, method: str = 'linear') -> float:
        """
        Calcule le facteur d'actualisation pour une maturité donnée
        
        Paramètres:
        -----------
        maturity : float
            Maturité en années
        method : str
            Méthode d'interpolation
        
        Retourne:
        ---------
        float : Facteur d'actualisation
        """
        rate = self.interpolate(maturity, method)
        return np.exp(-rate * maturity)
    
    def forward_rate(
        self,
        t1: float,
        t2: float,
        method: str = 'linear'
    ) -> float:
        """
        Calcule le taux forward entre deux dates
        
        Paramètres:
        -----------
        t1 : float
            Date de début
        t2 : float
            Date de fin
        method : str
            Méthode d'interpolation
        
        Retourne:
        ---------
        float : Taux forward
        """
        if t2 <= t1:
            raise ValueError("t2 doit être supérieur à t1")
        
        r1 = self.interpolate(t1, method)
        r2 = self.interpolate(t2, method)
        
        # Taux forward : f(t1,t2) = (r2*t2 - r1*t1) / (t2 - t1)
        forward_rate = (r2 * t2 - r1 * t1) / (t2 - t1)
        
        return forward_rate
    
    def instantaneous_forward_rate(
        self,
        maturity: float,
        method: str = 'cubic',
        h: float = 0.001
    ) -> float:
        """
        Calcule le taux forward instantané f(t) = r(t) + t * dr/dt
        
        Paramètres:
        -----------
        maturity : float
            Maturité
        method : str
            Méthode d'interpolation
        h : float
            Pas pour la différence finie
        
        Retourne:
        ---------
        float : Taux forward instantané
        """
        r = self.interpolate(maturity, method)
        r_plus = self.interpolate(maturity + h, method)
        
        dr_dt = (r_plus - r) / h
        
        return r + maturity * dr_dt
    
    def par_rate(
        self,
        maturity: float,
        frequency: int = 2,
        method: str = 'linear'
    ) -> float:
        """
        Calcule le taux par (taux du coupon qui donne un prix de 100)
        
        Paramètres:
        -----------
        maturity : float
            Maturité de l'obligation
        frequency : int
            Fréquence des paiements par an
        method : str
            Méthode d'interpolation
        
        Retourne:
        ---------
        float : Taux par
        """
        n_periods = int(maturity * frequency)
        discount_sum = 0
        
        for i in range(1, n_periods + 1):
            t = i / frequency
            discount_sum += self.discount_factor(t, method)
        
        # Par rate = (1 - DF(T)) / sum(DF)
        par_rate = (1 - self.discount_factor(maturity, method)) / discount_sum
        
        return par_rate * frequency
    
    def plot(self, n_points: int = 100, method: str = 'cubic'):
        """
        Trace la courbe de taux
        
        Paramètres:
        -----------
        n_points : int
            Nombre de points pour l'interpolation
        method : str
            Méthode d'interpolation
        """
        import matplotlib.pyplot as plt
        
        # Points interpolés
        mat_interp = np.linspace(self.maturities[0], self.maturities[-1], n_points)
        rates_interp = self.interpolate(mat_interp, method)
        
        # Graphique
        plt.figure(figsize=(12, 6))
        plt.plot(mat_interp, rates_interp * 100, '-', linewidth=2, label='Courbe interpolée')
        plt.scatter(self.maturities, self.rates * 100, s=100, c='red', 
                   zorder=5, label='Points de marché')
        
        plt.xlabel('Maturité (années)', fontsize=12)
        plt.ylabel('Taux (%)', fontsize=12)
        plt.title('Courbe de Taux', fontsize=14, fontweight='bold')
        plt.legend()
        plt.grid(True, alpha=0.3)
        plt.tight_layout()
        
        return plt.gcf()


class BondPortfolio:
    """
    Portefeuille d'obligations
    
    Paramètres:
    -----------
    bonds : list
        Liste d'objets Bond
    weights : array-like
        Poids de chaque obligation dans le portefeuille
    """
    
    def __init__(self, bonds: List[Bond], weights: np.ndarray):
        if len(bonds) != len(weights):
            raise ValueError("bonds et weights doivent avoir la même longueur")
        
        self.bonds = bonds
        self.weights = np.array(weights)
        
        # Normaliser les poids
        self.weights = self.weights / self.weights.sum()
    
    def price(self, ytm: Union[float, np.ndarray]) -> float:
        """
        Prix du portefeuille
        
        Paramètres:
        -----------
        ytm : float ou array
            YTM unique ou YTM pour chaque obligation
        
        Retourne:
        ---------
        float : Prix du portefeuille
        """
        if isinstance(ytm, (int, float)):
            ytm = np.full(len(self.bonds), ytm)
        
        portfolio_price = 0
        for bond, weight, y in zip(self.bonds, self.weights, ytm):
            portfolio_price += weight * bond.price(y)
        
        return portfolio_price
    
    def duration(self, ytm: Union[float, np.ndarray]) -> float:
        """Duration du portefeuille"""
        if isinstance(ytm, (int, float)):
            ytm = np.full(len(self.bonds), ytm)
        
        portfolio_duration = 0
        for bond, weight, y in zip(self.bonds, self.weights, ytm):
            portfolio_duration += weight * bond.duration(y)
        
        return portfolio_duration
    
    def modified_duration(self, ytm: Union[float, np.ndarray]) -> float:
        """Duration modifiée du portefeuille"""
        if isinstance(ytm, (int, float)):
            ytm = np.full(len(self.bonds), ytm)
        
        portfolio_mod_dur = 0
        for bond, weight, y in zip(self.bonds, self.weights, ytm):
            portfolio_mod_dur += weight * bond.modified_duration(y)
        
        return portfolio_mod_dur
    
    def convexity(self, ytm: Union[float, np.ndarray]) -> float:
        """Convexité du portefeuille"""
        if isinstance(ytm, (int, float)):
            ytm = np.full(len(self.bonds), ytm)
        
        portfolio_convexity = 0
        for bond, weight, y in zip(self.bonds, self.weights, ytm):
            portfolio_convexity += weight * bond.convexity(y)
        
        return portfolio_convexity
    
    def summary(self, ytm: Union[float, np.ndarray]) -> pd.DataFrame:
        """
        Résumé du portefeuille
        
        Retourne:
        ---------
        DataFrame : Résumé avec prix, duration, convexité, etc.
        """
        if isinstance(ytm, (int, float)):
            ytm_array = np.full(len(self.bonds), ytm)
        else:
            ytm_array = ytm
        
        data = []
        for i, (bond, weight, y) in enumerate(zip(self.bonds, self.weights, ytm_array)):
            data.append({
                'Bond': f'Bond {i+1}',
                'Weight': weight,
                'Price': bond.price(y),
                'Duration': bond.duration(y),
                'Modified Duration': bond.modified_duration(y),
                'Convexity': bond.convexity(y),
                'YTM': y
            })
        
        df = pd.DataFrame(data)
        
        # Ajouter les totaux du portefeuille
        portfolio_row = {
            'Bond': 'PORTFOLIO',
            'Weight': 1.0,
            'Price': self.price(ytm_array),
            'Duration': self.duration(ytm_array),
            'Modified Duration': self.modified_duration(ytm_array),
            'Convexity': self.convexity(ytm_array),
            'YTM': np.average(ytm_array, weights=self.weights)
        }
        
        df = pd.concat([df, pd.DataFrame([portfolio_row])], ignore_index=True)
        
        return df


def bootstrap_zero_curve(
    bond_prices: List[float],
    coupon_rates: List[float],
    maturities: List[float],
    face_value: float = 100,
    frequency: int = 2
) -> YieldCurve:
    """
    Bootstrap une courbe zéro-coupon à partir de prix d'obligations
    
    Paramètres:
    -----------
    bond_prices : list
        Prix des obligations
    coupon_rates : list
        Taux des coupons
    maturities : list
        Maturités
    face_value : float
        Valeur nominale
    frequency : int
        Fréquence des paiements
    
    Retourne:
    ---------
    YieldCurve : Courbe des taux zéro-coupon
    """
    zero_rates = []
    zero_maturities = []
    
    for i, (price, coupon_rate, maturity) in enumerate(
        zip(bond_prices, coupon_rates, maturities)
    ):
        n_periods = int(maturity * frequency)
        coupon = face_value * coupon_rate / frequency
        
        # Pour la première obligation ou si zéro-coupon
        if i == 0 or coupon_rate == 0:
            # Prix = FV / (1 + r)^T => r = (FV/Prix)^(1/T) - 1
            total_cash = face_value + coupon * n_periods if coupon_rate > 0 else face_value
            zero_rate = (total_cash / price)**(1/maturity) - 1
        else:
            # Soustraire la valeur des coupons actualisés avec les taux déjà calculés
            pv_coupons = 0
            
            for j in range(1, n_periods + 1):
                t = j / frequency
                
                # Interpoler le taux zéro pour cette maturité
                if t <= zero_maturities[-1]:
                    r = np.interp(t, zero_maturities, zero_rates)
                else:
                    r = zero_rates[-1]
                
                if j < n_periods:
                    cf = coupon
                else:
                    cf = coupon + face_value
                
                pv_coupons += cf * np.exp(-r * t)
            
            # Résoudre pour le taux zéro à cette maturité
            # price = pv_coupons => dernière composante actualisée
            # C'est une simplification, méthode exacte nécessite résolution itérative
            remaining_pv = price - pv_coupons + (coupon + face_value) * np.exp(-zero_rates[-1] * maturity)
            zero_rate = -np.log((coupon + face_value) / (remaining_pv)) / maturity
        
        zero_rates.append(zero_rate)
        zero_maturities.append(maturity)
    
    return YieldCurve(zero_maturities, zero_rates)


