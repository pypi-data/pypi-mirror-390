
## Pricing d'Options (`quantfinance.pricing`)

### `BlackScholes`

Modèle de Black-Scholes pour options européennes.

#### Méthodes :

---

##### `__init__(S, K, T, r, sigma, option_type='call', q=0.0)`

Initialise avec les paramètres de l’option.

**Exemple :**
```python
bs = BlackScholes(S=100, K=100, T=1, r=0.05, sigma=0.2, option_type='call')
```

---

##### `price() → float`

Calcule le prix de l’option.

**Exemple :**
```python
price = bs.price()
print("Prix:", price)
```

---

##### `delta() → float`

Calcule le Delta (∂V/∂S).

**Exemple :**
```python
delta = bs.delta()
print("Delta:", delta)
```

---

##### `gamma() → float`

Calcule le Gamma (∂²V/∂S²).

**Exemple :**
```python
gamma = bs.gamma()
print("Gamma:", gamma)
```

---

##### `vega() → float`

Calcule le Vega (∂V/∂σ).

**Exemple :**
```python
vega = bs.vega()
print("Vega:", vega)
```

---

##### `theta() → float`

Calcule le Theta (∂V/∂t).

**Exemple :**
```python
theta = bs.theta()
print("Theta:", theta)
```

---

##### `rho() → float`

Calcule le Rho (∂V/∂r).

**Exemple :**
```python
rho = bs.rho()
print("Rho:", rho)
```

---

##### `greeks() → Dict`

Retourne toutes les grecques.

**Exemple :**
```python
greeks = bs.greeks()
print("Grecques:", greeks)
```

---

##### `implied_volatility(market_price, initial_guess=0.3, ...) → float`

Calcule la volatilité implicite.

**Exemple :**
```python
iv = bs.implied_volatility(market_price=5.0)
print("Volatilité implicite:", iv)
```

---

### `BinomialTree`

Modèle binomial pour options européennes et américaines.

#### Méthodes :

---

##### `__init__(S, K, T, r, sigma, N=100, option_type='call', exercise_type='european', q=0.0)`

Initialise avec les paramètres.

**Exemple :**
```python
tree = BinomialTree(S=100, K=100, T=1, r=0.05, sigma=0.2, N=100, exercise_type='american')
```

---

##### `price() → float`

Calcule le prix de l’option.

**Exemple :**
```python
price = tree.price()
print("Prix:", price)
```

---

##### `delta() → float`

Calcule le Delta par différences finies.

**Exemple :**
```python
delta = tree.delta()
print("Delta:", delta)
```

---

### `MonteCarlo`

Pricing d’options par simulation Monte Carlo.

#### Méthodes :

---

##### `__init__(S, K, T, r, sigma, option_type='call', n_simulations=10000, n_steps=252, random_seed=None, q=0.0)`

Initialise avec les paramètres.

**Exemple :**
```python
mc = MonteCarlo(S=100, K=100, T=1, r=0.05, sigma=0.2, n_simulations=10000)
```

---

##### `price() → float`

Calcule le prix par simulation.

**Exemple :**
```python
price = mc.price()
print("Prix MC:", price)
```

---

##### `price_with_confidence_interval(confidence_level=0.95) → Tuple[float, float, float]`

Retourne le prix avec intervalle de confiance.

**Exemple :**
```python
price, lower, upper = mc.price_with_confidence_interval()
print(f"Prix: {price:.4f} [{lower:.4f}, {upper:.4f}]")
```

