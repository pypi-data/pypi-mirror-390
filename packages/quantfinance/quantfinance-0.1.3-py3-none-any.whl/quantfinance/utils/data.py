"""
Utilitaires pour le chargement et la manipulation de données financières

Fonctionnalités :
- Chargement depuis diverses sources (CSV, Yahoo Finance, APIs)
- Nettoyage et préparation de données
- Transformation de données
- Génération de données synthétiques
"""

import numpy as np
import pandas as pd
from typing import List, Union, Optional, Tuple, Dict
from datetime import datetime, timedelta
import warnings


class DataLoader:
    """Chargeur de données financières"""
    
    @staticmethod
    def load_csv(
        filepath: str,
        date_column: str = 'Date',
        parse_dates: bool = True,
        index_col: Optional[Union[str, int]] = None
    ) -> pd.DataFrame:
        """
        Charge des données depuis un fichier CSV
        
        Paramètres:
        -----------
        filepath : str
            Chemin vers le fichier CSV
        date_column : str
            Nom de la colonne de dates
        parse_dates : bool
            Parser automatiquement les dates
        index_col : str ou int, optional
            Colonne à utiliser comme index
        
        Retourne:
        ---------
        DataFrame : Données chargées
        """
        try:
            if index_col is None and date_column in pd.read_csv(filepath, nrows=0).columns:
                index_col = date_column
            
            df = pd.read_csv(
                filepath,
                parse_dates=[date_column] if parse_dates else False,
                index_col=index_col
            )
            
            return df
        
        except FileNotFoundError:
            raise FileNotFoundError(f"Fichier non trouvé: {filepath}")
        except Exception as e:
            raise Exception(f"Erreur lors du chargement: {str(e)}")
    
    @staticmethod
    def download_yahoo_finance(
        tickers: Union[str, List[str]],
        start_date: Union[str, datetime],
        end_date: Union[str, datetime] = None,
        column: str = 'Adj Close',
        interval: str = '1d'
    ) -> pd.DataFrame:
        """
        Télécharge des données depuis Yahoo Finance
        
        Paramètres:
        -----------
        tickers : str ou list
            Symbole(s) boursier(s)
        start_date : str ou datetime
            Date de début (format: 'YYYY-MM-DD')
        end_date : str ou datetime, optional
            Date de fin (défaut: aujourd'hui)
        column : str
            Colonne à extraire ('Open', 'High', 'Low', 'Close', 'Adj Close', 'Volume')
        interval : str
            Intervalle ('1d', '1wk', '1mo')
        
        Retourne:
        ---------
        DataFrame : Prix téléchargés
        """
        try:
            import yfinance as yf
        except ImportError:
            raise ImportError(
                "yfinance n'est pas installé. Installez-le avec: pip install yfinance"
            )
        
        if end_date is None:
            end_date = datetime.now()
        
        if isinstance(tickers, str):
            tickers = [tickers]
        
        # Télécharger les données
        data = yf.download(
            tickers,
            start=start_date,
            end=end_date,
            interval=interval,
            progress=False,
            auto_adjust=False
        )
        
        # Extraire la colonne souhaitée
        if len(tickers) == 1:
            if column in data.columns:
                result = data[[column]].rename(columns={column: tickers[0]})
            else:
                result = data
        else:
            if column in data.columns.levels[0]:
                result = data[column]
            else:
                result = data
        
        return result
    
    @staticmethod
    def download_pandas_datareader(
        tickers: Union[str, List[str]],
        start_date: Union[str, datetime],
        end_date: Union[str, datetime] = None,
        source: str = 'yahoo'
    ) -> pd.DataFrame:
        """
        Télécharge des données via pandas-datareader
        
        Paramètres:
        -----------
        tickers : str ou list
            Symbole(s) boursier(s)
        start_date : str ou datetime
            Date de début
        end_date : str ou datetime, optional
            Date de fin
        source : str
            Source de données ('yahoo', 'fred', 'iex', etc.)
        
        Retourne:
        ---------
        DataFrame : Données téléchargées
        """
        try:
            import pandas_datareader as pdr
        except ImportError:
            raise ImportError(
                "pandas-datareader n'est pas installé. "
                "Installez-le avec: pip install pandas-datareader"
            )
        
        if end_date is None:
            end_date = datetime.now()
        
        if isinstance(tickers, str):
            data = pdr.DataReader(tickers, source, start_date, end_date)
        else:
            data = {}
            for ticker in tickers:
                data[ticker] = pdr.DataReader(ticker, source, start_date, end_date)
            data = pd.concat(data, axis=1)
        
        return data
    
    @staticmethod
    def generate_synthetic_prices(
        n_assets: int = 5,
        n_days: int = 252,
        initial_price: float = 100,
        mu: float = 0.0001,
        sigma: float = 0.02,
        correlation: float = 0.3,
        random_seed: Optional[int] = None
    ) -> pd.DataFrame:
        """
        Génère des prix synthétiques via mouvement brownien géométrique
        
        Paramètres:
        -----------
        n_assets : int
            Nombre d'actifs
        n_days : int
            Nombre de jours
        initial_price : float
            Prix initial
        mu : float
            Rendement moyen quotidien
        sigma : float
            Volatilité quotidienne
        correlation : float
            Corrélation entre actifs (0 à 1)
        random_seed : int, optional
            Graine aléatoire pour reproductibilité
        
        Retourne:
        ---------
        DataFrame : Prix synthétiques
        """
        if random_seed is not None:
            np.random.seed(random_seed)
        
        # Matrice de corrélation
        corr_matrix = np.full((n_assets, n_assets), correlation)
        np.fill_diagonal(corr_matrix, 1.0)
        
        # Décomposition de Cholesky pour corrélation
        try:
            L = np.linalg.cholesky(corr_matrix)
        except np.linalg.LinAlgError:
            warnings.warn("Matrice de corrélation non définie positive, utilisation d'identité")
            L = np.eye(n_assets)
        
        # Générer les rendements non corrélés
        uncorrelated_returns = np.random.normal(mu, sigma, (n_days, n_assets))
        
        # Appliquer la corrélation
        correlated_returns = uncorrelated_returns @ L.T
        
        # Générer les prix
        prices = np.zeros((n_days + 1, n_assets))
        prices[0, :] = initial_price
        
        for t in range(1, n_days + 1):
            prices[t, :] = prices[t-1, :] * np.exp(correlated_returns[t-1, :])
        
        # Créer DataFrame avec dates
        dates = pd.date_range(start='2020-01-01', periods=n_days+1, freq='B')
        asset_names = [f'Asset_{i+1}' for i in range(n_assets)]
        
        return pd.DataFrame(prices, index=dates, columns=asset_names)
    
    @staticmethod
    def generate_ohlcv_data(
        n_days: int = 252,
        initial_price: float = 100,
        volatility: float = 0.02,
        volume_mean: int = 1000000,
        random_seed: Optional[int] = None
    ) -> pd.DataFrame:
        """
        Génère des données OHLCV (Open, High, Low, Close, Volume) synthétiques
        
        Paramètres:
        -----------
        n_days : int
            Nombre de jours
        initial_price : float
            Prix initial
        volatility : float
            Volatilité quotidienne
        volume_mean : int
            Volume moyen
        random_seed : int, optional
            Graine aléatoire
        
        Retourne:
        ---------
        DataFrame : Données OHLCV
        """
        if random_seed is not None:
            np.random.seed(random_seed)
        
        dates = pd.date_range(start='2020-01-01', periods=n_days, freq='B')
        
        # Générer les prix de clôture
        returns = np.random.normal(0, volatility, n_days)
        closes = initial_price * np.exp(np.cumsum(returns))
        
        # Générer OHLC
        ohlcv = pd.DataFrame(index=dates)
        
        # Open: légèrement différent du close précédent
        ohlcv['Open'] = closes * (1 + np.random.normal(0, volatility/4, n_days))
        ohlcv['Close'] = closes
        
        # High et Low basés sur la volatilité intraday
        intraday_range = np.abs(np.random.normal(0, volatility, n_days))
        ohlcv['High'] = np.maximum(ohlcv['Open'], ohlcv['Close']) * (1 + intraday_range)
        ohlcv['Low'] = np.minimum(ohlcv['Open'], ohlcv['Close']) * (1 - intraday_range)
        
        # Volume avec variation aléatoire
        ohlcv['Volume'] = np.random.poisson(volume_mean, n_days)
        
        return ohlcv


