# bambot/templates/server.py
from flask import Flask, request, render_template_string, jsonify
from flask_cors import CORS
from agent_runner import Agent

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes
app.name = "Bam AI Agent"
agent = Agent()

@app.route("/")
def index():
    """Render the landing page."""
    template = """
<!DOCTYPE html>
<html>
<head>
    <title>Bam AI Agent</title>
    <style>
        body { font-family: Arial; text-align: center; background-color: #f0f0f0; padding: 20px; }
        h1 { color: #333; font-size: 24px; margin-bottom: 20px; }
        p { color: #666; font-size: 16px; margin-bottom: 10px; }
        code { color: #007bff; }
    </style>
</head>
<body>
    <h1>Bam AI Agent</h1>
    <p>To get started, explore the following endpoints:</p>
    <p><a href="/api/agent/info">Agent Info</a></p>
    <p><a href="/api/agent/health">Agent Health</a></p>
    <p><code>POST /api/agent</code>: Run the AI agent.</p>
</body>
</html>
"""
    return render_template_string(template)

@app.route("/api/agent", methods=["POST"])
def run_agent():
    """Run the AI agent with the provided data."""
    data = request.get_json()
    response = agent.run(data)
    print(f"Agent response: {response}")
    return jsonify(response)

@app.route("/api/agent/info")
def agent_info():
    """Get information about the AI agent."""
    info = {
        "name": agent.__class__.__name__,
        "description": "AI agent powered by Bam framework"
    }
    print(f"Agent info: {info}")
    return jsonify(info)

@app.route("/api/agent/health")
def agent_health():
    """Check the health status of the AI agent."""
    health = {"status": "ok"}
    print(f"Agent health: {health}")
    return jsonify(health)

@app.errorhandler(404)
def not_found(error):
    """Handle 404 - Page Not Found errors."""
    template = """
<!DOCTYPE html>
<html>
<head>
    <title>404 - Page Not Found</title>
    <style>
        body { font-family: Arial; text-align: center; background-color: #f0f0f0; padding: 20px; }
        h1 { color: #333; font-size: 24px; margin-bottom: 20px; }
        p { color: #666; font-size: 16px; margin-bottom: 10px; }
        a { color: #007bff; text-decoration: none; }
        a:hover { text-decoration: underline; }
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
    app.run(host="0.0.0.0", port=1337)