# Function to read configuration from a text file
def read_config_file(filename):
    config = {}
    with open(filename, 'r') as file:
        lines = file.readlines()
        for line in lines:
            key, value = line.strip().split('=')
            config[key] = value
    return config
