import unittest
from bam.prometheus import setup_prometheus

class TestPrometheus(unittest.TestCase):
    def test_setup_prometheus(self):
        # Test setting up Prometheus metrics
        setup_prometheus()

if __name__ == "__main__":
    unittest.main()