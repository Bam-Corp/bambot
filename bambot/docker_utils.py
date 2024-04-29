# bambot/docker_utils.py
import os
import subprocess
import tempfile
import requests
import shutil
import zipfile
from jinja2 import Environment, FileSystemLoader

class DockerManager:
    def __init__(self):
        self.container_name_prefix = "bam-agent-"
        self.include_dashboard = False
        self.repo_url = "https://github.com/Bam-Corp/bambot"
        self.templates_dir = os.path.join(os.path.dirname(__file__), "templates")
        self.env = Environment(loader=FileSystemLoader(self.templates_dir))

    def is_docker_running(self):
        try:
            subprocess.run(["docker", "info"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
            return True
        except subprocess.CalledProcessError:
            return False

    def build_image(self, bot_file, bot_dir, include_dashboard):
        self.include_dashboard = include_dashboard

        try:
            # Create a separate directory for the build context
            with tempfile.TemporaryDirectory() as temp_dir:
                build_context_dir = os.path.join(temp_dir, "build_context")
                os.makedirs(build_context_dir, exist_ok=True)

                # Copy the bot.py file from the root project directory
                bot_file_path = os.path.join(bot_dir, bot_file)
                shutil.copy2(bot_file_path, os.path.join(build_context_dir, bot_file))
                print(f"Copied file: {bot_file_path} -> {build_context_dir}/{bot_file}")

                # Copy the bambot directory
                bambot_dir = os.path.dirname(__file__)
                shutil.copytree(bambot_dir, os.path.join(build_context_dir, "bambot"))
                print(f"Copied directory: {bambot_dir} -> {build_context_dir}/bambot")

                # Copy the Dockerfile template
                dockerfile_template = "Dockerfile.dashboard.j2" if include_dashboard else "Dockerfile.lightweight.j2"
                dockerfile_template_path = os.path.join(self.templates_dir, dockerfile_template)
                print(f"Dockerfile template path: {dockerfile_template_path}")

                if os.path.exists(dockerfile_template_path):
                    with open(dockerfile_template_path, "r") as template_file:
                        template_content = template_file.read()

                    rendered_dockerfile = self.env.from_string(template_content).render(bot_file=bot_file)

                    # Write the rendered Dockerfile to the build context directory
                    dockerfile_path = os.path.join(build_context_dir, "Dockerfile")
                    with open(dockerfile_path, "w") as dockerfile:
                        dockerfile.write(rendered_dockerfile)
                    print(f"Wrote Dockerfile: {dockerfile_path}")
                else:
                    print(f"Dockerfile template not found: {dockerfile_template_path}")

                # Copy the run.sh script
                run_sh_path = os.path.join(self.templates_dir, "run.sh.j2")
                print(f"run.sh path: {run_sh_path}")
                if os.path.exists(run_sh_path):
                    shutil.copy2(run_sh_path, os.path.join(build_context_dir, "run.sh"))
                    print(f"Copied run.sh script: {run_sh_path} -> {build_context_dir}")
                else:
                    print(f"run.sh script not found: {run_sh_path}")

                build_args = {
                    "INCLUDE_DASHBOARD": str(include_dashboard).lower()
                }

                subprocess.run([
                    "docker", "build", "-t", "bam-agent", ".",
                    "--build-arg", f"INCLUDE_DASHBOARD={build_args['INCLUDE_DASHBOARD']}"
                ], cwd=build_context_dir, check=True)

        except (subprocess.CalledProcessError, requests.exceptions.RequestException, zipfile.BadZipFile) as e:
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