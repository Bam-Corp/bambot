# bambot/run.py
import os
import signal
import sys
import docker
from .utils import echo_info, echo_success, echo_error

def run_project(container_name=None):
    """Run the Bam project"""
    project_dir = os.getcwd()
    if not container_name:
        container_name = os.path.basename(project_dir)

    echo_info(f"Starting container: {container_name}")

    try:
        docker_client = docker.from_env()
        container = docker_client.containers.get(container_name)
    except docker.errors.NotFound:
        echo_error(f"Container '{container_name}' not found. Please run 'bam init' and 'bam build' first.")
        return

    # Start container
    container.start()

    # Set up signal handler for SIGINT (Ctrl+C)
    def signal_handler(sig, frame):
        echo_info("\nStopping container, hang in there...")
        container.stop()
        echo_success("Container gracefully stopped. You may go about your life now.")
        sys.exit(0)

    signal.signal(signal.SIGINT, signal_handler)

    # Stream container logs
    echo_info("Container logs:")
    try:
        for log in container.logs(stream=True, follow=True):
            try:
                log_str = log.decode('utf-8')
                print(log_str, end='')
            except UnicodeDecodeError:
                echo_error(f"Error decoding log line: {log}")
    except KeyboardInterrupt:
        # Handle KeyboardInterrupt separately
        signal_handler(signal.SIGINT, None)