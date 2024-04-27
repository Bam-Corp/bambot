# bambot/agent.py
import importlib
import os

class Bot:
    def __init__(self, bot_file):
        self.bot_file = bot_file
        self.bot_module = self.load_bot_module()

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
            return bot_instance.run()
        except Exception as e:
            raise RuntimeError(f"Error running bot: {e}")