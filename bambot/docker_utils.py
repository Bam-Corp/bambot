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
                print(f"Copied file: {bot_file_path} -> {build_context_dir}/{bot_file}")

                # Copy the run.sh script to the build context
                run_sh_template = self.env.get_template("run.sh.j2")
                run_sh_path = os.path.join(build_context_dir, "run.sh")
                with open(run_sh_path, "w") as f:
                    f.write(run_sh_template.render(include_dashboard=str(include_dashboard)))
                print(f"Copied file: {run_sh_path}")

                # Copy the requirements.txt file to the build context
                requirements_file_path = os.path.join(bot_dir, "requirements.txt")
                if os.path.exists(requirements_file_path):
                    shutil.copy2(requirements_file_path, build_context_dir)
                    print(f"Copied file: {requirements_file_path} -> {build_context_dir}/requirements.txt")

                build_args = {
                    "INCLUDE_DASHBOARD": str(include_dashboard).lower()
                }

                # Build the Docker image
                docker_build_cmd = [
                    "docker", "build", "--no-cache", "--force-rm", "-t", "bam-agent", ".",
                    "--build-arg", f"INCLUDE_DASHBOARD={build_args['INCLUDE_DASHBOARD']}"
                ]
                print(f"Running command: {' '.join(docker_build_cmd)}")

                process = subprocess.Popen(docker_build_cmd, cwd=build_context_dir, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                stdout, stderr = process.communicate()

                if process.returncode != 0:
                    print(f"Docker build failed with exit code {process.returncode}")
                    print(f"Docker build output:\n{stdout.decode('utf-8')}")
                    print(f"Docker build error:\n{stderr.decode('utf-8')}")
                    raise RuntimeError(f"Error building Bam container image: Command '{' '.join(docker_build_cmd)}' returned non-zero exit status {process.returncode}")
                else:
                    print("Docker build completed successfully.")

        except Exception as e:
            raise RuntimeError(f"Error building Bam container image: {str(e)}")

    def cleanup(self):
        try:
            subprocess.run(["docker", "system", "prune", "-f"], check=True)
        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"Error cleaning up containers and images: {str(e)}")