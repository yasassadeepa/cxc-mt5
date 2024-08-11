import MetaTrader5 as mt5
from functions.scheduler import schedule_tasks, run_scheduler
from functions.utils import get_user_inputs
from functions.logger import get_logger

logger = get_logger()

def main():
    # Initialize the MetaTrader5 package
    if not mt5.initialize():
        logger.error("Initialize() failed")
        mt5.shutdown()
        return  # Exit the function if initialization fails

    # Get user inputs
    currency_pairs, day_high_low_time, asia_high_low_time, delete_orders_time, lot_size = get_user_inputs()

    # Initial schedule tasks
    schedule_tasks(currency_pairs, day_high_low_time, asia_high_low_time, delete_orders_time, lot_size)
    
    # Run the scheduler
    run_scheduler()

if __name__ == "__main__":
    main()
