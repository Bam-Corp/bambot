# testing.py
from bambot import BamClient
from pprint import pprint

# Initialize the Bam client with your API key
bam = BamClient(api_key="your_api_key")

# Upload documents that will be queued for indexing
bam.upload_documents(["venv/bin", "setup.py"])

# Search for documents using natural language queries
query = "What are the latest advancements in artificial intelligence?"
search_results = bam.search_documents(query)

pprint(search_results)