import pandas as pd
import numpy as np

def head_and_shoulders(data):
    """
    Simple detection: Three peaks, middle higher.
    """
    peaks = (data['High'] > data['High'].shift()) & (data['High'] > data['High'].shift(-1))
    left_shoulder = peaks.shift(2)
    head = peaks.shift(1) & (data['High'] > data['High'].shift(2)) & (data['High'] > data['High'].shift())
    right_shoulder = peaks
    return left_shoulder & head & right_shoulder

def double_top(data):
    """
    Two similar highs.
    """
    peaks = (data['High'] > data['High'].shift()) & (data['High'] > data['High'].shift(-1))
    first_top = peaks.shift(1)
    second_top = peaks
    similar = abs(data['High'].shift(1) - data['High']) / data['High'] < 0.05
    return first_top & second_top & similar

def ascending_triangle(data):
    """
    Higher lows, horizontal resistance.
    """
    resistance = data['High'].rolling(20).max()
    support_trend = data['Low'].rolling(5).min()
    return (data['High'] < resistance * 1.01) & (data['Low'] > support_trend)

# Add more patterns: double bottom, cup and handle, etc.

def cup_and_handle(data):
    """
    Cup: Rounding bottom, Handle: Small consolidation.
    """
    # Simplified: Look for U shape followed by flat
    lows = data['Low'].rolling(20).min()
    cup = data['Low'] > lows * 0.95
    handle = (data['High'] - data['Low']) < (data['High'].shift() - data['Low'].shift()) * 0.5
    return cup & handle.shift(-5)  # Approximate

def rising_wedge(data):
    """
    Converging trendlines, rising.
    """
    # Simplified: Decreasing volume, converging highs/lows
    high_trend = data['High'].rolling(10).max()
    low_trend = data['Low'].rolling(10).min()
    converging = (high_trend.diff() < 0) & (low_trend.diff() > 0)
    return converging
