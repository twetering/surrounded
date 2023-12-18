
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

if __name__ == "__main__":
    #test_text_to_speech()
    #print_cloned_voices()
    #build_voice_design()
    #play_random_voice()
    play_completed_voice()
