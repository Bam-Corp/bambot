import unittest
from bam.container import create_container, run_container

class TestContainer(unittest.TestCase):
    def test_create_container(self):
        # Test creating a container
        create_container("my_agent", "langchain")

    def test_run_container(self):
        # Test running a container
        run_container("my_agent")

if __name__ == "__main__":
    unittest.main()