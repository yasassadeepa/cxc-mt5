import MetaTrader5 as mt5
from datetime import datetime, timedelta
import pandas as pd
import time
import schedule

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
    yesterday = datetime.now() - timedelta(1)
    start = datetime(yesterday.year, yesterday.month, yesterday.day, 0, 0)
    end = datetime(yesterday.year, yesterday.month, yesterday.day, 23, 59)

    rates = mt5.copy_rates_range(symbol, mt5.TIMEFRAME_H1, start, end)
    
    if rates is not None and len(rates) > 0:
        df = pd.DataFrame(rates)
        high = df['high'].max()
        low = df['low'].min()
        return high, low
    else:
        return None, None

# Function to get the previous Asia session's high and low prices (2:30 AM to 10:30 AM)
def get_previous_asia_session_high_low(symbol):
    today = datetime.now()
    start = datetime(today.year, today.month, today.day, 2, 30)
    end = datetime(today.year, today.month, today.day, 10, 30)
    
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
        "sl": price - 0.001,  # Initial Stop loss 10 pips below the buy limit price
        "tp": price + 0.006,  # Initial Take profit 60 pips above the buy limit price
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
        "sl": price + 0.001,  # Initial Stop loss 10 pips above the sell limit price
        "tp": price - 0.006,  # Initial Take profit 60 pips below the sell limit price
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
        "sl": price - 0.001,  # Initial Stop loss 10 pips below the buy stop price
        "tp": price + 0.006,  # Initial Take profit 60 pips above the buy stop price
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
        "sl": price + 0.001,  # Initial Stop loss 10 pips above the sell stop price
        "tp": price - 0.006,  # Initial Take profit 60 pips below the sell stop price
        "deviation": 10,
        "magic": 234000,
        "comment": "Python script sell stop",
        "type_time": mt5.ORDER_TIME_GTC,
        "type_filling": mt5.ORDER_FILLING_RETURN,
    }
    result = mt5.order_send(request)
    return result

# Function to adjust stop loss and take profit based on the given conditions
def adjust_sl_tp():
    positions = mt5.positions_get()
    for pos in positions:
        symbol = pos.symbol
        ticket = pos.ticket
        order_type = pos.type
        open_price = pos.price_open
        current_price = mt5.symbol_info_tick(symbol).bid if order_type == mt5.ORDER_TYPE_BUY else mt5.symbol_info_tick(symbol).ask
        profit = (current_price - open_price) if order_type == mt5.ORDER_TYPE_BUY else (open_price - current_price)
        profit_pips = profit * 10000  # Convert profit to pips

        if profit_pips >= 60:
            mt5.order_close(ticket, pos.volume)
        elif profit_pips >= 30:
            sl_price = open_price + 0.0029 if order_type == mt5.ORDER_TYPE_BUY else open_price - 0.0029
            mt5.order_modify(ticket, sl=sl_price)
        elif profit_pips >= 20:
            sl_price = open_price + 0.001 if order_type == mt5.ORDER_TYPE_BUY else open_price - 0.001
            mt5.order_modify(ticket, sl=sl_price)
        elif profit_pips >= 10:
            sl_price = open_price + 0.0005 if order_type == mt5.ORDER_TYPE_BUY else open_price - 0.0005
            mt5.order_modify(ticket, sl=sl_price)

# Function to schedule tasks
def schedule_tasks():
    # Schedule get_previous_day_high_low at 3:00 AM
    schedule.every().day.at("03:00").do(run_get_previous_day_high_low)

    # Schedule get_previous_asia_session_high_low at 10:30 AM
    schedule.every().day.at("10:30").do(run_get_previous_asia_session_high_low)

# Function to run get_previous_day_high_low and place trades
def run_get_previous_day_high_low():
    for pair in currency_pairs:
        high, low = get_previous_day_high_low(pair)
        if high is not None and low is not None:
            # Place orders based on high and low prices
            place_buy_limit(pair, low, 0.1)
            place_sell_limit(pair, high, 0.1)
            place_buy_stop(pair, high, 0.1)
            place_sell_stop(pair, low, 0.1)

# Function to run get_previous_asia_session_high_low and place trades
def run_get_previous_asia_session_high_low():
    for pair in currency_pairs:
        asia_high, asia_low = get_previous_asia_session_high_low(pair)
        if asia_high is not None and asia_low is not None:
            # Place orders based on Asia session high and low prices
            place_buy_limit(pair, asia_low, 0.1)
            place_sell_limit(pair, asia_high, 0.1)
            place_buy_stop(pair, asia_high, 0.1)
            place_sell_stop(pair, asia_low, 0.1)

# Initial schedule tasks
schedule_tasks()

# Run the scheduler in a loop
while True:
    schedule.run_pending()
    time.sleep(1)

# Shutdown MetaTrader5 connection (Note: This part won't be reached in the loop above)
mt5.shutdown()
