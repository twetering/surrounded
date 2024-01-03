
import os
from elevenlabs import Voices, Voice, VoiceSettings, generate, clone, stream, set_api_key, play, save
import threading
from elevenlabs.api import User, Models, History
import datetime
from elevenlabs import VoiceDesign, Gender, Age, Accent, play
from dotenv import load_dotenv
import json
import random
from services.openai_service import OpenAIService
import requests
import uuid

load_dotenv()  # This loads the variables from .env

# Instantie van de OpenAI-service
openai_service = OpenAIService()

# List of voice designs
voice_designs = []

set_api_key(os.getenv('ELEVENLABS_API_KEY'))
# Function to test ElevenLabs text-to-speech
def test_text_to_speech():
    audio = generate(
        text="Hello! My name is Bella.",
        model="eleven_multilingual_v2",
        voice=Voice(
            voice_id='FiugCfL2Gbnicjj8Un2h',
            settings=VoiceSettings(stability=0.2, similarity_boost=0.1, style=0.3, use_speaker_boost=True)
        )
    )
    
    play(audio)

# Function to print all cloned voices
def print_cloned_voices():
    voices = Voices.from_api()
    cloned_voices = [voice for voice in voices if voice.category == 'cloned']
    for voice in cloned_voices:
        print(voice)

def voice_to_dict(voice):
    return {
        'voice_id': voice.voice_id,
        'name': voice.name,
        'category': voice.category,
        'description': voice.description,
        'labels': voice.labels,
        'samples': [sample_to_dict(sample) for sample in voice.samples],
        'design': voice.design,
        'preview_url': voice.preview_url,
        'settings': voice.settings,
    }

def sample_to_dict(sample):
    return {
        'sample_id': sample.sample_id,
        'file_name': sample.file_name,
        'mime_type': sample.mime_type,
        'size_bytes': sample.size_bytes,
        'hash': sample.hash,
    }

def save_cloned_voices():
    voices = Voices.from_api()
    cloned_voices = [voice for voice in voices if voice.category == 'cloned']

    # Convert the cloned voices to dictionaries
    cloned_voices_dict = [voice_to_dict(voice) for voice in cloned_voices]

    with open('static/data/cloned_voices.json', 'w') as f:
        json.dump(cloned_voices_dict, f, indent=4)

def save_cloned_voices_labels():
    voices = Voices.from_api()
    cloned_voices = [voice for voice in voices if voice.category == 'cloned']

    # Convert the cloned voices to dictionaries with only 'voice_id', 'name', and 'labels'
    cloned_voices_dict = [{'voice_id': voice.voice_id, 'name': voice.name, 'labels': voice.labels} for voice in cloned_voices]

    with open('static/data/voices_labels.json', 'w') as f:
        json.dump(cloned_voices_dict, f, indent=4)

# Build a voice design object
def build_voice_design():
    design = VoiceDesign(
        name='Lexa',
        text="I am VERY ANGRY TODAY!! Very, very ANGRY!! ... I am so angry that I want to scream!! AAAAAAAA!!! Get out of my way!!",
        voice_description="Very angry voice, always negative about everything, unusually high pitch like a scream.",
        gender=Gender.female,
        age=Age.middle_aged,
        accent=Accent.british,
        accent_strength=1.9,
    )

    # Generate audio from the design, and play it to test if it sounds good (optional)
    audio = design.generate()
    play(audio)

    # Convert design to usable voice
    voice = Voice.from_design(design)

# Function to load voice designs from a JSON file
def load_voice_designs(file_path):
    with open(file_path, 'r') as file:
        data = json.load(file)
    return data['voicedesigns']

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

# Path to the JSON file
json_file_path = os.path.join('static', 'data', 'voicedesigns.json')

# Load the voice designs
voice_designs = load_voice_designs(json_file_path)

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


# Function to play a random voice design
def play_random_voice():
    design = random.choice(voice_designs)
    voice_design = build_voice_from_design(design)
    print(f"Voice design: {voice_design}")
    print(f"Playing voice design: {voice_design.name}")
    audio = voice_design.generate()
    play(audio)

def generate_random_variables():
    accents = ['australian', 'indian', 'african', 'american', 'british']
    genders = ['male', 'female']
    age_groups = ['young', 'middle_aged', 'old']

    voice_accent = random.choice(accents)
    voice_gender = random.choice(genders)
    voice_strength = round(random.uniform(0.3, 1.9), 2)  # Rounded to 2 decimal places
    voice_age = random.choice(age_groups)

    return voice_accent, voice_gender, voice_strength, voice_age

def play_completed_voice():
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
    play(audio)


"""
    This function converts all audio files in the 'static/audio/bgaudio' directory from .wav or .flac format to .mp3 format.
    After conversion, the original file is deleted.

    It uses the pydub library to load and export audio files. 

    Note: The function does not return anything.

    Raises:
        Could raise an exception if the audio file cannot be loaded or exported, or if the original file cannot be deleted.
    """

def convert_audio_files():
    import os
    from pydub import AudioSegment
    # Directory containing the audio files
    directory = 'static/audio/amatourflits/bgaudio'

    # Iterate over all files in the directory
    for filename in os.listdir(directory):
        # Check if the file is an audio file
        if filename.endswith('.wav') or filename.endswith('.flac'):
            # Construct the full file path
            filepath = os.path.join(directory, filename)

            # Load the audio file
            audio = AudioSegment.from_file(filepath)

            # Construct the output file path
            output_filepath = os.path.join(directory, os.path.splitext(filename)[0] + '.mp3')

            # Export the audio file as .mp3
            audio.export(output_filepath, format='mp3')

            # Optionally, delete the original file
            os.remove(filepath)



