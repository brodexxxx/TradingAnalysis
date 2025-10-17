import time
import matplotlib.pyplot as plt
import pandas as pd
from data_fetcher import get_realtime_data, get_historical_data, is_market_open, symbols
from support_resistance import find_support_resistance, dynamic_support_resistance
from market_stages import identify_market_phase
from trending_ranging import is_trending
from candlestick_patterns import bullish_marubozu, doji, bullish_engulfing
from chart_patterns import head_and_shoulders, double_top
from volume_analysis import volume_analysis
from moving_averages import simple_ma, exponential_ma, ma_crossover
from price_rejection_acceptance import price_rejection, price_acceptance
from risk_management import position_size
from stop_losses import initial_stop_loss
from trading_journal import log_entry
from indicators import get_indicator_signals
from ml_predictor import predictor
from models import TradingRecord, session
import json
import ta  # For RSI

def analyze_symbol(symbol_name, symbol):
    """
    Advanced analysis with price targets and trend analysis for accurate trading signals.
    """
    try:
        # Get real-time data
        rt_data = get_realtime_data(symbol, period='1d', interval='5m')
        if rt_data.empty:
            return None

        # Calculate comprehensive indicators
        close_prices = rt_data['Close'].squeeze()
        high_prices = rt_data['High'].squeeze()
        low_prices = rt_data['Low'].squeeze()
        volume = rt_data['Volume'].squeeze()

        # Core indicators
        rsi = ta.momentum.RSIIndicator(close_prices).rsi().iloc[-1]
        macd_indicator = ta.trend.MACD(close_prices)
        macd = macd_indicator.macd().iloc[-1]
        macd_signal = macd_indicator.macd_signal().iloc[-1]

        # Bollinger Bands
        bb_indicator = ta.volatility.BollingerBands(close_prices)
        bb_upper = bb_indicator.bollinger_hband().iloc[-1]
        bb_lower = bb_indicator.bollinger_lband().iloc[-1]
        bb_middle = bb_indicator.bollinger_mavg().iloc[-1]

        # Moving averages
        sma_20 = ta.trend.SMAIndicator(close_prices, window=20).sma_indicator().iloc[-1]
        sma_50 = ta.trend.SMAIndicator(close_prices, window=50).sma_indicator().iloc[-1]
        ema_20 = ta.trend.EMAIndicator(close_prices, window=20).ema_indicator().iloc[-1]

        # Stochastic Oscillator
        stoch_indicator = ta.momentum.StochasticOscillator(high_prices, low_prices, close_prices)
        stoch_k = stoch_indicator.stoch().iloc[-1]
        stoch_d = stoch_indicator.stoch_signal().iloc[-1]

        # Additional advanced indicators
        adx_indicator = ta.trend.ADXIndicator(high_prices, low_prices, close_prices)
        adx = adx_indicator.adx().iloc[-1]

        cci = ta.trend.CCIIndicator(high_prices, low_prices, close_prices).cci().iloc[-1]
        williams_r = ta.momentum.WilliamsRIndicator(high_prices, low_prices, close_prices).williams_r().iloc[-1]
        mfi = ta.volume.MFIIndicator(high_prices, low_prices, close_prices, volume).money_flow_index().iloc[-1]
        roc = ta.momentum.ROCIndicator(close_prices).roc().iloc[-1]

        # Volume analysis
        avg_volume = volume.mean()
        volume_trend = volume.iloc[-5:].mean() / volume.iloc[-20:].mean() if len(volume) > 20 else 1.0

        # Volatility calculation
        volatility = close_prices.pct_change().std() * 100  # Daily volatility percentage

        # Trend analysis
        trend_strength = 0
        if macd > macd_signal:
            trend_strength += 1
        if close_prices.iloc[-1] > sma_20:
            trend_strength += 1
        if sma_20 > sma_50:
            trend_strength += 1
        if adx > 25:
            trend_strength += 1

        # Get ML prediction with enhanced indicators
        indicators = {
            'rsi': rsi,
            'macd': macd,
            'macd_signal': macd_signal,
            'sma': sma_20,
            'ema': ema_20,
            'volume': avg_volume,
            'bb_upper': bb_upper,
            'bb_lower': bb_lower,
            'bb_middle': bb_middle,
            'stoch_k': stoch_k,
            'stoch_d': stoch_d,
            'adx': adx,
            'cci': cci,
            'williams_r': williams_r,
            'mfi': mfi,
            'roc': roc,
            'volatility': volatility,
            'trend_strength': trend_strength / 4.0,  # Normalize to 0-1
            'momentum': macd,  # MACD as momentum proxy
        }

        action = predictor.predict(indicators)
        confidence = predictor.get_prediction_confidence(indicators)

        # Calculate precise price targets based on current market conditions
        current_price = close_prices.iloc[-1]

        # Dynamic stop loss and take profit based on volatility and trend
        atr = ta.volatility.AverageTrueRange(high_prices, low_prices, close_prices).average_true_range().iloc[-1]
        risk_multiplier = 1.5 if volatility > 2.0 else 2.0  # Higher risk in volatile markets

        if action == 'buy':
            stop_loss = current_price - (atr * risk_multiplier)
            # Profit targets based on resistance levels and trend strength
            if trend_strength >= 3:  # Strong uptrend
                take_profit = current_price + (atr * 4)  # Higher target in strong trends
            else:
                take_profit = current_price + (atr * 2.5)
        elif action == 'sell':
            stop_loss = current_price + (atr * risk_multiplier)
            if trend_strength >= 3:  # Strong downtrend
                take_profit = current_price - (atr * 4)
            else:
                take_profit = current_price - (atr * 2.5)
        else:
            stop_loss = None
            take_profit = None

        # Enhanced phase determination with realistic hold times for current market
        if rsi < 30 and macd > macd_signal and trend_strength >= 2:
            phase = "Strong Bullish"
            hold_time = "Intraday to 2 days (Target: ₹{:.0f})".format(current_price + 300)
        elif rsi < 35 and (macd > macd_signal or close_prices.iloc[-1] > sma_20):
            phase = "Bullish Recovery"
            hold_time = "Intraday to 1 day (Target: ₹{:.0f})".format(current_price + 200)
        elif rsi > 70 and macd < macd_signal and trend_strength >= 2:
            phase = "Strong Bearish"
            hold_time = "Intraday to 2 days (Target: ₹{:.0f})".format(current_price - 300)
        elif rsi > 65 and (macd < macd_signal or close_prices.iloc[-1] < sma_20):
            phase = "Bearish Setup"
            hold_time = "Intraday to 1 day (Target: ₹{:.0f})".format(current_price - 200)
        elif 40 <= rsi <= 60 and abs(macd - macd_signal) < atr * 0.5:
            phase = "Consolidation"
            # More realistic breakout levels
            resistance = round((current_price + 100) / 50) * 50
            support = round((current_price - 100) / 50) * 50
            hold_time = "Wait for breakout - Buy above ₹{:.0f} or Sell below ₹{:.0f}".format(resistance, support)
        else:
            phase = "Neutral"
            # Provide actionable levels instead of just current price
            resistance = round((current_price + 150) / 50) * 50
            support = round((current_price - 150) / 50) * 50
            hold_time = "Monitor key levels - Resistance: ₹{:.0f}, Support: ₹{:.0f}".format(resistance, support)

        # Enhanced hold range with support/resistance based on current price
        # Calculate dynamic range around current price
        price_range_percent = 0.02  # 2% range for intraday
        dynamic_low = current_price * (1 - price_range_percent)
        dynamic_high = current_price * (1 + price_range_percent)
        
        # Also consider recent highs/lows
        recent_high = high_prices.iloc[-20:].max()
        recent_low = low_prices.iloc[-20:].min()
        
        # Use the tighter range for better accuracy
        hold_low = max(dynamic_low, recent_low)
        hold_high = min(dynamic_high, recent_high)
        
        hold_range = f"₹{hold_low:.0f} - ₹{hold_high:.0f}"

        # Detailed reason with specific metrics
        if action == 'buy':
            reason = f"Strong buy signal: RSI {rsi:.1f} (oversold), MACD bullish (↑{macd:.2f}), Trend strength {trend_strength}/4, Volume {volume_trend:.1f}x avg"
        elif action == 'sell':
            reason = f"Strong sell signal: RSI {rsi:.1f} (overbought), MACD bearish (↓{macd:.2f}), Trend weakness {4-trend_strength}/4, Volume {volume_trend:.1f}x avg"
        else:
            reason = f"Hold position: Market equilibrium, RSI {rsi:.1f} (neutral), MACD flat, waiting for directional momentum"

        # Calculate option price targets for specific recommendations
        option_targets = calculate_option_targets(symbol_name, current_price, action, volatility, trend_strength)

        return {
            'symbol': symbol_name,
            'price': current_price,
            'action': action.upper(),
            'stop_loss': stop_loss,
            'take_profit': take_profit,
            'reason': reason,
            'rsi': rsi,
            'phase': phase,
            'hold_time': hold_time,
            'hold_range': hold_range,
            'confidence': confidence,
            'time_period': '1D',
            'trend_strength': trend_strength,
            'volatility': volatility,
            'adx': adx,
            'option_targets': option_targets
        }

    except Exception as e:
        print(f"Error analyzing {symbol_name}: {e}")
        return None

