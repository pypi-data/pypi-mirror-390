"""
Modèles de pricing d'options

Implémente :
- Black-Scholes pour options européennes
- Modèle binomial pour options américaines et européennes
- Simulations Monte Carlo
- Calcul de volatilité implicite
"""

import numpy as np
from scipy.stats import norm
from scipy.optimize import brentq, minimize_scalar
from typing import Literal, Optional, Tuple, Dict
import warnings


class BlackScholes:
    """
    Modèle de Black-Scholes pour le pricing d'options européennes
    
    Paramètres:
    -----------
    S : float
        Prix actuel du sous-jacent
    K : float
        Prix d'exercice (strike)
    T : float
        Temps jusqu'à maturité (en années)
    r : float
        Taux sans risque (annualisé)
    sigma : float
        Volatilité (annualisée)
    option_type : str
        Type d'option ('call' ou 'put')
    q : float, optional
        Taux de dividende continu (défaut: 0)
    """
    
    def __init__(
        self,
        S: float,
        K: float,
        T: float,
        r: float,
        sigma: float,
        option_type: Literal['call', 'put'] = 'call',
        q: float = 0.0
    ):
        self.S = S
        self.K = K
        self.T = T
        self.r = r
        self.sigma = sigma
        self.option_type = option_type.lower()
        self.q = q
        
        if self.option_type not in ['call', 'put']:
            raise ValueError("option_type doit être 'call' ou 'put'")
        
        if self.T <= 0:
            raise ValueError("La maturité T doit être positive")
        
        if self.sigma <= 0:
            raise ValueError("La volatilité sigma doit être positive")
    
    def d1(self) -> float:
        """Calcule d1 dans la formule de Black-Scholes"""
        return (np.log(self.S / self.K) + (self.r - self.q + 0.5 * self.sigma**2) * self.T) / \
               (self.sigma * np.sqrt(self.T))
    
    def d2(self) -> float:
        """Calcule d2 dans la formule de Black-Scholes"""
        return self.d1() - self.sigma * np.sqrt(self.T)
    
    def price(self) -> float:
        """
        Calcule le prix de l'option
        
        Retourne:
        ---------
        float : Prix de l'option
        """
        d1 = self.d1()
        d2 = self.d2()
        
        if self.option_type == 'call':
            price = (self.S * np.exp(-self.q * self.T) * norm.cdf(d1) - 
                    self.K * np.exp(-self.r * self.T) * norm.cdf(d2))
        else:  # put
            price = (self.K * np.exp(-self.r * self.T) * norm.cdf(-d2) - 
                    self.S * np.exp(-self.q * self.T) * norm.cdf(-d1))
        
        return price
    
    def delta(self) -> float:
        """
        Calcule le Delta (∂V/∂S)
        Sensibilité du prix de l'option au prix du sous-jacent
        """
        d1 = self.d1()
        
        if self.option_type == 'call':
            return np.exp(-self.q * self.T) * norm.cdf(d1)
        else:
            return np.exp(-self.q * self.T) * (norm.cdf(d1) - 1)
    
    def gamma(self) -> float:
        """
        Calcule le Gamma (∂²V/∂S²)
        Sensibilité du Delta au prix du sous-jacent
        """
        d1 = self.d1()
        return (np.exp(-self.q * self.T) * norm.pdf(d1)) / \
               (self.S * self.sigma * np.sqrt(self.T))
    
    def vega(self) -> float:
        """
        Calcule le Vega (∂V/∂σ)
        Sensibilité du prix à la volatilité
        """
        d1 = self.d1()
        return self.S * np.exp(-self.q * self.T) * norm.pdf(d1) * np.sqrt(self.T)
    
    def theta(self) -> float:
        """
        Calcule le Theta (∂V/∂t)
        Sensibilité du prix au passage du temps
        Retourne la valeur par année (diviser par 252 pour valeur quotidienne)
        """
        d1 = self.d1()
        d2 = self.d2()
        
        term1 = -(self.S * np.exp(-self.q * self.T) * norm.pdf(d1) * self.sigma) / \
                (2 * np.sqrt(self.T))
        
        if self.option_type == 'call':
            term2 = self.q * self.S * np.exp(-self.q * self.T) * norm.cdf(d1)
            term3 = -self.r * self.K * np.exp(-self.r * self.T) * norm.cdf(d2)
        else:
            term2 = -self.q * self.S * np.exp(-self.q * self.T) * norm.cdf(-d1)
            term3 = self.r * self.K * np.exp(-self.r * self.T) * norm.cdf(-d2)
        
        return term1 + term2 + term3
    
    def rho(self) -> float:
        """
        Calcule le Rho (∂V/∂r)
        Sensibilité du prix au taux sans risque
        """
        d2 = self.d2()
        
        if self.option_type == 'call':
            return self.K * self.T * np.exp(-self.r * self.T) * norm.cdf(d2)
        else:
            return -self.K * self.T * np.exp(-self.r * self.T) * norm.cdf(-d2)
    
    def greeks(self) -> Dict[str, float]:
        """
        Retourne toutes les grecques dans un dictionnaire
        
        Retourne:
        ---------
        dict : Dictionnaire contenant delta, gamma, vega, theta, rho
        """
        return {
            'delta': self.delta(),
            'gamma': self.gamma(),
            'vega': self.vega(),
            'theta': self.theta(),
            'rho': self.rho()
        }
    
    def implied_volatility(
        self,
        market_price: float,
        initial_guess: float = 0.3,
        max_iterations: int = 100,
        tolerance: float = 1e-6
    ) -> float:
        """
        Calcule la volatilité implicite par méthode de Newton-Raphson
        
        Paramètres:
        -----------
        market_price : float
            Prix de marché observé de l'option
        initial_guess : float
            Estimation initiale de la volatilité
        max_iterations : int
            Nombre maximum d'itérations
        tolerance : float
            Critère de convergence
        
        Retourne:
        ---------
        float : Volatilité implicite
        """
        sigma = initial_guess
        
        for i in range(max_iterations):
            # Créer une nouvelle instance avec la volatilité actuelle
            bs_temp = BlackScholes(self.S, self.K, self.T, self.r, sigma, 
                                  self.option_type, self.q)
            
            # Calculer le prix et le vega
            price_diff = bs_temp.price() - market_price
            vega_val = bs_temp.vega()
            
            # Vérifier la convergence
            if abs(price_diff) < tolerance:
                return sigma
            
            # Éviter division par zéro
            if vega_val < 1e-10:
                warnings.warn("Vega trop petit, utilisation de la méthode de Brent")
                return self._implied_volatility_brent(market_price)
            
            # Mise à jour Newton-Raphson
            sigma = sigma - price_diff / vega_val
            
            # S'assurer que sigma reste positif
            if sigma <= 0:
                sigma = 0.01
        
        warnings.warn(f"La méthode n'a pas convergé après {max_iterations} itérations")
        return sigma
    
    def _implied_volatility_brent(self, market_price: float) -> float:
        """Calcule la volatilité implicite par méthode de Brent (fallback)"""
        def objective(sigma):
            bs_temp = BlackScholes(self.S, self.K, self.T, self.r, sigma, 
                                  self.option_type, self.q)
            return bs_temp.price() - market_price
        
        try:
            return brentq(objective, 0.001, 5.0)
        except ValueError:
            raise ValueError("Impossible de trouver la volatilité implicite")


