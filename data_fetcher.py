import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import pytz
import os
import requests
import json
from alpha_vantage.timeseries import TimeSeries
# from polygon_api_client import RESTClient
from twelvedata import TDClient

def get_historical_data(symbol, years=1):
    """
    Fetch historical data for the last year using multiple sources.
    """
    ist = pytz.timezone('Asia/Kolkata')
    end_date = datetime.now(ist)
    start_date = end_date - timedelta(days=years*365)

    data = pd.DataFrame()

    # Try yfinance first for all symbols (including Indian markets with .NS symbols)
    try:
        data = yf.download(symbol, start=start_date, end=end_date, interval='1d', progress=False)
    except Exception as e:
        print(f"yfinance error for {symbol}: {e}")

    # Fallback to mock data if all sources fail
    if data.empty:
        print(f"Using mock data for {symbol}")
        data = generate_mock_data(start_date, end_date, symbol)

    return data

def get_mock_historical_data(symbol, years=6):
    """
    Generate mock historical data for demonstration.
    """
    dates = pd.date_range(end=datetime.now(), periods=years*365, freq='D')
    np.random.seed(42)  # For reproducible mock data

    base_price = {
        'Sensex': 83754,  # Updated to current market level
        'BankNifty': 52000,
        'Nifty50': 24000,
        'CrudeOil': 85
    }.get(symbol, 100)

    # Generate realistic price movements
    price_changes = np.random.normal(0, 0.01, len(dates))  # Small daily changes
    prices = base_price * (1 + np.cumsum(price_changes))

    data = pd.DataFrame({
        'Open': prices * (1 + np.random.normal(0, 0.005, len(dates))),
        'High': prices * (1 + np.random.normal(0.005, 0.01, len(dates))),
        'Low': prices * (1 - np.random.normal(0.005, 0.01, len(dates))),
        'Close': prices,
        'Volume': np.random.randint(100000, 1000000, len(dates))
    }, index=dates)

    # Ensure High >= Close >= Low >= Open
    data['High'] = data[['High', 'Close', 'Open']].max(axis=1)
    data['Low'] = data[['Low', 'Close', 'Open']].min(axis=1)

    return data



def get_indian_market_data(index_name, start_date, end_date, intraday=False):
    """
    Get Indian market data from NSE/BSE APIs or web scraping.
    """
    try:
        # Try NSE India API for historical data
        if index_name == 'NSEI':
            url = f"https://www.nseindia.com/api/historical/indicesHistory?indexType=NIFTY%2050&from={start_date.strftime('%d-%m-%Y')}&to={end_date.strftime('%d-%m-%Y')}"
        elif index_name == 'BSESN':
            url = f"https://www.bseindia.com/download/BhavCopy/Equity/eq{start_date.strftime('%d%m%y')}_csv.zip"
        elif index_name == 'NSEBANK':
            url = f"https://www.nseindia.com/api/historical/indicesHistory?indexType=NIFTY%20BANK&from={start_date.strftime('%d-%m-%Y')}&to={end_date.strftime('%d-%m-%Y')}"

        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }

        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code == 200:
            # Parse the response (this would need specific parsing logic for each exchange)
            # For now, return empty to trigger mock data
            pass

    except Exception as e:
        print(f"Failed to get data from NSE/BSE: {e}")

    # If API fails, try yfinance with different symbols
    try:
        alt_symbols = {
            'NSEI': 'NIFTY50.NS',
            'BSESN': 'SENSEX.NS',
            'NSEBANK': 'BANKNIFTY.NS'
        }

        if index_name in alt_symbols:
            data = yf.download(alt_symbols[index_name], start=start_date, end=end_date, interval='1d' if not intraday else '5m')
            if not data.empty:
                return data
    except:
        pass

    return pd.DataFrame()

