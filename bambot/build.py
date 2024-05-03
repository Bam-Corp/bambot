# bambot/build.py
import os
import docker
from .utils import echo_info, echo_success, echo_error, contextmanager_spinner


def build_project():
    """Build the Bam project"""
    project_dir = os.getcwd()
    container_name = os.path.basename(project_dir)

    with contextmanager_spinner(f"Building Docker image for '{container_name}'...") as spinner:
        try:
            docker_client = docker.from_env()
            image, _ = docker_client.images.build(path=project_dir, tag=f"{container_name}:latest", dockerfile="Dockerfile")
            spinner.stop()
            echo_success("Docker image built successfully!")

            # Create the container and mount the project directory as a volume
            container = docker_client.containers.create(
                f"{container_name}:latest",
                name=container_name,
                detach=True,
                tty=True,
                stdin_open=True,
                ports={'1337/tcp': ('127.0.0.1', 1337)},
                volumes={project_dir: {'bind': '/app', 'mode': 'rw'}}
            )
            echo_success(f"Container '{container_name}' created successfully!")
        except docker.errors.BuildError as e:
            spinner.stop()
            echo_error(f"Error building Docker image: {e}")
            raise

    echo_success(f"Project '{container_name}' built successfully! You can now start the AI agent by running 'bam start'.")