# bambot/app.py
import os
from flask import Flask
from flask_reloader import run_with_reloader
from agent_runner import Agent

agent = Agent()

app = Flask(__name__)
app.config.from_envvar('APP_CONFIG_FILE')

@app.route("/")
def index():
    return "Hello, World!"

@app.route("/api/agent", methods=["POST"])
def run_agent():
    # Your agent logic here
    pass

if __name__ == "__main__":
    run_with_reloader(app, extra_files=[os.path.join(os.getcwd(), 'app.py')])