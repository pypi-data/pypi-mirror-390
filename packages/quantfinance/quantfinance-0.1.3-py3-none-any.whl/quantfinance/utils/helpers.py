"""
Fonctions utilitaires diverses
"""

import numpy as np
import pandas as pd
from typing import Union
from datetime import datetime


def date_range(
    start: Union[str, datetime],
    end: Union[str, datetime],
    freq: str = 'D'
) -> pd.DatetimeIndex:
    """
    Crée une plage de dates
    
    Paramètres:
    -----------
    start : str ou datetime
        Date de début
    end : str ou datetime
        Date de fin
    freq : str
        Fréquence ('D', 'W', 'M', 'Q', 'Y', 'B' pour business days)
    
    Retourne:
    ---------
    DatetimeIndex : Plage de dates
    """
    return pd.date_range(start=start, end=end, freq=freq)


def annualize_return(
    returns: Union[float, np.ndarray, pd.Series],
    periods_per_year: int = 252
) -> Union[float, np.ndarray, pd.Series]:
    """
    Annualise un rendement
    
    Paramètres:
    -----------
    returns : float, array ou Series
        Rendement(s) à annualiser
    periods_per_year : int
        Nombre de périodes par an
    
    Retourne:
    ---------
    Rendement annualisé
    """
    return returns * periods_per_year


def annualize_volatility(
    volatility: Union[float, np.ndarray, pd.Series],
    periods_per_year: int = 252
) -> Union[float, np.ndarray, pd.Series]:
    """
    Annualise une volatilité
    
    Paramètres:
    -----------
    volatility : float, array ou Series
        Volatilité à annualiser
    periods_per_year : int
        Nombre de périodes par an
    
    Retourne:
    ---------
    Volatilité annualisée
    """
    return volatility * np.sqrt(periods_per_year)


def compound_returns(
    returns: Union[np.ndarray, pd.Series]
) -> float:
    """
    Calcule le rendement composé total
    
    Paramètres:
    -----------
    returns : array ou Series
        Série de rendements
    
    Retourne:
    ---------
    float : Rendement composé total
    """
    if isinstance(returns, pd.Series):
        returns = returns.values
    
    return np.prod(1 + returns) - 1


def deannualize_return(
    annual_return: float,
    periods_per_year: int = 252
) -> float:
    """
    Dé-annualise un rendement
    
    Paramètres:
    -----------
    annual_return : float
        Rendement annuel
    periods_per_year : int
        Périodes par an
    
    Retourne:
    ---------
    float : Rendement par période
    """
    return annual_return / periods_per_year


def deannualize_volatility(
    annual_volatility: float,
    periods_per_year: int = 252
) -> float:
    """
    Dé-annualise une volatilité
    
    Paramètres:
    -----------
    annual_volatility : float
        Volatilité annuelle
    periods_per_year : int
        Périodes par an
    
    Retourne:
    ---------
    float : Volatilité par période
    """
    return annual_volatility / np.sqrt(periods_per_year)
