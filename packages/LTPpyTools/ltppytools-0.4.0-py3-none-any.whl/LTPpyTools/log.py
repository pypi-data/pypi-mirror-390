import logging
import time
import os

class log:
    def __init__(self, log_file="execution_log.txt"):
        self.log_file = log_file
        self._setup_logger()
    @classmethod
    def _setup_logger(self):
        """Initialize the logger to write to both file and console."""
        self.logger = logging.getLogger("DebugTools")
        self.logger.setLevel(logging.DEBUG)

        # Create file handler to log to a file
        file_handler = logging.FileHandler(self.log_file)
        file_handler.setLevel(logging.DEBUG)

        # Create console handler to log to the console
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.DEBUG)

        # Create a formatter and set it for both handlers
        formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)

        # Add handlers to the logger
        self.logger.addHandler(file_handler)
        self.logger.addHandler(console_handler)
    @classmethod
    def log_info(self, message):
        """Log an informational message."""
        self.logger.info(message)
    @classmethod
    def log_warning(self, message):
        """Log a warning message."""
        self.logger.warning(message)
    @classmethod
    def log_error(self, message):
        """Log an error message."""
        self.logger.error(message)
    @classmethod
    def detect_none(self, variable, var_name="Variable"):
        """Check if a variable is None and log an error if it is."""
        if variable is None:
            self.log_error(f"{var_name} is None!")
            return False
        return True
    @classmethod
    def measure_execution_time(self, func, *args, **kwargs):
        """Measure and log the execution time of a function."""
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        elapsed_time = end_time - start_time
        self.log_info(f"Execution time for {func.__name__}: {elapsed_time:.2f} seconds.")
        return result