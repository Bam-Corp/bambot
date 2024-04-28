# docker_utils.py
import os
import subprocess

class DockerManager:
    def __init__(self):
        self.container_name_prefix = "bam-agent-"
        self.include_dashboard = False

    def is_docker_running(self):
        try:
            subprocess.run(["docker", "info"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
            return True
        except subprocess.CalledProcessError:
            return False

    def build_image(self, include_dashboard):
        self.include_dashboard = include_dashboard
        try:
            build_args = {
                "INCLUDE_DASHBOARD": str(include_dashboard).lower()
            }
            subprocess.run([
                "docker", "build", "-t", "bam-agent", ".",
                "--build-arg", f"INCLUDE_DASHBOARD={build_args['INCLUDE_DASHBOARD']}"
            ], check=True)
        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"Error building Bam container image: {e}")

    def run_container(self, bot_file):
        container_name = os.path.splitext(os.path.basename(bot_file))[0]
        # Removed the creation of log_dir and its mounting to the container
        try:
            subprocess.run([
                "docker", "run", "--rm", "--name", f"{self.container_name_prefix}{container_name}",
                "-v", f"{os.path.abspath(bot_file)}:/app/{os.path.basename(bot_file)}:ro",
                "--memory=256m", "--memory-swap=256m", "--cpus=1", "--cap-drop=ALL", "--security-opt=no-new-privileges",
                "bam-agent",
                "python", "-m", "bambot.agent", "--bot-file=/app/{}".format(os.path.basename(bot_file))
            ], check=True)
        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"Error running Bam container: {e}")
        return container_name

    def cleanup(self):
        try:
            subprocess.run(["docker", "system", "prune", "-f"], check=True)
        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"Error cleaning up containers and images: {e}")
