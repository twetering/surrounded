from openai import OpenAI
import os

class OpenAIService:
    def __init__(self):
        openai_api_key = os.getenv('OPENAI_API_KEY')
        self.client = OpenAI(api_key=openai_api_key)    

    def list_assistants(self, limit, order, after, before):
        return self.client.beta.assistants.list(order=order, limit=limit, after=after, before=before)

    def get_assistant(self, assistant_id):
        return self.client.beta.assistants.retrieve(assistant_id=assistant_id)

    def update_assistant(self, assistant_id, name, model, instructions, tools, file_ids):
        return self.client.beta.assistants.update(assistant_id, name=name, model=model, instructions=instructions, tools=tools, file_ids=file_ids)

    def delete_assistant(self, assistant_id):
        return self.client.beta.assistants.delete(assistant_id)