def generate_mock_data(start_date, end_date, symbol, intraday=False):
    """
    Generate realistic mock data for testing when APIs fail.
    """
    ist = pytz.timezone('Asia/Kolkata')

    if intraday:
        # Generate intraday data (5-minute intervals during market hours)
        dates = []
        current = start_date.replace(hour=9, minute=15, second=0, microsecond=0)
        market_close = start_date.replace(hour=15, minute=30, second=0, microsecond=0)

        while current <= market_close:
            if current.weekday() < 5:  # Monday to Friday
                dates.append(current)
            current += timedelta(minutes=5)

        if not dates:
            # If no market hours today, generate some data points
            dates = pd.date_range(start=start_date, end=end_date, freq='5min')[:50]
    else:
        # Generate daily data
        dates = pd.date_range(start=start_date, end=end_date, freq='D')

    if len(dates) == 0:
        return pd.DataFrame()

    np.random.seed(42)  # For reproducible results

    # Base prices for different symbols (updated for current market levels)
    base_prices = {
        '^BSESN': 83754,  # Updated Sensex base price to current market level
        '^NSEI': 25000,   # Updated Nifty50 base price
        '^NSEBANK': 52000, # Updated BankNifty base price
        'CL=F': 70,       # Updated Crude Oil base price
        'NIFTY50.NS': 25000,
        'SENSEX.NS': 83754,  # Updated Sensex base price to current market level
        'BANKNIFTY.NS': 52000
    }

    base_price = base_prices.get(symbol, 100)

    # Generate OHLCV data with realistic volatility and mean reversion
    n_points = len(dates)
    prices = []
    current_price = base_price
    
    for i in range(n_points):
        if intraday:
            # Smaller movements for intraday data
            change = np.random.normal(0, base_price * 0.003)  # 0.3% volatility
            # Strong mean reversion for intraday to keep price near base
            reversion = (base_price - current_price) * 0.15
        else:
            # Larger movements for daily data
            change = np.random.normal(0, base_price * 0.01)  # 1% daily volatility
            # Moderate mean reversion for daily data
            reversion = (base_price - current_price) * 0.05
        
        current_price = current_price + change + reversion
        current_price = max(current_price, base_price * 0.8)  # Floor at 80% of base
        current_price = min(current_price, base_price * 1.2)  # Cap at 120% of base
        prices.append(current_price)

    # Create OHLCV data
    data = []
    for i, price in enumerate(prices):
        volatility = abs(np.random.normal(0, price * 0.01))
        high = price + volatility
        low = price - volatility
        open_price = prices[i-1] if i > 0 else price
        volume = np.random.randint(100000, 10000000)

        data.append({
            'Open': open_price,
            'High': high,
            'Low': low,
            'Close': price,
            'Volume': volume
        })

    df = pd.DataFrame(data, index=dates)
    df.index.name = 'Date'

    return df

def is_market_open():
    """
    Check if Indian market is open (9:15 AM to 3:30 PM IST).
    """
    ist = pytz.timezone('Asia/Kolkata')
    now = datetime.now(ist)
    market_open = now.replace(hour=9, minute=15, second=0, microsecond=0)
    market_close = now.replace(hour=15, minute=30, second=0, microsecond=0)
    return market_open <= now <= market_close and now.weekday() < 5  # Mon-Fri

# Symbol mappings - Updated to use reliable Yahoo Finance .NS symbols
symbols = {
    'Sensex': 'SENSEX.NS',      # BSE Sensex
    'BankNifty': 'BANKNIFTY.NS', # Bank Nifty
    'Nifty50': 'NIFTY50.NS',    # Nifty 50
    'CrudeOil': 'CL=F'  # WTI Crude, adjust if needed for Brent
}

# Alternative symbols if primary fail
alt_symbols = {
    'Sensex': '^BSESN',
    'BankNifty': '^NSEBANK',
    'Nifty50': '^NSEI',
    'CrudeOil': 'BZ=F'  # Brent Crude
}

# Alpha Vantage API key (set as environment variable ALPHA_VANTAGE_API_KEY)
API_KEY = os.getenv('ALPHA_VANTAGE_API_KEY')

# API Keys
POLYGON_API_KEY = os.getenv('POLYGON_API_KEY')
FMP_API_KEY = os.getenv('FMP_API_KEY')
TWELVE_DATA_API_KEY = os.getenv('TWELVE_DATA_API_KEY')
ALPHA_VANTAGE_API_KEY = os.getenv('ALPHA_VANTAGE_API_KEY')

