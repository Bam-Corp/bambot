# bambot/docker_utils.py
import os
import subprocess
import click

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
            raise RuntimeError(f"Error building Bam container image: {e}")

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
                    "-v", f"{os.path.abspath(bot_file)}:/app/{os.path.basename(bot_file)}",
                    "bam-agent"
                ],
                check=True,
            )
        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"Error running Bam container: {e}")

        return os.path.splitext(os.path.basename(bot_file))[0]

    def cleanup(self):
        try:
            subprocess.run(["docker", "system", "prune", "-f"], check=True)
        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"Error cleaning up containers and images: {e}")