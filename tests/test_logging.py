import unittest
from bam.logging import setup_logging

class TestLogging(unittest.TestCase):
    def test_setup_logging(self):
        # Test setting up logging
        setup_logging()

if __name__ == "__main__":
    unittest.main()