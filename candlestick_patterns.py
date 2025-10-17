import pandas as pd
import numpy as np

def bullish_marubozu(data):
    """
    Bullish Marubozu: Open = Low, Close = High, no shadows.
    """
    return (data['Open'] == data['Low']) & (data['Close'] == data['High'])

def bearish_marubozu(data):
    """
    Bearish Marubozu: Open = High, Close = Low.
    """
    return (data['Open'] == data['High']) & (data['Close'] == data['Low'])

def hammer(data):
    """
    Hammer: Small body, long lower shadow.
    """
    body = abs(data['Close'] - data['Open'])
    lower_shadow = data['Open'] - data['Low'] if data['Close'] > data['Open'] else data['Close'] - data['Low']
    upper_shadow = data['High'] - data['Open'] if data['Close'] > data['Open'] else data['High'] - data['Close']
    return (lower_shadow > 2 * body) & (upper_shadow < body)

def doji(data):
    """
    Doji: Open ≈ Close.
    """
    body = abs(data['Close'] - data['Open'])
    total_range = data['High'] - data['Low']
    return body / total_range < 0.1

def bullish_engulfing(data):
    """
    Bullish Engulfing: Previous bearish, current bullish engulfing.
    """
    prev_bearish = data['Close'].shift() < data['Open'].shift()
    current_bullish = data['Close'] > data['Open']
    engulfing = (data['Open'] < data['Close'].shift()) & (data['Close'] > data['Open'].shift())
    return prev_bearish & current_bullish & engulfing

def morning_star(data):
    """
    Morning Star: Three candles - bearish, small, bullish.
    """
    first_bearish = data['Close'].shift(2) < data['Open'].shift(2)
    second_small = abs(data['Close'].shift() - data['Open'].shift()) < (data['High'].shift() - data['Low'].shift()) * 0.3
    third_bullish = data['Close'] > data['Open']
    star = data['Close'].shift() < data['Open'].shift(2) and data['Close'].shift() > data['Close'].shift(2)
    return first_bearish & second_small & third_bullish & star

# Add more patterns similarly...

def advanced_candlestick_analysis(data):
    """
    Analyze size, shadows, ratios.
    """
    body_size = abs(data['Close'] - data['Open'])
    upper_shadow = data['High'] - np.maximum(data['Open'], data['Close'])
    lower_shadow = np.minimum(data['Open'], data['Close']) - data['Low']
    body_to_shadow_ratio = body_size / (upper_shadow + lower_shadow + 0.001)  # avoid div0
    body_position = (np.minimum(data['Open'], data['Close']) - data['Low']) / (data['High'] - data['Low'] + 0.001)
    return body_size, upper_shadow, lower_shadow, body_to_shadow_ratio, body_position
