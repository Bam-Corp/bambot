import logging
import os
import sys
from logging.handlers import RotatingFileHandler


class Logger:
    def __init__(self, log_file_path, max_bytes=1024 * 1024, backup_count=5):
        os.makedirs(os.path.dirname(log_file_path), exist_ok=True)
        self.logger = logging.getLogger("bam-logger")
        self.logger.setLevel(logging.INFO)
        self.formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")

        self.file_handler = RotatingFileHandler(log_file_path, maxBytes=max_bytes, backupCount=backup_count)
        self.file_handler.setFormatter(self.formatter)
        self.logger.addHandler(self.file_handler)

        self.console_handler = logging.StreamHandler(sys.stdout)
        self.console_handler.setFormatter(self.formatter)
        self.logger.addHandler(self.console_handler)

    def write(self, message):
        self.logger.info(message)
        for handler in self.logger.handlers:
            handler.flush()

    def stop(self):
        for handler in self.logger.handlers:
            handler.close()
            self.logger.removeHandler(handler)