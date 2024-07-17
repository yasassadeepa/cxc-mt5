import MetaTrader5 as mt5
from datetime import datetime, timedelta
import pandas as pd
import time
import schedule

# Initialize the MetaTrader5 package
if not mt5.initialize():
    print("initialize() failed")
    mt5.shutdown()

# Function to read configuration from a text file
def read_config_file(filename):
    config = {}
    with open(filename, 'r') as file:
        lines = file.readlines()
        for line in lines:
            key, value = line.strip().split('=')
            config[key] = value
    return config

# Function to get user inputs with defaults from config file
def get_user_inputs():
    global currency_pairs, day_high_low_time, asia_high_low_time, delete_orders_time, lot_size

    config = read_config_file('config.txt')

    currency_pairs = input(f"Enter the currency pairs (default: {config['currency_pairs']}): ") or config['currency_pairs']
    currency_pairs = currency_pairs.split(',')
    
    day_high_low_time = input(f"Enter the time to get previous day high/low (default: {config['day_high_low_time']}): ") or config['day_high_low_time']
    
    asia_high_low_time = input(f"Enter the time to get Asia session high/low (default: {config['asia_high_low_time']}): ") or config['asia_high_low_time']
    
    delete_orders_time = input(f"Enter the time to delete pending orders (default: {config['delete_orders_time']}): ") or config['delete_orders_time']
    
    lot_size = input(f"Enter the lot size for orders (default: {config['lot_size']}): ") or config['lot_size']
    lot_size = float(lot_size)

# Function to get the previous day's high and low prices, considering weekends
def get_previous_day_high_low(symbol):
    now = datetime.now()
    end = now.replace(hour=5, minute=00, second=0, microsecond=0)
    if now < end:
        end -= timedelta(days=1)
    
    # Skip weekends
    while end.weekday() > 4:  # 5: Saturday, 6: Sunday
        end -= timedelta(days(1))

    start = end - timedelta(days=1)
    start = start.replace(hour=5, minute=00, second=0, microsecond=0)
    
    # Skip weekends
    while start.weekday() > 4:  # 5: Saturday, 6: Sunday
        start -= timedelta(days=1)

    print(f"Fetching data for {symbol}")

    rates = mt5.copy_rates_range(symbol, mt5.TIMEFRAME_H1, start, end)
    
    if rates is not None and len(rates) > 0:
        df = pd.DataFrame(rates)
        df['time'] = pd.to_datetime(df['time'], unit='s')
        print(df[['time', 'open', 'high', 'low', 'close', 'tick_volume']])
        high = df['high'].max()
        low = df['low'].min()
        return high, low
    else:
        print(f"No data retrieved for {symbol} in the given date range.")
        return None, None

# Function to get the previous Asia session's high and low prices (2:30 AM to 10:30 AM)
def get_previous_asia_session_high_low(symbol):
    today = datetime.now()
    start = datetime(today.year, today.month, today.day, 5, 00)
    end = datetime(today.year, today.month, today.day, 13, 00)
    print(f"Fetching data for {symbol}")

    rates = mt5.copy_rates_range(symbol, mt5.TIMEFRAME_H1, start, end)

    if rates is not None and len(rates) > 0:
        df = pd.DataFrame(rates)
        df['time'] = pd.to_datetime(df['time'], unit='s')
        print(df[['time', 'open', 'high', 'low', 'close', 'tick_volume']])
        high = df['high'].max()
        low = df['low'].min()
        return high, low
    else:
        print(f"No data retrieved for {symbol} in the given date range.")
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

def place_modified_sl(symbol, ticket, sl):
    request = {
        "action": mt5.TRADE_ACTION_SLTP,
        "symbol": symbol,
        "position": ticket,
        "sl": sl,
        "magic": 234000,
    }
    result = mt5.order_send(request)
    return result

def close_position(symbol, ticket, volume, current_price, order_type):
    request = {
        "action": mt5.TRADE_ACTION_DEAL,
        "symbol": symbol,
        "position": ticket,
        "volume": volume,
        "price": current_price,
        "type": order_type,
        "deviation": 10,
        "magic": 234000,
        "type_time": mt5.ORDER_TIME_GTC,
        "type_filling": mt5.ORDER_FILLING_IOC,
    }
    print(f"Sending order request: {request}")
    result = mt5.order_send(request)
    if result is None:
        print("Order send failed: result is None")
    else:
        print(f"Order send result: {result}")
    return result

