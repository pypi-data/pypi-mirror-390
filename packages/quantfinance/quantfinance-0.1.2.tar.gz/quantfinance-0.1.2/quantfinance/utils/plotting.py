"""
Utilitaires de visualisation pour la finance quantitative

Fournit :
- Graphiques de prix et rendements
- Visualisations de portefeuille
- Graphiques de risque
- Analyses techniques
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from typing import Optional, List, Tuple, Union
import warnings


class Plotter:
    """Visualisations financières de base"""
    
    def __init__(self, style: str = 'seaborn-v0_8-darkgrid', figsize: Tuple[int, int] = (12, 6)):
        """
        Paramètres:
        -----------
        style : str
            Style matplotlib
        figsize : tuple
            Taille par défaut des figures
        """
        try:
            plt.style.use(style)
        except:
            plt.style.use('default')
        
        self.figsize = figsize
        sns.set_palette("husl")
    
    @staticmethod
    def plot_prices(
        prices: pd.DataFrame,
        title: str = "Prix des Actifs",
        figsize: Tuple[int, int] = (12, 6),
        normalize: bool = False
    ):
        """
        Trace l'évolution des prix
        
        Paramètres:
        -----------
        prices : DataFrame
            Prix des actifs
        title : str
            Titre du graphique
        figsize : tuple
            Taille de la figure
        normalize : bool
            Normaliser à 100 au début
        
        Retourne:
        ---------
        Figure : Figure matplotlib
        """
        fig, ax = plt.subplots(figsize=figsize)
        
        if normalize:
            prices_plot = prices / prices.iloc[0] * 100
            ylabel = 'Valeur (Base 100)'
        else:
            prices_plot = prices
            ylabel = 'Prix'
        
        for column in prices_plot.columns:
            ax.plot(prices_plot.index, prices_plot[column], label=column, linewidth=2)
        
        ax.set_xlabel('Date', fontsize=12)
        ax.set_ylabel(ylabel, fontsize=12)
        ax.set_title(title, fontsize=14, fontweight='bold')
        ax.legend(loc='best', framealpha=0.9)
        ax.grid(True, alpha=0.3)
        plt.tight_layout()
        
        return fig
    
    @staticmethod
    def plot_returns(
        returns: pd.DataFrame,
        title: str = "Distribution des Rendements",
        figsize: Tuple[int, int] = (14, 8),
        bins: int = 50
    ):
        """
        Trace les distributions de rendements
        
        Paramètres:
        -----------
        returns : DataFrame
            Rendements
        title : str
            Titre
        figsize : tuple
            Taille
        bins : int
            Nombre de bins pour l'histogramme
        
        Retourne:
        ---------
        Figure : Figure matplotlib
        """
        n_assets = len(returns.columns)
        n_cols = min(3, n_assets)
        n_rows = (n_assets + n_cols - 1) // n_cols
        
        fig, axes = plt.subplots(n_rows, n_cols, figsize=figsize)
        
        if n_assets == 1:
            axes = [axes]
        else:
            axes = axes.flatten() if n_assets > 1 else [axes]
        
        for i, column in enumerate(returns.columns):
            ax = axes[i]
            data = returns[column].dropna()
            
            # Histogramme
            ax.hist(data, bins=bins, alpha=0.7, edgecolor='black', density=True)
            
            # Courbe normale pour comparaison
            mu, sigma = data.mean(), data.std()
            x = np.linspace(data.min(), data.max(), 100)
            ax.plot(x, 1/(sigma * np.sqrt(2 * np.pi)) * np.exp(-0.5 * ((x - mu) / sigma)**2),
                   'r--', linewidth=2, label='Distribution normale')
            
            # Statistiques
            ax.axvline(mu, color='red', linestyle='--', linewidth=2, label=f'Moyenne: {mu:.4f}')
            ax.axvline(data.median(), color='green', linestyle='--', linewidth=2,
                      label=f'Médiane: {data.median():.4f}')
            
            ax.set_title(f'{column}', fontweight='bold')
            ax.set_xlabel('Rendement')
            ax.set_ylabel('Densité')
            ax.legend(fontsize=8)
            ax.grid(True, alpha=0.3)
        
        # Cacher les axes vides
        for i in range(n_assets, len(axes)):
            axes[i].set_visible(False)
        
        plt.suptitle(title, fontsize=16, fontweight='bold', y=1.02)
        plt.tight_layout()
        
        return fig
    
    @staticmethod
    def plot_correlation_matrix(
        returns: pd.DataFrame,
        title: str = "Matrice de Corrélation",
        figsize: Tuple[int, int] = (10, 8),
        annot: bool = True,
        method: str = 'pearson'
    ):
        """
        Trace la matrice de corrélation
        
        Paramètres:
        -----------
        returns : DataFrame
            Rendements
        title : str
            Titre
        figsize : tuple
            Taille
        annot : bool
            Annoter les valeurs
        method : str
            Méthode de corrélation ('pearson', 'spearman', 'kendall')
        
        Retourne:
        ---------
        Figure : Figure matplotlib
        """
        fig, ax = plt.subplots(figsize=figsize)
        
        corr_matrix = returns.corr(method=method)
        
        # Masque pour le triangle supérieur
        mask = np.triu(np.ones_like(corr_matrix, dtype=bool), k=1)
        
        sns.heatmap(
            corr_matrix,
            mask=mask,
            annot=annot,
            fmt='.2f',
            cmap='RdBu_r',
            center=0,
            vmin=-1,
            vmax=1,
            square=True,
            linewidths=1,
            cbar_kws={"shrink": 0.8, "label": "Corrélation"},
            ax=ax
        )
        
        ax.set_title(title, fontsize=14, fontweight='bold', pad=20)
        plt.tight_layout()
        
        return fig
    
    @staticmethod
    def plot_drawdown(
        returns: Union[pd.Series, pd.DataFrame],
        title: str = "Analyse de Drawdown",
        figsize: Tuple[int, int] = (12, 8)
    ):
        """
        Trace l'analyse de drawdown
        
        Paramètres:
        -----------
        returns : Series ou DataFrame
            Rendements
        title : str
            Titre
        figsize : tuple
            Taille
        
        Retourne:
        ---------
        Figure : Figure matplotlib
        """
        from quantfinance.risk.metrics import RiskMetrics
        
        if isinstance(returns, pd.DataFrame):
            returns = returns.iloc[:, 0]
        
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=figsize, sharex=True)
        
        # Valeur du portefeuille
        cumulative = (1 + returns).cumprod()
        ax1.plot(cumulative.index, cumulative.values, linewidth=2, color='blue', label='Valeur')
        ax1.fill_between(cumulative.index, cumulative.values, alpha=0.3)
        ax1.set_ylabel('Valeur du Portefeuille', fontsize=12)
        ax1.set_title(title, fontsize=14, fontweight='bold')
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        
        # Drawdown
        drawdown = RiskMetrics.drawdown_series(returns)
        ax2.fill_between(drawdown.index, drawdown.values, 0, alpha=0.5, color='red', label='Drawdown')
        ax2.plot(drawdown.index, drawdown.values, linewidth=1, color='darkred')
        ax2.set_ylabel('Drawdown (%)', fontsize=12)
        ax2.set_xlabel('Date', fontsize=12)
        ax2.legend()
        ax2.grid(True, alpha=0.3)
        
        # Annoter le max drawdown
        max_dd = drawdown.min()
        max_dd_date = drawdown.idxmin()
        ax2.annotate(
            f'Max DD: {max_dd:.2%}\n{max_dd_date.strftime("%Y-%m-%d")}',
            xy=(max_dd_date, max_dd),
            xytext=(20, 20),
            textcoords='offset points',
            fontsize=10,
            bbox=dict(boxstyle='round,pad=0.5', facecolor='yellow', alpha=0.7),
            arrowprops=dict(arrowstyle='->', connectionstyle='arc3,rad=0.3', lw=2)
        )
        
        plt.tight_layout()
        
        return fig
    
    @staticmethod
    def plot_portfolio_weights(
        weights: pd.Series,
        title: str = "Allocation du Portefeuille",
        figsize: Tuple[int, int] = (12, 6),
        kind: str = 'both'
    ):
        """
        Trace les poids du portefeuille
        
        Paramètres:
        -----------
        weights : Series
            Poids des actifs
        title : str
            Titre
        figsize : tuple
            Taille
        kind : str
            Type de graphique ('bar', 'pie', 'both')
        
        Retourne:
        ---------
        Figure : Figure matplotlib
        """
        if kind == 'both':
            fig, (ax1, ax2) = plt.subplots(1, 2, figsize=figsize)
        else:
            fig, ax1 = plt.subplots(figsize=figsize)
            ax2 = None
        
        # Barres
        if kind in ['bar', 'both']:
            weights.plot(kind='bar', ax=ax1, color='skyblue', edgecolor='black', width=0.7)
            ax1.set_ylabel('Poids (%)', fontsize=12)
            ax1.set_xlabel('Actif', fontsize=12)
            ax1.set_title('Poids par Actif' if kind == 'both' else title,
                         fontsize=12, fontweight='bold')
            ax1.axhline(y=0, color='black', linestyle='-', linewidth=0.5)
            ax1.grid(True, alpha=0.3, axis='y')
            plt.setp(ax1.xaxis.get_majorticklabels(), rotation=45, ha='right')
            
            # Ajouter les valeurs sur les barres
            for i, v in enumerate(weights):
                ax1.text(i, v + 0.01, f'{v:.1%}', ha='center', va='bottom', fontsize=9)
        
        # Camembert
        if kind in ['pie', 'both'] and ax2 is not None:
            positive_weights = weights[weights > 0.001]  # Filtrer les poids très petits
            ax2.pie(positive_weights, labels=positive_weights.index, autopct='%1.1f%%',
                   startangle=90, counterclock=False)
            ax2.set_title('Répartition' if kind == 'both' else title,
                         fontsize=12, fontweight='bold')
        elif kind == 'pie' and ax2 is None:
            positive_weights = weights[weights > 0.001]
            ax1.pie(positive_weights, labels=positive_weights.index, autopct='%1.1f%%',
                   startangle=90, counterclock=False)
            ax1.set_title(title, fontsize=12, fontweight='bold')
        
        if kind == 'both':
            plt.suptitle(title, fontsize=14, fontweight='bold', y=1.02)
        
        plt.tight_layout()
        
        return fig
    
    @staticmethod
    def plot_efficient_frontier(
        returns: pd.DataFrame,
        n_portfolios: int = 10000,
        figsize: Tuple[int, int] = (12, 8),
        show_cml: bool = True,
        risk_free_rate: float = 0.02
    ):
        """
        Trace la frontière efficiente avec simulation Monte Carlo
        
        Paramètres:
        -----------
        returns : DataFrame
            Rendements des actifs
        n_portfolios : int
            Nombre de portefeuilles simulés
        figsize : tuple
            Taille
        show_cml : bool
            Afficher la ligne de marché des capitaux
        risk_free_rate : float
            Taux sans risque pour CML
        
        Retourne:
        ---------
        Figure : Figure matplotlib
        """
        n_assets = len(returns.columns)
        
        # Calculer statistiques
        mean_returns = returns.mean() * 252
        cov_matrix = returns.cov() * 252
        
        # Simulation Monte Carlo
        results = np.zeros((3, n_portfolios))
        weights_record = []
        
        for i in range(n_portfolios):
            weights = np.random.random(n_assets)
            weights /= weights.sum()
            weights_record.append(weights)
            
            portfolio_return = np.dot(weights, mean_returns)
            portfolio_std = np.sqrt(np.dot(weights.T, np.dot(cov_matrix, weights)))
            sharpe_ratio = (portfolio_return - risk_free_rate) / portfolio_std
            
            results[0, i] = portfolio_std
            results[1, i] = portfolio_return
            results[2, i] = sharpe_ratio
        
        # Trouver les portefeuilles optimaux
        max_sharpe_idx = results[2].argmax()
        min_vol_idx = results[0].argmin()
        
        # Graphique
        fig, ax = plt.subplots(figsize=figsize)
        
        scatter = ax.scatter(
            results[0, :],
            results[1, :],
            c=results[2, :],
            cmap='viridis',
            marker='o',
            s=10,
            alpha=0.3
        )
        
        # Colorbar
        cbar = plt.colorbar(scatter, ax=ax)
        cbar.set_label('Ratio de Sharpe', fontsize=12)
        
        # Marquer les portefeuilles optimaux
        ax.scatter(results[0, max_sharpe_idx], results[1, max_sharpe_idx],
                  marker='*', color='red', s=500, edgecolors='black',
                  label=f'Max Sharpe ({results[2, max_sharpe_idx]:.2f})', zorder=5)
        
        ax.scatter(results[0, min_vol_idx], results[1, min_vol_idx],
                  marker='*', color='green', s=500, edgecolors='black',
                  label='Min Volatilité', zorder=5)
        
        # Ligne de marché des capitaux (CML)
        if show_cml:
            max_sharpe_return = results[1, max_sharpe_idx]
            max_sharpe_std = results[0, max_sharpe_idx]
            
            cml_x = np.linspace(0, results[0].max(), 100)
            cml_y = risk_free_rate + (max_sharpe_return - risk_free_rate) / max_sharpe_std * cml_x
            ax.plot(cml_x, cml_y, 'r--', linewidth=2, label='CML', zorder=4)
        
        # Actifs individuels
        asset_returns = mean_returns.values
        asset_vols = np.sqrt(np.diag(cov_matrix))
        ax.scatter(asset_vols, asset_returns, marker='D', s=200, c='orange',
                  edgecolors='black', label='Actifs', zorder=5)
        
        for i, asset in enumerate(returns.columns):
            ax.annotate(asset, (asset_vols[i], asset_returns[i]),
                       xytext=(10, 10), textcoords='offset points',
                       fontsize=9, bbox=dict(boxstyle='round,pad=0.3', 
                       facecolor='yellow', alpha=0.7))
        
        ax.set_xlabel('Volatilité (Risque)', fontsize=12)
        ax.set_ylabel('Rendement Espéré', fontsize=12)
        ax.set_title('Frontière Efficiente', fontsize=14, fontweight='bold')
        ax.legend(fontsize=10, loc='best')
        ax.grid(True, alpha=0.3)
        
        plt.tight_layout()
        
        return fig


class FinancialPlotter:
    """Graphiques financiers avancés"""
    
    @staticmethod
    def plot_candlestick(
        data: pd.DataFrame,
        title: str = "Graphique en Chandelier",
        figsize: Tuple[int, int] = (14, 8),
        volume: bool = True
    ):
        """
        Trace un graphique en chandelier (candlestick)
        
        Paramètres:
        -----------
        data : DataFrame
            Données OHLCV
        title : str
            Titre
        figsize : tuple
            Taille
        volume : bool
            Afficher le volume
        
        Retourne:
        ---------
        Figure : Figure matplotlib
        """
        try:
            import mplfinance as mpf
            
            # Préparer les données pour mplfinance
            if not isinstance(data.index, pd.DatetimeIndex):
                raise ValueError("L'index doit être DatetimeIndex")
            
            # S'assurer d'avoir les colonnes nécessaires
            required_cols = ['Open', 'High', 'Low', 'Close']
            if not all(col in data.columns for col in required_cols):
                raise ValueError(f"Le DataFrame doit contenir: {required_cols}")
            
            # Style
            mc = mpf.make_marketcolors(up='g', down='r', edge='black', wick='black', volume='in')
            s = mpf.make_mpf_style(marketcolors=mc, gridstyle=':', y_on_right=False)
            
            # Plot
            fig, axes = mpf.plot(
                data,
                type='candle',
                style=s,
                title=title,
                ylabel='Prix',
                volume=volume and 'Volume' in data.columns,
                ylabel_lower='Volume',
                figsize=figsize,
                returnfig=True
            )
            
            return fig
        
        except ImportError:
            warnings.warn("mplfinance non installé. Utilisez: pip install mplfinance")
            return FinancialPlotter._plot_candlestick_manual(data, title, figsize, volume)
    
    @staticmethod
    def _plot_candlestick_manual(data, title, figsize, volume):
        """Version manuelle du candlestick sans mplfinance"""
        fig, ax = plt.subplots(figsize=figsize)
        
        # Version simplifiée avec lignes
        ax.plot(data.index, data['Close'], linewidth=2, label='Close')
        ax.fill_between(data.index, data['Low'], data['High'], alpha=0.3)
        
        ax.set_title(title, fontsize=14, fontweight='bold')
        ax.set_ylabel('Prix')
        ax.legend()
        ax.grid(True, alpha=0.3)
        
        plt.tight_layout()
        return fig
    
    @staticmethod
    def plot_risk_return_scatter(
        returns: pd.DataFrame,
        figsize: Tuple[int, int] = (12, 8),
        periods_per_year: int = 252
    ):
        """
        Nuage de points risque-rendement
        
        Paramètres:
        -----------
        returns : DataFrame
            Rendements des actifs
        figsize : tuple
            Taille
        periods_per_year : int
            Périodes par an
        
        Retourne:
        ---------
        Figure : Figure matplotlib
        """
        fig, ax = plt.subplots(figsize=figsize)
        
        # Calculer rendement et risque annualisés
        annual_returns = returns.mean() * periods_per_year
        annual_vols = returns.std() * np.sqrt(periods_per_year)
        
        # Scatter plot
        ax.scatter(annual_vols, annual_returns, s=200, alpha=0.6, edgecolors='black')
        
        # Annoter
        for asset in returns.columns:
            ax.annotate(
                asset,
                (annual_vols[asset], annual_returns[asset]),
                xytext=(10, 10),
                textcoords='offset points',
                fontsize=11,
                bbox=dict(boxstyle='round,pad=0.5', facecolor='yellow', alpha=0.7)
            )
        
        ax.set_xlabel('Volatilité Annualisée', fontsize=12)
        ax.set_ylabel('Rendement Annualisé', fontsize=12)
        ax.set_title('Risque vs Rendement', fontsize=14, fontweight='bold')
        ax.grid(True, alpha=0.3)
        ax.axhline(y=0, color='black', linestyle='-', linewidth=0.5)
        ax.axvline(x=0, color='black', linestyle='-', linewidth=0.5)
        
        plt.tight_layout()
        
        return fig
    
    @staticmethod
    def plot_rolling_metrics(
        returns: pd.Series,
        window: int = 60,
        figsize: Tuple[int, int] = (14, 10),
        periods_per_year: int = 252
    ):
        """
        Trace les métriques roulantes
        
        Paramètres:
        -----------
        returns : Series
            Rendements
        window : int
            Taille de la fenêtre
        figsize : tuple
            Taille
        periods_per_year : int
            Périodes par an
        
        Retourne:
        ---------
        Figure : Figure matplotlib
        """
        from quantfinance.risk.metrics import RiskMetrics
        
        fig, axes = plt.subplots(3, 1, figsize=figsize, sharex=True)
        
        # Rendement roulant
        rolling_return = returns.rolling(window).mean() * periods_per_year
        axes[0].plot(rolling_return.index, rolling_return.values, linewidth=2)
        axes[0].set_ylabel('Rendement Annualisé', fontsize=11)
        axes[0].set_title(f'Métriques Roulantes ({window} jours)', fontsize=14, fontweight='bold')
        axes[0].grid(True, alpha=0.3)
        axes[0].axhline(y=0, color='black', linestyle='--', linewidth=1)
        
        # Volatilité roulante
        rolling_vol = returns.rolling(window).std() * np.sqrt(periods_per_year)
        axes[1].plot(rolling_vol.index, rolling_vol.values, linewidth=2, color='orange')
        axes[1].fill_between(rolling_vol.index, rolling_vol.values, alpha=0.3, color='orange')
        axes[1].set_ylabel('Volatilité Annualisée', fontsize=11)
        axes[1].grid(True, alpha=0.3)
        
        # Sharpe ratio roulant
        rolling_sharpe = rolling_return / rolling_vol
        axes[2].plot(rolling_sharpe.index, rolling_sharpe.values, linewidth=2, color='green')
        axes[2].set_ylabel('Ratio de Sharpe', fontsize=11)
        axes[2].set_xlabel('Date', fontsize=11)
        axes[2].grid(True, alpha=0.3)
        axes[2].axhline(y=0, color='black', linestyle='--', linewidth=1)
        
        plt.tight_layout()
        
        return fig

