import pandas as pd
import numpy as np
from sklearn.cluster import KMeans
import yfinance as yf
from datetime import datetime, timedelta

class SectorTrendAnalyzer:
    def __init__(self):
        self.sectors = {
            'Tech': ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA'],
            'Pharma': ['JNJ', 'PFE', 'MRK', 'ABBV', 'LLY'],
            'Finance': ['JPM', 'BAC', 'WFC', 'C', 'GS'],
            'Energy': ['XOM', 'CVX', 'COP', 'EOG', 'SLB'],
            'Consumer': ['KO', 'PEP', 'WMT', 'HD', 'MCD']
        }

    def fetch_sector_data(self, period='1y'):
        sector_data = {}
        for sector, stocks in self.sectors.items():
            sector_prices = []
            for stock in stocks:
                try:
                    data = yf.download(stock, period=period, progress=False)
                    if not data.empty:
                        # Calculate weekly returns
                        weekly_returns = data['Close'].resample('W').last().pct_change()
                        sector_prices.append(weekly_returns)
                except:
                    continue
            if sector_prices:
                sector_data[sector] = pd.concat(sector_prices, axis=1).mean(axis=1)
        return pd.DataFrame(sector_data)

    def calculate_trend_strength(self, data):
        # Calculate rolling mean and trend
        trend_strength = {}
        for sector in data.columns:
            rolling_mean = data[sector].rolling(window=4).mean()
            trend = (rolling_mean - rolling_mean.shift(4)) / rolling_mean.shift(4)
            trend_strength[sector] = trend.iloc[-1] if not trend.empty else 0
        return trend_strength

    def cluster_sectors(self, data):
        # Simple clustering based on recent performance
        recent_performance = data.iloc[-4:].mean()
        performance_df = pd.DataFrame({'performance': recent_performance})

        # K-means clustering
        kmeans = KMeans(n_clusters=3, random_state=42)
        performance_df['cluster'] = kmeans.fit_predict(performance_df[['performance']])

        return performance_df

    def get_top_bullish_sectors(self, num=3):
        data = self.fetch_sector_data()
        trend_strength = self.calculate_trend_strength(data)
        clusters = self.cluster_sectors(data)

        # Combine trend strength and clustering
        sector_scores = {}
        for sector in data.columns:
            score = trend_strength.get(sector, 0) + (clusters.loc[sector, 'performance'] * 0.5)
            sector_scores[sector] = score

        # Sort and get top sectors
        sorted_sectors = sorted(sector_scores.items(), key=lambda x: x[1], reverse=True)
        top_sectors = [sector for sector, score in sorted_sectors[:num]]

        return top_sectors, sector_scores
