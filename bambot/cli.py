import os
import click
import shutil
import jinja2
import pkg_resources
import subprocess
import signal
import threading
from .log_utils import LogManager

# Load templates from the installed package
templates_loader = jinja2.PackageLoader("bambot", "templates")
env = jinja2.Environment(loader=templates_loader)

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

    For more information, visit https://github.com/Bam-Corp/bambot
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
            default_bot_template = env.get_template("bot.py.j2")
            with open(bot_path, "w") as f:
                f.write(default_bot_template.render())
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
            dockerfile_template = env.get_template("Dockerfile.dashboard.j2")
        else:
            dockerfile_template = env.get_template("Dockerfile.lightweight.j2")

        with open(os.path.join(bot_dir, "Dockerfile"), "w") as f:
            f.write(dockerfile_template.render(bot_file=os.path.basename(bot_file)))

        copy_template(env, "Procfile.j2", os.path.join(bot_dir, "Procfile"))
        copy_template(env, "agent_readme.md.j2", os.path.join(bot_dir, "agent_readme.md"))
        copy_template(env, "run.sh.j2", os.path.join(bot_dir, "run.sh"), include_dashboard=str(include_dashboard))

        config_file_path = os.path.join(bot_dir, "bambot.config")
        with open(config_file_path, "w") as config_file:
            config_file.write(f"include_dashboard={include_dashboard}")

        echo_info("Building Bam container image...")
        try:
            docker_manager.build_image(bot_file, bot_dir, include_dashboard)
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

def copy_template(env, template_name, output_path, **kwargs):
    template = env.get_template(template_name)
    with open(output_path, "w") as f:
        f.write(template.render(**kwargs))

class DockerManager:
    def __init__(self):
        self.container_name_prefix = "bam-agent-"

    def is_docker_running(self):
        try:
            subprocess.run(["docker", "info"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
            return True
        except subprocess.CalledProcessError:
            return False

    def build_image(self, bot_file, bot_dir, include_dashboard):
        try:
            build_context_dir = os.path.join(bot_dir, "build_context")
            os.makedirs(build_context_dir, exist_ok=True)

            # Copy the bot.py file to the build context
            bot_file_path = os.path.join(bot_dir, bot_file)
            shutil.copy2(bot_file_path, build_context_dir)

            # Copy the run.sh script to the build context
            run_sh_template = env.get_template("run.sh.j2")
            run_sh_path = os.path.join(build_context_dir, "run.sh")
            with open(run_sh_path, "w") as f:
                f.write(run_sh_template.render(include_dashboard=str(include_dashboard)))

            build_args = {
                "INCLUDE_DASHBOARD": str(include_dashboard).lower()
            }

            subprocess.run([
                "docker", "build", "-t", "bam-agent", ".",
                "--build-arg", f"INCLUDE_DASHBOARD={build_args['INCLUDE_DASHBOARD']}"
            ], cwd=build_context_dir, check=True)

        except (subprocess.CalledProcessError, Exception) as e:
            raise RuntimeError(f"Error building Bam container image: {str(e)}")

    def run_container(self, bot_file):
        container_name = os.path.splitext(os.path.basename(bot_file))[0]

        try:
            subprocess.run([
                "docker", "run", "--rm", "--name", f"{self.container_name_prefix}{container_name}",
                "-v", f"{os.path.abspath(bot_file)}:/app/{os.path.basename(bot_file)}:ro",
                "--memory=256m", "--memory-swap=256m", "--cpus=1", "--cap-drop=ALL", "--security-opt=no-new-privileges",
                "bam-agent", "python", "-m", "bambot.agent", "--bot-file=/app/{}".format(os.path.basename(bot_file))
            ], check=True)
        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"Error running Bam container: {str(e)}")

        return container_name

    def cleanup(self):
        try:
            subprocess.run(["docker", "system", "prune", "-f"], check=True)
        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"Error cleaning up containers and images: {str(e)}")

if __name__ == "__main__":
    cli()