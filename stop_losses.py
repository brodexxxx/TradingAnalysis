import pandas as pd

def initial_stop_loss(data, atr_multiplier=1.5):
    """
    Initial SL based on ATR.
    """
    from support_resistance import calculate_atr
    atr = calculate_atr(data)
    sl_long = data['Close'] - atr * atr_multiplier
    sl_short = data['Close'] + atr * atr_multiplier
    return sl_long, sl_short

def trailing_stop_loss(data, initial_sl, trail_percent=0.05):
    """
    Trailing SL.
    """
    trail_amount = data['Close'] * trail_percent
    trailing_sl = data['Close'] - trail_amount
    return pd.Series([max(sl, trail) for sl, trail in zip(initial_sl, trailing_sl)], index=data.index)
