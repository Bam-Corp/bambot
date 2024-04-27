import os
import click
from jinja2 import Environment, PackageLoader
from tqdm import tqdm
from .docker_utils import DockerManager
from .log_utils import LogManager
from .utils import copy_template, generate_random_string

env = Environment(loader=PackageLoader("bambot", "templates"))

@click.group()
def cli():
    pass

@cli.command()
@click.option("--bot-file", "-b", default="bot.py", help="Name of the bot file (default: bot.py)")
def build(bot_file):
    """Build and deploy an AI agent."""
    bot_dir = os.getcwd()
    bot_path = os.path.join(bot_dir, bot_file)

    if not os.path.exists(bot_path):
        click.echo(f"Error: {bot_file} not found in the current directory.", err=True)
        return

    docker_manager = DockerManager()
    log_manager = LogManager()

    try:
        click.echo("Cleaning up previous artifacts...")
        docker_manager.cleanup()

        click.echo("Generating Docker files...")
        copy_template(env, "Dockerfile.j2", os.path.join(bot_dir, "Dockerfile"))
        copy_template(env, "Procfile.j2", os.path.join(bot_dir, "Procfile"))
        copy_template(env, "README.md.j2", os.path.join(bot_dir, "README.md"))

        click.echo("Building Docker image...")
        with tqdm(total=100, unit="B", unit_scale=True, unit_divisor=1024, bar_format="{l_bar}{bar}| {n_fmt}/{total_fmt} [{elapsed}<{remaining}]") as pbar:
            for _ in pbar:
                pbar.set_postfix(operation="Building Docker image", refresh=False)
                pbar.update(1)
        docker_manager.build_image()

        click.echo("Running Docker container...")
        with tqdm(total=100, unit="B", unit_scale=True, unit_divisor=1024, bar_format="{l_bar}{bar}| {n_fmt}/{total_fmt} [{elapsed}<{remaining}]") as pbar:
            for _ in pbar:
                pbar.set_postfix(operation="Running Docker container", refresh=False)
                pbar.update(1)
        container_id = docker_manager.run_container()

        log_file = f"/app/output/bot_{container_id}.log"
        click.echo("Processing logs...")
        with tqdm(total=100, unit="B", unit_scale=True, unit_divisor=1024, bar_format="{l_bar}{bar}| {n_fmt}/{total_fmt} [{elapsed}<{remaining}]") as pbar:
            for _ in pbar:
                pbar.set_postfix(operation="Processing logs", refresh=False)
                pbar.update(1)
        log_manager.process_logs(log_file)

        click.echo("Archiving output...")
        with tqdm(total=100, unit="B", unit_scale=True, unit_divisor=1024, bar_format="{l_bar}{bar}| {n_fmt}/{total_fmt} [{elapsed}<{remaining}]") as pbar:
            for _ in pbar:
                pbar.set_postfix(operation="Archiving output", refresh=False)
                pbar.update(1)
        docker_manager.archive_output()

        click.echo("Deployment completed successfully!")
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
    finally:
        docker_manager.cleanup()

if __name__ == "__main__":
    cli()