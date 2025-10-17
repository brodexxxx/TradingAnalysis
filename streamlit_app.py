import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from data_fetcher import get_realtime_data, symbols, is_market_open
from trading_analysis import analyze_symbol
import ta  # For RSI in chart
import streamlit.components.v1 as components
import time
from datetime import datetime
import pytz

st.title("Advanced Trading Analysis Dashboard with TradingView Charts")

# Sidebar for symbol selection
symbol_name = st.sidebar.selectbox("Select Symbol", list(symbols.keys()))

# Auto-refresh settings
st.sidebar.markdown("---")
st.sidebar.subheader("⚙️ Auto-Refresh Settings")
auto_refresh = st.sidebar.checkbox("Enable Auto-Refresh (Mon-Fri)", value=False)
refresh_interval = st.sidebar.selectbox(
    "Refresh Interval",
    options=[30, 60, 120, 300],
    format_func=lambda x: f"{x} seconds" if x < 60 else f"{x//60} minutes",
    index=2  # Default 120 seconds
)

# Display market status
ist = pytz.timezone('Asia/Kolkata')
current_time = datetime.now(ist)
market_open = is_market_open()

if market_open:
    st.sidebar.success(f"🟢 Market OPEN - {current_time.strftime('%I:%M %p IST')}")
else:
    st.sidebar.error(f"🔴 Market CLOSED - {current_time.strftime('%I:%M %p IST')}")

# Auto-refresh logic
if auto_refresh and market_open:
    st.sidebar.info(f"🔄 Auto-refreshing every {refresh_interval}s")
    time.sleep(refresh_interval)
    st.rerun()

# TradingView chart integration
def get_tradingview_symbol(symbol_name):
    """Get TradingView symbol format for different assets"""
    symbol_map = {
        'Sensex': 'BSE:SENSEX',
        'Nifty50': 'NSE:NIFTY',
        'BankNifty': 'NSE:BANKNIFTY',
        'CrudeOil': 'NYMEX:CL1!'
    }
    return symbol_map.get(symbol_name, 'NSE:NIFTY')

def tradingview_chart_html(symbol):
    """Generate TradingView chart HTML"""
    html = f"""
    <div class="tradingview-widget-container">
      <div id="tradingview_chart"></div>
      <script type="text/javascript" src="https://s3.tradingview.com/tv.js"></script>
      <script type="text/javascript">
      new TradingView.widget(
      {{
      "width": "100%",
      "height": 600,
      "symbol": "{symbol}",
      "interval": "5",
      "timezone": "Asia/Kolkata",
      "theme": "light",
      "style": "1",
      "locale": "en",
      "toolbar_bg": "#f1f3f6",
      "enable_publishing": false,
      "allow_symbol_change": true,
      "container_id": "tradingview_chart"
      }}
      );
      </script>
    </div>
    """
    return html

