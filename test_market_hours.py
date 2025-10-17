# Test market hours check
from data_fetcher import is_market_open
from datetime import datetime
import pytz

# Test market open check
market_open = is_market_open()
print(f'Market open check: {market_open}')

# Get current IST time
ist = pytz.timezone('Asia/Kolkata')
now = datetime.now(ist)
print(f'Current IST time: {now.strftime("%H:%M:%S %A")}')

print('Market hours test complete.')
