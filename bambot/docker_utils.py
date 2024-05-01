# bam/docker_utils.py
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
        detach=True,
        name=container_name,
        environment=env_vars
    )
    return container

def prune_system():
    """Prune Docker system resources"""
    docker_client = docker.from_env()
    with tqdm(total=4, desc="Pruning system resources") as pbar:
        docker_client.containers.prune()
        pbar.update(1)
        docker_client.images.prune()
        pbar.update(1)
        docker_client.networks.prune()
        pbar.update(1)
        docker_client.volumes.prune()
        pbar.update(1)

def list_containers():
    """List all Docker containers"""
    docker_client = docker.from_env()
    return docker_client.containers.list(all=True)