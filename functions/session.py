import MetaTrader5 as mt5
from functions.orders import place_modified_sl
from functions.logger import get_logger

logger = get_logger()

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

        current_sl = pos.sl
        current_tp = pos.tp

        try:
            if profit_pips >= 60:
                close_position(symbol, ticket, volume, current_price, negative_order_type)
            elif profit_pips >= 30:
                sl_price = open_price + 0.0029 if order_type == mt5.ORDER_TYPE_BUY else open_price - 0.0029
                if (order_type == mt5.ORDER_TYPE_BUY and sl_price > current_sl) or (order_type == mt5.ORDER_TYPE_SELL and sl_price < current_sl):
                    place_modified_sl(symbol, ticket, sl_price, current_tp)
            elif profit_pips >= 20:
                sl_price = open_price + 0.001 if order_type == mt5.ORDER_TYPE_BUY else open_price - 0.001
                if (order_type == mt5.ORDER_TYPE_BUY and sl_price > current_sl) or (order_type == mt5.ORDER_TYPE_SELL and sl_price < current_sl):
                    place_modified_sl(symbol, ticket, sl_price, current_tp)
            elif profit_pips >= 10:
                sl_price = open_price + 0.00005 if order_type == mt5.ORDER_TYPE_BUY else open_price - 0.00005
                if (order_type == mt5.ORDER_TYPE_BUY and sl_price > current_sl) or (order_type == mt5.ORDER_TYPE_SELL and sl_price < current_sl):
                    place_modified_sl(symbol, ticket, sl_price, current_tp)
        except Exception as e:
            logger.error(f"Error adjusting SL/TP for {symbol} (ticket: {ticket}): {e}")

# Function to delete pending orders scheduled for 1 AM
def delete_pending_orders_at_1am():
    positions = mt5.positions_get()
    print(positions)
    orders = mt5.orders_get()
    for order in orders:
        close_request = {
            "action": mt5.TRADE_ACTION_REMOVE,
            "order": order.ticket,
            "type_time": mt5.ORDER_TIME_GTC,
            "type_filling": mt5.ORDER_FILLING_IOC,
        }
        result = mt5.order_send(close_request)
