# bambot/log_utils.py
import os
from .logger import Logger

class LogManager:
    def __init__(self):
        self.logger = Logger()

    def process_logs(self, log_file):
        if not os.path.exists(log_file):
            raise FileNotFoundError(f"Log file not found: {log_file}")

        self.logger.start()
        try:
            with open(log_file, "r") as file:
                for line in file:
                    self.logger.write(line.strip())
        except Exception as e:
            self.logger.write(f"Error processing logs: {e}")
        finally:
            self.logger.stop()