import pandas as pd

def price_rejection(data, threshold=0.02):
    """
    Price rejection: Touches level but reverses.
    """
    highs, lows = find_support_resistance(data)
    rejection_up = (data['High'] > highs * (1 - threshold)) & (data['Close'] < highs * (1 - threshold))
    rejection_down = (data['Low'] < lows * (1 + threshold)) & (data['Close'] > lows * (1 + threshold))
    return rejection_up, rejection_down

def price_acceptance(data, threshold=0.02):
    """
    Price acceptance: Breaks and holds.
    """
    highs, lows = find_support_resistance(data)
    acceptance_up = (data['Close'] > highs * (1 + threshold)) & (data['Close'].shift() > highs.shift() * (1 + threshold))
    acceptance_down = (data['Close'] < lows * (1 - threshold)) & (data['Close'].shift() < lows.shift() * (1 - threshold))
    return acceptance_up, acceptance_down

# Import for S/R
from support_resistance import find_support_resistance
