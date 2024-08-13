import MetaTrader5 as mt5
from datetime import datetime
import time

# Initialize the MT5 terminal
if not mt5.initialize():
    print("initialize() failed, error code =", mt5.last_error())
    quit()

# Dictionary to store pending orders' tickets
pending_orders_dict = {}

def get_previous_h4_candle(symbol):
    rates = mt5.copy_rates_from_pos(symbol, mt5.TIMEFRAME_M5, 0, 2)
    if rates is None or len(rates) < 2:
        print(f"No H4 candle data available for {symbol}")
        return None
    
    previous_candle = rates[-2]
    return previous_candle['high'], previous_candle['low']

def monitor_new_candle(symbol):
    last_candle = get_latest_candle(symbol)
    if last_candle is None:
        return None, None
    
    last_time = last_candle['time']
    
    while True:
        latest_candle = get_latest_candle(symbol)
        if latest_candle is None:
            continue
        
        if latest_candle['time'] > last_time:
            print(f"New candle detected for {symbol} at {datetime.utcfromtimestamp(latest_candle['time'])}")
            last_time = latest_candle['time']
            previous_candle = last_candle
            return previous_candle['high'], previous_candle['low']
        
        time.sleep(1)

def get_latest_candle(symbol):
    rates = mt5.copy_rates_from_pos(symbol, mt5.TIMEFRAME_M5, 0, 1)
    if rates is None or len(rates) < 1:
        print(f"No H4 candle data available for {symbol}")
        return None
    
    latest_candle = rates[0]
    return latest_candle

def delete_pending_orders(symbol, tickets=None):
    orders = mt5.orders_get(symbol=symbol)
    if orders is None:
        print(f"No pending orders to delete for {symbol}")
        return
    
    for order in orders:
        if tickets is None or order.ticket in tickets:
            close_request = {
                "action": mt5.TRADE_ACTION_REMOVE,
                "order": order.ticket,
                "type_time": mt5.ORDER_TIME_GTC,
                "type_filling": mt5.ORDER_FILLING_IOC,
            }
            result = mt5.order_send(close_request)
            if result.retcode != mt5.TRADE_RETCODE_DONE:
                print(f"Failed to delete order {order.ticket} for {symbol}: {result.retcode}")
            else:
                print(f"Deleted order {order.ticket} for {symbol}")

def place_pending_order(symbol, price, volume, order_type):
    request = {
        "action": mt5.TRADE_ACTION_PENDING,
        "symbol": symbol,
        "volume": volume,
        "type": order_type,
        "price": price,
        "sl": price - 0.0005 if order_type == mt5.ORDER_TYPE_BUY_STOP or order_type == mt5.ORDER_TYPE_BUY_LIMIT else price + 0.0005,
        "tp": price + 0.005 if order_type == mt5.ORDER_TYPE_BUY_STOP or order_type == mt5.ORDER_TYPE_BUY_LIMIT else price - 0.005,
        "deviation": 10,
        "magic": 234000,
        "comment": "Automated Order",
        "type_time": mt5.ORDER_TIME_GTC,
        "type_filling": mt5.ORDER_FILLING_RETURN,
    }
    result = mt5.order_send(request)
    if result.retcode != mt5.TRADE_RETCODE_DONE:
        print(f"Failed to place {order_type} order at {price} for {symbol}: {result.retcode}")
        return None
    else:
        print(f"Placed {order_type} order at {price} for {symbol}")
        return result.order

def monitor_triggered_orders(symbol):
    while True:
        positions = mt5.positions_get(symbol=symbol)
        if positions:
            for pos in positions:
                print(f"Trade triggered for {symbol} with ticket {pos.ticket}. Deleting corresponding pending orders.")
                for tickets in pending_orders_dict.get(symbol, []):
                    if pos.ticket in tickets:
                        delete_pending_orders(symbol, tickets)
                        break
                manage_trailing_stop(pos)  # Manage the trailing stop for the position
                return
        
        time.sleep(1)

