import unittest
from bam.docker_utils import build_image, create_container

class TestDocker(unittest.TestCase):
    def test_build_image(self):
        # Test building a Docker image
        build_image("my_agent")

    def test_create_container(self):
        # Test creating a Docker container
        create_container("my_agent")

if __name__ == "__main__":
    unittest.main()