from flask import Flask, render_template, request, jsonify, session, send_file, Response
import requests
from dotenv import load_dotenv
import os
import json
from services.elevenlabs_service import ElevenLabsService
from services.openai_service import OpenAIService
from elevenlabs import VoiceDesign, Gender, Age, Accent, play
import base64
import hashlib
import traceback
import logging
import random


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
    threads = openai_service.read_threads_from_csv()
    return render_template('threads.html', threads=threads, title='Threads')

@app.route('/create_thread', methods=['POST'])
def create_thread():
    try:
        thread = openai_service.create_thread()
        thread_dict = {
            'id': thread.id,
            'object': thread.object,
            'created_at': thread.created_at,
            'metadata': thread.metadata,
        }

        openai_service.save_thread_to_csv(thread)

        return jsonify(thread_dict), 201
    except Exception as e:
        print(f"Error creating thread: {e}")  # Log the error
        return jsonify({'error': str(e)}), 500
    
@app.route('/threads/<thread_id>', methods=['GET'])
def get_messages(thread_id):
    try:
        messages_list = openai_service.get_thread_messages(thread_id)
        return render_template('thread.html', thread_id=thread_id, messages=messages_list)
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

        try:
            assistant_message = openai_service.get_chat_completions(messages)
            return jsonify({'assistant_message': assistant_message})

        except Exception as e:
            return jsonify({'error': str(e)}), 500

    else:
        return render_template('chat.html', title='Chat')


# Route for generate speech with OpenAI
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
            'stability': float(settings.get('stabilitysetting', 0.71)),
            'clarity': float(settings.get('claritysetting', 0.5)),
            'style': float(settings.get('stylesetting', 0.1)),
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

# Route for generate multiple voices 
@app.route('/generate-multiple-voices', methods=['POST'])
def generate_multiple_voices():
    data = request.get_json()
    sentences = data.get('sentences')

    if sentences is None:
        return jsonify({'error': 'No sentences provided'}), 400

    try:
        # Initialize the ElevenLabsService
        service = ElevenLabsService()

        # Generate the multiple voices
        audio_path = service.generate_multiple_voices(sentences)

        return jsonify({'audio_file': audio_path})

    except Exception as e:
        return jsonify({'error': str(e)}), 500
    
# Route for generate multiple voices 
@app.route('/generate-multiple-voices-overlay', methods=['POST'])
def generate_multiple_voices_overlay():
    data = request.get_json()
    sentences = data.get('sentences')
    app.logger.info(f"Received JSON data: {data}")  # Log the JSON payload
    first_voice_id = data.get('voice_id')
    settings = data.get('settings')

    if not settings:
        return jsonify({'error': 'Missing settings'}), 400  # Return an error if settings are missing
    # Convert settings values to appropriate types
    settings = {
        'stability': float(settings.get('stabilitysetting', 0.71)),
        'clarity': float(settings.get('claritysetting', 0.5)),
        'style': float(settings.get('stylesetting', 0.1)),
        'speakerBoost': settings.get('speakerBoost', True) in ['true', True]
    }
    
    if sentences is None:
        return jsonify({'error': 'No sentences provided'}), 400

    try:
        # Initialize the ElevenLabsService
        service = ElevenLabsService()

        # Generate the multiple voices
        audio_path = service.generate_multiple_voices_overlay(sentences, first_voice_id, settings)

        return jsonify({'audio_file': audio_path})

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/elevenlabs')
def elevenlabs():
    return render_template('elevenlabs.html',title='Elevenlabs')

@app.route('/voice_designer')
def voice_designer():
    return render_template('voice_designer.html',title='Voice Designer')

@app.route('/text_to_voice')
def text_to_voice():
    return render_template('text_to_voice.html',title='Text-to-speech')

@app.route('/speech_to_speech')
def speech_to_speech():
    return render_template('speech_to_speech.html',title='Speech-to-speech')

@app.route('/multiple_voices')
def multiple_voices():
    return render_template('multiple_voices.html',title='Multiple voices')

@app.route('/get_voices')
def get_voices():
    try:
        voices = elevenlabs_service.list_voices()
        voices = [voice for voice in voices if voice.category == 'cloned']
        voices_data = [{'voice_id': voice.voice_id, 'name': voice.name} for voice in voices]
        return jsonify(voices_data)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Generate OpenAI speech
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


