import MetaTrader5 as mt5
from datetime import datetime, timedelta
import pandas as pd
import time
import schedule

# Initialize the MetaTrader5 package
if not mt5.initialize():
    print("initialize() failed")
    mt5.shutdown()
    exit()

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
    if positions is None:
        print("No positions found")
        return

    for pos in positions:
        symbol = pos.symbol
        ticket = pos.ticket
        order_type = pos.type
        open_price = pos.price_open
        volume = pos.volume

        current_price = mt5.symbol_info_tick(symbol).bid if order_type == mt5.ORDER_TYPE_BUY else mt5.symbol_info_tick(symbol).ask
        profit = (current_price - open_price) if order_type == mt5.ORDER_TYPE_BUY else (open_price - current_price)
        profit_pips = profit * 10000  # Convert profit to pips

        order_type = mt5.ORDER_TYPE_SELL if order_type == mt5.ORDER_TYPE_BUY else mt5.ORDER_TYPE_BUY

        print(f"Closing position: symbol={symbol}, ticket={ticket}, volume={volume}, current_price={current_price}, order_type={order_type}")
        result = close_position(symbol, ticket, volume, current_price, order_type)
        if result is None or result.retcode != mt5.TRADE_RETCODE_DONE:
            print(f"Failed to close position: {result}")
        else:
            print(f"Position closed: {result}")

adjust_sl_tp()
