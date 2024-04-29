# bambot/cli.py
import os
import click
import shutil
from jinja2 import Environment, FileSystemLoader
from pkg_resources import resource_filename
from .docker_utils import DockerManager
from .log_utils import LogManager
from .utils import copy_template
import signal

templates_dir = resource_filename("bambot", "templates")
env = Environment(loader=FileSystemLoader(templates_dir))

def echo_error(message):
    click.echo(click.style(f"Error: {message}", fg="red"), err=True)

def echo_warning(message):
    click.echo(click.style(f"Warning: {message}", fg="yellow"), err=True)

def echo_info(message):
    click.echo(click.style(f"Info: {message}", fg="green"))

def print_bam_ascii_art():
    bam_ascii_art = r"""
  ____                  
 |  _ \                 
 | |_) | __ _ _ __ ___  
 |  _ < / _` | '_ ` _ \ 
 | |_) | (_| | | | | | |
 |____/ \__,_|_| |_| |_|
"""
    click.echo(click.style(bam_ascii_art, fg="green"))

@click.group()
def cli():
    """
    Bambot: A framework for deploying AI agents as Docker containers.

    For more information, visit https://github.com/BamCorp/bambot
    """
    pass

@cli.command()
@click.option("--bot-file", "-b", default="bot.py", help="Name of the bot file (e.g., my_bot.py).")
@click.option("--include-dashboard", "-d", is_flag=True, help="Include the Streamlit dashboard in the Docker image.")
def build(bot_file, include_dashboard):
    """Build and generate deployment files for an AI agent."""
    bot_dir = os.getcwd()
    bot_path = os.path.join(bot_dir, bot_file)

    if not os.path.exists(bot_path):
        echo_warning(f"{bot_file} not found in the current directory.")
        generate_default = click.confirm(
            f"To continue, you must provide a {bot_file} file. Generate a default one?",
            default=True,
        )
        if generate_default:
            copy_template(env, "bot.py.j2", bot_path)
            echo_info(f"Generated default {bot_file} file. Customize it to add your AI agent logic.")
        else:
            echo_info(f"Please create a {bot_file} file and run 'bam build' again.")
            echo_info(f"Refer to GitHub for examples or help: https://github.com/Bam-Corp/bambot")
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
        echo_info("Cleaning up unused containers and images...")
        confirm_cleanup = click.confirm("Remove unused containers and images? [y/N]", default=False)
        if confirm_cleanup:
            docker_manager.cleanup()
        else:
            echo_info("Skipping cleanup operation.")

        echo_info("Generating deployment files...")
        if include_dashboard:
            copy_template(env, "Dockerfile.dashboard.j2", os.path.join(bot_dir, "Dockerfile"))
            include_dashboard_value = "true"
        else:
            copy_template(env, "Dockerfile.lightweight.j2", os.path.join(bot_dir, "Dockerfile"))
            include_dashboard_value = "false"
        copy_template(env, "Procfile.j2", os.path.join(bot_dir, "Procfile"))
        copy_template(env, "agent_readme.md.j2", os.path.join(bot_dir, "agent_readme.md"))
        copy_template(env, "run.sh.j2", os.path.join(bot_dir, "run.sh"), include_dashboard=include_dashboard_value)

        config_file_path = os.path.join(bot_dir, "bambot.config")
        with open(config_file_path, "w") as config_file:
            config_file.write(f"include_dashboard={include_dashboard}")

        echo_info("Building Bam container image...")
        try:
            docker_manager.build_image(include_dashboard)
        except RuntimeError as e:
            echo_error(f"Failed to build Docker image: {str(e)}")
            return

        echo_info("Deployment files prepared successfully!")
        echo_info("You can now run the 'bam run' command to start your AI agent container.")
    except Exception as e:
        echo_error(f"An unexpected error occurred: {str(e)}")

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

    if not docker_manager.is_docker_running():
        echo_error("Docker daemon is not running.")
        echo_warning("Please start the Docker daemon and try again.")
        echo_info("You can check the status of the Docker daemon using the following command:")
        echo_info("  docker info")
        echo_info("If Docker is not installed, you can download it from https://www.docker.com/get-started")
        return

    try:
        print_bam_ascii_art()
        echo_info("Running container...")
        container_name = docker_manager.run_container(bot_path)

        log_manager = LogManager()

        # Read the include_dashboard value from the configuration file
        config_file_path = os.path.join(bot_dir, "bambot.config")
        with open(config_file_path, "r") as config_file:
            config_lines = config_file.readlines()

        include_dashboard = False
        for line in config_lines:
            if line.startswith("include_dashboard="):
                include_dashboard = line.split("=")[1].strip() == "true"
                break

        # Check if the Streamlit dashboard is included
        if include_dashboard:
            echo_info("Streamlit dashboard is available at http://localhost:8501")
            echo_info("Press Ctrl+C to stop the AI agent and Streamlit dashboard.")

        # Run the log manager in a separate thread to simulate real-time log generation
        log_thread = threading.Thread(target=log_manager.process_logs)
        log_thread.start()

        # Wait for the user to press Ctrl+C to stop the container
        try:
            signal.pause()
        except KeyboardInterrupt:
            echo_info("Stopping the AI agent...")

        # Terminate the log thread
        log_thread.join(timeout=5)

        echo_info("AI agent execution completed.")
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
        "run.sh",
        "bambot.config",
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