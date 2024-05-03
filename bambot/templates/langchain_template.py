# bambot/templates/langchain_template.py
from langchain import OpenAI, ConversationChain

class Agent:
    def __init__(self):
        self.llm = OpenAI(temperature=0)
        self.conversation = ConversationChain(llm=self.llm)

    def run(self):
        print("Running the Langchain agent...")
        while True:
            user_input = input("User: ")
            if user_input.lower() == 'exit':
                break
            response = self.conversation.predict(input=user_input)
            print("Agent:", response)