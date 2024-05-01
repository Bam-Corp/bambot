# bam/templates/main.py
from {{AGENT_TYPE}}_agent import Agent

def main():
    agent = Agent()
    agent.run()

if __name__ == "__main__":
    main()