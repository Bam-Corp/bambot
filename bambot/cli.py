# bambot/cli.py
import click
from .project import init_project
from .build import build_project
from .run import run_project
from .utils import setup_logging, echo_info, echo_success, echo_error, confirm_with_style, prune_system

@click.group()
def cli():
    """Bam CLI application"""
    setup_logging()

@cli.command("init")
@click.argument("container_name", required=False)
def init_command(container_name):
    """Initialize a new Bam project"""
    try:
        init_project(container_name)
    except Exception as e:
        echo_error(f"Error initializing project: {e}")

@cli.command("build")
def build_command():
    """Build the Bam project"""
    if confirm_with_style("Do you want to clean up unused Docker resources before building?"):
        prune_system()
        echo_success("Unused Docker resources cleaned up successfully!")

    try:
        build_project()
    except Exception as e:
        echo_error(f"Error building project: {e}")

@cli.command("start")
@click.option("--container-name", "-n", default=None, help="Name of the container to start")
def start_command(container_name):
    """Start the Bam project"""
    try:
        run_project(container_name)
    except Exception as e:
        echo_error(f"Error starting project: {e}")

def main():
    cli()

if __name__ == "__main__":
    main()