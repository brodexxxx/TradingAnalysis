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

## Indian Index Algo Trading Toolkit (NIFTY 50 / SENSEX)

This repo now includes `indian_index_algo.py`, a modular foundation to build algo trading workflows for Indian indices.

It provides:
- Scope and execution mode controls (`signals_only`, `paper`, `live`)
- Compliance checks for NSE/BSE session timing
- Data layer with OHLCV quality validation
- Backtesting with realistic Indian transaction cost assumptions (brokerage, STT, GST, slippage, latency)
- Risk controls (max risk per trade, daily loss limit, max exposure, kill switch)
- Paper execution broker with reconciliation
- Monitoring snapshots and daily health report generation
- Strategy version registry with out-of-sample and walk-forward promotion gates

Quick usage:
```python
from indian_index_algo import DataLayer, BacktestEngine, RiskController, PaperBroker
```

Run toolkit tests:
```bash
python -m unittest test_indian_index_algo.py
```

## License
See `LICENSE` for details.
