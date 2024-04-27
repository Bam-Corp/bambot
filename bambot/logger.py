# bambot/logger.py
import logging
import sys
import datetime

class Logger:
    def __init__(self):
        self.logger = logging.getLogger("bam-logger")
        self.logger.setLevel(logging.INFO)
        self.formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")

    def start(self):
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        log_file = f"/app/output/bot_{timestamp}.log"
        self.file_handler = logging.FileHandler(log_file)
        self.file_handler.setFormatter(self.formatter)
        self.logger.addHandler(self.file_handler)
        self.console_handler = logging.StreamHandler(sys.stdout)
        self.console_handler.setFormatter(self.formatter)
        self.logger.addHandler(self.console_handler)
        self.logger.info("Bot execution started.")

    def write(self, message):
        self.logger.info(message)

    def stop(self):
        self.logger.info("Bot execution completed.")
        self.logger.removeHandler(self.file_handler)
        self.logger.removeHandler(self.console_handler)
        self.file_handler.close()