def calculate_option_targets(symbol_name, current_price, action, volatility, trend_strength):
    """
    Calculate specific option price targets with detailed profit points for precise trading recommendations.
    """
    # Base strike calculation - round to nearest 100
    base_strike = round(current_price / 100) * 100

    # Adjust for volatility and trend
    volatility_adjustment = int(volatility * 10)  # Scale volatility to strike adjustment
    trend_adjustment = trend_strength * 50  # Trend strength adjustment

    targets = {}

    if action == 'buy':
        # For bullish positions, recommend calls with specific price point targets
        # Recommended strike: slightly OTM or ATM for best risk/reward
        recommended_strike = base_strike + 100 if current_price > base_strike + 50 else base_strike
        
        # Calculate profit points - where underlying price should reach
        profit_point_1 = base_strike + 200  # First target
        profit_point_2 = base_strike + 300  # Second target
        profit_point_3 = base_strike + 400  # Third target (aggressive)
        
        # Estimate option premiums at different price points
        # Current premium estimation
        if recommended_strike <= current_price:
            intrinsic_value = current_price - recommended_strike
            time_value = max(50, volatility * 20)
            current_premium = intrinsic_value + time_value
        else:
            time_value = max(30, volatility * 15)
            current_premium = time_value
        
        # Premium at profit point 1 (underlying moves 200 points up)
        premium_at_point_1 = current_premium + (profit_point_1 - current_price) * 0.7  # Delta ~0.7
        
        # Premium at profit point 2 (underlying moves 300 points up)
        premium_at_point_2 = current_premium + (profit_point_2 - current_price) * 0.75  # Delta ~0.75
        
        # Premium at profit point 3 (underlying moves 400 points up)
        premium_at_point_3 = current_premium + (profit_point_3 - current_price) * 0.8  # Delta ~0.8
        
        targets['recommendation'] = {
            'type': 'CALL',
            'strike': recommended_strike,
            'current_price': round(current_price, 0),
            'entry_premium': round(current_premium, 1),
            'profit_points': [
                {
                    'underlying_price': profit_point_1,
                    'expected_premium': round(premium_at_point_1, 1),
                    'profit': round(premium_at_point_1 - current_premium, 1),
                    'profit_percent': round(((premium_at_point_1 - current_premium) / current_premium) * 100, 1)
                },
                {
                    'underlying_price': profit_point_2,
                    'expected_premium': round(premium_at_point_2, 1),
                    'profit': round(premium_at_point_2 - current_premium, 1),
                    'profit_percent': round(((premium_at_point_2 - current_premium) / current_premium) * 100, 1)
                },
                {
                    'underlying_price': profit_point_3,
                    'expected_premium': round(premium_at_point_3, 1),
                    'profit': round(premium_at_point_3 - current_premium, 1),
                    'profit_percent': round(((premium_at_point_3 - current_premium) / current_premium) * 100, 1)
                }
            ]
        }

    elif action == 'sell':
        # For bearish positions, recommend puts with specific price point targets
        recommended_strike = base_strike - 100 if current_price < base_strike - 50 else base_strike
        
        # Calculate profit points - where underlying price should reach
        profit_point_1 = base_strike - 200  # First target
        profit_point_2 = base_strike - 300  # Second target
        profit_point_3 = base_strike - 400  # Third target (aggressive)
        
        # Estimate option premiums at different price points
        if recommended_strike >= current_price:
            intrinsic_value = recommended_strike - current_price
            time_value = max(50, volatility * 20)
            current_premium = intrinsic_value + time_value
        else:
            time_value = max(30, volatility * 15)
            current_premium = time_value
        
        # Premium at profit points
        premium_at_point_1 = current_premium + (current_price - profit_point_1) * 0.7
        premium_at_point_2 = current_premium + (current_price - profit_point_2) * 0.75
        premium_at_point_3 = current_premium + (current_price - profit_point_3) * 0.8
        
        targets['recommendation'] = {
            'type': 'PUT',
            'strike': recommended_strike,
            'current_price': round(current_price, 0),
            'entry_premium': round(current_premium, 1),
            'profit_points': [
                {
                    'underlying_price': profit_point_1,
                    'expected_premium': round(premium_at_point_1, 1),
                    'profit': round(premium_at_point_1 - current_premium, 1),
                    'profit_percent': round(((premium_at_point_1 - current_premium) / current_premium) * 100, 1)
                },
                {
                    'underlying_price': profit_point_2,
                    'expected_premium': round(premium_at_point_2, 1),
                    'profit': round(premium_at_point_2 - current_premium, 1),
                    'profit_percent': round(((premium_at_point_2 - current_premium) / current_premium) * 100, 1)
                },
                {
                    'underlying_price': profit_point_3,
                    'expected_premium': round(premium_at_point_3, 1),
                    'profit': round(premium_at_point_3 - current_premium, 1),
                    'profit_percent': round(((premium_at_point_3 - current_premium) / current_premium) * 100, 1)
                }
            ]
        }

    else:
        # For hold positions, show potential entry points for both calls and puts
        targets['entry_signals'] = {
            'call_entry': base_strike,
            'put_entry': base_strike,
            'monitoring_range': f"{base_strike-200} - {base_strike+200}",
            'call_trigger': f"Buy {base_strike} CE if price crosses {base_strike + 50}",
            'put_trigger': f"Buy {base_strike} PE if price falls below {base_strike - 50}"
        }

    return targets

def main():
    while True:
        if is_market_open():
            print("Market open, analyzing...")
            for name, sym in symbols.items():
                result = analyze_symbol(name, sym)
                if result:
                    print(f"{result['symbol']}: {result['action']} at {result['price']:.2f}, SL: {result['stop_loss']:.2f if result['stop_loss'] else 'N/A'}, TP: {result['take_profit']:.2f if result['take_profit'] else 'N/A'}")
                    print(f"Reason: {result['reason']}")
            time.sleep(300)  # 5 min
        else:
            print("Market closed, waiting...")
            time.sleep(60)  # Check every min

if __name__ == "__main__":
    main()
