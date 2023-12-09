
import os
from elevenlabs import voices, Voice, VoiceSettings, generate, clone, stream, set_api_key, play, save
import threading
from elevenlabs.api import User, Models, History
import datetime
from elevenlabs import VoiceDesign, Gender, Age, Accent, play
from dotenv import load_dotenv

load_dotenv()  # This loads the variables from .env

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

if __name__ == "__main__":
    test_text_to_speech()
