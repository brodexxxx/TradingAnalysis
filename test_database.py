import sqlite3
import json

# Check database logging
conn = sqlite3.connect('trading_analysis.db')
cursor = conn.cursor()

cursor.execute('SELECT COUNT(*) FROM trading_records')
count = cursor.fetchone()[0]
print(f'Total records in database: {count}')

if count > 0:
    cursor.execute('SELECT symbol, prediction, indicators FROM trading_records ORDER BY id DESC LIMIT 5')
    records = cursor.fetchall()
    print('Recent records:')
    for record in records:
        symbol, prediction, indicators = record
        indicators_dict = json.loads(indicators)
        rsi_val = indicators_dict.get('rsi', 'N/A')
        print(f'  {symbol}: {prediction} - RSI: {rsi_val}')

conn.close()
print('Database logging test complete.')