# Symbol mappings for different APIs
# Polygon.io symbols (global markets)
polygon_symbols = {
    'Sensex': 'I:OMXS30',  # OMX Stockholm 30 as proxy for global index
    'BankNifty': 'I:OMXC25',  # OMX Copenhagen 25 as proxy
    'Nifty50': 'I:OMXH25',  # OMX Helsinki 25 as proxy
    'CrudeOil': 'C:CL'  # WTI Crude
}

# Financial Modeling Prep symbols
fmp_symbols = {
    'Sensex': 'HDFCBANK.NS',  # Indian proxy
    'BankNifty': 'ICICIBANK.NS',  # Indian proxy
    'Nifty50': 'RELIANCE.NS',  # Indian proxy
    'CrudeOil': 'CL=F'  # Yahoo symbol
}

# Twelve Data symbols
twelve_symbols = {
    'Sensex': 'HDFCBANK.NS',  # Indian proxy
    'BankNifty': 'ICICIBANK.NS',  # Indian proxy
    'Nifty50': 'RELIANCE.NS',  # Indian proxy
    'CrudeOil': 'CL'  # WTI Crude
}

# Alpha Vantage symbol mappings (for Indian markets, use proxy stocks or global equivalents)
av_symbols = {
    'Sensex': 'HDFCBANK.NS',  # Proxy for Indian market
    'BankNifty': 'HDFCBANK.NS',  # Proxy
    'Nifty50': 'RELIANCE.NS',  # Proxy
    'CrudeOil': 'CL'  # WTI Crude
}

def get_alpha_vantage_data(symbol, interval='5min', outputsize='compact'):
    """
    Fetch intraday data from Alpha Vantage.
    """
    if not API_KEY:
        return pd.DataFrame()  # Return empty if no API key

    ts = TimeSeries(key=API_KEY, output_format='pandas')
    try:
        if interval == '1min':
            data, meta_data = ts.get_intraday(symbol=av_symbols.get(symbol, symbol), interval='1min', outputsize=outputsize)
        elif interval == '5min':
            data, meta_data = ts.get_intraday(symbol=av_symbols.get(symbol, symbol), interval='5min', outputsize=outputsize)
        elif interval == '15min':
            data, meta_data = ts.get_intraday(symbol=av_symbols.get(symbol, symbol), interval='15min', outputsize=outputsize)
        elif interval == '30min':
            data, meta_data = ts.get_intraday(symbol=av_symbols.get(symbol, symbol), interval='30min', outputsize=outputsize)
        elif interval == '60min':
            data, meta_data = ts.get_intraday(symbol=av_symbols.get(symbol, symbol), interval='60min', outputsize=outputsize)
        else:
            data, meta_data = ts.get_intraday(symbol=av_symbols.get(symbol, symbol), interval='5min', outputsize=outputsize)

        # Rename columns to match yfinance format
        data = data.rename(columns={
            '1. open': 'Open',
            '2. high': 'High',
            '3. low': 'Low',
            '4. close': 'Close',
            '5. volume': 'Volume'
        })
        return data
    except Exception as e:
        print(f"Alpha Vantage error for {symbol}: {e}")
        return pd.DataFrame()

def get_mock_data(symbol):
    """
    Generate mock data for demonstration when APIs fail.
    """
    dates = pd.date_range(end=datetime.now(), periods=100, freq='5min')
    
    # Use a different seed or no seed to get varied data each time
    # This ensures fresh data that's closer to current market levels
    
    base_price = {
        'Sensex': 83754,  # Updated to current market level
        'BankNifty': 52000,
        'Nifty50': 24000,
        'CrudeOil': 85
    }.get(symbol, 100)

    # Generate realistic price movements with mean reversion to keep prices near base
    prices = []
    current_price = base_price
    
    for i in range(len(dates)):
        # Small random change with mean reversion
        change = np.random.normal(0, base_price * 0.002)  # Reduced volatility
        # Mean reversion: pull price back towards base
        reversion = (base_price - current_price) * 0.1
        current_price = current_price + change + reversion
        prices.append(current_price)
    
    prices = np.array(prices)

    data = pd.DataFrame({
        'Open': prices * (1 + np.random.normal(0, 0.0005, len(dates))),
        'High': prices * (1 + np.random.normal(0.0005, 0.001, len(dates))),
        'Low': prices * (1 - np.random.normal(0.0005, 0.001, len(dates))),
        'Close': prices,
        'Volume': np.random.randint(1000, 100000, len(dates))
    }, index=dates)

    # Ensure High >= Close >= Low >= Open (basic OHLC integrity)
    data['High'] = data[['High', 'Close', 'Open']].max(axis=1)
    data['Low'] = data[['Low', 'Close', 'Open']].min(axis=1)

    return data

