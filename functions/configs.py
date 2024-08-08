from typing import Dict

# Function to read configuration from a text file
def read_config_file(filename: str) -> Dict[str, str]:
    config = {}
    try:
        with open(filename, 'r') as file:
            lines = file.readlines()
            for line in lines:
                key, value = line.strip().split('=')
                config[key] = value
    except FileNotFoundError:
        print(f"Configuration file {filename} not found.")
    except Exception as e:
        print(f"Error reading configuration file: {e}")
    return config
