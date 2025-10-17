import pandas as pd
import numpy as np

def identify_market_phase(data, short_ma=50, long_ma=200):
    """
    Identify Accumulation, Advancing, Distribution, Declining phases.
    Based on MA crossovers and volume.
    """
    if data.empty:
        return 'Neutral'

    # Handle MultiIndex if present
    if isinstance(data.index, pd.MultiIndex):
        data = data.droplevel(0)

    short_ma = data['Close'].rolling(short_ma).mean()
    long_ma = data['Close'].rolling(long_ma).mean()
    volume_ma = data['Volume'].rolling(20).mean()

    accumulation = (data['Close'] < long_ma) & (data['Volume'] > volume_ma)
    advancing = (short_ma > long_ma) & (data['Close'] > short_ma)
    distribution = (data['Close'] > long_ma) & (data['Volume'] > volume_ma)
    declining = (short_ma < long_ma) & (data['Close'] < short_ma)

    if accumulation.iloc[-1].any():
        return 'Accumulation'
    elif advancing.iloc[-1].any():
        return 'Advancing'
    elif distribution.iloc[-1].any():
        return 'Distribution'
    elif declining.iloc[-1].any():
        return 'Declining'
    else:
        return 'Neutral'