def get_polygon_data(symbol, period='1d', interval='5m'):
    """
    Fetch intraday data from Polygon.io.
    """
    if not POLYGON_API_KEY:
        return pd.DataFrame()

    try:
        client = RESTClient(POLYGON_API_KEY)
        poly_symbol = polygon_symbols.get(symbol, symbol)

        # Convert interval to Polygon format
        multiplier = 5
        timespan = 'minute'
        if interval == '1m':
            multiplier = 1
        elif interval == '5m':
            multiplier = 5
        elif interval == '15m':
            multiplier = 15
        elif interval == '30m':
            multiplier = 30
        elif interval == '1h':
            multiplier = 60
            timespan = 'hour'

        # Get bars
        bars = client.get_aggs(poly_symbol, multiplier, timespan, "2024-01-01", datetime.now().strftime("%Y-%m-%d"))

        if bars:
            data = pd.DataFrame([{
                'timestamp': bar.timestamp,
                'Open': bar.open,
                'High': bar.high,
                'Low': bar.low,
                'Close': bar.close,
                'Volume': bar.volume
            } for bar in bars])

            data['timestamp'] = pd.to_datetime(data['timestamp'], unit='ms')
            data.set_index('timestamp', inplace=True)
            return data

    except Exception as e:
        print(f"Polygon.io error for {symbol}: {e}")

    return pd.DataFrame()

def get_fmp_data(symbol, period='1d', interval='5m'):
    """
    Fetch intraday data from Financial Modeling Prep.
    """
    if not FMP_API_KEY:
        return pd.DataFrame()

    try:
        fmp_symbol = fmp_symbols.get(symbol, symbol)
        url = f"https://financialmodelingprep.com/api/v3/historical-chart/{interval}/{fmp_symbol}?apikey={FMP_API_KEY}"

        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            if data:
                df = pd.DataFrame(data)
                df['date'] = pd.to_datetime(df['date'])
                df.set_index('date', inplace=True)
                df = df.rename(columns={'open': 'Open', 'high': 'High', 'low': 'Low', 'close': 'Close', 'volume': 'Volume'})
                return df[['Open', 'High', 'Low', 'Close', 'Volume']]

    except Exception as e:
        print(f"FMP error for {symbol}: {e}")

    return pd.DataFrame()

def get_twelve_data(symbol, period='1d', interval='5m'):
    """
    Fetch intraday data from Twelve Data.
    """
    if not TWELVE_DATA_API_KEY:
        return pd.DataFrame()

    try:
        td = TDClient(apikey=TWELVE_DATA_API_KEY)
        twelve_symbol = twelve_symbols.get(symbol, symbol)

        # Convert interval to Twelve Data format
        interval_map = {
            '1m': '1min',
            '5m': '5min',
            '15m': '15min',
            '30m': '30min',
            '1h': '1h'
        }
        td_interval = interval_map.get(interval, '5min')

        ts = td.time_series(symbol=twelve_symbol, interval=td_interval, outputsize=100)
        data = ts.as_pandas()

        if not data.empty:
            data = data.rename(columns={
                'open': 'Open',
                'high': 'High',
                'low': 'Low',
                'close': 'Close',
                'volume': 'Volume'
            })
            return data[['Open', 'High', 'Low', 'Close', 'Volume']]

    except Exception as e:
        print(f"Twelve Data error for {symbol}: {e}")

    return pd.DataFrame()

