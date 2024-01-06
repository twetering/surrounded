import os
from praatio import textgrid
from pydub import AudioSegment
from elevenlabs import Voices, Voice, VoiceSettings, generate, clone, stream, set_api_key, play, save
from elevenlabs.api import User, Models, History
from elevenlabs import VoiceDesign, Gender, Age, Accent, play
from dotenv import load_dotenv
import datetime

# from elevenlabs_api import ElevenLabsAPI  # Hypothetische API-bibliotheek voor Elevenlabs
load_dotenv()  # This loads the variables from .env

set_api_key(os.getenv('ELEVENLABS_API_KEY'))

def generate_speech(text, voice_id):
    """
    Genereer spraak met Elevenlabs en sla het audiobestand op.
    """
    # Deze functie is hypothetisch en vereist de Elevenlabs API
    
    # Function to test ElevenLabs text-to-speech
    audio = generate(
        text= text,
        model="eleven_multilingual_v2",
        voice=Voice(
            voice_id= voice_id,
            settings=VoiceSettings(stability=0.2, similarity_boost=0.1, style=0.3, use_speaker_boost=True)
        )
    )
    
    play(audio)
    
    # api.generate_speech(text, voice_id, output_path=audio_path)
    return audio

def open_textgrid(textgrid_path):
    """
    Open een TextGrid-bestand en vang fouten op.
    """
    try:
        tg = textgrid.openTextgrid(textgrid_path, includeEmptyIntervals=True)
        return tg
    except Exception as e:
        print(f"Fout bij het openen van TextGrid: {e}")
        return None

def transcribe_and_identify_segment(audio_path, target_phrase):
    """
    Transcribeer het audiobestand en identificeer de segmenten van de doelfrase.
    """
    filename = f"praat_{datetime.datetime.now().strftime('%Y%m%d')}_original.mp3"
    with open(filename, 'wb') as f:
        f.write(audio_path)
    tg_path = filename.replace('.mp3', '.TextGrid')
    tg = open_textgrid(tg_path)
    if tg is None:
        print("Kan TextGrid-bestand niet verwerken.")
        return None

    # Identificeer segmenten met de doelfrase
    # Voor deze demonstratie gaan we ervan uit dat 'target_phrase' overeenkomt met een label in het TextGrid.
    for tier in tg.tierDict.values():
        for start, end, label in tier.entries:
            if label == target_phrase:
                print(f"Segment '{target_phrase}' gevonden van {start} tot {end} seconden.")

def main():
    text = "Let's go to the moon!!, he screamed in a loud voice"
    voice_id = "pMikxrtSTkFoa3lMbjNO"
    output_filename = "generated_speech.mp3"

    # Stap 1: Genereer MP3 met Elevenlabs
    audio = generate_speech(text, voice_id)

    # Stap 2: Transcribeer en identificeer segmenten
    target_phrase = "he screamed in a loud voice"
    transcribe_and_identify_segment(audio, target_phrase)

    # Stap 3: Verwijder een deel van het audiobestand met PyDub (simulatie)

    # Stap 4: Download het nieuwe audiobestand naar de computer (simulatie)

if __name__ == "__main__":
    main()