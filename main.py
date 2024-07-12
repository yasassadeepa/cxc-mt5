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

# Function to get the previous Asia session's high and low prices
def get_previous_asia_session_high_low(symbol):
    # Define the Asia session time range (00:00 to 09:00 GMT)
    today = datetime.now()
    start = datetime(today.year, today.month, today.day, 0, 0) - timedelta(1)
    end = datetime(today.year, today.month, today.day, 9, 0) - timedelta(1)
    
    # Get the historical data for the previous Asia session
    rates = mt5.copy_rates_range(symbol, mt5.TIMEFRAME_H1, start, end)
    
    if rates is not None and len(rates) > 0:
        df = pd.DataFrame(rates)
        high = df['high'].max()
        low = df['low'].min()
        return high, low
    else:
        return None, None

# Function to place a buy limit order
def place_buy_limit(symbol, price, volume):
    request = {
        "action": mt5.TRADE_ACTION_PENDING,
        "symbol": symbol,
        "volume": volume,
        "type": mt5.ORDER_TYPE_BUY_LIMIT,
        "price": price,
        "sl": price - 0.001,  # Stop loss 10 pips below the buy limit price
        "tp": price + 0.001,  # Take profit 10 pips above the buy limit price
        "deviation": 10,
        "magic": 234000,
        "comment": "Python script buy limit",
        "type_time": mt5.ORDER_TIME_GTC,
        "type_filling": mt5.ORDER_FILLING_RETURN,
    }
    result = mt5.order_send(request)
    return result

# Function to place a sell limit order
def place_sell_limit(symbol, price, volume):
    request = {
        "action": mt5.TRADE_ACTION_PENDING,
        "symbol": symbol,
        "volume": volume,
        "type": mt5.ORDER_TYPE_SELL_LIMIT,
        "price": price,
        "sl": price + 0.001,  # Stop loss 10 pips above the sell limit price
        "tp": price - 0.001,  # Take profit 10 pips below the sell limit price
        "deviation": 10,
        "magic": 234000,
        "comment": "Python script sell limit",
        "type_time": mt5.ORDER_TIME_GTC,
        "type_filling": mt5.ORDER_FILLING_RETURN,
    }
    result = mt5.order_send(request)
    return result

# Function to place a buy stop order
def place_buy_stop(symbol, price, volume):
    request = {
        "action": mt5.TRADE_ACTION_PENDING,
        "symbol": symbol,
        "volume": volume,
        "type": mt5.ORDER_TYPE_BUY_STOP,
        "price": price,
        "sl": price - 0.001,  # Stop loss 10 pips below the buy stop price
        "tp": price + 0.001,  # Take profit 10 pips above the buy stop price
        "deviation": 10,
        "magic": 234000,
        "comment": "Python script buy stop",
        "type_time": mt5.ORDER_TIME_GTC,
        "type_filling": mt5.ORDER_FILLING_RETURN,
    }
    result = mt5.order_send(request)
    return result

# Function to place a sell stop order
def place_sell_stop(symbol, price, volume):
    request = {
        "action": mt5.TRADE_ACTION_PENDING,
        "symbol": symbol,
        "volume": volume,
        "type": mt5.ORDER_TYPE_SELL_STOP,
        "price": price,
        "sl": price + 0.001,  # Stop loss 10 pips above the sell stop price
        "tp": price - 0.001,  # Take profit 10 pips below the sell stop price
        "deviation": 10,
        "magic": 234000,
        "comment": "Python script sell stop",
        "type_time": mt5.ORDER_TIME_GTC,
        "type_filling": mt5.ORDER_FILLING_RETURN,
    }
    result = mt5.order_send(request)
    return result

# Get high and low prices for all currency pairs and place orders
volume = 0.1  # Define the trade volume
results = {}
for pair in currency_pairs:
    # Get previous day's high and low prices
    high, low = get_previous_day_high_low(pair)
    if high is not None and low is not None:
        results[pair] = {'Day_High': high, 'Day_Low': low}

        # Place Buy Limit order at previous day's low price
        buy_limit_result = place_buy_limit(pair, low, volume)
        print(f"Buy Limit for {pair} at {low}: {buy_limit_result}")

        # Place Sell Limit order at previous day's high price
        sell_limit_result = place_sell_limit(pair, high, volume)
        print(f"Sell Limit for {pair} at {high}: {sell_limit_result}")

        # Place Buy Stop order at previous day's high price
        buy_stop_result = place_buy_stop(pair, high, volume)
        print(f"Buy Stop for {pair} at {high}: {buy_stop_result}")

        # Place Sell Stop order at previous day's low price
        sell_stop_result = place_sell_stop(pair, low, volume)
        print(f"Sell Stop for {pair} at {low}: {sell_stop_result}")
    else:
        results[pair] = {'Day_High': 'N/A', 'Day_Low': 'N/A'}

    # Get previous Asia session's high and low prices
    asia_high, asia_low = get_previous_asia_session_high_low(pair)
    if asia_high is not None and asia_low is not None:
        results[pair].update({'Asia_High': asia_high, 'Asia_Low': asia_low})

        # Place Buy Limit order at previous Asia session's low price
        buy_limit_result = place_buy_limit(pair, asia_low, volume)
        print(f"Buy Limit for {pair} at {asia_low} (Asia session): {buy_limit_result}")

        # Place Sell Limit order at previous Asia session's high price
        sell_limit_result = place_sell_limit(pair, asia_high, volume)
        print(f"Sell Limit for {pair} at {asia_high} (Asia session): {sell_limit_result}")

        # Place Buy Stop order at previous Asia session's high price
        buy_stop_result = place_buy_stop(pair, asia_high, volume)
        print(f"Buy Stop for {pair} at {asia_high} (Asia session): {buy_stop_result}")

        # Place Sell Stop order at previous Asia session's low price
        sell_stop_result = place_sell_stop(pair, asia_low, volume)
        print(f"Sell Stop for {pair} at {asia_low} (Asia session): {sell_stop_result}")
    else:
        results[pair].update({'Asia_High': 'N/A', 'Asia_Low': 'N/A'})

# Print the results
for pair, prices in results.items():
    print(f"{pair} - Day High: {prices['Day_High']}, Day Low: {prices['Day_Low']}, Asia High: {prices['Asia_High']}, Asia Low: {prices['Asia_Low']}")

# Shutdown MetaTrader5 connection
mt5.shutdown()