def get_fo_data(symbol='NIFTY', expiry_date=None):
    """
    Fetch Futures and Options (F&O) data from NSE using web scraping.
    """
    try:
        # If no expiry date provided, get the nearest expiry
        if not expiry_date:
            ist = pytz.timezone('Asia/Kolkata')
            today = datetime.now(ist).date()
            # Find next Thursday (typical F&O expiry)
            days_ahead = (3 - today.weekday()) % 7
            if days_ahead == 0:
                days_ahead = 7
            expiry_date = today + timedelta(days=days_ahead)

        # Format expiry date for NSE URL
        expiry_str = expiry_date.strftime('%d%b%Y').upper()

        # NSE F&O data URL
        url = f"https://www.nseindia.com/api/option-chain-indices?symbol={symbol}"

        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'en-US,en;q=0.9',
            'Referer': 'https://www.nseindia.com/option-chain'
        }

        response = requests.get(url, headers=headers, timeout=10)

        if response.status_code == 200:
            data = response.json()

            if 'records' in data and 'data' in data['records']:
                fo_data = []

                for record in data['records']['data']:
                    # Extract relevant F&O data
                    fo_record = {
                        'strikePrice': record.get('strikePrice', 0),
                        'expiryDate': record.get('expiryDate', ''),
                        'CE': {
                            'openInterest': record.get('CE', {}).get('openInterest', 0),
                            'changeinOpenInterest': record.get('CE', {}).get('changeinOpenInterest', 0),
                            'totalTradedVolume': record.get('CE', {}).get('totalTradedVolume', 0),
                            'impliedVolatility': record.get('CE', {}).get('impliedVolatility', 0),
                            'lastPrice': record.get('CE', {}).get('lastPrice', 0),
                            'change': record.get('CE', {}).get('change', 0)
                        },
                        'PE': {
                            'openInterest': record.get('PE', {}).get('openInterest', 0),
                            'changeinOpenInterest': record.get('PE', {}).get('changeinOpenInterest', 0),
                            'totalTradedVolume': record.get('PE', {}).get('totalTradedVolume', 0),
                            'impliedVolatility': record.get('PE', {}).get('impliedVolatility', 0),
                            'lastPrice': record.get('PE', {}).get('lastPrice', 0),
                            'change': record.get('PE', {}).get('change', 0)
                        }
                    }
                    fo_data.append(fo_record)

                return pd.DataFrame(fo_data)

    except Exception as e:
        print(f"Failed to fetch F&O data for {symbol}: {e}")

    return pd.DataFrame()

def auto_update_fo_data(symbols=['NIFTY', 'BANKNIFTY'], update_interval_minutes=15):
    """
    Automatically update F&O data at regular intervals.
    """
    import time
    import threading

    def update_worker():
        while True:
            try:
                print(f"Updating F&O data at {datetime.now()}")

                for symbol in symbols:
                    fo_data = get_fo_data(symbol)
                    if not fo_data.empty:
                        # Save to CSV for persistence
                        filename = f"fo_data_{symbol.lower()}_{datetime.now().strftime('%Y%m%d')}.csv"
                        fo_data.to_csv(filename, index=False)
                        print(f"Updated F&O data for {symbol}: {len(fo_data)} records")

                # Wait for next update
                time.sleep(update_interval_minutes * 60)

            except Exception as e:
                print(f"Error in auto-update: {e}")
                time.sleep(60)  # Wait 1 minute before retrying

    # Start background thread for auto-updates
    update_thread = threading.Thread(target=update_worker, daemon=True)
    update_thread.start()

    print(f"Started auto-update for F&O data (every {update_interval_minutes} minutes)")

def get_realtime_data(symbol, period='1d', interval='5m'):
    """
    Fetch real-time intraday data using multiple sources.
    """
    data = pd.DataFrame()

    # Try yfinance first for all symbols (including Indian markets with .NS symbols)
    try:
        data = yf.download(symbol, period=period, interval=interval, progress=False)
    except Exception as e:
        print(f"yfinance error for {symbol}: {e}")

    # Fallback to mock data
    if data.empty:
        print(f"Using mock data for {symbol}")
        ist = pytz.timezone('Asia/Kolkata')
        end_date = datetime.now(ist)
        start_date = end_date - timedelta(days=1)
        data = generate_mock_data(start_date, end_date, symbol, intraday=True)

    return data
