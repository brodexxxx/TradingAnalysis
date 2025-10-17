import pandas as pd
import numpy as np
from indicators import rsi_indicator, get_indicator_signals

# Create sample data
dates = pd.date_range('2023-01-01', periods=50, freq='D')
np.random.seed(42)
close_prices = 100 + np.cumsum(np.random.randn(50) * 2)
data = pd.DataFrame({
    'Open': close_prices - 1,
    'High': close_prices + 1,
    'Low': close_prices - 1,
    'Close': close_prices,
    'Volume': np.random.randint(1000, 10000, 50)
}, index=dates)

# Test rsi_indicator
rsi = rsi_indicator(data)
print('RSI calculation test:')
print(f'RSI length: {len(rsi)}')
print(f'Last RSI value: {rsi.iloc[-1]:.2f}')
print(f'RSI range: {rsi.min():.2f} to {rsi.max():.2f}')
print()

# Test get_indicator_signals
signals = get_indicator_signals(data)
print('Signals test:')
print(f'Total signals: {len(signals)}')
rsi_buy = signals.get('rsi_buy', False)
rsi_sell = signals.get('rsi_sell', False)
print(f'RSI Buy signal: {rsi_buy}')
print(f'RSI Sell signal: {rsi_sell}')
print(f'RSI value for signal: {rsi.iloc[-1]:.2f}')
