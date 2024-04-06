# bambot/core.py
import os
import time
import requests
from typing import Any, Dict, Optional

class AuthenticationError(Exception):
    pass

class TaskSubmissionError(Exception):
    pass

class TaskStatusError(Exception):
    pass

class Bam:
    def __init__(self, api_key: Optional[str] = None) -> None:
        self.api_key: str = api_key if api_key is not None else os.getenv('BAM_API_KEY')
        if not self.api_key:
            raise ValueError("API key must be provided or set as 'BAM_API_KEY' environment variable.")
        self.base_url: str = 'https://api.bam.bot/v1/run/'

    def _submit_task(self, task: str, model: Optional[str] = None, data: Optional[str] = None, 
                     mission: Optional[str] = None, objectives: Optional[Any] = None, 
                     response_format: str = "json", output_filename: Optional[str] = None) -> str:
        """Submit a task to the API and return the task ID."""
        headers: Dict[str, str] = {'Authorization': f'Bearer {self.api_key}'}
        payload: Dict[str, Any] = {
            'task': task,
            'model': model,
            'data': data,
            'mission': mission,
            'objectives': objectives,
            'response_format': response_format,
            'output_filename': output_filename
        }
        response = requests.post(self.base_url, headers=headers, json=payload)
        if response.status_code != 200:
            raise TaskSubmissionError(f"Failed to submit task: {response.text}")
        task_id: str = response.json().get('task_id')
        if not task_id:
            raise TaskSubmissionError("Task ID not returned by the API.")
        return task_id

    def _poll_task_status(self, task_id: str) -> Dict[str, Any]:
        """Poll the task status until it's completed and return the result."""
        headers: Dict[str, str] = {'Authorization': f'Bearer {self.api_key}'}
        while True:
            response = requests.get(f"{self.base_url}{task_id}/", headers=headers)
            if response.status_code == 401:
                raise AuthenticationError("Invalid API key")
            elif response.status_code not in [200, 202]:
                raise TaskStatusError(f"Unexpected error fetching task status: {response.text}")
            
            data = response.json()
            status = data.get('status')
            if status in ['SUCCESS', 'FAILURE']:
                return data
            elif status == 'PENDING':
                time.sleep(0.25)
            else:
                raise TaskStatusError(f"Unexpected task status: {status}")


    def run(self, task: str, model: Optional[str] = None, data: Optional[str] = None, 
            mission: Optional[str] = None, objectives: Optional[Any] = None, 
            response_format: str = "json", output_filename: Optional[str] = None) -> Dict[str, Any]:
        """Submits a task to the API and polls for its completion."""
        task_id: str = self._submit_task(task, model, data, mission, objectives, response_format, output_filename)
        result: Dict[str, Any] = self._poll_task_status(task_id)
        return result