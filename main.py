import MetaTrader5 as mt5
from datetime import datetime, timedelta
import pandas as pd

# Initialize the MetaTrader5 package
if not mt5.initialize():
    print("initialize() failed")
    mt5.shutdown()

# Define the list of currency pairs you are interested in
currency_pairs = [
    'EURUSD', 'GBPUSD', 'USDJPY', 'USDCHF', 'AUDUSD', 'USDCAD', 'NZDUSD'
]

# Function to get the previous day's high and low prices
def get_previous_day_high_low(symbol):
    # Get yesterday's date
    yesterday = datetime.now() - timedelta(1)
    start = datetime(yesterday.year, yesterday.month, yesterday.day, 0, 0)
    end = datetime(yesterday.year, yesterday.month, yesterday.day, 23, 59)

    # Get the historical data for the previous day
    rates = mt5.copy_rates_range(symbol, mt5.TIMEFRAME_H1, start, end)
    
    if rates is not None and len(rates) > 0:
        df = pd.DataFrame(rates)
        high = df['high'].max()
        low = df['low'].min()
        return high, low
    else:
        return None, None

# Get high and low prices for all currency pairs
results = {}
for pair in currency_pairs:
    high, low = get_previous_day_high_low(pair)
    if high is not None and low is not None:
        results[pair] = {'High': high, 'Low': low}
    else:
        results[pair] = {'High': 'N/A', 'Low': 'N/A'}

# Print the results
for pair, prices in results.items():
    print(f"{pair} - High: {prices['High']}, Low: {prices['Low']}")

# Shutdown MetaTrader5 connection
mt5.shutdown()
