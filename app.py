from flask import Flask, render_template, request, jsonify, session, send_file, Response
import requests
from dotenv import load_dotenv
import os
import json
from openai import OpenAI
import csv
from services.elevenlabs_service import ElevenLabsService
from services.openai_service import OpenAIService
import base64
import hashlib
import traceback
import logging
import csv

app = Flask(__name__)
load_dotenv()
elevenlabs_service = ElevenLabsService()
openai_service = OpenAIService()

# Configure headers for ElevenLabs API
#headers_elevenlabs = {
 #   'Authorization': f'Bearer {elevenlabs_api_key}',
 #   'Content-Type': 'application/json'
#}

# Initialiseer OpenAI client

assistant_id = 'asst_MM5LyMKLgKze3oKY5006i9UP'

class LoggingSession(requests.Session):
    def request(self, *args, **kwargs):
        print(f"Sending request: {args} {kwargs}")
        response = super().request(*args, **kwargs)
        print(f"Received response: {response.status_code} {response.text}")
        return response

# Route voor homepage
@app.route('/')
def home():
    return render_template('index.html',title='Home')

# List all assistants
@app.route('/get_assistants', methods=['GET'])
def get_assistants():
    try:
        limit = request.args.get('limit', default=20, type=int)
        order = request.args.get('order', default='desc', type=str)
        after = request.args.get('after', default=None, type=str)
        before = request.args.get('before', default=None, type=str)

        assistants = openai_service.list_assistants(limit, order, after, before)
        return render_template('assistants.html', assistants=assistants, title='Assistants')
    except Exception as e:
        return render_template('error.html', error_message=str(e))

# Retrieve a specific assistant
@app.route('/assistants/<assistant_id>', methods=['GET'])
def get_assistant(assistant_id):
    try:
        assistant = openai_service.get_assistant(assistant_id)
        assistant_dict = {
            'id': assistant.id,
            'object': assistant.object,
            'created_at': assistant.created_at,
            'name': assistant.name,
            'model': assistant.model,
            'instructions': assistant.instructions,
            'file_ids': assistant.file_ids,
            'metadata': assistant.metadata,
        }
        return render_template('assistant_detail.html', assistant=assistant_dict)
    except Exception as e:
        return render_template('error.html', error_message=str(e))

# Update a specific assistant
@app.route('/update_assistant/<assistant_id>', methods=['PUT'])
def update_assistant(assistant_id):
    name = request.json.get('name')
    model = request.json.get('model')
    instructions = request.json.get('instructions')
    tools = request.json.get('tools')
    file_ids = request.json.get('file_ids')

    try:
        assistant = openai_service.update_assistant(assistant_id, name, model, instructions, tools, file_ids)
        return jsonify(assistant), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Delete a specific assistant
