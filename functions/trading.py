import MetaTrader5 as mt5
from typing import Tuple, Optional
from datetime import datetime, timedelta
import pandas as pd
from functions.orders import place_buy_limit, place_sell_limit, place_buy_stop, place_sell_stop

# Function to get the previous day's high and low prices, considering weekends
def get_previous_day_high_low(symbol: str) -> Tuple[Optional[float], Optional[float]]:
    now = datetime.now() # 03:00
    end = now.replace(hour=5, minute=00, second=0, microsecond=0) #18 05:00
    # if now < end:
    #     end -= timedelta(days=1)
    
    # Skip weekends
    if end.weekday() == 5:  # Saturday
        end -= timedelta(days=1)
    elif end.weekday() == 6:  # Sunday
        end -= timedelta(days=2)

    start = end - timedelta(days=1) # 17 05:00
    start = start.replace(hour=5, minute=00, second=0, microsecond=0)
    
    # Skip weekends
    if start.weekday() == 5:  # Saturday
        start -= timedelta(days=1)
    elif start.weekday() == 6:  # Sunday
        start -= timedelta(days=2)

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

# Function to run get_previous_day_high_low and place trades
def run_get_previous_day_high_low(currency_pairs, lot_size):
    for pair in currency_pairs:
        symbol_info = mt5.symbol_info_tick(pair)
        if symbol_info is not None:
            current_price = symbol_info.bid
            day_high, day_low = get_previous_day_high_low(pair)
            if day_high is not None and day_low is not None:
                if current_price < day_high:
                    place_sell_limit(pair, day_high, lot_size)
                    place_buy_stop(pair, day_high, lot_size)
                else:
                    print(f"Current price ({current_price}) is outside previous day's high for {pair}. No orders placed.")
                if current_price > day_low:
                    place_buy_limit(pair, day_low, lot_size)
                    place_sell_stop(pair, day_low, lot_size)
                else:
                    print(f"Current price ({current_price}) is outside previous day's low for {pair}. No orders placed.")
            else:
                print(f"Failed to retrieve previous day's high and low for {pair}.")
        else:
            print(f"Failed to retrieve symbol info for {pair}")

# Function to run get_previous_asia_session_high_low and place trades
def run_get_previous_asia_session_high_low(currency_pairs, lot_size):
    for pair in currency_pairs:
        symbol_info = mt5.symbol_info_tick(pair)
        if symbol_info is not None:
            current_price = symbol_info.bid
            asia_high, asia_low = get_previous_asia_session_high_low(pair)
            if asia_high is not None and asia_low is not None:
                if current_price < asia_high:
                    place_sell_limit(pair, asia_high, lot_size)
                    place_buy_stop(pair, asia_high, lot_size)
                else:
                    print(f"Current price ({current_price}) is outside Asia session's high for {pair}. No orders placed.")
                if current_price > asia_low:
                    place_buy_limit(pair, asia_low, lot_size)
                    place_sell_stop(pair, asia_low, lot_size)
                else:
                    print(f"Current price ({current_price}) is outside Asia session's low for {pair}. No orders placed.")
            else:
                print(f"Failed to retrieve previous Asia session's high and low for {pair}.")
        else:
            print(f"Failed to retrieve symbol info for {pair}")