class BinomialTree:
    """
    Modèle binomial (Cox-Ross-Rubinstein) pour le pricing d'options
    Supporte les options européennes et américaines
    
    Paramètres:
    -----------
    S : float
        Prix actuel du sous-jacent
    K : float
        Prix d'exercice
    T : float
        Temps jusqu'à maturité (années)
    r : float
        Taux sans risque
    sigma : float
        Volatilité
    N : int
        Nombre de pas dans l'arbre
    option_type : str
        'call' ou 'put'
    exercise_type : str
        'european' ou 'american'
    q : float
        Taux de dividende continu
    """
    
    def __init__(
        self,
        S: float,
        K: float,
        T: float,
        r: float,
        sigma: float,
        N: int = 100,
        option_type: Literal['call', 'put'] = 'call',
        exercise_type: Literal['european', 'american'] = 'european',
        q: float = 0.0
    ):
        self.S = S
        self.K = K
        self.T = T
        self.r = r
        self.sigma = sigma
        self.N = N
        self.option_type = option_type.lower()
        self.exercise_type = exercise_type.lower()
        self.q = q
        
        # Paramètres de l'arbre
        self.dt = T / N
        self.u = np.exp(sigma * np.sqrt(self.dt))
        self.d = 1 / self.u
        self.p = (np.exp((r - q) * self.dt) - self.d) / (self.u - self.d)
        self.discount = np.exp(-r * self.dt)
    
    def price(self) -> float:
        """
        Calcule le prix de l'option
        
        Retourne:
        ---------
        float : Prix de l'option
        """
        # Initialiser les prix du sous-jacent à maturité
        stock_prices = np.zeros(self.N + 1)
        option_values = np.zeros(self.N + 1)
        
        # Prix du sous-jacent à maturité
        for i in range(self.N + 1):
            stock_prices[i] = self.S * (self.u ** (self.N - i)) * (self.d ** i)
        
        # Valeurs de l'option à maturité
        if self.option_type == 'call':
            option_values = np.maximum(stock_prices - self.K, 0)
        else:
            option_values = np.maximum(self.K - stock_prices, 0)
        
        # Remontée dans l'arbre
        for j in range(self.N - 1, -1, -1):
            for i in range(j + 1):
                # Prix du sous-jacent à ce nœud
                S_node = self.S * (self.u ** (j - i)) * (self.d ** i)
                
                # Valeur de continuation (espérance actualisée)
                continuation_value = self.discount * (
                    self.p * option_values[i] + 
                    (1 - self.p) * option_values[i + 1]
                )
                
                if self.exercise_type == 'american':
                    # Valeur d'exercice immédiat
                    if self.option_type == 'call':
                        exercise_value = max(S_node - self.K, 0)
                    else:
                        exercise_value = max(self.K - S_node, 0)
                    
                    # Prendre le maximum
                    option_values[i] = max(continuation_value, exercise_value)
                else:
                    option_values[i] = continuation_value
        
        return option_values[0]
    
    def delta(self) -> float:
        """Calcule le Delta par différences finies"""
        dS = self.S * 0.01
        
        bs_up = BinomialTree(self.S + dS, self.K, self.T, self.r, self.sigma,
                            self.N, self.option_type, self.exercise_type, self.q)
        bs_down = BinomialTree(self.S - dS, self.K, self.T, self.r, self.sigma,
                              self.N, self.option_type, self.exercise_type, self.q)
        
        return (bs_up.price() - bs_down.price()) / (2 * dS)
    
    def gamma(self) -> float:
        """Calcule le Gamma par différences finies"""
        dS = self.S * 0.01
        
        bs_up = BinomialTree(self.S + dS, self.K, self.T, self.r, self.sigma,
                            self.N, self.option_type, self.exercise_type, self.q)
        bs_center = BinomialTree(self.S, self.K, self.T, self.r, self.sigma,
                                self.N, self.option_type, self.exercise_type, self.q)
        bs_down = BinomialTree(self.S - dS, self.K, self.T, self.r, self.sigma,
                              self.N, self.option_type, self.exercise_type, self.q)
        
        return (bs_up.price() - 2*bs_center.price() + bs_down.price()) / (dS**2)


