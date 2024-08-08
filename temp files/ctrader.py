import MetaTrader5 as mt5
from datetime import datetime, timedelta
import pandas as pd
import time
import schedule
import json
import logging
from typing import Dict, Tuple, Optional

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def read_config_file(filename: str) -> Dict[str, str]:
    """
    Reads configuration settings from a JSON file.
    
    Args:
        filename (str): Path to the configuration file.
    
    Returns:
        Dict[str, str]: Configuration settings.
    """
    try:
        with open(filename, 'r') as file:
            config = json.load(file)
        return config
    except FileNotFoundError:
        logger.error(f"Configuration file {filename} not found.")
        raise
    except json.JSONDecodeError as e:
        logger.error(f"Error reading configuration file: {e}")
        raise

def get_user_inputs() -> Dict[str, str]:
    """
    Retrieves user inputs, falling back to defaults from the configuration file if not provided.
    
    Returns:
        Dict[str, str]: User inputs and configuration settings.
    """
    config = read_config_file('config.json')

    currency_pairs = input(f"Enter the currency pairs (default: {config['currency_pairs']}): ") or config['currency_pairs']
    currency_pairs = currency_pairs.split(',')
    
    day_high_low_time = input(f"Enter the time to get previous day high/low (default: {config['day_high_low_time']}): ") or config['day_high_low_time']
    
    asia_high_low_time = input(f"Enter the time to get Asia session high/low (default: {config['asia_high_low_time']}): ") or config['asia_high_low_time']
    
    delete_orders_time = input(f"Enter the time to delete pending orders (default: {config['delete_orders_time']}): ") or config['delete_orders_time']
    
    lot_size = input(f"Enter the lot size for orders (default: {config['lot_size']}): ") or config['lot_size']
    lot_size = float(lot_size)

    return {
        "currency_pairs": currency_pairs,
        "day_high_low_time": day_high_low_time,
        "asia_high_low_time": asia_high_low_time,
        "delete_orders_time": delete_orders_time,
        "lot_size": lot_size
    }

def get_previous_day_high_low(symbol: str) -> Tuple[Optional[float], Optional[float]]:
    """
    Retrieves the previous day's high and low prices for a given symbol, accounting for weekends.
    
    Args:
        symbol (str): The trading symbol (e.g., 'EURUSD').
    
    Returns:
        Tuple[Optional[float], Optional[float]]: High and low prices, or (None, None) if no data is retrieved.
    """
    now = datetime.now()
    end = now.replace(hour=5, minute=0, second=0, microsecond=0)
    
    if end.weekday() == 5:  # Saturday
        end -= timedelta(days=1)
    elif end.weekday() == 6:  # Sunday
        end -= timedelta(days=2)

    start = end - timedelta(days=1)
    start = start.replace(hour=5, minute=0, second=0, microsecond=0)
    
    if start.weekday() == 5:  # Saturday
        start -= timedelta(days=1)
    elif start.weekday() == 6:  # Sunday
        start -= timedelta(days=2)

    logger.info(f"Fetching data for {symbol}")

    rates = mt5.copy_rates_range(symbol, mt5.TIMEFRAME_H1, start, end)
    
    if rates is not None and len(rates) > 0:
        df = pd.DataFrame(rates)
        df['time'] = pd.to_datetime(df['time'], unit='s')
        logger.info(df[['time', 'open', 'high', 'low', 'close', 'tick_volume']])
        high = df['high'].max()
        low = df['low'].min()
        return high, low
    else:
        logger.warning(f"No data retrieved for {symbol} in the given date range.")
        return None, None