def test_audio_pipeline():
    from diffusers import AudioLDM2Pipeline
    import torch
    import scipy

    repo_id = "cvssp/audioldm2"
    pipe = AudioLDM2Pipeline.from_pretrained(repo_id, torch_dtype=torch.float32)
    pipe = pipe.to("cpu")

    prompt = "Techno music with a strong, upbeat tempo and high melodic riffs."
    audio = pipe(prompt, num_inference_steps=200, audio_length_in_s=10.0).audios[0]

    scipy.io.wavfile.write("techno.wav", rate=16000, data=audio)

def download_podcasts(rss_url):

    import os
    import requests
    import shutil
    from xml.etree import ElementTree as ET
    # Fetch the RSS feed
    response = requests.get(rss_url)

    # Parse the RSS feed
    root = ET.fromstring(response.content)

    # Extract the titles, publication dates, and MP3 links
    titles = [item.find('title').text for item in root.findall('.//item')]
    pubDates = [item.find('pubDate').text for item in root.findall('.//item')]
    mp3Links = [item.find('enclosure').get('url') for item in root.findall('.//item')]

    # Create a directory for the downloaded files if it doesn't exist
    os.makedirs('downloaded_podcasts', exist_ok=True)

    # Loop over the MP3 links to download and rename
    for i in range(len(mp3Links)):
        title = ''.join(e for e in titles[i] if e.isalnum())
        date = pubDates[i].replace(' ', '_')
        filename = f"downloaded_podcasts/{date}_{title}.mp3"

        # Download the MP3 file
        response = requests.get(mp3Links[i], stream=True)
        with open(filename, 'wb') as out_file:
            shutil.copyfileobj(response.raw, out_file)


def fast_whisper():
    import os
    import torch
    from transformers import pipeline
    from transformers.utils import is_flash_attn_2_available

    pipe = pipeline(
        "automatic-speech-recognition",
        model="openai/whisper-large-v3", # select checkpoint from https://huggingface.co/openai/whisper-large-v3#model-details
        torch_dtype=torch.float16,
        device="mps", # or mps for Mac devices or cuda:0 for Linux Nvidia devices
        model_kwargs={"use_flash_attention_2": is_flash_attn_2_available()},
    )

    # Loop over all audio files in the /whisper/ directory
    for filename in os.listdir('whisper/'):
        if filename.endswith('.mp3') or filename.endswith('.wav'):
            print(f"Processing {filename}...")
            try:
                # Process the audio file with the Whisper ASR model
                outputs = pipe(
                    f"whisper/{filename}",
                    chunk_length_s=30,
                    batch_size=1,
                    return_timestamps=True,
                )
                print(f"ASR processing completed for {filename}.")
                print(f"Outputs: {outputs}")

                # Write the results to a .txt file with the same name as the audio file
                with open(f"whisper/{os.path.splitext(filename)[0]}.txt", 'w') as f:
                    for output in outputs:
                        f.write(output['text'] + '\n')

                print(f"Finished processing {filename}")
            except Exception as e:
                import traceback
                print(f"Failed to process {filename}: {e}")
                traceback.print_exc()


def download_samples_for_cloned_voices(output_dir):
    import os
    import requests

    set_api_key(os.getenv('ELEVENLABS_API_KEY'))
    voices = Voices.from_api()
    cloned_voices = [voice for voice in voices if voice.category == 'cloned']

    for voice in cloned_voices:
        # Assuming each voice object has an 'id' attribute
        voice_id = voice.voice_id

        # Assuming each voice object has a 'samples' attribute that is a list of sample IDs
        for sample in voice.samples:
            sample_id = sample.sample_id
            # Construct the URL
            url = f"https://api.elevenlabs.io/v1/voices/{voice_id}/samples/{sample_id}/audio"

            # Define the headers for the request
            headers = {
                'xi-api-key': os.getenv("ELEVENLABS_API_KEY")
            }
            print(f"Downloading sample {sample.sample_id} for voice {voice_id}... with url {url} and headers {headers}")
            # Send a GET request to the URL
            response = requests.get(url, headers=headers)

            # Check if the request was successful
            if response.status_code == 200:
                # Get the file name from the sample URL
                file_name = f"{voice.name}_{voice_id}_{sample_id}.mp3"

                # Create the output path
                output_path = os.path.join(output_dir, file_name)

                # Create the directory if it doesn't exist
                os.makedirs(os.path.dirname(output_path), exist_ok=True)

                # Write the content of the response to a file
                with open(output_path, 'wb') as file:
                    file.write(response.content)
            else:
                print(f"Error: Received status code {response.status_code} from Elevenlabs API")
            

def download_samples_initialize():
    # Specify the voice_id and sample_id
    #voice_id = 'pMikxrtSTkFoa3lMbjNO'  # Replace with the actual voice_id
    #sample_id = 'qeuxjTethFiZigIaf6A7'  # Replace with the actual sample_id

    # Specify the output directory in your file system.
    output_dir = "static/audio/samples"

    # Download the sample
    download_samples_for_cloned_voices(output_dir)

# Test the function with a URL
if __name__ == "__main__":
    #test_text_to_speech()
    #print_cloned_voices()
    #save_cloned_voices()
    #build_voice_design()
    #play_random_voice()
    #play_completed_voice()
    convert_audio_files()
    #test_audio_pipeline()
    #download_podcasts("https://feeds.acast.com/public/shows/live-slow-ride-fast")
    #fast_whisper()
    #print_sample_audio('pMikxrtSTkFoa3lMbjNO', 'qeuxjTethFiZigIaf6A7')  # Replace with the actual voice_id and sample_id
    #download_samples_initialize()
