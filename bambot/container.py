# bam/container.py
import os
import click
import pkg_resources
from dotenv import load_dotenv
from .docker_utils import build_image, create_docker_container
import docker


def create_container(container_name, agent_type, env_file=".env"):
    """Create a new container for an AI agent"""
    # Create a new directory for the container
    container_dir = os.path.join(os.getcwd(), container_name)
    os.makedirs(container_dir, exist_ok=True)

    # Generate template project structure
    click.echo(click.style("Generating project structure...", fg="yellow"))
    templates_dir = pkg_resources.resource_filename(__name__, 'templates')
    template_path = os.path.join(templates_dir, "agent_template.py")
    with open(template_path, "r") as f:
        template = f.read()
    template = template.replace("{{AGENT_TYPE}}", agent_type)
    
    # Create the agent file
    agent_file_path = os.path.join(container_dir, f"{agent_type}_agent.py")
    with open(agent_file_path, "w") as f:
        f.write(template)
    
    # Generate requirements.txt based on the agent type
    click.echo(click.style("Generating requirements.txt...", fg="yellow"))
    requirements_template = pkg_resources.resource_string(__name__, "templates/requirements.txt").decode()
    requirements_template = requirements_template.replace("{{AGENT_TYPE}}", agent_type)
    requirements_path = os.path.join(container_dir, "requirements.txt")
    with open(requirements_path, "w") as f:
        f.write(requirements_template)
    
    # Generate Dockerfile
    click.echo(click.style("Generating Dockerfile...", fg="yellow"))
    dockerfile_path = os.path.join(container_dir, "Dockerfile")
    dockerfile_template = pkg_resources.resource_string(__name__, "templates/Dockerfile").decode()
    with open(dockerfile_path, "w") as f:
        f.write(dockerfile_template)
    
    # Copy main.py file
    main_file_path = os.path.join(container_dir, "main.py")
    main_template = pkg_resources.resource_string(__name__, "templates/main.py").decode()
    main_template = main_template.replace("{{AGENT_TYPE}}", agent_type)
    with open(main_file_path, "w") as f:
        f.write(main_template)
    
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
    click.echo(click.style(f"Container '{container_name}' created successfully!", fg="green"))

def run_container(container_name):
    """Run a container for an AI agent"""
    docker_client = docker.from_env()
    container = docker_client.containers.get(container_name)
    
    click.echo(click.style(f"Starting container: {container_name}", fg="yellow"))
    container.start()
    
    # Stream container logs
    click.echo(click.style("Container logs:", fg="yellow"))
    for log in container.logs(stream=True):
        click.echo(log.decode(), nl=False)
    
    container.wait()