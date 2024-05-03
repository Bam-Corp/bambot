# container.py
import os
import click
import pkg_resources
from dotenv import load_dotenv
from .docker_utils import build_image, create_docker_container
import docker
import signal
import sys

TEMPLATE_FILES = [
    "agent_template.py", "Dockerfile", "agent_runner.py", "requirements.txt", "server.py"
]

def create_app(container_name, agent_type, env_file=".env"):
    """Create a new app for an AI agent"""
    # Create a new directory for the container
    container_dir = os.path.join(os.getcwd(), container_name)
    os.makedirs(container_dir, exist_ok=True)

    # Copy template files to the container directory
    click.echo(click.style("Generating project structure...", fg="yellow"))
    templates_dir = pkg_resources.resource_filename(__name__, 'templates')
    for filename in TEMPLATE_FILES:
        template_path = os.path.join(templates_dir, filename)
        with open(template_path, "r") as f:
            template = f.read()
        template = template.replace("{{AGENT_TYPE}}", agent_type)
        file_path = os.path.join(container_dir, filename.replace("agent_template.py", f"{agent_type}_agent.py"))
        with open(file_path, "w") as f:
            f.write(template)

    # Load environment variables from .env file
    env_file_path = os.path.join(container_dir, env_file)
    load_dotenv(env_file_path)
    env_vars = {key: value for key, value in os.environ.items()}

    # Build Docker image
    click.echo(click.style("Building Docker image...", fg="yellow"))
    build_image(container_dir)
    click.echo(click.style("Docker image built successfully!", fg="green"))

    # Create Docker container
    click.echo(click.style("Creating Docker container...", fg="yellow"))
    create_docker_container(container_name, env_vars)

def run_app(container_name):
    """Run an app for an AI agent"""
    docker_client = docker.from_env()
    container = docker_client.containers.get(container_name)
    click.echo(click.style(f"Starting container: {container_name}", fg="yellow"))
    container.start()

    # Stream container logs
    click.echo(click.style("Container logs:", fg="yellow"))

    # Set up signal handler for SIGINT (Ctrl+C)
    def signal_handler(sig, frame):
        click.echo(click.style("\nStopping container...", fg="yellow"))
        container.stop()
        click.echo(click.style("Container stopped.", fg="green"))
        sys.exit(0)

    signal.signal(signal.SIGINT, signal_handler)

    try:
        for log in container.logs(stream=True, follow=True):
            try:
                log_str = log.decode('utf-8')
                click.echo(log_str, nl=False)
            except UnicodeDecodeError:
                click.echo(f"Error decoding log line: {log}", nl=False)
    except KeyboardInterrupt:
        # Handle KeyboardInterrupt separately
        signal_handler(signal.SIGINT, None)