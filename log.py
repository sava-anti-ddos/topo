import logging
import os

class Log:
    def __init__(self):
        self.current_directory = os.getcwd()
        self.log_directory = os.path.join(self.current_directory, 'log')
        # Ensure the log directory exists
        if not os.path.exists(self.log_directory):
            os.makedirs(self.log_directory)
        self.log_file = os.path.join(self.log_directory, 'topo.log')

# Initialize the Log instance to setup the logging directory and file
log_instance = Log()

# Set up logging with the log file path from the Log instance
logging.basicConfig(filename=log_instance.log_file,
                    filemode='a',
                    format='[%(asctime)s]-%(levelname)s-%(name)s: %(message)s',
                    level=logging.INFO)

def get_logger(name):
    return logging.getLogger(name)