@app.route('/delete_assistant/<assistant_id>', methods=['DELETE'])
def delete_assistant(assistant_id):
    try:
        openai_service.delete_assistant(assistant_id)
        return jsonify({'message': 'Assistant deleted successfully'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/threads')
def get_threads():
    threads = []

    # Read the thread information from the CSV file
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

    return render_template('threads.html', threads=threads, title='Threads')

@app.route('/create_thread', methods=['POST'])
def create_thread():
    try:
        thread = client.beta.threads.create()
        thread_dict = {
            'id': thread.id,
            'object': thread.object,
            'created_at': thread.created_at,
            'metadata': thread.metadata,
        }

        # Store the thread information in a CSV file
        with open('threads.csv', 'a', newline='') as file:
            writer = csv.writer(file)
            writer.writerow([thread.id, thread.object, thread.created_at, thread.metadata])

        return jsonify(thread_dict), 201
    except Exception as e:
        print(f"Error creating thread: {e}")  # Log the error
        return jsonify({'error': str(e)}), 500

# This route creates a threads message
@app.route('/create_thread_message', methods=['POST'])
def create_thread_message():
    thread_id = request.json.get('thread_id')
    content = request.json.get('content')

    try:
        thread_message = client.beta.threads.messages.create(
            thread_id,
            role="user",
            content=content
        )
        thread_message_dict = {
            'id': thread_message.id,
            'object': thread_message.object,
            'created_at': thread_message.created_at,
            'thread_id': thread_message.thread_id,
            'role': thread_message.role,
            'content': thread_message.content,
            'file_ids': thread_message.file_ids,
            'assistant_id': thread_message.assistant_id,
            'run_id': thread_message.run_id,
            'metadata': thread_message.metadata,
        }
        return jsonify(thread_message_dict), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    
@app.route('/threads/<thread_id>', methods=['GET'])
def get_messages(thread_id):
    try:
        thread_messages = client.beta.threads.messages.list(thread_id=thread_id)
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

        # Render the messages in a new HTML page
        return render_template('thread.html', thread_id = thread_id,messages=messages_list)
    except Exception as e:
        return str(e), 500

# This route creates a threads message
@app.route('/threads/<thread_id>/add_message', methods=['POST'])
def add_message(thread_id):
    # Get the message from the JSON data in the request body
    data = request.get_json()
    message = data.get('message')

    # Check if message is None
    if message is None:
        return jsonify({'error': 'No message provided'}), 400

    try:
        # Add the message to the thread
        thread_message = client.beta.threads.messages.create(
            thread_id,
            role="user",
            content=message
        )

        # Create a dictionary from the thread message
        thread_message_dict = {
            'id': thread_message.id,
            'object': thread_message.object,
            'created_at': thread_message.created_at,
            'thread_id': thread_message.thread_id,
            'role': thread_message.role,
            'content': thread_message.content[0].text.value if thread_message.content else '',
            'file_ids': thread_message.file_ids,
            'assistant_id': thread_message.assistant_id,
            'run_id': thread_message.run_id,
            'metadata': thread_message.metadata,
        }

        # Return the thread message as JSON
        return jsonify(thread_message_dict), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# Route voor het ophalen van een thread message
@app.route('/retrieve_message/<thread_id>/<message_id>', methods=['GET'])
def retrieve_message(thread_id, message_id):
    try:
        message = client.beta.threads.messages.retrieve(
            message_id=message_id,
            thread_id=thread_id
        )
        return jsonify(message)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Route voor het listen van runs
@app.route('/get_runs', defaults={'thread_id': None}, methods=['GET'])
@app.route('/get_runs/<thread_id>', methods=['GET'])
def get_runs(thread_id):
    try:
        if thread_id is None:
            # If no thread_id is provided, return an error message
            return jsonify({'error': 'No thread_id provided'}), 400
        else:
            # If a thread_id is provided, get the runs for the specified thread
            runs = client.beta.threads.runs.list(thread_id=thread_id)
            runs_list = []
            for run in runs:
                run_dict = {
                    'id': run.id,
                    'object': run.object,
                    'created_at': run.created_at,
                    'assistant_id': run.assistant_id,
                    'thread_id': run.thread_id,
                    'status': run.status,
                    'started_at': run.started_at,
                    # Add more fields as needed
                }
                runs_list.append(run_dict)
            return jsonify(runs_list), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# Route voor het creëren van een run
@app.route('/create_run', methods=['POST'])
def create_run():
    thread_id = request.json.get('thread_id')
    assistant_id = request.json.get('assistant_id')

    try:
        run = client.beta.threads.runs.create(
            thread_id=thread_id,
            assistant_id=assistant_id
        )
        run_dict = {
            'id': run.id,
            'object': run.object,
            'created_at': run.created_at,
            'assistant_id': run.assistant_id,
            'thread_id': run.thread_id,
            'status': run.status,
            'started_at': run.started_at,
            'expires_at': run.expires_at,
            'cancelled_at': run.cancelled_at,
            'failed_at': run.failed_at,
            'completed_at': run.completed_at,
            'last_error': run.last_error,
            'model': run.model,
            'instructions': run.instructions,
            'tools': run.tools,
            'file_ids': run.file_ids,
            'metadata': run.metadata,
        }
        return jsonify(run_dict), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500



@app.route('/chat', methods=['POST', 'GET'])
def get_chat():
    if request.method == 'POST':
        data = request.get_json()
        messages = data.get('messages')

        if messages is None:
            return jsonify({'error': 'No messages provided'}), 400

        response = client.chat.completions.create(
            model="gpt-4-1106-preview",
            messages=messages,
        )       

        assistant_message = response.choices[0].message.content
        audio = generate_audio(assistant_message, 'EXAVITQu4vr4xnSDxMaL')

        return jsonify({'message': assistant_message, 'audio': audio}), 200

    else:
        voices = elevenlabs_service.list_voices()
        return render_template('chat.html', voices=voices, title='Chat')

@app.route('/speak', methods=['POST'])
def speak():
    data = request.get_json()
    text = data.get('text')

    speech_file_path = "speech.mp3"
    response = client.audio.speech.create(
        model="tts-1",
        voice="nova",
        input=text
    )

    # Store the audio data in a variable
    audio_data = response.read()

    with open(speech_file_path, "wb") as f:
        f.write(audio_data)

    return Response(audio_data, mimetype='audio/mpeg')
# Experiment with different voices (alloy, echo, fable, onyx, nova, and shimmer).

@app.route('/text-to-speech', methods=['POST'])
def text_to_speech():
    
    try:
        data = request.json
        app.logger.info(f"Received JSON data: {data}")  # Log the JSON payload
        voice_id = data.get('voice_id')
        text = data.get('text')
        settings = data.get('settings')

        if not settings:
            return jsonify({'error': 'Missing settings'}), 400  # Return an error if settings are missing
        # Convert settings values to appropriate types
        settings = {
            'stability': float(settings.get('stability', 0.71)),
            'clarity': float(settings.get('clarity', 0.5)),
            'style': float(settings.get('style', 0.1)),
            'speakerBoost': settings.get('speakerBoost', True) in ['true', True]
        }

        audio = elevenlabs_service.generate_speech(text, voice_id, settings)

        filename = hashlib.sha256((voice_id + text).encode()).hexdigest() + '.mp3'
        audio_path = os.path.join('static', 'audio', filename)
        with open(audio_path, 'wb') as f:
            f.write(audio)

        return jsonify({'audio_file': audio_path})

        # The rest of your code to save and return the audio...
    except Exception as e:
        print(f"An error occurred: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/elevenlabs')
def elevenlabs():
    return render_template('elevenlabs.html',title='Elevenlabs')

@app.route('/get_voices')
def get_voices():
    try:
        voices = elevenlabs_service.list_voices()
        voices_data = [{'voice_id': voice.voice_id, 'name': voice.name} for voice in voices]
        return jsonify(voices_data)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/generate_speech', methods=['POST'])
def generate_speech():
    try:
        data = request.json
        text = data['text']
        voice_id = data['voice_id']
        settings = data.get('settings')

        audio_bytes = elevenlabs_service.generate_speech(text, voice_id, settings)
        audio_base64 = base64.b64encode(audio_bytes).decode('utf-8')

        return jsonify({'audio': audio_base64})
    except Exception as e:
        return jsonify({'error': str(e)}), 500



@app.route('/save_audio', methods=['POST'])
def save_audio():
    try:
        data = request.json
        audio_bytes = data['audio']
        filename = data['filename']
        elevenlabs_service.save_audio(audio_bytes, filename)
        return jsonify({'message': 'Audio opgeslagen'})
    except Exception as e:
        return jsonify(error=str(e)), 500

@app.route('/get_history')
def get_history():
    try:
        history_data = elevenlabs_service.get_user_history()[:10]  # Neem de laatste 10 items
        return jsonify(history_data)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/get_audio/<history_item_id>')
def get_audio(history_item_id):
    try:
        audio_data = elevenlabs_service.get_audio_data(history_item_id)
        if audio_data:
            return Response(audio_data, mimetype='audio/mpeg')
        else:
            return jsonify({'error': 'Audio niet gevonden'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500


if __name__ == "__main__":
    app.run(debug=True)