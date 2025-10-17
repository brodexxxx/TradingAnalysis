from flask import Flask, render_template, jsonify, request
import json
import logging
from trading_analysis import analyze_symbol
from data_fetcher import symbols
from models import TradingRecord, session
from ml_predictor import predictor

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/welcome')
def welcome():
    logger.info(f"Request received: {request.method} {request.path}")
    return jsonify({'message': 'Welcome to the Flask API Service!'})

@app.route('/analyze/<symbol>')
def analyze(symbol):
    if symbol in symbols:
        result = analyze_symbol(symbol, symbols[symbol])
        if result:
            return jsonify(result)
        else:
            return jsonify({'error': 'No data available'})
    return jsonify({'error': 'Symbol not found'})

@app.route('/symbols')
def get_symbols():
    return jsonify(list(symbols.keys()))

@app.route('/predict', methods=['POST'])
def predict():
    data = request.get_json()
    indicators = data.get('indicators', {})
    prediction = predictor.predict(indicators)
    return jsonify({'prediction': prediction})

@app.route('/records')
def get_records():
    records = session.query(TradingRecord).all()
    result = []
    for record in records:
        result.append({
            'symbol': record.symbol,
            'timestamp': record.timestamp.isoformat(),
            'close_price': record.close_price,
            'prediction': record.prediction,
            'indicators': json.loads(record.indicators)
        })
    return jsonify(result)

if __name__ == '__main__':
    app.run(debug=True)
