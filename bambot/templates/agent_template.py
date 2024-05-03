# bambot/templates/agent_template.py
import os

class Agent:
    def __init__(self, data=None):
        # Load environment variables
        self.env_vars = {key: value for key, value in os.environ.items()}

        # Initialize agent-specific configurations
        self.setup(data)

    def setup(self, data=None):
        # Validate input data
        if data is not None:
            self.data = data
        else:
            self.data = {}

        # Implement agent-specific setup logic here
        # You can use self.data and self.env_vars in this method

    def run(self, data=None):
        print(f"Running the {self.__class__.__name__} agent...")

        # Validate input data
        if data is not None:
            self.data = data

        # Add agent-specific logic here
        # You can use self.data and self.env_vars in this method

        # Return a sample response
        return {"message": "Hello from the agent!"}