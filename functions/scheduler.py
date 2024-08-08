import schedule
import time
from functions.trading import run_get_previous_day_high_low, run_get_previous_asia_session_high_low
from functions.session import delete_pending_orders_at_1am, adjust_sl_tp
from functions.logger import get_logger

logger = get_logger()

# Function to schedule tasks
def schedule_tasks(currency_pairs:list, day_high_low_time:str, asia_high_low_time:str, delete_orders_time:str, lot_size:float):
    # Schedule get_previous_day_high_low at the specified time
    schedule.every().day.at(day_high_low_time).do(lambda: run_get_previous_day_high_low(currency_pairs, lot_size))

    # Schedule get_previous_asia_session_high_low at the specified time
    schedule.every().day.at(asia_high_low_time).do(lambda: run_get_previous_asia_session_high_low(currency_pairs, lot_size))

    # Schedule delete_pending_orders_at_1am at the specified time
    schedule.every().day.at(delete_orders_time).do(delete_pending_orders_at_1am)

def run_scheduler():
    try:
        while True:
            adjust_sl_tp()
            schedule.run_pending()
            time.sleep(1)
    except KeyboardInterrupt:
        logger.info("Execution interrupted by user.")
    finally:
        # Shutdown MetaTrader5 connection
        mt5.shutdown()