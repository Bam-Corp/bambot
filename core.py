class Bam:
    def __init__(self, api_key):
        self.api_key = api_key
    
    def run(self, model="", task="", data="", mission=None, objectives=None, response_format="json", output_filename=None):
        print(f"Running model {model} for task '{task}' with data '{data}'")
        return {"status": "success", "data": "Result of the operation"}