class MonteCarlo:
    """
    Pricing d'options par simulation Monte Carlo
    
    Paramètres:
    -----------
    S : float
        Prix actuel du sous-jacent
    K : float
        Prix d'exercice
    T : float
        Temps jusqu'à maturité
    r : float
        Taux sans risque
    sigma : float
        Volatilité
    option_type : str
        'call' ou 'put'
    n_simulations : int
        Nombre de simulations
    n_steps : int
        Nombre de pas de temps
    random_seed : int, optional
        Graine aléatoire pour reproductibilité
    q : float
        Taux de dividende continu
    """
    
    def __init__(
        self,
        S: float,
        K: float,
        T: float,
        r: float,
        sigma: float,
        option_type: Literal['call', 'put'] = 'call',
        n_simulations: int = 10000,
        n_steps: int = 252,
        random_seed: Optional[int] = None,
        q: float = 0.0
    ):
        self.S = S
        self.K = K
        self.T = T
        self.r = r
        self.sigma = sigma
        self.option_type = option_type.lower()
        self.n_simulations = n_simulations
        self.n_steps = n_steps
        self.random_seed = random_seed
        self.q = q
        self.dt = T / n_steps
        
        if random_seed is not None:
            np.random.seed(random_seed)
    
    def _simulate_paths(self) -> np.ndarray:
        """
        Simule les trajectoires du sous-jacent (mouvement brownien géométrique)
        
        Retourne:
        ---------
        array : Matrice (n_simulations x n_steps+1) des prix simulés
        """
        # Générer les chocs aléatoires
        Z = np.random.standard_normal((self.n_simulations, self.n_steps))
        
        # Initialiser la matrice des prix
        S = np.zeros((self.n_simulations, self.n_steps + 1))
        S[:, 0] = self.S
        
        # Simulation
        for t in range(1, self.n_steps + 1):
            S[:, t] = S[:, t-1] * np.exp(
                (self.r - self.q - 0.5 * self.sigma**2) * self.dt + 
                self.sigma * np.sqrt(self.dt) * Z[:, t-1]
            )
        
        return S
    
    def price(self) -> float:
        """
        Calcule le prix de l'option européenne
        
        Retourne:
        ---------
        float : Prix de l'option
        """
        # Simuler les trajectoires
        np.random.seed(42)
        
        S = self._simulate_paths()
        
        # Prix à maturité
        S_T = S[:, -1]
        
        # Payoffs
        if self.option_type == 'call':
            payoffs = np.maximum(S_T - self.K, 0)
        else:
            payoffs = np.maximum(self.K - S_T, 0)
        
        # Prix = espérance actualisée des payoffs
        price = np.exp(-self.r * self.T) * np.mean(payoffs)
        
        return price
    
    def price_with_confidence_interval(
        self,
        confidence_level: float = 0.95
    ) -> Tuple[float, float, float]:
        """
        Calcule le prix avec intervalle de confiance
        
        Paramètres:
        -----------
        confidence_level : float
            Niveau de confiance (ex: 0.95 pour 95%)
        
        Retourne:
        ---------
        tuple : (prix, borne_inf, borne_sup)
        """
        # Simuler les trajectoires
        S = self._simulate_paths()
        S_T = S[:, -1]
        
        # Payoffs
        if self.option_type == 'call':
            payoffs = np.maximum(S_T - self.K, 0)
        else:
            payoffs = np.maximum(self.K - self.S_T, 0)
        
        # Prix actualisés
        discounted_payoffs = np.exp(-self.r * self.T) * payoffs
        
        # Statistiques
        price = np.mean(discounted_payoffs)
        std_error = np.std(discounted_payoffs) / np.sqrt(self.n_simulations)
        
        # Intervalle de confiance (approximation normale)
        z_score = norm.ppf((1 + confidence_level) / 2)
        lower_bound = price - z_score * std_error
        upper_bound = price + z_score * std_error
        
        return price, lower_bound, upper_bound
    
    def price_asian_option(self, option_type: str = 'arithmetic') -> float:
        """
        Prix d'une option asiatique (moyenne)
        
        Paramètres:
        -----------
        option_type : str
            'arithmetic' ou 'geometric'
        
        Retourne:
        ---------
        float : Prix de l'option asiatique
        """
        S = self._simulate_paths()
        
        if option_type == 'arithmetic':
            S_avg = np.mean(S, axis=1)
        elif option_type == 'geometric':
            S_avg = np.exp(np.mean(np.log(S), axis=1))
        else:
            raise ValueError("option_type doit être 'arithmetic' ou 'geometric'")
        
        # Payoffs
        if self.option_type == 'call':
            payoffs = np.maximum(S_avg - self.K, 0)
        else:
            payoffs = np.maximum(self.K - S_avg, 0)
        
        price = np.exp(-self.r * self.T) * np.mean(payoffs)
        
        return price
    
    def price_barrier_option(
        self,
        barrier: float,
        barrier_type: Literal['up-and-out', 'down-and-out', 'up-and-in', 'down-and-in']
    ) -> float:
        """
        Prix d'une option à barrière
        
        Paramètres:
        -----------
        barrier : float
            Niveau de la barrière
        barrier_type : str
            Type de barrière
        
        Retourne:
        ---------
        float : Prix de l'option à barrière
        """
        S = self._simulate_paths()
        S_T = S[:, -1]
        
        # Vérifier si la barrière a été touchée
        if barrier_type == 'up-and-out':
            knocked_out = np.any(S >= barrier, axis=1)
            active = ~knocked_out
        elif barrier_type == 'down-and-out':
            knocked_out = np.any(S <= barrier, axis=1)
            active = ~knocked_out
        elif barrier_type == 'up-and-in':
            knocked_in = np.any(S >= barrier, axis=1)
            active = knocked_in
        elif barrier_type == 'down-and-in':
            knocked_in = np.any(S <= barrier, axis=1)
            active = knocked_in
        else:
            raise ValueError(f"barrier_type inconnu: {barrier_type}")
        
        # Payoffs
        if self.option_type == 'call':
            payoffs = np.maximum(S_T - self.K, 0) * active
        else:
            payoffs = np.maximum(self.K - S_T, 0) * active
        
        price = np.exp(-self.r * self.T) * np.mean(payoffs)
        
        return price


