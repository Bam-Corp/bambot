# bambot/templates/agent_runner.py
from {{AGENT_TYPE}}_agent import Agent

def run_agent():
    agent = Agent()
    agent.run()

if __name__ == "__main__":
    run_agent()