import pandas as pd

def volume_analysis(data):
    """
    Analyze volume: Increasing volume on breakouts, etc.
    """
    volume_ma = data['Volume'].rolling(20).mean()
    high_volume = data['Volume'] > volume_ma * 1.5
    low_volume = data['Volume'] < volume_ma * 0.5
    return high_volume, low_volume, volume_ma

def volume_price_trend(data):
    """
    Volume Price Trend indicator.
    """
    vpt = ((data['Close'] - data['Close'].shift()) / data['Close'].shift()) * data['Volume']
    vpt_cum = vpt.cumsum()
    return vpt_cum
