import MetaTrader5 as mt5

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
        "comment": "CXC Buy Limit",
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
        "comment": "CXC Sell Limit",
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
        "comment": "CXC Buy Stop",
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
        "comment": "CXC Sell Stop",
        "type_time": mt5.ORDER_TIME_GTC,
        "type_filling": mt5.ORDER_FILLING_RETURN,
    }
    result = mt5.order_send(request)
    return result

def place_modified_sl(symbol, ticket, sl, tp):
    request = {
        "action": mt5.TRADE_ACTION_SLTP,
        "symbol": symbol,
        "position": ticket,
        "sl": sl,
        "tp": tp,
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