import unittest
from bam.metrics import setup_metrics

class TestMetrics(unittest.TestCase):
    def test_setup_metrics(self):
        # Test setting up metrics
        setup_metrics()

if __name__ == "__main__":
    unittest.main()