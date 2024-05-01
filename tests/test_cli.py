import unittest
from bam.cli import cli

class TestCLI(unittest.TestCase):
    def test_create_container(self):
        # Test creating a container
        cli(["create", "container", "my_agent", "--agent-framework", "langchain"])

    def test_run_container(self):
        # Test running a container
        cli(["run", "container", "my_agent"])

if __name__ == "__main__":
    unittest.main()