# cli.py
import click
import random
import string
from .app import create_app, run_app
from .docker_utils import prune_system, list_apps
import docker


def generate_app_name():
    prefix = "bam"
    adjectives = ["brave", "clever", "friendly", "gentle", "kind", "lucky", "silly", "witty"]
    nouns = ["panda", "tiger", "lion", "eagle", "owl", "dolphin", "turtle", "penguin", "koala", "kangaroo"]
    adjective = random.choice(adjectives)
    noun = random.choice(nouns)
    number = ''.join(random.choices(string.digits, k=4))
    return f"{prefix}-{adjective}-{noun}-{number}"

@click.group()
def cli():
    """Bam CLI application"""
    pass

@cli.group("app")
def app_group():
    """Manage AI agent applications"""
    pass

@app_group.command("create")
@click.argument("name", required=False)
@click.option("--agent-type", default="langchain", help="AI agent type")
@click.option("--env-file", default=".env", help="Path to the .env file")
def create_command(name, agent_type, env_file):
    """Create a new application for an AI agent"""
    if not name:
        name = generate_app_name()

    click.echo(click.style(f"Creating app: {name}", fg="yellow"))

    if click.confirm("Do you want to clean unused docker resources before building the app?"):
        with click.progressbar(length=4, label="Pruning system resources") as bar:
            prune_system(bar)
        click.echo(click.style("System resources pruned successfully!", fg="green"))

    create_app(name, agent_type, env_file)
    click.echo(click.style(f"App '{name}' created successfully!", fg="green"))

@app_group.command("run")
@click.argument("name", required=False)
def run_command(name):
    """Run an AI agent application"""
    apps = list_apps(prefix="bam")
    if not apps:
        click.echo(click.style("No apps found.", fg="red"))
        return

    click.echo(click.style("Available apps:", fg="yellow"))
    for index, app in enumerate(apps, start=1):
        click.echo(f"{index}. {app.name}")

    if not name:
        choice = click.prompt("Please select the app to run", type=int)
        if choice < 1 or choice > len(apps):
            click.echo(click.style("Invalid choice.", fg="red"))
            return
        name = apps[choice - 1].name

    click.echo(click.style(r"""
       ____                  
      |  _ \                 
      | |_) | __ _ _ __ ___  
      |  _ < / _` | '_ ` _ \ 
      | |_) | (_| | | | | | |
      |____/ \__,_|_| |_| |_|
                              
    """, fg="bright_yellow"))
    click.echo(click.style(f"🚀 Running app: {name}", fg="bright_blue"))

    try:
        run_app(name)
        click.echo(click.style(f"App '{name}' exited.", fg="green"))
    except docker.errors.APIError as e:
        click.echo(click.style(f"Error running app: {str(e)}", fg="red"))

def main():
    cli()

if __name__ == "__main__":
    main()