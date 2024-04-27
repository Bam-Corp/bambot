import os
import subprocess
import click  # Import the click library

class DockerManager:
    def __init__(self):
        self.output_dir = "output"
        self.container_name_prefix = "bam-agent-"

    def is_docker_running(self):
        try:
            subprocess.run(["docker", "info"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
            return True
        except subprocess.CalledProcessError:
            return False

    def build_image(self):
        try:
            subprocess.run(["docker", "build", "-t", "bam-agent", "."], check=True)
        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"Error building Docker image: {e}")

    def run_container(self, bot_file):
        container_name = f"{self.container_name_prefix}{os.path.splitext(os.path.basename(bot_file))[0]}"
        os.makedirs(self.output_dir, exist_ok=True)

        try:
            subprocess.run(
                [
                    "docker", "run", "--rm", "--name", container_name,
                    "-v", f"{os.path.abspath(self.output_dir)}:/app/output",
                    "--cap-drop=ALL", "--security-opt=no-new-privileges",
                    "--memory=256m", "--cpus=1",
                    "bam-agent", "--bot-file", os.path.basename(bot_file)
                ],
                check=True,
            )
        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"Error running Docker container: {e}")

        return os.path.splitext(os.path.basename(bot_file))[0]

    def cleanup(self):
        confirm = click.confirm("This operation will remove unused Docker resources to free up disk space. Do you want to proceed?", default=False)
        if not confirm:
            click.echo("Skipping cleanup operation.")
            return

        try:
            subprocess.run(["docker", "system", "prune", "-f"], check=True)
            click.echo("Docker resources cleaned up successfully.")
        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"Error cleaning up Docker resources: {e}")