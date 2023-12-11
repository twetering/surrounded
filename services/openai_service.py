from openai import OpenAI
import os
import csv

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
    
    def create_thread(self):
        thread = self.client.beta.threads.create()
        return thread

    def save_thread_to_csv(self, thread):
        with open('threads.csv', 'a', newline='') as file:
            writer = csv.writer(file)
            writer.writerow([thread.id, thread.object, thread.created_at, thread.metadata])
    
    def read_threads_from_csv(self):
        threads = []
        with open('threads.csv', 'r') as file:
            reader = csv.reader(file)
            for row in reader:
                thread = {
                    'id': row[0],
                    'object': row[1],
                    'created_at': row[2],
                    'metadata': row[3],
                }
                threads.append(thread)
        return threads
    
    def get_thread_messages(self, thread_id):
        thread_messages = self.client.beta.threads.messages.list(thread_id=thread_id)
        messages_list = []
        for message in thread_messages.data:
            # Extract the text of the message
            text = ''
            if message.content and message.content[0].type == 'text':
                text = message.content[0].text.value

            message_dict = {
                'id': message.id,
                'object': message.object,
                'created_at': message.created_at,
                'thread_id': message.thread_id,
                'role': message.role,
                'content': text,
                'file_ids': message.file_ids,
                'assistant_id': message.assistant_id,
                'run_id': message.run_id,
                'metadata': message.metadata,
            }
            messages_list.append(message_dict)
        return messages_list

    
    def get_chat_completions(self, messages):
        response = self.client.chat.completions.create(
            model="gpt-4-1106-preview",
            messages=messages,
        )
        answer = response.choices[0].message.content
        html = answer.replace('\n', '<br/>')
        return html

    # Assuming generate_audio is a method that needs to be refactored from app.py
    def generate_audio(self, message, voice_id):
        # Add the logic for audio generation here
        # This might call ElevenLabsService or another service if needed
        return audio_generated

    