def get_previous_asia_session_high_low(symbol: str) -> Tuple[Optional[float], Optional[float]]:
    """
    Retrieves the previous Asia session's high and low prices for a given symbol.
    
    Args:
        symbol (str): The trading symbol (e.g., 'EURUSD').
    
    Returns:
        Tuple[Optional[float], Optional[float]]: High and low prices, or (None, None) if no data is retrieved.
    """
    today = datetime.now()
    start = datetime(today.year, today.month, today.day, 5, 0)
    end = datetime(today.year, today.month, today.day, 13, 0)
    logger.info(f"Fetching data for {symbol}")

    rates = mt5.copy_rates_range(symbol, mt5.TIMEFRAME_H1, start, end)

    if rates is not None and len(rates) > 0:
        df = pd.DataFrame(rates)
        df['time'] = pd.to_datetime(df['time'], unit='s')
        logger.info(df[['time', 'open', 'high', 'low', 'close', 'tick_volume']])
        high = df['high'].max()
        low = df['low'].min()
        return high, low
    else:
        logger.warning(f"No data retrieved for {symbol} in the given date range.")
        return None, None

def place_order(request: Dict[str, any]) -> Optional[mt5.TradeResult]:
    """
    Places an order in MetaTrader 5.
    
    Args:
        request (Dict[str, any]): Order request parameters.
    
    Returns:
        Optional[mt5.TradeResult]: The result of the order placement.
    """
    logger.info(f"Placing order: {request}")
    result = mt5.order_send(request)
    if result is None:
        logger.error("Order send failed: result is None")
    else:
        logger.info(f"Order send result: {result}")
    return result

def place_buy_limit(symbol: str, price: float, volume: float) -> Optional[mt5.TradeResult]:
    """
    Places a buy limit order.
    
    Args:
        symbol (str): The trading symbol (e.g., 'EURUSD').
        price (float): The limit price for the buy order.
        volume (float): The volume of the order.
    
    Returns:
        Optional[mt5.TradeResult]: The result of the order placement.
    """
    request = {
        "action": mt5.TRADE_ACTION_PENDING,
        "symbol": symbol,
        "volume": volume,
        "type": mt5.ORDER_TYPE_BUY_LIMIT,
        "price": price,
        "sl": price - 0.001,
        "tp": price + 0.006,
        "deviation": 10,
        "magic": 234000,
        "comment": "CXC Buy Limit",
        "type_time": mt5.ORDER_TIME_GTC,
        "type_filling": mt5.ORDER_FILLING_RETURN,
    }
    return place_order(request)

def place_sell_limit(symbol: str, price: float, volume: float) -> Optional[mt5.TradeResult]:
    """
    Places a sell limit order.
    
    Args:
        symbol (str): The trading symbol (e.g., 'EURUSD').
        price (float): The limit price for the sell order.
        volume (float): The volume of the order.
    
    Returns:
        Optional[mt5.TradeResult]: The result of the order placement.
    """
    request = {
        "action": mt5.TRADE_ACTION_PENDING,
        "symbol": symbol,
        "volume": volume,
        "type": mt5.ORDER_TYPE_SELL_LIMIT,
        "price": price,
        "sl": price + 0.001,
        "tp": price - 0.006,
        "deviation": 10,
        "magic": 234000,
        "comment": "CXC Sell Limit",
        "type_time": mt5.ORDER_TIME_GTC,
        "type_filling": mt5.ORDER_FILLING_RETURN,
    }
    return place_order(request)

def place_buy_stop(symbol: str, price: float, volume: float) -> Optional[mt5.TradeResult]:
    """
    Places a buy stop order.
    
    Args:
        symbol (str): The trading symbol (e.g., 'EURUSD').
        price (float): The stop price for the buy order.
        volume (float): The volume of the order.
    
    Returns:
        Optional[mt5.TradeResult]: The result of the order placement.
    """
    request = {
        "action": mt5.TRADE_ACTION_PENDING,
        "symbol": symbol,
        "volume": volume,
        "type": mt5.ORDER_TYPE_BUY_STOP,
        "price": price,
        "sl": price - 0.001,
        "tp": price + 0.006,
        "deviation": 10,
        "magic": 234000,
        "comment": "CXC Buy Stop",
        "type_time": mt5.ORDER_TIME_GTC,
        "type_filling": mt5.ORDER_FILLING_RETURN,
    }
    return place_order(request)

