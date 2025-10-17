import pandas as pd

def simple_ma(data, period=50):
    return data['Close'].rolling(period).mean()

def exponential_ma(data, period=50):
    return data['Close'].ewm(span=period).mean()

def weighted_ma(data, period=50):
    weights = pd.Series(range(1, period+1))
    return data['Close'].rolling(period).apply(lambda x: (x * weights).sum() / weights.sum(), raw=False)

def ma_crossover(data, short=50, long=200):
    short_ma = simple_ma(data, short)
    long_ma = simple_ma(data, long)
    bullish_cross = (short_ma > long_ma) & (short_ma.shift() < long_ma.shift())
    bearish_cross = (short_ma < long_ma) & (short_ma.shift() > long_ma.shift())
    return bullish_cross, bearish_cross
