import pandas as pd
from datetime import datetime

def log_entry(symbol, action, price, reason, stop_loss=None, take_profit=None):
    """
    Log a trade entry to journal.
    """
    entry = {
        'timestamp': datetime.now(),
        'symbol': symbol,
        'action': action,  # Buy/Sell
        'price': price,
        'reason': reason,
        'stop_loss': stop_loss,
        'take_profit': take_profit
    }
    # Append to CSV
    df = pd.DataFrame([entry])
    try:
        existing = pd.read_csv('trading_journal.csv')
        df = pd.concat([existing, df])
    except FileNotFoundError:
        pass
    df.to_csv('trading_journal.csv', index=False)
    return entry

def journal_elements():
    """
    Main elements: Date, Symbol, Action, Entry Price, Exit Price, P/L, Notes.
    """
    elements = ['Date', 'Symbol', 'Action', 'Entry Price', 'Exit Price', 'Stop Loss', 'Take Profit', 'P/L', 'Notes']
    return elements
