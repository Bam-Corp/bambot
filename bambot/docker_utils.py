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
        self.templates_dir = os.path.join(os.path.dirname(__file__), "bambot", "templates")
        print(f"Templates directory: {self.templates_dir}")
        self.env = Environment(loader=FileSystemLoader(self.templates_dir))

    def is_docker_running(self):
        try:
            subprocess.run(["docker", "info"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
            return True
        except subprocess.CalledProcessError:
            return False

    def build_image(self, include_dashboard):
        self.include_dashboard = include_dashboard

        try:
            # Download the bambot directory from the remote repository
            with tempfile.TemporaryDirectory() as temp_dir:
                self.download_directory(temp_dir)

                # Copy the necessary files to the Docker build context
                build_context = os.path.join(temp_dir, "build_context")
                os.makedirs(build_context, exist_ok=True)
                print(f"Build context: {build_context}")

                # Copy the bambot package files
                bambot_dir = os.path.join(temp_dir, "bambot")
                for item in os.listdir(bambot_dir):
                    if item == "templates":
                        continue  # Skip the templates directory
                    src_path = os.path.join(bambot_dir, item)
                    dst_path = os.path.join(build_context, item)
                    if os.path.isdir(src_path):
                        shutil.copytree(src_path, dst_path)
                        print(f"Copied directory: {src_path} -> {dst_path}")
                    else:
                        shutil.copy2(src_path, dst_path)
                        print(f"Copied file: {src_path} -> {dst_path}")

                # Copy the Dockerfile template
                dockerfile_template = "Dockerfile.dashboard.j2" if include_dashboard else "Dockerfile.lightweight.j2"
                dockerfile_template_path = os.path.join(self.templates_dir, "bambot", "templates", dockerfile_template)
                print(f"Dockerfile template path: {dockerfile_template_path}")

                if os.path.exists(dockerfile_template_path):
                    with open(dockerfile_template_path, "r") as template_file:
                        template_content = template_file.read()

                    rendered_dockerfile = template_content.replace("{{ bot_file }}", os.path.basename("bot.py"))

                    # Write the rendered Dockerfile to the build context
                    dockerfile_path = os.path.join(build_context, "Dockerfile")
                    with open(dockerfile_path, "w") as dockerfile:
                        dockerfile.write(rendered_dockerfile)
                    print(f"Wrote Dockerfile: {dockerfile_path}")

                    # Debug: List files in the build context
                    print("Files in the build context:")
                    subprocess.run(["ls", "-l", build_context], check=True)
                else:
                    print(f"Dockerfile template not found: {dockerfile_template_path}")

                # Copy the run.sh script
                run_sh_path = os.path.join(temp_dir, "bambot", "templates", "run.sh.j2")
                print(f"run.sh path: {run_sh_path}")
                if os.path.exists(run_sh_path):
                    shutil.copy2(run_sh_path, os.path.join(build_context, "run.sh"))
                    print(f"Copied run.sh script: {run_sh_path} -> {build_context}")
                else:
                    print(f"run.sh script not found: {run_sh_path}")

                build_args = {
                    "INCLUDE_DASHBOARD": str(include_dashboard).lower()
                }

                subprocess.run([
                    "docker", "build", "-t", "bam-agent", ".",
                    "--build-arg", f"INCLUDE_DASHBOARD={build_args['INCLUDE_DASHBOARD']}"
                ], cwd=build_context, check=True)

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

    def download_directory(self, target_path):
        # Get the main branch archive URL
        download_url = f"{self.repo_url}/archive/refs/heads/main.zip"

        response = requests.get(download_url, stream=True)
        response.raise_for_status()

        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            for chunk in response.iter_content(chunk_size=8192):
                temp_file.write(chunk)
            temp_file_path = temp_file.name

        with zipfile.ZipFile(temp_file_path, 'r') as zip_ref:
            # Find the extracted directory name
            extracted_dir = zip_ref.namelist()[0]

            # Extract the contents of the archive to the target directory
            zip_ref.extractall(target_path)

            # Copy the contents of the extracted directory to the target directory
            extracted_dir_path = os.path.join(target_path, extracted_dir)
            for item in os.listdir(extracted_dir_path):
                src_path = os.path.join(extracted_dir_path, item)
                dst_path = os.path.join(target_path, item)
                if os.path.isdir(src_path):
                    shutil.copytree(src_path, dst_path)
                else:
                    shutil.copy2(src_path, dst_path)

            # Remove the extracted directory
            shutil.rmtree(extracted_dir_path)

        os.remove(temp_file_path)