import MetaTrader5 as mt5
from datetime import datetime
import time

# Initialize the MT5 terminal
if not mt5.initialize():
    print("initialize() failed, error code =", mt5.last_error())
    quit()

pending_orders_dict = {}
latest_candles_dict = {}
pending_orders_list = []
first_cond = False

symbols = ["EURUSD", "AUDUSD", "GBPUSD"]
volume = 20.0
timeframe = mt5.TIMEFRAME_H4

def get_previous_candle(symbol, timeframe):
    rates = mt5.copy_rates_from_pos(symbol, timeframe, 0, 2)
    if rates is None or len(rates) < 2:
        print(f"No candle data available for {symbol}")
        return None, None, None
    
    previous_candle = rates[-2]

    candle_time = datetime.fromtimestamp(previous_candle['time'])
    candle_hour = candle_time.hour

    if candle_hour == 1:
        return None, None, None

    return previous_candle['high'], previous_candle['low'], previous_candle['time']

def check_is_new_candle(symbol, previous_time):
    global latest_candles_dict

    if symbol in latest_candles_dict:
        if latest_candles_dict[symbol] < previous_time:
            latest_candles_dict[symbol] = previous_time

            return True
        else:
            return False
    else:
        latest_candles_dict[symbol] = previous_time
        return True

def delete_pending_orders(symbol, tickets=None):
    orders = mt5.orders_get(symbol=symbol)
    if not orders:
        print(f"No pending orders to delete for {symbol}")
        return

    if tickets:
        for order in orders:
            if order.ticket in tickets:
                run_delete_order(order.ticket, symbol)       
    else:
        for order in orders:
            run_delete_order(order.ticket, symbol)
    return

def remove_item_and_clean(symbol, item_to_remove):
    global pending_orders_dict

    if symbol not in pending_orders_dict:
        return

    # Clean up the pending orders dictionary
    new_pending_orders_dict = []

    for trade_group in pending_orders_dict[symbol]:
        new_trade_group = []

        for trade_list in trade_group:
            # Remove specific items and also filter out lists that contain only None
            new_trade_list = [item for item in trade_list if item != item_to_remove]
            if new_trade_list and any(val is not None for val in new_trade_list):
                new_trade_group.append(new_trade_list)

        if new_trade_group:
            new_pending_orders_dict.append(new_trade_group)

    if new_pending_orders_dict:
        pending_orders_dict[symbol] = new_pending_orders_dict
    else:
        del pending_orders_dict[symbol]

def run_delete_order(ticket, symbol):
    close_request = {
        "action": mt5.TRADE_ACTION_REMOVE,
        "order": ticket,
        "type_time": mt5.ORDER_TIME_GTC,
        "type_filling": mt5.ORDER_FILLING_IOC,
    }

    result = mt5.order_send(close_request)
    if result.retcode != mt5.TRADE_RETCODE_DONE:
        print(f"Failed to delete order {ticket} for {symbol}: {result.retcode}")
    else:
        remove_item_and_clean(symbol, ticket)
        print(f"Successfully deleted order {ticket} for {symbol}")
    return

def place_pending_order(symbol, price, volume, order_type):
    global first_cond
    
    if order_type == mt5.ORDER_TYPE_BUY_STOP:
        comment = "M2 Buy Stop"
    elif order_type == mt5.ORDER_TYPE_BUY_LIMIT:
        comment = "M2 Buy Limit"
    elif order_type == mt5.ORDER_TYPE_SELL_LIMIT:
        comment = "M2 Sell Limit"
    else:
        comment = "M2 Sell Stop"

    request = {
        "action": mt5.TRADE_ACTION_PENDING,
        "symbol": symbol,
        "volume": volume,
        "type": order_type,
        "price": price,
        "sl": price - 0.0005 if order_type in [mt5.ORDER_TYPE_BUY_STOP, mt5.ORDER_TYPE_BUY_LIMIT] else price + 0.0005,
        "tp": price + 0.005 if order_type in [mt5.ORDER_TYPE_BUY_STOP, mt5.ORDER_TYPE_BUY_LIMIT] else price - 0.005,
        "deviation": 10,
        "magic": 234000,
        "comment": comment,
        "type_time": mt5.ORDER_TIME_GTC,
        "type_filling": mt5.ORDER_FILLING_RETURN,
    }
    result = mt5.order_send(request)
    if result.retcode != mt5.TRADE_RETCODE_DONE:
        print(f"Failed to place {order_type} order at {price} for {symbol}: {result.retcode}")
        return None
    else:
        first_cond = True
        pending_orders_list.append(result.order)
        print(f"Placed {order_type} order at {price} for {symbol}")
        return result.order

