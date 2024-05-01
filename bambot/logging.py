import logging

def setup_logging():
    """Set up logging for the Bam CLI application"""
    logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")