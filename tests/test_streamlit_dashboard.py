import unittest
from bam.streamlit_dashboard import setup_streamlit_dashboard

class TestStreamlitDashboard(unittest.TestCase):
    def test_setup_streamlit_dashboard(self):
        # Test setting up the Streamlit dashboard
        setup_streamlit_dashboard()

if __name__ == "__main__":
    unittest.main()