def remove_opposite_trades(symbol, ticket, order_type1, order_type2):
    global pending_orders_dict

    if symbol not in pending_orders_dict:
        return

    deletable_oposit_tickets = []
    condition = False

    for trade_group in pending_orders_dict[symbol]:
        for trade_list in trade_group:
            if ticket in trade_list:
                condition = True
                remove_item_and_clean(symbol, ticket)
                target_trade_group = trade_group
                break
        if condition:
            break

    if condition:
        target_tickets = []
        for new_trade_list in target_trade_group:
            for target_ticket in new_trade_list:
                target_tickets.append(target_ticket)

        delete_pending_orders(symbol, target_tickets)            
        return

def remove_orders_for_positions(symbol):
    positions = mt5.positions_get(symbol=symbol)
    if positions:
        active_trades = {pos.ticket: pos.comment for pos in positions}
        for ticket, trade_type in active_trades.items():
            if trade_type in ["M2 Sell Limit", "M2 Buy Stop"]:
                remove_opposite_trades(symbol, ticket, "M2 Buy Limit", "M2 Sell Stop")
            elif trade_type in ["M2 Buy Limit", "M2 Sell Stop"]:
                remove_opposite_trades(symbol, ticket, "M2 Sell Limit", "M2 Buy Stop")

def update_sl(position, new_sl):
    request = {
        "action": mt5.TRADE_ACTION_SLTP,
        "position": position.ticket,
        "sl": new_sl,
        "tp": position.tp,
    }
    result = mt5.order_send(request)
    if result.retcode != mt5.TRADE_RETCODE_DONE:
        if result.retcode != 10025:
            print(f"Failed to modify SL for position {position.ticket}: {result.retcode}")
    else:
        print(f"SL for position {position.ticket} modified to {new_sl}")

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
        if (order_type == mt5.ORDER_TYPE_BUY and new_sl > sl) or (order_type == mt5.ORDER_TYPE_SELL and new_sl < sl):
            update_sl(position, new_sl)
    
    elif profit_pips >= 20:
        new_sl = open_price + 0.0005 if order_type == mt5.ORDER_TYPE_BUY else open_price - 0.0005
        if (order_type == mt5.ORDER_TYPE_BUY and new_sl > sl) or (order_type == mt5.ORDER_TYPE_SELL and new_sl < sl):
            update_sl(position, new_sl)
    
    elif profit_pips >= 5:
        new_sl = open_price + 0.00005 if order_type == mt5.ORDER_TYPE_BUY else open_price - 0.00005
        if (order_type == mt5.ORDER_TYPE_BUY and new_sl > sl) or (order_type == mt5.ORDER_TYPE_SELL and new_sl < sl):
            update_sl(position, new_sl)

def monitor_triggered_orders(symbol):
    positions = mt5.positions_get(symbol=symbol)
    if positions:
        for pos in positions:
            manage_trailing_stop(pos)
    
    return

while True:
    for symbol in symbols:
        pre_high, pre_low, pre_time = get_previous_candle(symbol, timeframe)

        if pre_high is None or pre_low is None or pre_time is None:
            continue

        new_candle = check_is_new_candle(symbol, pre_time)
        if new_candle:
            if first_cond:
                delete_pending_orders(symbol, pending_orders_list)

            high_trades = []
            low_trades = []

            sell_limit = place_pending_order(symbol, pre_high, volume, mt5.ORDER_TYPE_SELL_LIMIT)
            high_trades.append(sell_limit)
            buy_stop = place_pending_order(symbol, pre_high, volume, mt5.ORDER_TYPE_BUY_STOP)
            high_trades.append(buy_stop)
            buy_limit = place_pending_order(symbol, pre_low, volume, mt5.ORDER_TYPE_BUY_LIMIT)
            low_trades.append(buy_limit)
            sell_stop = place_pending_order(symbol, pre_low, volume, mt5.ORDER_TYPE_SELL_STOP)
            low_trades.append(sell_stop)
                
            trade_group = [high_trades, low_trades]

            if symbol in pending_orders_dict:
                pending_orders_dict[symbol].append(trade_group)
            else:
                pending_orders_dict[symbol] = [trade_group]

        remove_orders_for_positions(symbol)
        monitor_triggered_orders(symbol)
    
    pending_orders_list.clear()
    first_cond = False
