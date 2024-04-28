import os
from .logger import Logger

class LogManager:
    def __init__(self, log_file_path):
        self.logger = Logger(log_file_path)

    def process_logs(self):
        try:
            with open(self.logger.file_handler.baseFilename, "r") as file:
                for line in file:
                    self.logger.write(line.strip())
        except Exception as e:
            self.logger.write(f"Error processing logs: {e}")
        finally:
            self.logger.stop()