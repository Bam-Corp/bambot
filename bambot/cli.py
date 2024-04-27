# bambot/cli.py
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

def print_bam_ascii_art():
    bam_ascii_art = r"""
   _____   ____  ____   ____
  / ___/  / __ \/ __ \ / __ \
  \__ \  / /_/ / /_/ / /_/ /
 ___/ /  \____/ ____/ ____/
/____/      /_/     /_/
"""
    click.echo(click.style(bam_ascii_art, fg="light_green"))

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
    bot_dir = os.getcwd()
    bot_path = os.path.join(bot_dir, bot_file)

    if not os.path.exists(bot_path):
        echo_error(f"{bot_file} not found in the current directory.")
        return

    docker_manager = DockerManager()

    if not docker_manager.is_docker_running():
        echo_error("Docker daemon is not running.")
        echo_warning("Please start the Docker daemon and try again.")
        echo_info("You can check the status of the Docker daemon using the following command:")
        echo_info("  docker info")
        echo_info("If Docker is not installed, you can download it from https://www.docker.com/get-started")
        return

    try:
        echo_info("Cleaning up unused Docker resources...")
        confirm_cleanup = click.confirm("Remove unused Docker resources (e.g., containers and images)? Skip this step with 'No'", default=False)
        if confirm_cleanup:
            docker_manager.cleanup()
        else:
            echo_info("Skipping Docker cleanup operation.")

        echo_info("Generating deployment files...")
        copy_template(env, "Dockerfile.j2", os.path.join(bot_dir, "Dockerfile"))
        copy_template(env, "Procfile.j2", os.path.join(bot_dir, "Procfile"))
        copy_template(env, "agent_readme.md.j2", os.path.join(bot_dir, "agent_readme.md"))

        echo_info("Building Docker image...")
        docker_manager.build_image()

        echo_info("Deployment files generated successfully.")
    except Exception as e:
        echo_error(str(e))

@cli.command()
@click.option("--bot-file", "-b", default="bot.py", help="Name of the bot file (e.g., my_bot.py).")
def run(bot_file):
    """Run an AI agent locally."""
    bot_dir = os.getcwd()
    bot_path = os.path.join(bot_dir, bot_file)

    if not os.path.exists(bot_path):
        echo_error(f"{bot_file} not found in the current directory.")
        return

    docker_manager = DockerManager()
    log_manager = LogManager()

    if not docker_manager.is_docker_running():
        echo_error("Docker daemon is not running.")
        echo_warning("Please start the Docker daemon and try again.")
        echo_info("You can check the status of the Docker daemon using the following command:")
        echo_info("  docker info")
        echo_info("If Docker is not installed, you can download it from https://www.docker.com/get-started")
        return

    try:
        print_bam_ascii_art()
        echo_info("Running Bam container...")
        container_id = docker_manager.run_container(bot_path)

        log_file = f"/app/output/bot_{container_id}.log"
        echo_info("Processing logs...")
        log_manager.process_logs(log_file)

        echo_info("AI agent execution completed successfully.")
    except Exception as e:
        echo_error(str(e))

@cli.command()
def clean():
    """Clean up generated deployment files."""
    bot_dir = os.getcwd()
    files_to_remove = [
        "Dockerfile",
        "Procfile",
        "agent_readme.md",
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