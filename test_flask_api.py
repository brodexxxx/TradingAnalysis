# Test Flask API endpoints
import requests
import time

# Start Flask app in background (assuming it's not running)
# For testing, we'll simulate the API calls

print('Testing Flask API endpoints (simulated):')

# Simulate /symbols endpoint
from data_fetcher import symbols
symbols_list = list(symbols.keys())
print(f'/symbols: {symbols_list}')

# Simulate /analyze/Sensex endpoint
from trading_analysis import analyze_symbol
result = analyze_symbol('Sensex', symbols['Sensex'])
if result:
    print(f'/analyze/Sensex: Action={result["action"]}, Price={result["price"]:.2f}')
else:
    print('/analyze/Sensex: No data')

# Simulate /predict endpoint
from ml_predictor import predictor
sample_indicators = {'rsi': 55.0, 'ma50': 18000, 'ma200': 17500}
prediction = predictor.predict(sample_indicators)
print(f'/predict: {prediction}')

print('Flask API endpoints test complete.')
