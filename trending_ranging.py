import pandas as pd
import numpy as np

def is_trending(data, adx_period=14, threshold=25):
    """
    Determine if market is trending using ADX.
    """
    # Simple ADX calculation
    high = data['High']
    low = data['Low']
    close = data['Close']

    tr = pd.concat([high - low, abs(high - close.shift()), abs(low - close.shift())], axis=1).max(axis=1)
    atr = tr.rolling(adx_period).mean()

    dm_plus = np.where((high - high.shift()) > (low.shift() - low), high - high.shift(), 0).flatten()
    dm_minus = np.where((low.shift() - low) > (high - high.shift()), low.shift() - low, 0).flatten()

    di_plus = 100 * (pd.Series(dm_plus).rolling(adx_period).mean() / atr)
    di_minus = 100 * (pd.Series(dm_minus).rolling(adx_period).mean() / atr)

    dx = 100 * abs(di_plus - di_minus) / (di_plus + di_minus)
    adx = dx.rolling(adx_period).mean()

    trending = adx > threshold
    ranging = ~trending
    return trending, ranging