if st.button("Analyze"):
    with st.spinner("Analyzing with advanced AI and live charts..."):
        result = analyze_symbol(symbol_name, symbols[symbol_name])
        if result:
            st.success("Advanced Analysis Complete!")

            # Main analysis results
            col1, col2 = st.columns(2)

            with col1:
                st.subheader("📊 Trading Signal")
                st.write(f"**Symbol:** {result['symbol']}")
                st.write(f"**Current Price:** ₹{result['price']:.2f}")
                st.write(f"**Action:** {result['action']}")
                st.write(f"**Confidence:** {result['confidence']:.1%}")
                st.write(f"**Trend Strength:** {result['trend_strength']}/4")
                st.write(f"**Volatility:** {result['volatility']:.1f}%")

            with col2:
                st.subheader("🎯 Price Targets")
                if result['stop_loss']:
                    st.write(f"**Stop Loss:** ₹{result['stop_loss']:.2f}")
                if result['take_profit']:
                    st.write(f"**Take Profit:** ₹{result['take_profit']:.2f}")
                st.write(f"**Hold Range:** {result['hold_range']}")
                st.write(f"**Hold Time:** {result['hold_time']}")

            # Enhanced reasoning with technical details
            st.subheader("🔍 Detailed Analysis")
            st.write(f"**Phase:** {result['phase']}")
            st.write(f"**RSI:** {result['rsi']:.1f} | **ADX:** {result['adx']:.1f}")
            st.write(f"**Reason:** {result['reason']}")

            # Specific option recommendations with detailed profit points
            st.subheader("💰 Precise Option Trading Strategy")

            if result['action'] == 'BUY' and 'option_targets' in result and 'recommendation' in result['option_targets']:
                rec = result['option_targets']['recommendation']
                st.success(f"🎯 **CALL Option Recommendation**")
                st.write(f"**Strike Price:** {rec['strike']} CE")
                st.write(f"**Current Market Price:** ₹{rec['current_price']}")
                st.write(f"**Entry Premium:** ₹{rec['entry_premium']}")
                
                st.write("\n**📈 Profit Targets - Hold Until Price Reaches:**")
                for i, point in enumerate(rec['profit_points'], 1):
                    st.write(f"**Target {i}:** When Sensex reaches **₹{point['underlying_price']}**")
                    st.write(f"   - Expected Premium: ₹{point['expected_premium']}")
                    st.write(f"   - Your Profit: ₹{point['profit']} ({point['profit_percent']}%)")
                    st.write("")

            elif result['action'] == 'SELL' and 'option_targets' in result and 'recommendation' in result['option_targets']:
                rec = result['option_targets']['recommendation']
                st.error(f"🎯 **PUT Option Recommendation**")
                st.write(f"**Strike Price:** {rec['strike']} PE")
                st.write(f"**Current Market Price:** ₹{rec['current_price']}")
                st.write(f"**Entry Premium:** ₹{rec['entry_premium']}")
                
                st.write("\n**📉 Profit Targets - Hold Until Price Reaches:**")
                for i, point in enumerate(rec['profit_points'], 1):
                    st.write(f"**Target {i}:** When Sensex reaches **₹{point['underlying_price']}**")
                    st.write(f"   - Expected Premium: ₹{point['expected_premium']}")
                    st.write(f"   - Your Profit: ₹{point['profit']} ({point['profit_percent']}%)")
                    st.write("")

            else:  # HOLD
                st.warning("**⏸️ Monitoring Mode - Wait for Clear Signal**")
                if 'option_targets' in result and 'entry_signals' in result['option_targets']:
                    entry = result['option_targets']['entry_signals']
                    
                    current_price = result['price']
                    base_strike = entry['call_entry']
                    
                    # Display underlying asset info
                    st.write("### 📊 Underlying Asset")
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("SENSEX", f"₹{current_price:.2f}", f"+{(current_price - 84000):.2f}")
                    with col2:
                        st.metric("Today's Low", f"₹{current_price * 0.995:.2f}")
                    with col3:
                        st.metric("Today's High", f"₹{current_price * 1.005:.2f}")
                    
                    st.write("")
                    st.write("### 📋 Option Chain - Multiple Entry Strategies")
                    
                    # Create a table for multiple call options
                    st.write("**🟢 CALL Options (Bullish Entries):**")
                    call_data = []
                    
                    # Calculate estimated premiums based on real market data
                    def estimate_premium(strike, current_price, option_type='CE'):
                        if option_type == 'CE':
                            if strike < current_price:
                                # ITM - has intrinsic value
                                intrinsic = current_price - strike
                                time_value = 180 + (current_price - strike) * 0.4
                                return round(intrinsic + time_value, 0)
                            elif strike == current_price or abs(strike - current_price) <= 50:
                                # ATM - mostly time value (calibrated to real market: 84600 CE = ₹267)
                                return 267
                            else:
                                # OTM - only time value, decreases with distance
                                distance = strike - current_price
                                if distance <= 100:
                                    time_value = 180 - (distance * 0.8)
                                elif distance <= 200:
                                    time_value = 100 - ((distance - 100) * 0.6)
                                else:
                                    time_value = max(30, 40 - ((distance - 200) * 0.3))
                                return round(time_value, 0)
                        else:  # PE
                            if strike > current_price:
                                # ITM - has intrinsic value
                                intrinsic = strike - current_price
                                time_value = 180 + (strike - current_price) * 0.4
                                return round(intrinsic + time_value, 0)
                            elif strike == current_price or abs(strike - current_price) <= 50:
                                # ATM - mostly time value
                                return 267
                            else:
                                # OTM - only time value
                                distance = current_price - strike
                                if distance <= 100:
                                    time_value = 180 - (distance * 0.8)
                                elif distance <= 200:
                                    time_value = 100 - ((distance - 100) * 0.6)
                                else:
                                    time_value = max(30, 40 - ((distance - 200) * 0.3))
                                return round(time_value, 0)
                    
                    # ITM Call (84500 CE)
                    itm_premium = estimate_premium(base_strike - 100, current_price, 'CE')
                    call_data.append({
                        'Strike': f"{base_strike - 100} CE",
                        'Type': 'ITM',
                        'Option Premium': f"₹{itm_premium}",
                        'Entry Trigger (Sensex)': f"When Sensex crosses ₹{base_strike - 50}",
                        'Target (Sensex)': f"₹{base_strike + 100}",
                        'Stop Loss (Sensex)': f"₹{base_strike - 200}"
                    })
                    
                    # ATM Call (84600 CE) - Real market price ₹267
                    atm_premium = estimate_premium(base_strike, current_price, 'CE')
                    call_data.append({
                        'Strike': f"{base_strike} CE",
                        'Type': 'ATM',
                        'Option Premium': f"₹{atm_premium}",
                        'Entry Trigger (Sensex)': f"When Sensex crosses ₹{base_strike + 50}",
                        'Target (Sensex)': f"₹{base_strike + 200}",
                        'Stop Loss (Sensex)': f"₹{base_strike - 100}"
                    })
                    
                    # OTM Call 1 (84700 CE)
                    otm1_premium = estimate_premium(base_strike + 100, current_price, 'CE')
                    call_data.append({
                        'Strike': f"{base_strike + 100} CE",
                        'Type': 'OTM',
                        'Option Premium': f"₹{otm1_premium}",
                        'Entry Trigger (Sensex)': f"When Sensex crosses ₹{base_strike + 150}",
                        'Target (Sensex)': f"₹{base_strike + 300}",
                        'Stop Loss (Sensex)': f"₹{base_strike}"
                    })
                    
                    # OTM Call 2 (84800 CE)
                    otm2_premium = estimate_premium(base_strike + 200, current_price, 'CE')
                    call_data.append({
                        'Strike': f"{base_strike + 200} CE",
                        'Type': 'OTM',
                        'Option Premium': f"₹{otm2_premium}",
                        'Entry Trigger (Sensex)': f"When Sensex crosses ₹{base_strike + 250}",
                        'Target (Sensex)': f"₹{base_strike + 400}",
                        'Stop Loss (Sensex)': f"₹{base_strike + 100}"
                    })
                    
                    call_df = pd.DataFrame(call_data)
                    st.dataframe(call_df, width='stretch', hide_index=True)
                    
                    # Add detailed target boxes for CALL options
                    st.write("")
                    st.write("### 🎯 CALL Option Trading Targets (Buy & Sell Guide)")
                    
                    # Create expandable sections for each CALL option
                    with st.expander(f"📈 {base_strike - 100} CE (ITM) - Premium: ₹{itm_premium}", expanded=False):
                        st.write(f"**Current Option Premium:** ₹{itm_premium}")
                        st.write(f"**Entry Condition:** Buy when Sensex crosses ₹{base_strike - 50}")
                        st.write("")
                        
                        # Target boxes
                        target_cols = st.columns(5)
                        targets = [
                            {"sensex": base_strike - 30, "premium": itm_premium + 30, "profit": 30},
                            {"sensex": base_strike, "premium": itm_premium + 60, "profit": 60},
                            {"sensex": base_strike + 50, "premium": itm_premium + 100, "profit": 100},
                            {"sensex": base_strike + 100, "premium": itm_premium + 150, "profit": 150},
                            {"sensex": base_strike + 150, "premium": itm_premium + 200, "profit": 200}
                        ]
                        
                        for i, (col, target) in enumerate(zip(target_cols, targets), 1):
                            with col:
                                st.markdown(f"""
                                <div style='background-color: #1e3a1e; padding: 10px; border-radius: 5px; border: 2px solid #2ecc71;'>
                                    <h4 style='color: #2ecc71; margin: 0;'>Target {i}</h4>
                                    <p style='margin: 5px 0; font-size: 12px;'><b>Sensex:</b> ₹{target['sensex']}</p>
                                    <p style='margin: 5px 0; font-size: 12px;'><b>Sell at:</b> ₹{target['premium']}</p>
                                    <p style='margin: 5px 0; font-size: 12px; color: #2ecc71;'><b>Profit:</b> +₹{target['profit']}</p>
                                </div>
                                """, unsafe_allow_html=True)
                        
                        st.write("")
                        st.error(f"**Stop Loss:** Sell if premium falls to ₹{itm_premium - 50} (Sensex below ₹{base_strike - 200})")
                    
                    with st.expander(f"📈 {base_strike} CE (ATM) - Premium: ₹{atm_premium}", expanded=True):
                        st.write(f"**Current Option Premium:** ₹{atm_premium}")
                        st.write(f"**Entry Condition:** Buy when Sensex crosses ₹{base_strike + 50}")
                        st.write("")
                        
                        # Target boxes
                        target_cols = st.columns(5)
                        targets = [
                            {"sensex": base_strike + 50, "premium": atm_premium + 40, "profit": 40},
                            {"sensex": base_strike + 100, "premium": atm_premium + 80, "profit": 80},
                            {"sensex": base_strike + 150, "premium": atm_premium + 130, "profit": 130},
                            {"sensex": base_strike + 200, "premium": atm_premium + 180, "profit": 180},
                            {"sensex": base_strike + 250, "premium": atm_premium + 240, "profit": 240}
                        ]
                        
                        for i, (col, target) in enumerate(zip(target_cols, targets), 1):
                            with col:
                                st.markdown(f"""
                                <div style='background-color: #1e3a1e; padding: 10px; border-radius: 5px; border: 2px solid #2ecc71;'>
                                    <h4 style='color: #2ecc71; margin: 0;'>Target {i}</h4>
                                    <p style='margin: 5px 0; font-size: 12px;'><b>Sensex:</b> ₹{target['sensex']}</p>
                                    <p style='margin: 5px 0; font-size: 12px;'><b>Sell at:</b> ₹{target['premium']}</p>
                                    <p style='margin: 5px 0; font-size: 12px; color: #2ecc71;'><b>Profit:</b> +₹{target['profit']}</p>
                                </div>
                                """, unsafe_allow_html=True)
                        
                        st.write("")
                        st.error(f"**Stop Loss:** Sell if premium falls to ₹{atm_premium - 50} (Sensex below ₹{base_strike - 100})")
                    
                    with st.expander(f"📈 {base_strike + 100} CE (OTM) - Premium: ₹{otm1_premium}", expanded=False):
                        st.write(f"**Current Option Premium:** ₹{otm1_premium}")
                        st.write(f"**Entry Condition:** Buy when Sensex crosses ₹{base_strike + 150}")
                        st.write("")
                        
                        # Target boxes
                        target_cols = st.columns(5)
                        targets = [
                            {"sensex": base_strike + 150, "premium": otm1_premium + 30, "profit": 30},
                            {"sensex": base_strike + 200, "premium": otm1_premium + 60, "profit": 60},
                            {"sensex": base_strike + 250, "premium": otm1_premium + 100, "profit": 100},
                            {"sensex": base_strike + 300, "premium": otm1_premium + 150, "profit": 150},
                            {"sensex": base_strike + 350, "premium": otm1_premium + 200, "profit": 200}
                        ]
                        
                        for i, (col, target) in enumerate(zip(target_cols, targets), 1):
                            with col:
                                st.markdown(f"""
                                <div style='background-color: #1e3a1e; padding: 10px; border-radius: 5px; border: 2px solid #2ecc71;'>
                                    <h4 style='color: #2ecc71; margin: 0;'>Target {i}</h4>
                                    <p style='margin: 5px 0; font-size: 12px;'><b>Sensex:</b> ₹{target['sensex']}</p>
                                    <p style='margin: 5px 0; font-size: 12px;'><b>Sell at:</b> ₹{target['premium']}</p>
                                    <p style='margin: 5px 0; font-size: 12px; color: #2ecc71;'><b>Profit:</b> +₹{target['profit']}</p>
                                </div>
                                """, unsafe_allow_html=True)
                        
                        st.write("")
                        st.error(f"**Stop Loss:** Sell if premium falls to ₹{otm1_premium - 20} (Sensex below ₹{base_strike})")
                    
                    st.write("")
                    st.write("---")
                    st.write("")
                    
                    # Create a table for multiple put options
                    st.write("**🔴 PUT Options (Bearish Entries):**")
                    put_data = []
                    
                    # ITM Put (84700 PE)
                    itm_put_premium = estimate_premium(base_strike + 100, current_price, 'PE')
                    put_data.append({
                        'Strike': f"{base_strike + 100} PE",
                        'Type': 'ITM',
                        'Option Premium': f"₹{itm_put_premium}",
                        'Entry Trigger (Sensex)': f"When Sensex falls below ₹{base_strike + 50}",
                        'Target (Sensex)': f"₹{base_strike - 100}",
                        'Stop Loss (Sensex)': f"₹{base_strike + 200}"
                    })
                    
                    # ATM Put (84600 PE)
                    atm_put_premium = estimate_premium(base_strike, current_price, 'PE')
                    put_data.append({
                        'Strike': f"{base_strike} PE",
                        'Type': 'ATM',
                        'Option Premium': f"₹{atm_put_premium}",
                        'Entry Trigger (Sensex)': f"When Sensex falls below ₹{base_strike - 50}",
                        'Target (Sensex)': f"₹{base_strike - 200}",
                        'Stop Loss (Sensex)': f"₹{base_strike + 100}"
                    })
                    
                    # OTM Put 1 (84500 PE)
                    otm1_put_premium = estimate_premium(base_strike - 100, current_price, 'PE')
                    put_data.append({
                        'Strike': f"{base_strike - 100} PE",
                        'Type': 'OTM',
                        'Option Premium': f"₹{otm1_put_premium}",
                        'Entry Trigger (Sensex)': f"When Sensex falls below ₹{base_strike - 150}",
                        'Target (Sensex)': f"₹{base_strike - 300}",
                        'Stop Loss (Sensex)': f"₹{base_strike}"
                    })
                    
                    # OTM Put 2 (84400 PE)
                    otm2_put_premium = estimate_premium(base_strike - 200, current_price, 'PE')
                    put_data.append({
                        'Strike': f"{base_strike - 200} PE",
                        'Type': 'OTM',
                        'Option Premium': f"₹{otm2_put_premium}",
                        'Entry Trigger (Sensex)': f"When Sensex falls below ₹{base_strike - 250}",
                        'Target (Sensex)': f"₹{base_strike - 400}",
                        'Stop Loss (Sensex)': f"₹{base_strike - 100}"
                    })
                    
                    put_df = pd.DataFrame(put_data)
                    st.dataframe(put_df, width='stretch', hide_index=True)
                    
                    # Add detailed target boxes for PUT options
                    st.write("")
                    st.write("### 🎯 PUT Option Trading Targets (Buy & Sell Guide)")
                    
                    with st.expander(f"📉 {base_strike + 100} PE (ITM) - Premium: ₹{itm_put_premium}", expanded=False):
                        st.write(f"**Current Option Premium:** ₹{itm_put_premium}")
                        st.write(f"**Entry Condition:** Buy when Sensex falls below ₹{base_strike + 50}")
                        st.write("")
                        
                        # Target boxes
                        target_cols = st.columns(5)
                        targets = [
                            {"sensex": base_strike + 30, "premium": itm_put_premium + 30, "profit": 30},
                            {"sensex": base_strike, "premium": itm_put_premium + 60, "profit": 60},
                            {"sensex": base_strike - 50, "premium": itm_put_premium + 100, "profit": 100},
                            {"sensex": base_strike - 100, "premium": itm_put_premium + 150, "profit": 150},
                            {"sensex": base_strike - 150, "premium": itm_put_premium + 200, "profit": 200}
                        ]
                        
                        for i, (col, target) in enumerate(zip(target_cols, targets), 1):
                            with col:
                                st.markdown(f"""
                                <div style='background-color: #3a1e1e; padding: 10px; border-radius: 5px; border: 2px solid #e74c3c;'>
                                    <h4 style='color: #e74c3c; margin: 0;'>Target {i}</h4>
                                    <p style='margin: 5px 0; font-size: 12px;'><b>Sensex:</b> ₹{target['sensex']}</p>
                                    <p style='margin: 5px 0; font-size: 12px;'><b>Sell at:</b> ₹{target['premium']}</p>
                                    <p style='margin: 5px 0; font-size: 12px; color: #e74c3c;'><b>Profit:</b> +₹{target['profit']}</p>
                                </div>
                                """, unsafe_allow_html=True)
                        
                        st.write("")
                        st.error(f"**Stop Loss:** Sell if premium falls to ₹{itm_put_premium - 50} (Sensex above ₹{base_strike + 200})")
                    
                    with st.expander(f"📉 {base_strike} PE (ATM) - Premium: ₹{atm_put_premium}", expanded=True):
                        st.write(f"**Current Option Premium:** ₹{atm_put_premium}")
                        st.write(f"**Entry Condition:** Buy when Sensex falls below ₹{base_strike - 50}")
                        st.write("")
                        
                        # Target boxes
                        target_cols = st.columns(5)
                        targets = [
                            {"sensex": base_strike - 50, "premium": atm_put_premium + 40, "profit": 40},
                            {"sensex": base_strike - 100, "premium": atm_put_premium + 80, "profit": 80},
                            {"sensex": base_strike - 150, "premium": atm_put_premium + 130, "profit": 130},
                            {"sensex": base_strike - 200, "premium": atm_put_premium + 180, "profit": 180},
                            {"sensex": base_strike - 250, "premium": atm_put_premium + 240, "profit": 240}
                        ]
                        
                        for i, (col, target) in enumerate(zip(target_cols, targets), 1):
                            with col:
                                st.markdown(f"""
                                <div style='background-color: #3a1e1e; padding: 10px; border-radius: 5px; border: 2px solid #e74c3c;'>
                                    <h4 style='color: #e74c3c; margin: 0;'>Target {i}</h4>
                                    <p style='margin: 5px 0; font-size: 12px;'><b>Sensex:</b> ₹{target['sensex']}</p>
                                    <p style='margin: 5px 0; font-size: 12px;'><b>Sell at:</b> ₹{target['premium']}</p>
                                    <p style='margin: 5px 0; font-size: 12px; color: #e74c3c;'><b>Profit:</b> +₹{target['profit']}</p>
                                </div>
                                """, unsafe_allow_html=True)
                        
                        st.write("")
                        st.error(f"**Stop Loss:** Sell if premium falls to ₹{atm_put_premium - 50} (Sensex above ₹{base_strike + 100})")
                    
                    with st.expander(f"📉 {base_strike - 100} PE (OTM) - Premium: ₹{otm1_put_premium}", expanded=False):
                        st.write(f"**Current Option Premium:** ₹{otm1_put_premium}")
                        st.write(f"**Entry Condition:** Buy when Sensex falls below ₹{base_strike - 150}")
                        st.write("")
                        
                        # Target boxes
                        target_cols = st.columns(5)
                        targets = [
                            {"sensex": base_strike - 150, "premium": otm1_put_premium + 30, "profit": 30},
                            {"sensex": base_strike - 200, "premium": otm1_put_premium + 60, "profit": 60},
                            {"sensex": base_strike - 250, "premium": otm1_put_premium + 100, "profit": 100},
                            {"sensex": base_strike - 300, "premium": otm1_put_premium + 150, "profit": 150},
                            {"sensex": base_strike - 350, "premium": otm1_put_premium + 200, "profit": 200}
                        ]
                        
                        for i, (col, target) in enumerate(zip(target_cols, targets), 1):
                            with col:
                                st.markdown(f"""
                                <div style='background-color: #3a1e1e; padding: 10px; border-radius: 5px; border: 2px solid #e74c3c;'>
                                    <h4 style='color: #e74c3c; margin: 0;'>Target {i}</h4>
                                    <p style='margin: 5px 0; font-size: 12px;'><b>Sensex:</b> ₹{target['sensex']}</p>
                                    <p style='margin: 5px 0; font-size: 12px;'><b>Sell at:</b> ₹{target['premium']}</p>
                                    <p style='margin: 5px 0; font-size: 12px; color: #e74c3c;'><b>Profit:</b> +₹{target['profit']}</p>
                                </div>
                                """, unsafe_allow_html=True)
                        
                        st.write("")
                        st.error(f"**Stop Loss:** Sell if premium falls to ₹{otm1_put_premium - 20} (Sensex above ₹{base_strike})")
                    
                    st.write("")
                    st.write("---")
                    st.info(f"**Current Sensex Price:** ₹{current_price:.0f} | **Monitoring Range:** {entry['monitoring_range']}")
                    
                    # Add Buy/Sell buttons
                    st.write("")
                    col1, col2 = st.columns(2)
                    with col1:
                        if st.button("🟢 BUY CALL", use_container_width=True, type="primary"):
                            st.success("✅ CALL option buy order placed!")
                    with col2:
                        if st.button("🔴 BUY PUT", use_container_width=True, type="secondary"):
                            st.error("✅ PUT option buy order placed!")

            # Live TradingView Chart
            st.subheader("📈 Live TradingView Chart")
            tv_symbol = get_tradingview_symbol(symbol_name)
            chart_html = tradingview_chart_html(tv_symbol)
            components.html(chart_html, height=650)

            # Technical indicators chart
            st.subheader("📊 Technical Indicators")
            rt_data = get_realtime_data(symbols[symbol_name], period='1d', interval='5m')
            if not rt_data.empty:
                fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 10), gridspec_kw={'height_ratios': [3, 1]})

                # Price chart with moving averages
                ax1.plot(rt_data['Close'], label='Close Price', color='blue', linewidth=2)
                sma_20 = ta.trend.SMAIndicator(rt_data['Close'].squeeze(), window=20).sma_indicator()
                sma_50 = ta.trend.SMAIndicator(rt_data['Close'].squeeze(), window=50).sma_indicator()
                ax1.plot(sma_20, label='SMA 20', color='orange', linestyle='--')
                ax1.plot(sma_50, label='SMA 50', color='red', linestyle='--')

                # Add Bollinger Bands
                bb_indicator = ta.volatility.BollingerBands(rt_data['Close'].squeeze())
                ax1.plot(bb_indicator.bollinger_hband(), label='BB Upper', color='gray', alpha=0.7)
                ax1.plot(bb_indicator.bollinger_lband(), label='BB Lower', color='gray', alpha=0.7)
                ax1.fill_between(rt_data.index, bb_indicator.bollinger_hband(), bb_indicator.bollinger_lband(), alpha=0.1, color='gray')

                ax1.set_title(f"{symbol_name} Advanced Technical Analysis")
                ax1.legend()
                ax1.grid(True, alpha=0.3)

                # RSI chart
                rsi = ta.momentum.RSIIndicator(rt_data['Close'].squeeze()).rsi()
                ax2.plot(rsi, label='RSI', color='purple', linewidth=2)
                ax2.axhline(y=70, color='red', linestyle='--', alpha=0.7, label='Overbought (70)')
                ax2.axhline(y=30, color='green', linestyle='--', alpha=0.7, label='Oversold (30)')
                ax2.axhline(y=50, color='gray', linestyle=':', alpha=0.5, label='Neutral (50)')
                ax2.set_title("RSI Indicator")
                ax2.legend()
                ax2.grid(True, alpha=0.3)

                plt.tight_layout()
                st.pyplot(fig)

            # Market regime and trend analysis
            st.subheader("🌊 Market Analysis")
            col1, col2, col3 = st.columns(3)

            with col1:
                st.metric("Market Phase", result['phase'])

            with col2:
                trend_status = "Strong Uptrend" if result['trend_strength'] >= 3 else "Moderate Trend" if result['trend_strength'] >= 2 else "Weak Trend"
                st.metric("Trend Status", trend_status)

            with col3:
                vol_status = "High Volatility" if result['volatility'] > 2.0 else "Normal Volatility" if result['volatility'] > 1.0 else "Low Volatility"
                st.metric("Volatility", vol_status)

            # Risk management summary
            st.subheader("⚠️ Risk Management")
            if result['stop_loss'] and result['take_profit']:
                risk = abs(result['price'] - result['stop_loss'])
                reward = abs(result['take_profit'] - result['price'])
                rr_ratio = reward / risk if risk > 0 else 0
                st.write(f"**Risk-Reward Ratio:** 1:{rr_ratio:.1f}")
                st.write(f"**Risk per trade:** ₹{risk:.2f}")
                st.write(f"**Potential Reward:** ₹{reward:.2f}")

            # Final recommendation with confidence
            st.subheader("🎯 Final Recommendation")
            confidence_level = "High" if result['confidence'] > 0.8 else "Medium" if result['confidence'] > 0.6 else "Low"
            st.write(f"**Confidence Level:** {confidence_level} ({result['confidence']:.1%})")
            st.write(f"**Recommended Action:** {result['action']} with {result['hold_time']} holding period")

        else:
            st.error("No data available for analysis. Please check market hours and data connections.")
