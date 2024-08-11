import json
from typing import Dict
from functions.logger import get_logger

logger = get_logger()

# Function to read configuration from a text file
def read_config_file(filename: str) -> Dict[str, str]:
    config = {}
    try:
        with open(filename, 'r') as file:
            config = json.load(file)
    except FileNotFoundError:
        logger.error(f"Configuration file {filename} not found.")
    except json.JSONDecodeError as e:
        logger.error(f"Error decoding JSON from file: {e}")
    except Exception as e:
        logger.error(f"Error reading configuration file: {e}")
    return config