def place_sell_stop(symbol: str, price: float, volume: float) -> Optional[mt5.TradeResult]:
    """
    Places a sell stop order.
    
    Args:
        symbol (str): The trading symbol (e.g., 'EURUSD').
        price (float): The stop price for the sell order.
        volume (float): The volume of the order.
    
    Returns:
        Optional[mt5.TradeResult]: The result of the order placement.
    """
    request = {
        "action": mt5.TRADE_ACTION_PENDING,
        "symbol": symbol,
        "volume": volume,
        "type": mt5.ORDER_TYPE_SELL_STOP,
        "price": price,
        "sl": price + 0.001,
        "tp": price - 0.006,
        "deviation": 10,
        "magic": 234000,
        "comment": "CXC Sell Stop",
        "type_time": mt5.ORDER_TIME_GTC,
        "type_filling": mt5.ORDER_FILLING_RETURN,
    }
    return place_order(request)

def delete_pending_orders(symbol: str):
    """
    Deletes all pending orders for a given symbol.
    
    Args:
        symbol (str): The trading symbol (e.g., 'EURUSD').
    """
    orders = mt5.orders_get(symbol=symbol)
    if orders is None:
        logger.warning(f"No pending orders found for {symbol}.")
    else:
        for order in orders:
            request = {
                "action": mt5.TRADE_ACTION_REMOVE,
                "order": order.ticket,
            }
            result = place_order(request)
            if result is None:
                logger.error(f"Failed to delete order {order.ticket}")
            else:
                logger.info(f"Deleted order {order.ticket}")

def adjust_sl_tp(symbol: str):
    """
    Adjusts the stop loss (SL) and take profit (TP) for all open positions for a given symbol.
    
    Args:
        symbol (str): The trading symbol (e.g., 'EURUSD').
    """
    positions = mt5.positions_get(symbol=symbol)
    if positions is None:
        logger.warning(f"No positions found for {symbol}.")
    else:
        for position in positions:
            if position.type == mt5.ORDER_TYPE_BUY:
                sl = position.price_open - 0.001
                tp = position.price_open + 0.006
            else:
                sl = position.price_open + 0.001
                tp = position.price_open - 0.006

            request = {
                "action": mt5.TRADE_ACTION_SLTP,
                "position": position.ticket,
                "sl": sl,
                "tp": tp,
            }
            result = place_order(request)
            if result is None:
                logger.error(f"Failed to modify SL/TP for position {position.ticket}")
            else:
                logger.info(f"Modified SL/TP for position {position.ticket}")

def run_get_previous_day_high_low():
    """
    Schedules the retrieval of the previous day's high and low prices for each currency pair.
    """
    for symbol in config["currency_pairs"]:
        high, low = get_previous_day_high_low(symbol)
        if high is not None and low is not None:
            logger.info(f"Previous day high/low for {symbol}: High={high}, Low={low}")

def run_get_previous_asia_session_high_low():
    """
    Schedules the retrieval of the previous Asia session's high and low prices for each currency pair.
    """
    for symbol in config["currency_pairs"]:
        high, low = get_previous_asia_session_high_low(symbol)
        if high is not None and low is not None:
            logger.info(f"Previous Asia session high/low for {symbol}: High={high}, Low={low}")

def run_delete_pending_orders():
    """
    Schedules the deletion of pending orders for each currency pair.
    """
    for symbol in config["currency_pairs"]:
        delete_pending_orders(symbol)

if __name__ == "__main__":
    config = get_user_inputs()
    
    if not mt5.initialize():
        logger.error("initialize() failed, error code =", mt5.last_error())
        quit()
    
    schedule.every().day.at(config["day_high_low_time"]).do(run_get_previous_day_high_low)
    schedule.every().day.at(config["asia_high_low_time"]).do(run_get_previous_asia_session_high_low)
    schedule.every().day.at(config["delete_orders_time"]).do(run_delete_pending_orders)
    
    while True:
        schedule.run_pending()
        time.sleep(1)

    mt5.shutdown()
