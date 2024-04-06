# tests/test_bam.py
import unittest
from bambot.core import Bam
from unittest.mock import patch, MagicMock


class TestBam(unittest.TestCase):
    def test_init(self):
        """Test initialization of Bam class with an API key."""
        api_key = "test_api_key"
        bam = Bam(api_key=api_key)
        self.assertEqual(bam.api_key, api_key)


class TestBamRun(unittest.TestCase):
    def setUp(self):
        self.bam = Bam(api_key="dummy_api_key")

    @patch('bambot.core.requests.post')
    @patch('bambot.core.requests.get')
    def test_run_success(self, mock_get, mock_post):
        # Mocking the POST request to submit the task
        mock_post.return_value = MagicMock(status_code=200, json=lambda: {'task_id': '123'})

        # Setup GET request mock to simulate task status polling
        # Initial 'PENDING' responses followed by a 'SUCCESS' response
        def get_side_effect(*args, **kwargs):
            # Track how many times this function is called
            if getattr(get_side_effect, 'count', 0) < 2:  # Simulate 2 'PENDING' responses
                get_side_effect.count = getattr(get_side_effect, 'count', 0) + 1
                return MagicMock(status_code=200, json=lambda: {'status': 'PENDING'})
            return MagicMock(status_code=200, json=lambda: {'status': 'SUCCESS', 'result': 'task-specific-data'})

        # Apply side effect to the mock
        mock_get.side_effect = get_side_effect

        # Run the method under test
        result = self.bam.run(task="generate an image of an orca")
        
        # Assertions
        self.assertEqual(result['status'], 'SUCCESS')
        self.assertEqual(result['result'], 'task-specific-data')

if __name__ == '__main__':
    unittest.main()