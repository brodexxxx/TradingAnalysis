import pandas as pd
import numpy as np

def find_support_resistance(data, window=20):
    """
    Identify support and resistance levels using rolling highs/lows.
    """
    highs = data['High'].rolling(window=window).max()
    lows = data['Low'].rolling(window=window).min()
    return highs, lows

def dynamic_support_resistance(data, atr_period=14):
    """
    Dynamic S/R using ATR.
    """
    atr = calculate_atr(data, atr_period)
    support = data['Close'] - atr
    resistance = data['Close'] + atr
    return support, resistance

def calculate_atr(data, period=14):
    """
    Calculate Average True Range.
    """
    high_low = data['High'] - data['Low']
    high_close = np.abs(data['High'] - data['Close'].shift())
    low_close = np.abs(data['Low'] - data['Close'].shift())
    true_range = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
    atr = true_range.rolling(period).mean()
    return atr

def reversal_support_resistance(data, threshold=0.02):
    """
    Identify reversal points at S/R.
    """
    highs, lows = find_support_resistance(data)
    reversal_up = (data['Close'] > highs * (1 - threshold)) & (data['Close'].shift() < highs.shift() * (1 - threshold))
    reversal_down = (data['Close'] < lows * (1 + threshold)) & (data['Close'].shift() > lows.shift() * (1 + threshold))
    return reversal_up, reversal_down
