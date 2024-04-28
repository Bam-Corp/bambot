import importlib
import os
import sys
from io import StringIO
from contextlib import redirect_stdout, redirect_stderr
from .logger import Logger

class Agent:
    def __init__(self, bot_file):
        self.bot_file = bot_file
        self.bot_module = self.load_bot_module()
        self.logger = None

    def load_bot_module(self):
        try:
            bot_dir, bot_filename = os.path.split(self.bot_file)
            bot_module_name, _ = os.path.splitext(bot_filename)
            spec = importlib.util.spec_from_file_location(bot_module_name, self.bot_file)
            bot_module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(bot_module)
            return bot_module
        except Exception as e:
            raise RuntimeError(f"Error loading bot module: {e}")

    def run(self):
        try:
            bot_class = getattr(self.bot_module, "Bot")
            bot_instance = bot_class()

            log_file_path = os.path.join("logs", f"bot_{os.path.splitext(os.path.basename(self.bot_file))[0]}.log")
            self.logger = Logger(log_file_path)

            stdout_buffer = StringIO()
            stderr_buffer = StringIO()

            with redirect_stdout(stdout_buffer), redirect_stderr(stderr_buffer):
                result = bot_instance.run()

            stdout_value = stdout_buffer.getvalue()
            stderr_value = stderr_buffer.getvalue()

            if stdout_value:
                self.logger.write(stdout_value.strip())
                print(stdout_value.strip(), flush=True)
            if stderr_value:
                self.logger.write(stderr_value.strip())
                print(stderr_value.strip(), file=sys.stderr, flush=True)

            self.logger.write(f"Bot result: {result}")
            self.logger.stop()

            return result
        except Exception as e:
            error_message = f"Error running bot: {e}"
            if self.logger:
                self.logger.write(error_message)
            print(error_message, file=sys.stderr, flush=True)
            if self.logger:
                self.logger.stop()
            raise RuntimeError(error_message)