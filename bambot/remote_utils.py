# bambot/remote_utils.py
import os
import tempfile
import requests
import shutil
import time

def download_file(url, target_path, max_retries=3, retry_delay=5):
    for attempt in range(max_retries):
        try:
            response = requests.get(url)
            response.raise_for_status()
            with open(target_path, "wb") as file:
                file.write(response.content)
            return
        except requests.exceptions.RequestException as e:
            if attempt < max_retries - 1:
                print(f"Error downloading file: {str(e)}. Retrying in {retry_delay} seconds...")
                time.sleep(retry_delay)
            else:
                raise RuntimeError(f"Failed to download file after {max_retries} attempts: {str(e)}")

def download_directory(repo_url, directory, target_path, max_retries=3, retry_delay=5):
    url = f"{repo_url}/zipball/main"
    for attempt in range(max_retries):
        try:
            response = requests.get(url, stream=True)
            response.raise_for_status()

            with tempfile.NamedTemporaryFile(delete=False) as temp_file:
                shutil.copyfileobj(response.raw, temp_file)
                temp_file_path = temp_file.name

            with tempfile.TemporaryDirectory() as temp_dir:
                shutil.unpack_archive(temp_file_path, temp_dir, format="zip")
                repo_dir = os.listdir(temp_dir)[0]
                directory_path = os.path.join(temp_dir, repo_dir, directory)
                shutil.copytree(directory_path, target_path, dirs_exist_ok=True)

            os.unlink(temp_file_path)
            return
        except (requests.exceptions.RequestException, shutil.Error, IOError) as e:
            if attempt < max_retries - 1:
                print(f"Error downloading directory: {str(e)}. Retrying in {retry_delay} seconds...")
                time.sleep(retry_delay)
            else:
                raise RuntimeError(f"Failed to download directory after {max_retries} attempts: {str(e)}")