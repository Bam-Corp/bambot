# bambot/templates/agent_template.py
import os

class Agent:
    def __init__(self):
        # Load environment variables
        self.env_vars = {key: value for key, value in os.environ.items()}
        
        # Initialize agent-specific configurations
        self.setup()

    def setup(self):
        # Implement agent-specific setup logic here
        pass

    def run(self):
        print(f"Running the {self.__class__.__name__} agent...")
        # Add agent-specific logic here