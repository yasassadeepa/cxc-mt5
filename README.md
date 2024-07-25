
# MetaTrader 5 Trading Bot

This Python script is a trading bot for MetaTrader 5 (MT5), designed to automate the process of placing limit and stop orders based on the previous day's high/low prices and the previous Asia session's high/low prices. The bot also adjusts stop-loss (SL) and take-profit (TP) dynamically based on profit conditions and deletes pending orders at a specified time.

## Features

- Retrieves previous day's high and low prices.
- Retrieves previous Asia session's high and low prices.
- Places buy/sell limit and stop orders based on these prices.
- Adjusts SL and TP dynamically based on profit conditions.
- Deletes pending orders at a specified time.
- Uses a configuration file (`config.txt`) for default settings.
- Interactive user input for customization.

## Requirements

- Python 3.x
- MetaTrader5 package
- pandas
- schedule

## Installation

1. Clone this repository:

```sh
git https://github.com/yasassadeepa/cxc-mt5.git
cd cxc-mt5
```

2. Install the required Python packages:

```sh
pip install MetaTrader5 pandas schedule
```

## Configuration

Create a `config.txt` file in the same directory as your script with the following format:

```
currency_pairs=EURUSD,GBPUSD
day_high_low_time=03:00
asia_high_low_time=10:30
delete_orders_time=01:00
lot_size=0.1
```

## Usage

1. Initialize MetaTrader 5:

Make sure your MetaTrader 5 application is running and you are logged in to your trading account.

2. Run the script:

```sh
python trading_bot.py
```

3. Follow the prompts to enter or confirm the currency pairs, times, and lot size.

## Code Overview

### Initialization

```python
if not mt5.initialize():
    print("initialize() failed")
    mt5.shutdown()
```

### Configuration

The script reads the configuration from `config.txt`:

```python
def read_config_file(filename):
    # code to read config file
```

### User Input

The script prompts the user for inputs, with defaults from the config file:

```python
def get_user_inputs():
    # code to get user inputs
```

### Retrieve Prices

Functions to get the previous day's high/low and the previous Asia session's high/low prices:

```python
def get_previous_day_high_low(symbol):
    # code to get previous day high/low

def get_previous_asia_session_high_low(symbol):
    # code to get previous Asia session high/low
```

### Place Orders

Functions to place various types of orders:

```python
def place_buy_limit(symbol, price, volume):
    # code to place buy limit order

def place_sell_limit(symbol, price, volume):
    # code to place sell limit order

def place_buy_stop(symbol, price, volume):
    # code to place buy stop order

def place_sell_stop(symbol, price, volume):
    # code to place sell stop order
```

### Adjust SL/TP

Function to adjust stop-loss and take-profit based on profit conditions:

```python
def adjust_sl_tp():
    # code to adjust SL and TP
```

### Delete Pending Orders

Function to delete pending orders at the specified time:

```python
def delete_pending_orders_at_1am():
    # code to delete pending orders
```

### Scheduling Tasks

The script schedules tasks using the `schedule` library:

```python
def schedule_tasks():
    # code to schedule tasks
```

### Main Loop

The main loop runs the scheduler and adjusts SL/TP:

```python
while True:
    adjust_sl_tp()
    schedule.run_pending()
    time.sleep(1)
```

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
