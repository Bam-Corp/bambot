# bambot/templates/server.py
import logging
from colorama import Fore, Style
from flask import Flask, render_template_string, jsonify, request
from flask_cors import CORS
import datetime
from dotenv import load_dotenv
load_dotenv()

from agent_runner import Agent

# Custom logging formatter for color-coded logs
class ColoredFormatter(logging.Formatter):
    def __init__(self, msg, use_color=True):
        super().__init__(msg)
        self.use_color = use_color

    def format(self, record):
        level_color = {
            "DEBUG": Fore.CYAN,
            "INFO": Fore.GREEN,
            "WARNING": Fore.YELLOW,
            "ERROR": Fore.RED,
            "CRITICAL": Fore.RED + Style.BRIGHT
        }

        timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        level_name = record.levelname
        message = record.getMessage()

        if self.use_color and level_name in level_color:
            level_name = level_color[level_name] + level_name + Style.RESET_ALL
            message = level_color[record.levelname] + message + Style.RESET_ALL

        log_line = f"{Fore.MAGENTA}[{timestamp}]{Style.RESET_ALL} {Fore.BLUE}[{level_name}]{Style.RESET_ALL} {message}"
        return log_line

# Setup Flask application
app = Flask(__name__)
app.name = "Bam AI Agent"
CORS(app)  # Enable CORS for all routes
agent = Agent()

# Logger setup
logger = logging.getLogger("bam_logger")
logger.setLevel(logging.DEBUG)
console_handler = logging.StreamHandler()
console_handler.setFormatter(ColoredFormatter("[%(levelname)s] %(message)s"))
logger.addHandler(console_handler)

# Routes
@app.route("/")
def index():
    """Serve the landing page with helpful links and commands."""
    template = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Bam AI Agent</title>
        <style>
            body { font-family: Arial, sans-serif; text-align: center; padding: 20px; }
            h1 { color: #333; display: flex; align-items: center; justify-content: center; }
            p { margin-bottom: 10px; }
            code { color: #007bff; font-weight: bold; }
        </style>
    </head>
    <body>
        <h1>🚀 Bam AI Agent</h1>
        <p>To get started, explore the following endpoints:</p>
        <p><a href="/api/agent/info">Agent Info</a></p>
        <p><a href="/api/agent/health">Agent Health</a></p>
        <p><code>curl -X POST -d '{"input": "whats up?"}' localhost:1337/api/agent</code></p>
    </body>
    </html>
    """
    return render_template_string(template)

@app.route("/api/agent", methods=["POST"])
def run_agent():
    """Run the AI agent and return its response."""
    input_data = request.get_json(force=True)
    response = agent.run(input_data)
    logger.info(f"Agent response: {response}")
    return jsonify(response)

@app.route("/api/agent/info")
def agent_info():
    """Return information about the AI agent."""
    info = {"name": agent.__class__.__name__, "description": "AI agent powered by Bam framework"}
    logger.info(f"Agent info: {info}")
    return jsonify(info)

@app.route("/api/agent/health")
def agent_health():
    """Check the health of the AI agent."""
    health = {"status": "ok"}
    logger.info(f"Agent health: {health}")
    return jsonify(health)

@app.errorhandler(404)
def not_found(error):
    """Serve a custom 404 error page."""
    template = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>404 - Page Not Found</title>
        <style>
            body { font-family: Arial, sans-serif; text-align: center; padding: 20px; }
            h1 { color: #333; }
        </style>
    </head>
    <body>
        <h1>404 - Page Not Found</h1>
        <p>The requested page could not be found.</p>
        <p><a href="/">Go back to the homepage</a></p>
    </body>
    </html>
    """
    return render_template_string(template), 404

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=1337, debug=True)