from typing import Tuple, List
from functions.configs import read_config_file

def get_user_inputs() -> Tuple[List[str], str, str, str, float]:
    config = read_config_file('config/config.json')

    currency_pairs = input(f"Enter the currency pairs (default: {', '.join(config['currency_pairs'])}): ") or ','.join(config['currency_pairs'])
    currency_pairs = [pair.strip() for pair in currency_pairs.split(',')]
    
    day_high_low_time = input(f"Enter the time to get previous day high/low (default: {config['day_high_low_time']}): ") or config['day_high_low_time']
    
    asia_high_low_time = input(f"Enter the time to get Asia session high/low (default: {config['asia_high_low_time']}): ") or config['asia_high_low_time']
    
    delete_orders_time = input(f"Enter the time to delete pending orders (default: {config['delete_orders_time']}): ") or config['delete_orders_time']
    
    lot_size = input(f"Enter the lot size for orders (default: {config['lot_size']}): ") or config['lot_size']
    lot_size = float(lot_size)

    return currency_pairs, day_high_low_time, asia_high_low_time, delete_orders_time, lot_size

    return currency_pairs, day_high_low_time, asia_high_low_time, delete_orders_time, lot_size