class DataCleaner:
    """Nettoyage et préparation de données financières"""
    
    @staticmethod
    def handle_missing_values(
        data: pd.DataFrame,
        method: str = 'ffill',
        limit: Optional[int] = None
    ) -> pd.DataFrame:
        """
        Gère les valeurs manquantes
        
        Paramètres:
        -----------
        data : DataFrame
            Données avec possibles valeurs manquantes
        method : str
            Méthode: 'ffill' (forward fill), 'bfill' (backward fill),
                    'interpolate', 'drop', 'mean', 'median'
        limit : int, optional
            Nombre maximum de valeurs consécutives à remplir
        
        Retourne:
        ---------
        DataFrame : Données nettoyées
        """
        if method == 'ffill':
            return data.ffill(limit=limit)
        
        elif method == 'bfill':
            return data.bfill(limit=limit)
        
        elif method == 'interpolate':
            return data.interpolate(method='linear', limit=limit)
        
        elif method == 'drop':
            return data.dropna()
        
        elif method == 'mean':
            return data.fillna(data.mean())
        
        elif method == 'median':
            return data.fillna(data.median())
        
        else:
            raise ValueError(f"Méthode inconnue: {method}")
    
    @staticmethod
    def remove_outliers(
        data: pd.DataFrame,
        n_std: float = 3.0,
        method: str = 'clip'
    ) -> pd.DataFrame:
        """
        Retire ou ajuste les valeurs aberrantes
        
        Paramètres:
        -----------
        data : DataFrame
            Données
        n_std : float
            Nombre d'écarts-types pour définir un outlier
        method : str
            'clip' (ajuster aux bornes), 'remove' (retirer), 'winsorize'
        
        Retourne:
        ---------
        DataFrame : Données nettoyées
        """
        if method == 'clip':
            lower_bound = data.mean() - n_std * data.std()
            upper_bound = data.mean() + n_std * data.std()
            return data.clip(lower=lower_bound, upper=upper_bound, axis=1)
        
        elif method == 'remove':
            z_scores = np.abs((data - data.mean()) / data.std())
            return data[(z_scores < n_std).all(axis=1)]
        
        elif method == 'winsorize':
            return DataCleaner.winsorize(data, lower_percentile=0.05, upper_percentile=0.95)
        
        else:
            raise ValueError(f"Méthode inconnue: {method}")
    
    @staticmethod
    def winsorize(
        data: pd.DataFrame,
        lower_percentile: float = 0.05,
        upper_percentile: float = 0.95
    ) -> pd.DataFrame:
        """
        Winsorise les données (clip aux percentiles)
        
        Paramètres:
        -----------
        data : DataFrame
            Données
        lower_percentile : float
            Percentile inférieur (0 à 1)
        upper_percentile : float
            Percentile supérieur (0 à 1)
        
        Retourne:
        ---------
        DataFrame : Données winsorisées
        """
        lower_bound = data.quantile(lower_percentile)
        upper_bound = data.quantile(upper_percentile)
        
        return data.clip(lower=lower_bound, upper=upper_bound, axis=1)
    
    @staticmethod
    def calculate_returns(
        prices: pd.DataFrame,
        method: str = 'simple',
        periods: int = 1
    ) -> pd.DataFrame:
        """
        Calcule les rendements
        
        Paramètres:
        -----------
        prices : DataFrame
            Prix des actifs
        method : str
            'simple' (arithmétique) ou 'log' (logarithmique)
        periods : int
            Nombre de périodes (1 pour rendements d'une période)
        
        Retourne:
        ---------
        DataFrame : Rendements
        """
        if method == 'simple':
            returns = prices.pct_change(periods=periods)
        
        elif method == 'log':
            returns = np.log(prices / prices.shift(periods))
        
        else:
            raise ValueError(f"Méthode inconnue: {method}")
        
        return returns.dropna()
    
    @staticmethod
    def align_data(
        *dataframes: pd.DataFrame,
        join: str = 'inner'
    ) -> Tuple[pd.DataFrame, ...]:
        """
        Aligne plusieurs DataFrames sur les mêmes dates
        
        Paramètres:
        -----------
        dataframes : DataFrames
            DataFrames à aligner
        join : str
            Type de jointure ('inner', 'outer', 'left', 'right')
        
        Retourne:
        ---------
        tuple : DataFrames alignés
        """
        if len(dataframes) < 2:
            return dataframes
        
        # Concaténer et ré-séparer pour aligner
        combined = pd.concat(dataframes, axis=1, join=join, keys=range(len(dataframes)))
        
        aligned = []
        for i in range(len(dataframes)):
            if i in combined.columns.levels[0]:
                aligned.append(combined[i])
            else:
                aligned.append(dataframes[i].reindex(combined.index))
        
        return tuple(aligned)
    
    @staticmethod
    def resample_data(
        data: pd.DataFrame,
        frequency: str,
        method: str = 'last'
    ) -> pd.DataFrame:
        """
        Rééchantillonne les données à une fréquence différente
        
        Paramètres:
        -----------
        data : DataFrame
            Données avec index temporel
        frequency : str
            Nouvelle fréquence ('D', 'W', 'M', 'Q', 'Y')
        method : str
            Méthode d'agrégation ('last', 'first', 'mean', 'sum')
        
        Retourne:
        ---------
        DataFrame : Données rééchantillonnées
        """
        if not isinstance(data.index, pd.DatetimeIndex):
            raise ValueError("L'index doit être de type DatetimeIndex")
        
        resampler = data.resample(frequency)
        
        if method == 'last':
            return resampler.last()
        elif method == 'first':
            return resampler.first()
        elif method == 'mean':
            return resampler.mean()
        elif method == 'sum':
            return resampler.sum()
        else:
            raise ValueError(f"Méthode inconnue: {method}")


