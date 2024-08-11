import MetaTrader5 as mt5
import time

# Initialize MT5 connection
mt5.initialize()

# Define symbol and timeframe
symbols = ["EURUSD", "GBPUSD"]  # Example symbol, replace with your desired one
timeframe = mt5.TIMEFRAME_H4

# Function to get the previous H4 candle
def get_previous_candle():
    rates = mt5.copy_rates_from_pos(symbol, timeframe, 1, 2)
    if rates is None or len(rates) < 2:
        print("Failed to retrieve data")
        return None
    return rates[0]  # Return the second last candle

# Function to place pending orders
def place_orders(high, low):
    # Define the parameters for each order
    orders = [
        {"action": mt5.ORDER_TYPE_BUY_STOP, "price": high},
        {"action": mt5.ORDER_TYPE_SELL_LIMIT, "price": high},
        {"action": mt5.ORDER_TYPE_SELL_STOP, "price": low},
        {"action": mt5.ORDER_TYPE_BUY_LIMIT, "price": low},
    ]
    
    # Place each order
    for order in orders:
        request = {
            "action": mt5.TRADE_ACTION_PENDING,
            "symbol": symbol,
            "volume": 0.1,  # Replace with desired volume
            "type": order["action"],
            "price": order["price"],
            "deviation": 10,  # Slippage tolerance
            "magic": 234000,  # Arbitrary identifier
            "comment": "Automated Order",
            "type_time": mt5.ORDER_TIME_GTC,  # Good till canceled
            "type_filling": mt5.ORDER_FILLING_FOK,  # Fill or kill
        }
        result = mt5.order_send(request)
        if result.retcode != mt5.TRADE_RETCODE_DONE:
            print(f"Order failed, retcode={result.retcode}")
        else:
            print(f"Order placed successfully at {order['price']}")


def check_triggers(symbol, high, low):
    orders = mt5.orders_get(symbol=symbol)
    if orders:
        for order in orders:
            if order.price == high and order.type in [mt5.ORDER_TYPE_BUY_STOP, mt5.ORDER_TYPE_SELL_LIMIT]:
                print(f"High price trade triggered for {symbol}. Deleting low-side orders.")
                delete_orders(symbol)
                break
            elif order.price == low and order.type in [mt5.ORDER_TYPE_SELL_STOP, mt5.ORDER_TYPE_BUY_LIMIT]:
                print(f"Low price trade triggered for {symbol}. Deleting high-side orders.")
                delete_orders(symbol)
                break

# Main loop to check for new candles
last_candle_time = {}


for symbol in symbols:
    last_candle_time[symbol] = None

while True:
    for symbol in symbols:
        candle = get_previous_candle(symbol)
        if candle is None:
            continue

        # Check if there's a new candle
        if last_candle_time[symbol] != candle['time']:
            high = candle['high']
            low = candle['low']
            print(f"New candle detected for {symbol}: High={high}, Low={low}")
            delete_orders(symbol)  # Delete old orders before placing new ones
            place_orders(symbol, high, low)
            last_candle_time[symbol] = candle['time']
        else:
            check_triggers(symbol, candle['high'], candle['low'])

    time.sleep(1)  # Check every minute
