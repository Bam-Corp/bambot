# docker_utils.py
import os
import docker
from tqdm import tqdm

def build_image(container_dir):
    """Build a Docker image for an AI agent"""
    docker_client = docker.from_env()
    image, _ = docker_client.images.build(path=container_dir, tag=f"{os.path.basename(container_dir)}:latest", dockerfile="Dockerfile")
    return image

def create_docker_container(container_name, env_vars=None):
    """Create a Docker container for an AI agent"""
    docker_client = docker.from_env()
    container = docker_client.containers.create(
        f"{container_name}:latest",
        name=container_name,
        environment=env_vars,
        detach=True,
        tty=True,
        stdin_open=True,
        ports={'1337/tcp': ('127.0.0.1', 1337)},
    )
    return container

def prune_system(progress_bar=None):
    """Prune Docker system resources"""
    docker_client = docker.from_env()
    tasks = [
        docker_client.containers.prune,
        docker_client.images.prune,
        docker_client.networks.prune,
        docker_client.volumes.prune,
    ]
    if progress_bar:
        for task in tasks:
            task()
            progress_bar.update(1)
    else:
        with tqdm(total=4, desc="Pruning system resources") as pbar:
            for task in tasks:
                task()
                pbar.update(1)

def list_apps(prefix=""):
    """List all Bam apps"""
    docker_client = docker.from_env()
    containers = docker_client.containers.list(all=True)
    if prefix:
        containers = [c for c in containers if c.name.startswith(prefix)]
    return containers