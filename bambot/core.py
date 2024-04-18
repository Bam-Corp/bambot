# bambot/core.py
import os
import requests
from typing import List
from tqdm import tqdm

class BamClient:
    def __init__(self, api_key: str = None) -> None:
        self.api_key: str = api_key or os.getenv('BAM_API_KEY')
        if not self.api_key:
            raise ValueError("API key must be provided or set as 'BAM_API_KEY' environment variable.")
        self.base_url: str = 'https://api.bam.bot/v1'
        self.max_files: int = 1000

    def upload_documents(self, paths: List[str]) -> None:
        """Upload documents from the given paths to Bam storage."""
        file_paths = []
        for path in paths:
            if os.path.isfile(path):
                file_paths.append(path)
            elif os.path.isdir(path):
                for root, dirs, files in os.walk(path):
                    for file in files:
                        file_path = os.path.join(root, file)
                        file_paths.append(file_path)
            else:
                print(f"Skipping invalid path: {path}")

        total_files = len(file_paths)
        if total_files > self.max_files:
            print(f"Warning: The number of files ({total_files}) exceeds the maximum limit of {self.max_files}. Only the first {self.max_files} files will be uploaded.")
            file_paths = file_paths[:self.max_files]
            total_files = self.max_files

        success_count = 0
        failed_files = []

        with tqdm(total=total_files, desc="Uploading documents", unit="file") as pbar:
            for file_path in file_paths:
                try:
                    url = f"{self.base_url}/documents"
                    headers = {'Authorization': f'Bearer {self.api_key}'}
                    with open(file_path, 'rb') as file:
                        files = {'document': file}
                        response = requests.post(url, headers=headers, files=files)
                        response.raise_for_status()
                    success_count += 1
                except Exception as e:
                    failed_files.append(file_path)
                    print(f"Error uploading {file_path}: {str(e)}")
                pbar.update(1)

        if failed_files:
            print(f"Failed to upload the following files:")
            for file_path in failed_files:
                print(f"- {file_path}")

        print(f"\nSuccessfully uploaded {success_count} out of {total_files} documents.")