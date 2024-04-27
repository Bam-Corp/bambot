import os
import click
import shutil
from jinja2 import Environment, PackageLoader
from tqdm import tqdm
from .docker_utils import DockerManager
from .log_utils import LogManager
from .utils import copy_template

env = Environment(loader=PackageLoader("bambot", "templates"))

def echo_error(message):
    click.echo(click.style(f"Error: {message}", fg="red"), err=True)

def echo_warning(message):
    click.echo(click.style(f"Warning: {message}", fg="yellow"), err=True)

def echo_info(message):
    click.echo(click.style(f"Info: {message}", fg="green"))

@click.group()
def cli():
    """
    Bambot: A framework for deploying AI agents as Docker containers.

    For more information, visit https://github.com/BamCorp/bambot
    """
    pass

@cli.command()
@click.option("--bot-file", "-b", default="bot.py", help="Name of the bot file (e.g., my_bot.py).")
def build(bot_file):
    """Build and generate deployment files for an AI agent."""
    # ... (existing build command code) ...

@cli.command()
@click.option("--bot-file", "-b", default="bot.py", help="Name of the bot file (e.g., my_bot.py).")
def run(bot_file):
    """Run an AI agent locally."""
    # ... (existing run command code) ...

@cli.command()
def clean():
    """Clean up generated deployment files."""
    bot_dir = os.getcwd()
    files_to_remove = [
        "Dockerfile",
        "Procfile",
        "README.md",
        "output.zip",
    ]

    for file_name in files_to_remove:
        file_path = os.path.join(bot_dir, file_name)
        if os.path.exists(file_path):
            try:
                if os.path.isfile(file_path):
                    os.remove(file_path)
                    echo_info(f"Removed {file_name}")
                else:
                    shutil.rmtree(file_path)
                    echo_info(f"Removed directory {file_name}")
            except Exception as e:
                echo_error(f"Error removing {file_name}: {str(e)}")

    echo_info("Clean up completed successfully.")

if __name__ == "__main__":
    cli()