 from trading_analysis import analyze_symbol
from data_fetcher import symbols

# Test analysis for one symbol
symbol_name = 'Sensex'
symbol = symbols[symbol_name]

print(f"Testing analysis for {symbol_name}...")
result = analyze_symbol(symbol_name, symbol)

if result:
    print("Analysis successful!")
    print(f"Symbol: {result['symbol']}")
    print(f"Price: {result['price']:.2f}")
    print(f"Action: {result['action']}")
    print(f"Stop Loss: {result['stop_loss'] if result['stop_loss'] else 'N/A'}")
    print(f"Take Profit: {result['take_profit'] if result['take_profit'] else 'N/A'}")
    print(f"Reason: {result['reason']}")
    print(f"RSI: {result['rsi']:.2f}")
    print(f"Phase: {result['phase']}")
else:
    print("Analysis failed - no data available")
