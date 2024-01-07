import os
import tempfile
from pydub import AudioSegment
from openai import OpenAI
from dotenv import load_dotenv
from elevenlabs import generate, Voice, VoiceSettings, set_api_key
from faster_whisper import WhisperModel
import stable_whisper
import json

# Laad environment variabelen
load_dotenv()
openai_api_key = os.getenv('OPENAI_API_KEY')
elevenlabs_api_key = os.getenv('ELEVENLABS_API_KEY')

# Instellen van API-keys
set_api_key(elevenlabs_api_key)
openai_audio = OpenAI(api_key=openai_api_key)

''' 
we use faster whisper and stable whisper to transcribe audio
def transcribe_audio_with_prompt(audio_path, prompt):
    with open(audio_path, "rb") as audio_file:
        transcript = openai_audio.audio.transcriptions.create(
            model="whisper-1", 
            file=audio_file,
            prompt=prompt,
            response_format="srt"
        )
        return transcript
'''
    
def transcribe_audio(audio_path, prompt):
    
    model = stable_whisper.load_faster_whisper('base')
    result = model.transcribe_stable(audio_path, initial_prompt=prompt)
    # Opslaan als een JSON-bestand
    transcript_file = 'audio.json'
    result.save_as_json(transcript_file)

    # Het JSON-bestand inlezen en de inhoud returnen
    with open(transcript_file, 'r') as file:
        transcript_data = json.load(file)
    # os.remove(transcript_file)
    return transcript_data

def generate_speech(text, voice_id):
    audio = generate(
        text=text,
        model="eleven_multilingual_v2",
        voice=Voice(
            voice_id=voice_id,
            settings=VoiceSettings(stability=0.3, similarity_boost=0.98, style=0.5, use_speaker_boost=True)
        )
    )
    return audio

def find_keyword_times(data, start_word, end_word):
    start_time = None
    end_time = None
    for segment in data['segments']:
        for word_info in segment['words']:
            cleaned_word = word_info['word'].strip().lower().strip(',.!?:;')
            if cleaned_word == start_word.lower():
                print('Start word Word Info: ',word_info)
                start_time = word_info['end']
            if end_word and cleaned_word == end_word.lower():
                print('End word Word Info: ',word_info)
                end_time = word_info['start']
                break
    return start_time, end_time

def main():
    text = "Rising anger, whispering to shouting, superman. 'For Ukraine, this endurance race for freedom is far from over!', obama screamed."
    voice_id = "pMikxrtSTkFoa3lMbjNO"
    start_word = "superman"
    end_word = "obama"

    # Genereer MP3 met Elevenlabs
    audio_data = generate_speech(text, voice_id)

    # Sla de audio op in een tijdelijk bestand
    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as tmp_file:
        tmp_file.write(audio_data)
        audio_path = tmp_file.name

    # Prompt is a string with start_word, end_word
    prompt = f"{start_word}, {end_word}"
    # Transcribeer en identificeer segmenten met Whisper
    transcript_data = transcribe_audio(audio_path, prompt)

    #print(transcript_data)
    # Controleer of de transcriptie succesvol was
    if transcript_data is None:
        print("Transcriptie mislukt.")
        return

    # Verwerk de transcriptie
    start_time, end_time = find_keyword_times(transcript_data, start_word, end_word)

    # Verwijder een deel van het audiobestand met PyDub
    audio = AudioSegment.from_file(audio_path)

    # Definieer start_time_ms en end_time_ms
    start_time_ms = int(start_time * 1000) if start_time is not None else None
    end_time_ms = int(end_time * 1000) if end_time is not None else None

    # Trim het audiobestand gebaseerd op start_time_ms en end_time_ms
    if start_time_ms is not None and end_time_ms is not None:
        trimmed_audio = audio[start_time_ms:end_time_ms]
    elif start_time_ms is not None:
        trimmed_audio = audio[start_time_ms:]
    elif end_time_ms is not None:
        trimmed_audio = audio[:end_time_ms]
    else:
        trimmed_audio = audio

    trimmed_audio.export("edited_audio.mp3", format="mp3")

    # Verwijder tijdelijke bestanden
    os.remove(audio_path)

if __name__ == "__main__":
    main()