# Function to adjust stop loss and take profit based on the given conditions
def adjust_sl_tp():
    positions = mt5.positions_get()
    for pos in positions:
        symbol = pos.symbol
        ticket = pos.ticket
        order_type = pos.type
        open_price = pos.price_open
        volume = pos.volume

        current_price = mt5.symbol_info_tick(symbol).bid if order_type == mt5.ORDER_TYPE_BUY else mt5.symbol_info_tick(symbol).ask
        profit = (current_price - open_price) if order_type == mt5.ORDER_TYPE_BUY else (open_price - current_price)
        profit_pips = profit * 10000  # Convert profit to pips
        negative_order_type = mt5.ORDER_TYPE_SELL if order_type == mt5.ORDER_TYPE_BUY else mt5.ORDER_TYPE_BUY

        if profit_pips >= 60:
            close_position(symbol, ticket, volume, current_price, negative_order_type)
        elif profit_pips >= 30:
            sl_price = open_price + 0.0029 if order_type == mt5.ORDER_TYPE_BUY else open_price - 0.0029
            place_modified_sl(symbol, ticket, sl_price)
        elif profit_pips >= 20:
            sl_price = open_price + 0.001 if order_type == mt5.ORDER_TYPE_BUY else open_price - 0.001
            place_modified_sl(symbol, ticket, sl_price)
        elif profit_pips >= 10:
            sl_price = open_price + 0.00005 if order_type == mt5.ORDER_TYPE_BUY else open_price - 0.00005
            place_modified_sl(symbol, ticket, sl_price)

# Function to delete pending orders scheduled for 1 AM
def delete_pending_orders_at_1am():
    orders = mt5.orders_get()
    for order in orders:
        if order.type_time == mt5.ORDER_TIME_SPECIFIED and order.time_setup.hour == 1:
            mt5.order_delete(order.ticket)

# Function to schedule tasks
def schedule_tasks():
    # Schedule get_previous_day_high_low at the specified time
    schedule.every().day.at(day_high_low_time).do(run_get_previous_day_high_low)

    # Schedule get_previous_asia_session_high_low at the specified time
    schedule.every().day.at(asia_high_low_time).do(run_get_previous_asia_session_high_low)

    # Schedule delete_pending_orders_at_1am at the specified time
    schedule.every().day.at(delete_orders_time).do(delete_pending_orders_at_1am)

    # Schedule adjust_sl_tp to run every minute
    schedule.every().minute.do(adjust_sl_tp)

# Function to run get_previous_day_high_low and place trades
def run_get_previous_day_high_low():
    for pair in currency_pairs:
        symbol_info = mt5.symbol_info_tick(pair)
        if symbol_info is not None:
            current_price = symbol_info.bid
            day_high, day_low = get_previous_day_high_low(pair)
            if day_high is not None and day_low is not None:
                if day_low <= current_price <= day_high:
                    place_buy_limit(pair, day_low, lot_size)
                    place_sell_limit(pair, day_high, lot_size)
                    place_buy_stop(pair, day_high, lot_size)
                    place_sell_stop(pair, day_low, lot_size)
                else:
                    print(f"Current price ({current_price}) is outside previous day's range for {pair}. No orders placed.")
            else:
                print(f"Failed to retrieve previous day's high and low for {pair}.")
        else:
            print(f"Failed to retrieve symbol info for {pair}")

# Function to run get_previous_asia_session_high_low and place trades
def run_get_previous_asia_session_high_low():
    for pair in currency_pairs:
        symbol_info = mt5.symbol_info_tick(pair)
        if symbol_info is not None:
            current_price = symbol_info.bid
            asia_high, asia_low = get_previous_asia_session_high_low(pair)
            if asia_high is not None and asia_low is not None:
                if asia_low <= current_price <= asia_high:
                    place_buy_limit(pair, asia_low, lot_size)
                    place_sell_limit(pair, asia_high, lot_size)
                    place_buy_stop(pair, asia_high, lot_size)
                    place_sell_stop(pair, asia_low, lot_size)
                else:
                    print(f"Current price ({current_price}) is outside Asia session's range for {pair}. No orders placed.")
            else:
                print(f"Failed to retrieve previous Asia session's high and low for {pair}.")
        else:
            print(f"Failed to retrieve symbol info for {pair}")

# Get user inputs
get_user_inputs()

# Initial schedule tasks
schedule_tasks()

# Run the scheduler in a loop
while True:
    schedule.run_pending()
    time.sleep(1)

# Shutdown MetaTrader5 connection (Note: This part won't be reached in the loop above)
mt5.shutdown()
