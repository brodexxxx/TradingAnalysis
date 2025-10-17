import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from stock_trend_predictor import StockTrendPredictor
from sector_trend_analyzer import SectorTrendAnalyzer
from trading_analysis import analyze_symbol
from data_fetcher import symbols

st.title("AI Stock Market Trend Predictor & Sector Analyzer")

# Sidebar for navigation
page = st.sidebar.selectbox("Choose Analysis", ["Stock Trend Predictor", "Sector Trend Analyzer", "Real-time Analysis"])

if page == "Stock Trend Predictor":
    st.header("Stock Trend Predictor")
    symbol = st.selectbox("Select Stock Symbol", list(symbols.values()) + ['AAPL', 'GOOGL', 'MSFT'])
    if st.button("Predict Trend"):
        predictor = StockTrendPredictor(symbol)
        result = predictor.run()
        st.write(f"**Symbol:** {result['symbol']}")
        st.write(f"**Predicted Trend:** {result['predicted_trend']}")
        st.write(f"**Confidence:** {result['confidence']:.2f}")
        st.write(f"**Model Accuracy:** {result['model_accuracy']:.2f}")

elif page == "Sector Trend Analyzer":
    st.header("Sector Trend Analyzer")
    if st.button("Analyze Sectors"):
        analyzer = SectorTrendAnalyzer()
        top_sectors, scores = analyzer.get_top_bullish_sectors()
        st.write("**Top 3 Bullish Sectors:**")
        for i, sector in enumerate(top_sectors, 1):
            st.write(f"{i}. {sector}")
        st.write("**Sector Scores:**")
        st.json(scores)

elif page == "Real-time Analysis":
    st.header("Real-time Trading Analysis")
    symbol_name = st.selectbox("Select Symbol", list(symbols.keys()))
    if st.button("Analyze"):
        result = analyze_symbol(symbol_name, symbols[symbol_name])
        if result:
            st.write(f"**Symbol:** {result['symbol']}")
            st.write(f"**Price:** {result['price']:.2f}")
            st.write(f"**Action:** {result['action']}")
            st.write(f"**Stop Loss:** {result['stop_loss']:.2f if result['stop_loss'] else 'N/A'}")
            st.write(f"**Take Profit:** {result['take_profit']:.2f if result['take_profit'] else 'N/A'}")
            st.write(f"**RSI:** {result['rsi']:.2f}")
            st.write(f"**Phase:** {result['phase']}")
            st.write(f"**Reason:** {result['reason']}")
        else:
            st.write("Unable to fetch data. Market may be closed.")

# Footer
st.markdown("---")
st.markdown("**Disclaimer:** This is for educational purposes only. Not financial advice.")