class DataTransformer:
    """Transformations de données financières"""
    
    @staticmethod
    def normalize(
        data: pd.DataFrame,
        method: str = 'zscore'
    ) -> pd.DataFrame:
        """
        Normalise les données
        
        Paramètres:
        -----------
        data : DataFrame
            Données à normaliser
        method : str
            'zscore' (standardisation), 'minmax' (0-1), 'robust' (médiane/IQR)
        
        Retourne:
        ---------
        DataFrame : Données normalisées
        """
        if method == 'zscore':
            return (data - data.mean()) / data.std()
        
        elif method == 'minmax':
            return (data - data.min()) / (data.max() - data.min())
        
        elif method == 'robust':
            median = data.median()
            iqr = data.quantile(0.75) - data.quantile(0.25)
            return (data - median) / iqr
        
        else:
            raise ValueError(f"Méthode inconnue: {method}")
    
    @staticmethod
    def add_technical_indicators(
        data: pd.DataFrame,
        indicators: List[str] = None
    ) -> pd.DataFrame:
        """
        Ajoute des indicateurs techniques
        
        Paramètres:
        -----------
        data : DataFrame
            Données OHLCV
        indicators : list
            Liste d'indicateurs à calculer
            ['SMA', 'EMA', 'RSI', 'MACD', 'BB', 'ATR']
        
        Retourne:
        ---------
        DataFrame : Données avec indicateurs
        """
        result = data.copy()
        
        if indicators is None:
            indicators = ['SMA', 'EMA']
        
        # Prix de clôture
        close = data['Close'] if 'Close' in data.columns else data.iloc[:, 0]
        
        for indicator in indicators:
            if indicator == 'SMA':
                # Simple Moving Average
                for period in [20, 50, 200]:
                    result[f'SMA_{period}'] = close.rolling(window=period).mean()
            
            elif indicator == 'EMA':
                # Exponential Moving Average
                for period in [12, 26]:
                    result[f'EMA_{period}'] = close.ewm(span=period, adjust=False).mean()
            
            elif indicator == 'RSI':
                # Relative Strength Index
                delta = close.diff()
                gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
                loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
                rs = gain / loss
                result['RSI'] = 100 - (100 / (1 + rs))
            
            elif indicator == 'MACD':
                # Moving Average Convergence Divergence
                ema_12 = close.ewm(span=12, adjust=False).mean()
                ema_26 = close.ewm(span=26, adjust=False).mean()
                result['MACD'] = ema_12 - ema_26
                result['MACD_Signal'] = result['MACD'].ewm(span=9, adjust=False).mean()
                result['MACD_Hist'] = result['MACD'] - result['MACD_Signal']
            
            elif indicator == 'BB':
                # Bollinger Bands
                sma_20 = close.rolling(window=20).mean()
                std_20 = close.rolling(window=20).std()
                result['BB_Upper'] = sma_20 + (2 * std_20)
                result['BB_Middle'] = sma_20
                result['BB_Lower'] = sma_20 - (2 * std_20)
            
            elif indicator == 'ATR':
                # Average True Range
                if all(col in data.columns for col in ['High', 'Low', 'Close']):
                    high = data['High']
                    low = data['Low']
                    prev_close = close.shift(1)
                    
                    tr1 = high - low
                    tr2 = abs(high - prev_close)
                    tr3 = abs(low - prev_close)
                    
                    tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
                    result['ATR'] = tr.rolling(window=14).mean()
        
        return result
    
    @staticmethod
    def create_lagged_features(
        data: pd.DataFrame,
        lags: List[int] = [1, 2, 3, 5]
    ) -> pd.DataFrame:
        """
        Crée des features retardées (pour ML)
        
        Paramètres:
        -----------
        data : DataFrame
            Données
        lags : list
            Liste des retards à créer
        
        Retourne:
        ---------
        DataFrame : Données avec features retardées
        """
        result = data.copy()
        
        for col in data.columns:
            for lag in lags:
                result[f'{col}_lag_{lag}'] = data[col].shift(lag)
        
        return result.dropna()
    
    @staticmethod
    def rolling_statistics(
        data: pd.DataFrame,
        windows: List[int] = [20, 60, 120]
    ) -> pd.DataFrame:
        """
        Calcule des statistiques roulantes
        
        Paramètres:
        -----------
        data : DataFrame
            Données
        windows : list
            Tailles de fenêtres
        
        Retourne:
        ---------
        DataFrame : Données avec statistiques roulantes
        """
        result = data.copy()
        
        for col in data.columns:
            for window in windows:
                result[f'{col}_mean_{window}'] = data[col].rolling(window).mean()
                result[f'{col}_std_{window}'] = data[col].rolling(window).std()
                result[f'{col}_min_{window}'] = data[col].rolling(window).min()
                result[f'{col}_max_{window}'] = data[col].rolling(window).max()
        
        return result.dropna()
