# logger.py
import logging
import sys

class Logger:
    def __init__(self):
        self.logger = logging.getLogger("bam-logger")
        self.logger.setLevel(logging.INFO)
        formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s", datefmt='%Y-%m-%d %H:%M:%S')
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(formatter)
        self.logger.addHandler(console_handler)

    def info(self, message):
        self.logger.info(message)

    def error(self, message):
        self.logger.error(message)

    def stop(self):
        for handler in self.logger.handlers:
            handler.close()
        self.logger.removeHandler(handler)
