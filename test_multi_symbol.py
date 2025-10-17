from trading_analysis import analyze_symbol
from data_fetcher import symbols
import time

test_symbols = ['Sensex', 'BankNifty', 'Nifty50', 'CrudeOil']
for symbol_name in test_symbols:
    if symbol_name in symbols:
        print(f'Testing {symbol_name}...')
        result = analyze_symbol(symbol_name, symbols[symbol_name])
        if result:
            print(f'  Action: {result["action"]}')
            print(f'  Price: {result["price"]:.2f}')
            print(f'  RSI: {result["rsi"]:.2f}')
            print(f'  Phase: {result["phase"]}')
            print(f'  Hold Time: {result["hold_time"]}')
            print(f'  Time Period: {result.get("time_period", "N/A")}')
            print('  ---')
        else:
            print(f'  No data for {symbol_name}')
        time.sleep(1)  # Brief pause
print('Multi-symbol testing complete.')
