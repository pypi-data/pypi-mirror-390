"""
Exemple 1: Pricing d'options avec différents modèles

Ce script démontre :
- Pricing Black-Scholes
- Calcul des grecques
- Volatilité implicite
- Comparaison avec binomial et Monte Carlo
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from quantfinance.pricing.options import BlackScholes, BinomialTree, MonteCarlo


def main():
    print("=" * 80)
    print("EXEMPLE 1: PRICING D'OPTIONS")
    print("=" * 80)
    
    # Paramètres de l'option
    S = 100      # Prix du sous-jacent
    K = 105      # Strike
    T = 1        # Maturité (1 an)
    r = 0.05     # Taux sans risque
    sigma = 0.25 # Volatilité
    
    print(f"\nParamètres de l'option:")
    print(f"  Prix spot (S):        {S}")
    print(f"  Strike (K):           {K}")
    print(f"  Maturité (T):         {T} an")
    print(f"  Taux sans risque (r): {r:.2%}")
    print(f"  Volatilité (σ):       {sigma:.2%}")
    
    # 1. Black-Scholes
    print("\n" + "-" * 80)
    print("1. MODÈLE BLACK-SCHOLES")
    print("-" * 80)
    
    bs_call = BlackScholes(S, K, T, r, sigma, option_type='call')
    bs_put = BlackScholes(S, K, T, r, sigma, option_type='put')
    
    print(f"\nCall européen:")
    print(f"  Prix:   {bs_call.price():.4f}")
    print(f"  Delta:  {bs_call.delta():.4f}")
    print(f"  Gamma:  {bs_call.gamma():.6f}")
    print(f"  Vega:   {bs_call.vega():.4f}")
    print(f"  Theta:  {bs_call.theta():.4f} (par an)")
    print(f"  Rho:    {bs_call.rho():.4f}")
    
    print(f"\nPut européen:")
    print(f"  Prix:   {bs_put.price():.4f}")
    print(f"  Delta:  {bs_put.delta():.4f}")
    
    # Vérification de la parité put-call
    parity_lhs = bs_call.price() - bs_put.price()
    parity_rhs = S - K * np.exp(-r * T)
    print(f"\nVérification parité put-call:")
    print(f"  C - P = {parity_lhs:.4f}")
    print(f"  S - K*e^(-rT) = {parity_rhs:.4f}")
    print(f"  Différence: {abs(parity_lhs - parity_rhs):.10f}")
    
    # 2. Modèle Binomial
    print("\n" + "-" * 80)
    print("2. MODÈLE BINOMIAL")
    print("-" * 80)
    
    binomial_euro = BinomialTree(S, K, T, r, sigma, N=500, 
                                  option_type='call', exercise_type='european')
    binomial_amer = BinomialTree(S, K, T, r, sigma, N=500, 
                                  option_type='call', exercise_type='american')
    
    print(f"\nCall européen (500 pas):")
    print(f"  Prix: {binomial_euro.price():.4f}")
    print(f"  Écart avec BS: {abs(binomial_euro.price() - bs_call.price()):.4f}")
    
    print(f"\nCall américain (500 pas):")
    print(f"  Prix: {binomial_amer.price():.4f}")
    print(f"  Prime exercice anticipé: {binomial_amer.price() - binomial_euro.price():.4f}")
    
    # 3. Monte Carlo
    print("\n" + "-" * 80)
    print("3. SIMULATION MONTE CARLO")
    print("-" * 80)
    
    mc = MonteCarlo(S, K, T, r, sigma, option_type='call', 
                    n_simulations=100000, random_seed=42)
    
    mc_price, lower, upper = mc.price_with_confidence_interval(confidence_level=0.95)
    
    print(f"\nCall européen (100,000 simulations):")
    print(f"  Prix:         {mc_price:.4f}")
    print(f"  IC 95%:       [{lower:.4f}, {upper:.4f}]")
    print(f"  Largeur IC:   {upper - lower:.4f}")
    print(f"  Écart avec BS: {abs(mc_price - bs_call.price()):.4f}")
    
    # 4. Volatilité implicite
    print("\n" + "-" * 80)
    print("4. VOLATILITÉ IMPLICITE")
    print("-" * 80)
    
    market_price = 8.50
    bs_iv = BlackScholes(S, K, T, r, 0.3, option_type='call')
    
    try:
        implied_vol = bs_iv.implied_volatility(market_price)
        print(f"\nPrix de marché: {market_price:.4f}")
        print(f"Volatilité implicite: {implied_vol:.4f} ({implied_vol:.2%})")
        
        # Vérification
        bs_check = BlackScholes(S, K, T, r, implied_vol, option_type='call')
        print(f"Vérification (prix recalculé): {bs_check.price():.4f}")
    except Exception as e:
        print(f"Erreur: {e}")
    
    # 5. Comparaison graphique
    print("\n" + "-" * 80)
    print("5. VISUALISATION")
    print("-" * 80)
    
    # Prix vs Spot
    spots = np.linspace(80, 120, 50)
    bs_prices = [BlackScholes(s, K, T, r, sigma, 'call').price() for s in spots]
    intrinsic = np.maximum(spots - K, 0)
    
    plt.figure(figsize=(14, 10))
    
    # Subplot 1: Prix vs Spot
    plt.subplot(2, 2, 1)
    plt.plot(spots, bs_prices, 'b-', linewidth=2, label='Prix option')
    plt.plot(spots, intrinsic, 'r--', linewidth=2, label='Valeur intrinsèque')
    plt.axvline(K, color='gray', linestyle=':', alpha=0.7, label='Strike')
    plt.xlabel('Prix du sous-jacent (S)')
    plt.ylabel('Prix de l\'option')
    plt.title('Prix du Call vs Prix Spot')
    plt.legend()
    plt.grid(True, alpha=0.3)
    
    # Subplot 2: Delta vs Spot
    plt.subplot(2, 2, 2)
    deltas = [BlackScholes(s, K, T, r, sigma, 'call').delta() for s in spots]
    plt.plot(spots, deltas, 'g-', linewidth=2)
    plt.axvline(K, color='gray', linestyle=':', alpha=0.7)
    plt.axhline(0.5, color='r', linestyle='--', alpha=0.5, label='Delta = 0.5')
    plt.xlabel('Prix du sous-jacent (S)')
    plt.ylabel('Delta')
    plt.title('Delta vs Prix Spot')
    plt.legend()
    plt.grid(True, alpha=0.3)
    
    # Subplot 3: Prix vs Volatilité
    plt.subplot(2, 2, 3)
    vols = np.linspace(0.05, 0.60, 50)
    prices_vs_vol = [BlackScholes(S, K, T, r, v, 'call').price() for v in vols]
    plt.plot(vols * 100, prices_vs_vol, 'purple', linewidth=2)
    plt.axvline(sigma * 100, color='r', linestyle='--', alpha=0.7, label=f'σ actuelle = {sigma:.0%}')
    plt.xlabel('Volatilité (%)')
    plt.ylabel('Prix de l\'option')
    plt.title('Prix du Call vs Volatilité')
    plt.legend()
    plt.grid(True, alpha=0.3)
    
    # Subplot 4: Prix vs Maturité
    plt.subplot(2, 2, 4)
    maturities = np.linspace(0.1, 2, 50)
    prices_vs_mat = [BlackScholes(S, K, t, r, sigma, 'call').price() for t in maturities]
    plt.plot(maturities, prices_vs_mat, 'orange', linewidth=2)
    plt.axvline(T, color='r', linestyle='--', alpha=0.7, label=f'T actuelle = {T}')
    plt.xlabel('Maturité (années)')
    plt.ylabel('Prix de l\'option')
    plt.title('Prix du Call vs Maturité')
    plt.legend()
    plt.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('option_pricing_analysis.png', dpi=300, bbox_inches='tight')
    print("\n✓ Graphique sauvegardé: option_pricing_analysis.png")
    
    print("\n" + "=" * 80)
    print("Exemple terminé avec succès!")
    print("=" * 80)


if __name__ == "__main__":
    main()