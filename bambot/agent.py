# bambot/agent.py
import importlib
import os
import sys
from datetime import datetime
import logging
from io import StringIO
from contextlib import redirect_stdout

def run(bot_file):
    logger = logging.getLogger("agent_logger")
    logger.setLevel(logging.INFO)
    console_handler = logging.StreamHandler(sys.stdout)
    formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s", datefmt='%Y-%m-%d %H:%M:%S')
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    try:
        bot_module_name = os.path.splitext(os.path.basename(bot_file))[0]
        bot_module = importlib.import_module(bot_module_name)
        logger.info(f"Starting AI agent: {bot_module_name}")
        start_time = datetime.now()
        bot_instance = bot_module.Bot()

        # Redirect stdout to capture print statements
        output_buffer = StringIO()
        with redirect_stdout(output_buffer):
            result = bot_instance.run()

        # Log captured output
        output = output_buffer.getvalue()
        if output.strip():  # Only log if there's something to log
            logger.info(output)

        end_time = datetime.now()
        execution_time = end_time - start_time
        logger.info(f"AI agent executed successfully. Execution time: {execution_time}")
        metrics = {
            "start_time": start_time.isoformat(),
            "end_time": end_time.isoformat(),
            "execution_time": str(execution_time),
            "result": result,
        }
        logger.info(f"Metrics: {metrics}")
    except Exception as e:
        logger.error(f"Error running AI agent: {e}")
    finally:
        for handler in logger.handlers:
            handler.close()
        logger.removeHandler(handler)

if __name__ == "__main__":
    bot_file = "bot.py"
    run(bot_file)