# Function to get a random sample text from the JSON file
def get_sample_text(design):
    samples = design.get('samples', {})
    backup_samples = [
        "Surprise! How odd, I'm sad, yet curious.",
        "Ah, such joy! Wait, fear grips me...",
        "Anger boils. Now, calm. A whirlwind of feelings.",
        "I am so angry that I want to scream!!",
        "AAAAAAAA!!! Get out of my way!!"
    ]
    sample_keys = ['sample1', 'sample2', 'sample3']
    #selected_samples = random.sample(sample_keys, 2)  # Select two sample keys
    #text = ''.join(samples.get(key, backup_samples[i]) for i, key in enumerate(selected_samples))  # Concatenate the selected samples
    text = ' '.join(samples.get(key, backup_samples[i]) for i, key in enumerate(sample_keys))  # Concatenate the samples
    return text

# Function to convert design to usable voice
def build_voice_from_design(design):
    # Ensure that assisted_voice is a dictionary
    if isinstance(design, str):
        try:
            design = json.loads(design)
        except json.JSONDecodeError:
            print("Error: assisted_voice is not a valid JSON string")
            return None
    
    # Get the random text from the json file
    text = get_sample_text(design)

    return VoiceDesign(
        name=design['name'],
        text=text,
        voice_description=design['description'],
        gender=Gender[design['gender']],
        age=Age[design['age']],
        accent=Accent[design['accent']],
        accent_strength=design['accent_strength'],
    )

def generate_random_variables():
    accents = ['australian', 'indian', 'african', 'american', 'british']
    genders = ['male', 'female']
    age_groups = ['young', 'middle_aged', 'old']

    voice_accent = random.choice(accents)
    voice_gender = random.choice(genders)
    voice_strength = round(random.uniform(0.3, 1.9), 2)  # Rounded to 2 decimal places
    voice_age = random.choice(age_groups)

    return voice_accent, voice_gender, voice_strength, voice_age


@app.route('/generate_voice_design', methods=['POST'])
def generate_voice_design():
    voice_accent, voice_gender, voice_strength, voice_age = generate_random_variables()
    prompt =  f"""This is a conversation with a helpful assistant designed to output JSON. 
        You help me design a voice for Elevenlabs. 
        I will give you a voice design, and you will add: 
        1. a creative description 
        2. a suiting name and 
        3. three sample sentences that suit the voice design:
        - a positive sentence that introduces the speaker
        - a neutral sentence that describes the voice
        - a negative sentence with a lot of emotion

        This is the voice design:
        - Gender: {voice_gender}  
        - Age: {voice_age}  
        - Accent: {voice_accent} 
        - Accent_strength on a scale from 0.3-1.9:: {voice_strength}

        Below you find an example of an output format in JSON:
        
        {{
                    "name": "Raj",
                    "description": "Energetic and youthful, with a vibrant Indian accent, like an enthusiastic college student.",
                    "gender": "male",
                    "age": "young",
                    "accent": "indian",
                    "accent_strength": 0.8,
                    "samples": {{
                        "sample1": "Hey there! I'm Raj, buzzing with energy like a lively campus on a sunny day.",
                        "sample2": "My voice carries the excitement of a new adventure, waiting just around the corner.",
                        "sample3": "Imagine the thrill of a breakthrough discovery, that's the zest I bring to every word."
                    }}
                }},
        """
    #print("Prompt: ", prompt)
    messages=[
        {"role": "system", "content": "You are a helpful assistant designed to output JSON."},
        {"role": "user", "content": prompt}
        ]
    assisted_voice = openai_service.get_json_completions(messages)
    voice_design = build_voice_from_design(assisted_voice)
    print(f"Voice design: {voice_design}")
    print(f"Playing voice design: {voice_design.name}")
    
    audio = voice_design.generate()
    filename = hashlib.sha256(voice_design.name.encode()).hexdigest() + '.mp3'
    audio_path = os.path.join('static', 'audio', filename)
    with open(audio_path, 'wb') as f:
        f.write(audio)

    return jsonify({'audio_file': audio_path, 'voice_name': voice_design.name, 'voice_text': voice_design.text})



if __name__ == "__main__":
    app.run(debug=True)