import pandas as pd
import numpy as np
import ta
from math import isnan

def macd_indicator(data, fast=12, slow=26, signal=9):
    """
    Calculate MACD indicator.
    Returns: macd_line, signal_line, histogram
    """
    if data.empty:
        return pd.Series(), pd.Series(), pd.Series()

    macd_obj = ta.trend.MACD(data['Close'].squeeze(), window_fast=fast, window_slow=slow, window_sign=signal)
    macd_line = macd_obj.macd()
    signal_line = macd_obj.macd_signal()
    histogram = macd_obj.macd_diff()
    return macd_line, signal_line, histogram

def stochastic_oscillator(data, k_period=14, d_period=3):
    """
    Calculate Stochastic Oscillator.
    Returns: %K, %D
    """
    if data.empty:
        return pd.Series(), pd.Series()

    k = ta.momentum.StochasticOscillator(data['High'].squeeze(), data['Low'].squeeze(), data['Close'].squeeze(), window=k_period, smooth_window=d_period).stoch()
    d = ta.momentum.StochasticOscillator(data['High'].squeeze(), data['Low'].squeeze(), data['Close'].squeeze(), window=k_period, smooth_window=d_period).stoch_signal()
    return k, d

def on_balance_volume(data):
    """
    Calculate On-Balance Volume (OBV).
    """
    if data.empty:
        return pd.Series()

    obv = ta.volume.OnBalanceVolumeIndicator(data['Close'].squeeze(), data['Volume'].squeeze()).on_balance_volume()
    return obv

def bollinger_bands(data, period=20, std_dev=2):
    """
    Calculate Bollinger Bands.
    Returns: upper_band, middle_band, lower_band
    """
    if data.empty:
        return pd.Series(), pd.Series(), pd.Series()

    bb = ta.volatility.BollingerBands(data['Close'].squeeze(), window=period, window_dev=std_dev)
    upper = bb.bollinger_hband()
    middle = bb.bollinger_mavg()
    lower = bb.bollinger_lband()
    return upper, middle, lower

def rsi_indicator(data, period=14):
    """
    Calculate RSI (Relative Strength Index).
    Returns: rsi
    """
    if data.empty:
        return pd.Series()

    rsi = ta.momentum.RSIIndicator(data['Close'].squeeze(), window=period).rsi()
    return rsi

def range_filter(data, period=20, multiplier=1.6):
    """
    Calculate Range Filter for buy/sell signals.
    Returns: range_filter, trend
    """
    if data.empty:
        return pd.Series(), pd.Series()

    # Calculate range
    high_low_range = data['High'] - data['Low']
    range_ma = high_low_range.rolling(period).mean()
    range_filter = range_ma * multiplier

    # Calculate trend
    trend = pd.Series(index=data.index, dtype=float)
    trend.iloc[0] = 0
    for i in range(1, len(data)):
        rf_val_raw = range_filter.iloc[i]
        if isinstance(rf_val_raw, pd.Series):
            rf_val = float(rf_val_raw.iloc[0]) if not rf_val_raw.empty and pd.notna(rf_val_raw.iloc[0]) else np.nan
        else:
            rf_val = float(rf_val_raw) if pd.notna(rf_val_raw) else np.nan

        close_val_raw = data['Close'].iloc[i]
        if isinstance(close_val_raw, pd.Series):
            close_val = float(close_val_raw.iloc[0]) if not close_val_raw.empty and pd.notna(close_val_raw.iloc[0]) else np.nan
        else:
            close_val = float(close_val_raw) if pd.notna(close_val_raw) else np.nan

        prev_close_val_raw = data['Close'].iloc[i-1]
        if isinstance(prev_close_val_raw, pd.Series):
            prev_close_val = float(prev_close_val_raw.iloc[0]) if not prev_close_val_raw.empty and pd.notna(prev_close_val_raw.iloc[0]) else np.nan
        else:
            prev_close_val = float(prev_close_val_raw) if pd.notna(prev_close_val_raw) else np.nan

        if isnan(rf_val) or isnan(close_val) or isnan(prev_close_val):
            trend.iloc[i] = trend.iloc[i-1]
        elif close_val > prev_close_val + rf_val:
            trend.iloc[i] = 1  # Uptrend
        elif close_val < prev_close_val - rf_val:
            trend.iloc[i] = -1  # Downtrend
        else:
            trend.iloc[i] = trend.iloc[i-1]  # Continue trend

    return range_filter, trend

def get_indicator_signals(data):
    """
    Get buy/sell signals from all indicators.
    Returns a dictionary with signals.
    """
    signals = {}

    # MACD
    macd_line, signal_line, hist = macd_indicator(data)
    if not macd_line.empty:
        signals['macd_buy'] = (macd_line.iloc[-1] > signal_line.iloc[-1]) and (hist.iloc[-1] > 0)
        signals['macd_sell'] = (macd_line.iloc[-1] < signal_line.iloc[-1]) and (hist.iloc[-1] < 0)

    # Stochastic
    k, d = stochastic_oscillator(data)
    if not k.empty:
        signals['stoch_buy'] = (k.iloc[-1] < 20) and (d.iloc[-1] < 20) and (k.iloc[-1] > d.iloc[-1])
        signals['stoch_sell'] = (k.iloc[-1] > 80) and (d.iloc[-1] > 80) and (k.iloc[-1] < d.iloc[-1])

    # OBV
    obv = on_balance_volume(data)
    if not obv.empty:
        obv_ma = obv.rolling(20).mean()
        signals['obv_buy'] = obv.iloc[-1] > obv_ma.iloc[-1]
        signals['obv_sell'] = obv.iloc[-1] < obv_ma.iloc[-1]

    # Bollinger Bands
    upper, middle, lower = bollinger_bands(data)
    if not upper.empty:
        signals['bb_buy'] = data['Close'].iloc[-1] < lower.iloc[-1]
        signals['bb_sell'] = data['Close'].iloc[-1] > upper.iloc[-1]

    # Range Filter
    rf, trend = range_filter(data)
    if not rf.empty:
        signals['rf_buy'] = trend.iloc[-1] == 1
        signals['rf_sell'] = trend.iloc[-1] == -1

    # RSI
    rsi = rsi_indicator(data)
    if not rsi.empty:
        signals['rsi_buy'] = rsi.iloc[-1] < 30
        signals['rsi_sell'] = rsi.iloc[-1] > 70

    return signals
