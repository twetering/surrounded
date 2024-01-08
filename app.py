from flask import Flask, render_template, request, jsonify, url_for, session, send_file, Response
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
import glob
from flask_cors import CORS, cross_origin # needed for React on other server


# TO DO: Add logging
# TO DO: Add error handling
# TO DO: Add tests
# TO DO: Add documentation
# TO DO: Add authentication
# TO DO: Add database
# TO DO: Add Docker
# TO DO: Add CI/CD
# TO DO: Add frontend
# TO DO: Add voice designer
# TO DO: Add speech-to-speech
# TO DO: Add speech-to-text
# TO DO: Add Voice selection for multiple voices
# TO DO: Add Background music
# TO DO: Add Foley and sound effects
# TO DO: Add Assistants


app = Flask(__name__, static_folder='static')
CORS(app, supports_credentials=True)
load_dotenv()
elevenlabs_service = ElevenLabsService()
openai_service = OpenAIService()

# Set up logging
logging.basicConfig(level=logging.INFO)

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

@app.route('/generate-multiple-voices', methods=['POST'])
def generate_multiple_voices():
    DEFAULT_SETTINGS = {
        'stability': 0.3,
        'clarity': 0.98,
        'style': 0.5,
        'speakerBoost': True
    }

    data = request.get_json()
    print("DATA: ", data)
    text_voice_bgvoice_pairs = data.get('textVoicePairs', [])  # Expects a list of {text, voiceId, bgVoice}
    print("TEXT VOICE BGVOICE PAIRS: ", text_voice_bgvoice_pairs)
    voicesettings = data.get('voicesettings', DEFAULT_SETTINGS)
    intro = data.get('intro', {})
    outro = data.get('outro', {})
    bgaudio = data.get('bgaudio', {})
    
    # Pas de settings aan
    voicesettings = {
        'stability': float(voicesettings.get('stabilitysetting', DEFAULT_SETTINGS['stability'])),
        'clarity': float(voicesettings.get('claritysetting', DEFAULT_SETTINGS['clarity'])),
        'style': float(voicesettings.get('stylesetting', DEFAULT_SETTINGS['style'])),
        'speakerBoost': voicesettings.get('speakerBoost', DEFAULT_SETTINGS['speakerBoost']) in ['true', True, 'True']
    }

    service = ElevenLabsService()
    # old version without bgaudio: audio_file = service.generate_multiple_voices(text_voice_pairs, settings)
    audio_file = service.generate_multiple_voices_bgvoice(text_voice_bgvoice_pairs, intro,outro,bgaudio, voicesettings)
    return jsonify({'audio_file': audio_file})
    
# This route includes background audio but does not overlay the voices
@app.route('/generate-multiple-voices-bgaudio', methods=['POST'])
def generate_multiple_voices_bgaudio():
    data = request.get_json()
    sentences = data.get('sentences')
    app.logger.info(f"Received JSON data: {data}")  # Log the JSON payload
    first_voice_id = data.get('voice_id')
    settings = data.get('settings')
    background_audio_file = data.get('bgaudio')

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

        # Generate the multiple voices with background audio overlay
        audio_path = service.generate_multiple_voices_audio(sentences, first_voice_id, settings, background_audio_file)

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
    
# This route includes background audio AND overlays the voices
@app.route('/generate-multiple-voices-bgaudio-overlay', methods=['POST'])
def generate_multiple_voices_bgaudio_overlay():
    data = request.get_json()
    sentences = data.get('sentences')
    app.logger.info(f"Received JSON data: {data}")  # Log the JSON payload
    first_voice_id = data.get('voice_id')
    settings = data.get('settings')
    background_audio_file = data.get('bgaudio')

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

        # Generate the multiple voices with background audio overlay
        audio_path = service.generate_multiple_voices_bgaudio_overlay(sentences, first_voice_id, settings, background_audio_file)

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

@app.route('/amatourflits')
def amatourflits():
    return render_template('amatourflits.html',title='Amatourflits')

# Get all background audio files
@app.route('/get_bgaudio')
def get_bgaudio():

    try:
        # Get the list of all mp3 files in /static/audio/bgaudio
        bgaudio_files = glob.glob('static/audio/bgaudio/*.mp3')

        # Extract the filename from the full path
        bgaudio_files = [{'filename': os.path.basename(bgaudio_file)} for bgaudio_file in bgaudio_files]

        return jsonify(bgaudio_files)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Get all background audio files
@app.route('/api/audio')
def api_get_bgaudio():
    #print("API GET BGAUDIO", request.args.get('folder', default='bgaudio', type=str))
    try:
        folder_name = request.args.get('folder', default='bgaudio', type=str)
        audio_files_path = os.path.join('static', 'audio', folder_name, '*.mp3')
        audio_files = glob.glob(audio_files_path)
        #print("AUDIO FILES: ", audio_files)

        # Extract the filename from the full path
        audio_files = [{'filename': os.path.basename(file)} for file in audio_files]

        return jsonify({'files': audio_files})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Get all voices
@app.route('/get_voices')
def get_voices():
    try:
        voices = elevenlabs_service.list_voices()
        voices = [voice for voice in voices if voice.category == 'cloned']
        voices_data = [{'voice_id': voice.voice_id, 'name': voice.name} for voice in voices]
        return jsonify(voices_data)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Get voices with a specific label
@app.route('/get_voices_with_label/<label_key>/<label_value>')
def get_voices_with_label(label_key, label_value):
    try:
        voices = elevenlabs_service.list_voices_with_label(label_key, label_value)
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
            return jsonify({'error': 'Audio not found'}), 404
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
        voice_description=design['voice_description'],
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
    voice_accent_strength = round(random.uniform(0.3, 1.9), 2)  # Rounded to 2 decimal places
    voice_age = random.choice(age_groups)

    return voice_accent, voice_gender, voice_accent_strength, voice_age


@app.route('/generate_voice_design', methods=['POST'])
def generate_voice_design():
    voice_accent, voice_gender, voice_accent_strength, voice_age = generate_random_variables()
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
        - Accent_strength on a scale from 0.3-1.9:: {voice_accent_strength}

        Below you find an example of an output format in JSON:
        
        {{
                    "name": "Raj",
                    "voice_description": "Energetic and youthful, with a vibrant Indian accent, like an enthusiastic college student.",
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
    filename = f"{voice_design.name}_{voice_design.accent}_{voice_design.gender}_{voice_design.accent_strength}.mp3"    
    audio_path = os.path.join('static', 'audio', filename)
    with open(audio_path, 'wb') as f:
        f.write(audio)

    json = jsonify({
        'audio_file': audio_path, 
        'voice_name': voice_design.name,
        'voice_description': voice_design.voice_description,
        'voice_text': voice_design.text,
        'voice_accent': voice_design.accent,
        'voice_accent_strength': voice_design.accent_strength,
        'voice_age': voice_design.age,
        'voice_gender': voice_design.gender
        })
    
    return json



if __name__ == "__main__":
    app.run(debug=True)