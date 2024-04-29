# bambot/docker_utils.py
import os
import subprocess
import tempfile
import shutil
from jinja2 import Environment, FileSystemLoader

class DockerManager:
    def __init__(self):
        self.container_name_prefix = "bam-agent-"
        self.templates_dir = os.path.join(os.path.dirname(__file__), "templates")
        self.env = Environment(loader=FileSystemLoader(self.templates_dir))

    def is_docker_running(self):
        try:
            subprocess.run(["docker", "info"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
            return True
        except subprocess.CalledProcessError:
            return False

    def build_image(self, bot_file, bot_dir, include_dashboard):
        try:
            with tempfile.TemporaryDirectory() as build_context_dir:
                # Copy the bot.py file to the build context
                bot_file_path = os.path.join(bot_dir, bot_file)
                shutil.copy2(bot_file_path, build_context_dir)

                # Copy the run.sh script to the build context
                run_sh_template = self.env.get_template("run.sh.j2")
                run_sh_path = os.path.join(build_context_dir, "run.sh")
                with open(run_sh_path, "w") as f:
                    f.write(run_sh_template.render(include_dashboard=str(include_dashboard)))

                # Copy the requirements.txt file to the build context
                requirements_file_path = os.path.join(bot_dir, "requirements.txt")
                if os.path.exists(requirements_file_path):
                    shutil.copy2(requirements_file_path, build_context_dir)

                build_args = {
                    "INCLUDE_DASHBOARD": str(include_dashboard).lower()
                }

                # Build the Docker image
                subprocess.run([
                    "docker", "build", "--no-cache", "--force-rm", "-t", "bam-agent", ".",
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