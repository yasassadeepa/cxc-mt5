from typing import Tuple, Dict
from functions.configs import read_config_file

def get_user_inputs() -> Tuple[list, str, str, str, float]:
    config = read_config_file('config/config.txt')

    currency_pairs = input(f"Enter the currency pairs (default: {config['currency_pairs']}): ") or config['currency_pairs']
    currency_pairs = currency_pairs.split(',')
    
    day_high_low_time = input(f"Enter the time to get previous day high/low (default: {config['day_high_low_time']}): ") or config['day_high_low_time']
    
    asia_high_low_time = input(f"Enter the time to get Asia session high/low (default: {config['asia_high_low_time']}): ") or config['asia_high_low_time']
    
    delete_orders_time = input(f"Enter the time to delete pending orders (default: {config['delete_orders_time']}): ") or config['delete_orders_time']
    
    lot_size = input(f"Enter the lot size for orders (default: {config['lot_size']}): ") or config['lot_size']
    lot_size = float(lot_size)

    return currency_pairs, day_high_low_time, asia_high_low_time, delete_orders_time, lot_size