class ImpliedVolatility:
    """Utilitaires pour le calcul de volatilité implicite"""
    
    @staticmethod
    def calculate(
        market_price: float,
        S: float,
        K: float,
        T: float,
        r: float,
        option_type: str,
        method: str = 'newton'
    ) -> float:
        """
        Calcule la volatilité implicite
        
        Paramètres:
        -----------
        market_price : float
            Prix de marché
        S, K, T, r : float
            Paramètres Black-Scholes
        option_type : str
            'call' ou 'put'
        method : str
            'newton' ou 'brent'
        
        Retourne:
        ---------
        float : Volatilité implicite
        """
        bs = BlackScholes(S, K, T, r, 0.3, option_type)
        return bs.implied_volatility(market_price)
    
    @staticmethod
    def volatility_surface(
        market_prices: np.ndarray,
        S: float,
        strikes: np.ndarray,
        maturities: np.ndarray,
        r: float,
        option_type: str
    ) -> np.ndarray:
        """
        Calcule une surface de volatilité implicite
        
        Paramètres:
        -----------
        market_prices : array
            Matrice (n_strikes x n_maturities) des prix de marché
        S : float
            Prix du sous-jacent
        strikes : array
            Prix d'exercice
        maturities : array
            Maturités
        r : float
            Taux sans risque
        option_type : str
            'call' ou 'put'
        
        Retourne:
        ---------
        array : Surface de volatilité implicite
        """
        iv_surface = np.zeros_like(market_prices)
        
        for i, K in enumerate(strikes):
            for j, T in enumerate(maturities):
                try:
                    bs = BlackScholes(S, K, T, r, 0.3, option_type)
                    iv_surface[i, j] = bs.implied_volatility(market_prices[i, j])
                except:
                    iv_surface[i, j] = np.nan
        
        return iv_surface