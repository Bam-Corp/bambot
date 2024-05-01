# bam/cli.py
import click
from .container import create_container, run_container
from .docker_utils import prune_system, list_containers
from .logging import setup_logging
from .metrics import setup_metrics
from .prometheus import setup_prometheus
from .streamlit_dashboard import setup_streamlit_dashboard
import docker
import random
import string


def generate_container_name():
    adjectives = ["happy", "jolly", "brave", "clever", "friendly", "gentle", "kind", "lucky", "silly", "witty"]
    nouns = ["panda", "tiger", "lion", "eagle", "owl", "dolphin", "turtle", "penguin", "koala", "kangaroo"]
    adjective = random.choice(adjectives)
    noun = random.choice(nouns)
    number = ''.join(random.choices(string.digits, k=4))
    return f"{adjective}-{noun}-{number}"

@click.group()
def cli():
    """Bam CLI application"""
    pass

@cli.group()
def create():
    """Create a new container for an AI agent"""
    pass

@create.command()
@click.argument("container_name", default="")
@click.option("--agent-type", default="langchain", help="AI agent type")
@click.option("--env-file", default=".env", help="Path to the .env file")
def container(container_name, agent_type, env_file):
    if not container_name:
        container_name = generate_container_name()
    
    click.echo(click.style(f"Creating container: {container_name}", fg="yellow"))
    
    if click.confirm("Do you want to clean unused docker resources before building the container?"):
        click.echo(click.style("Pruning system resources...", fg="yellow"))
        prune_system()
        click.echo(click.style("System resources pruned successfully!", fg="green"))
    
    create_container(container_name, agent_type, env_file)
    click.echo(click.style(f"Container '{container_name}' created successfully!", fg="green"))

@cli.command()
def run():
    """Run an AI agent container"""
    containers = list_containers()
    if not containers:
        click.echo(click.style("No containers found.", fg="red"))
        return
    
    click.echo(click.style("Available containers:", fg="yellow"))
    for index, container in enumerate(containers, start=1):
        click.echo(f"{index}. {container.name}")
    
    choice = click.prompt("Enter the number of the container to run", type=int)
    if choice < 1 or choice > len(containers):
        click.echo(click.style("Invalid choice.", fg="red"))
        return
    
    container_name = containers[choice - 1].name
    click.echo(click.style(f"Starting container: {container_name}", fg="yellow"))
    try:
        run_container(container_name)
        click.echo(click.style(f"Container '{container_name}' exited.", fg="green"))
    except docker.errors.APIError as e:
        click.echo(click.style(f"Error running container: {str(e)}", fg="red"))

@cli.command()
def dashboard():
    """Launch the Streamlit dashboard"""
    setup_streamlit_dashboard()
    click.echo(click.style("Streamlit dashboard launched successfully!", fg="green"))

@cli.command()
def metrics():
    """Set up metrics for the Bam CLI application"""
    setup_metrics()
    click.echo(click.style("Metrics set up successfully!", fg="green"))

@cli.command()
def prometheus():
    """Set up Prometheus metrics for the Bam CLI application"""
    setup_prometheus()
    click.echo(click.style("Prometheus metrics set up successfully!", fg="green"))

@cli.command()
def logging():
    """Set up logging for the Bam CLI application"""
    setup_logging()
    click.echo(click.style("Logging set up successfully!", fg="green"))

def main():
    cli()

if __name__ == "__main__":
    main()