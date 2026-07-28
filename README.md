# TradingAnalysis

This repository contains a comprehensive trading analysis toolkit for stock market research and prediction. It includes:

- Real-time and historical data fetching
- Technical indicators (RSI, MACD, Bollinger Bands, etc.)
- Candlestick and chart pattern recognition
- Volume and volatility analysis
- Machine learning-based predictions
- Risk management and stop loss calculations
- Trading journal logging
- Streamlit dashboard for visualization

## Getting Started

1. Clone the repository:
	```
	git clone https://github.com/brodexxxx/TradingAnalysis.git
	```
2. Install dependencies:
	```
	pip install -r requirements.txt
	```
3. Run the main analysis script:
	```
	python trading_analysis.py
	```

## Note
- The file `trading_model.pkl` is excluded due to GitHub's file size limits. Please add your own model file if needed.

## License
See `LICENSE` for details.
# TradingAnalysis

## Indian Index Algo Toolkit

The repository includes `indian_index_algo.py`, a baseline modular workflow for Indian index algo-trading research and simulation with:

- OHLCV data quality validation
- Transaction-cost-aware backtesting
- Risk limit checks
- Paper execution simulation
- Basic performance monitoring and strategy promotion gating

Run targeted tests:

```
python -m pytest test_indian_index_algo.py
```