def manage_trailing_stop(position):
    symbol = position.symbol
    ticket = position.ticket
    order_type = position.type
    open_price = position.price_open
    volume = position.volume

    sl = position.sl
    tp = position.tp

    current_price = mt5.symbol_info_tick(symbol).bid if order_type == mt5.ORDER_TYPE_BUY else mt5.symbol_info_tick(symbol).ask
    profit = (current_price - open_price) if order_type == mt5.ORDER_TYPE_BUY else (open_price - current_price)
    profit_pips = profit * 10000

    negative_order_type = mt5.ORDER_TYPE_SELL if order_type == mt5.ORDER_TYPE_BUY else mt5.ORDER_TYPE_BUY

    if profit_pips >= 25:
        new_sl = open_price + 0.0024 if order_type == mt5.ORDER_TYPE_BUY else open_price - 0.0024
        if new_sl != sl:
            update_sl(position, new_sl)
    
    elif profit_pips >= 20:
        new_sl = open_price + 0.0005 if order_type == mt5.ORDER_TYPE_BUY else open_price - 0.0005
        if new_sl != sl:
            update_sl(position, new_sl)
    
    elif profit_pips >= 5:
        new_sl = open_price + 0.00005 if order_type == mt5.ORDER_TYPE_BUY else open_price - 0.00005
        if new_sl != sl:
            update_sl(position, new_sl)

def update_sl(position, new_sl):
    request = {
        "action": mt5.TRADE_ACTION_SLTP,
        "position": position.ticket,
        "sl": new_sl,
        "tp": position.tp,
    }
    result = mt5.order_send(request)
    if result.retcode != mt5.TRADE_RETCODE_DONE:
        print(f"Failed to modify SL for position {position.ticket}: {result.retcode}")
    else:
        print(f"SL for position {position.ticket} modified to {new_sl}")

# Main process
symbols = ["EURUSD"]
volume = 10.0

for symbol in symbols:
    high, low = get_previous_h4_candle(symbol)
    
    if high and low:
        delete_pending_orders(symbol)  # Delete all previous pending orders
        
        # Place all pending orders and store their tickets
        tickets_group = [
            place_pending_order(symbol, high, volume, mt5.ORDER_TYPE_SELL_LIMIT),
            place_pending_order(symbol, high, volume, mt5.ORDER_TYPE_BUY_STOP),
            place_pending_order(symbol, low, volume, mt5.ORDER_TYPE_BUY_LIMIT),
            place_pending_order(symbol, low, volume, mt5.ORDER_TYPE_SELL_STOP)
        ]
        
        # Store the tickets in a list for the current symbol
        if symbol in pending_orders_dict:
            pending_orders_dict[symbol].append(tickets_group)
        else:
            pending_orders_dict[symbol] = [tickets_group]

    print(f"Previous H4 candle for {symbol} - High: {high}, Low: {low}")

while True:
    for symbol in symbols:
        monitor_triggered_orders(symbol)
        high, low = monitor_new_candle(symbol)
        
        if high and low:
            delete_pending_orders(symbol)  # Delete all old pending orders when new candle forms
            
            # Place all pending orders and store their tickets
            tickets_group = [
                place_pending_order(symbol, high, volume, mt5.ORDER_TYPE_SELL_LIMIT),
                place_pending_order(symbol, high, volume, mt5.ORDER_TYPE_BUY_STOP),
                place_pending_order(symbol, low, volume, mt5.ORDER_TYPE_BUY_LIMIT),
                place_pending_order(symbol, low, volume, mt5.ORDER_TYPE_SELL_STOP)
            ]
            
            # Store the tickets in a list for the current symbol
            if symbol in pending_orders_dict:
                pending_orders_dict[symbol].append(tickets_group)
            else:
                pending_orders_dict[symbol] = [tickets_group]

            print(f"New candle formed. Previous H4 candle for {symbol} - High: {high}, Low: {low}")

# Shutdown the MT5 terminal
mt5.shutdown()
