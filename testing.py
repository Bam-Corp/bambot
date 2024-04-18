# quickstart.py
from bambot import BamClient

# Initialize the Bam client with your API key
bam = BamClient(api_key="your_api_key")

# Upload documents from various paths
bam.upload_documents(["venv/bin", "setup.py"])