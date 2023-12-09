
from elevenlabs import voices, Voice, VoiceSettings, generate, clone, stream, set_api_key, play, save
import threading
from elevenlabs.api import User, Models, History
import os
import datetime
from elevenlabs import VoiceDesign, Gender, Age, Accent, play

set_api_key(os.getenv('ELEVENLABS_API_KEY'))
elevenlabs_model="eleven_multilingual_v2"

class ElevenLabsService:

    def get_user_info(self):
        user = User.from_api()
        return user

    def list_voices(self):
        """ Lijst alle beschikbare stemmen op. """
        return voices()
    
    def generate_speech(self, text, voice_id, settings):
        # Generate speech from text with customized settings."""
        # If settings are provided, construct a VoiceSettings object
        
        if settings:
            print("Settings provided: ", settings)
            
            voice_settings = VoiceSettings(
                stability=settings.get('stability', 0.71),  # Provide default value if not set
                similarity_boost=settings.get('clarity', 0.5),
                style=settings.get('style', 0.1),
                use_speaker_boost=settings.get('speakerBoost', True)
            )
            voice = Voice(voice_id=voice_id, settings=voice_settings)
        else:
            # If no settings are provided, just create a Voice object without VoiceSettings
            print("No settings provided, using default voice settings")
            settings = self.get_default_voice_settings()
            voice = Voice(voice_id=voice_id,settings=settings)

        # Generate the audio using the voice and text
        try:
            audio = generate(text=text, voice=voice, model="eleven_multilingual_v2")
            return audio
        except Exception as e:
            print(f"Error generating speech: {e}")
            raise e


    def clone_voice(self, name, description, sample_files):
        """ Clone een stem. """
        return clone(name=name, description=description, files=sample_files)

    def stream_speech(self, text, voice_id=None, settings=None, model=None, is_text_stream=False):
        """ Stream spraak in realtime. """
        if is_text_stream:
            text_generator = self._text_stream_generator(text)
        else:
            text_generator = text

        if settings:
            voice = Voice(voice_id=voice_id, settings=settings) if voice_id else None
        else:
            voice = voice_id

        audio_stream = generate(text=text_generator, voice=voice, model=model, stream=True)
        stream_thread = threading.Thread(target=stream, args=(audio_stream,))
        stream_thread.start()
        return stream_thread

    def _text_stream_generator(self, text_chunks):
        """ Hulpfunctie om tekst in chunks te streamen. """
        for chunk in text_chunks:
            yield chunk

    def get_available_models(self):
        """ Haal een lijst van beschikbare modellen op. """
        models = Models.from_api()
        return models

    def get_default_voice_settings(self):
        """ Geef de standaardinstellingen voor stemmen terug. """
        return VoiceSettings(stability=0.71, similarity_boost=0.5, style=0.1, use_speaker_boost=True)

    def get_user_history(self):
        history = History.from_api()
        formatted_history = [{
            'history_item_id': item.history_item_id,
            'request_id': item.request_id,
            'voice_name': self.get_voice_name_by_id(item.voice_id),
            'text': item.text,
            'date': item.date.isoformat() if isinstance(item.date, datetime.datetime) else item.date,
            'audio_url': '/path/to/audio/' + item.history_item_id + '.mp3'  # Pas dit aan aan je bestandsopslaglogica
            # Voeg eventueel andere velden toe
        } for item in history.history]
        return formatted_history

    def save_audio(self, audio_bytes, filename):
        """ Sla audiobytes op in een bestand. """
        save(audio=audio_bytes, filename=filename)

    def play_audio(self, audio_bytes, use_notebook=False, use_ffmpeg=True):
        """ Speel audiobytes af. """
        play(audio=audio_bytes, notebook=use_notebook, use_ffmpeg=use_ffmpeg) 

    def get_audio_data(self, history_item_id):
        history = History.from_api()
        for item in history.history:
            if item.history_item_id == history_item_id:
                return item.audio  # Dit zou de audiogegevens moeten zijn
        return None  # Geen overeenkomend item gevonden
   
    def __init__(self):
        self.voices_dict = {voice.voice_id: voice.name for voice in voices()}

    def get_voice_name_by_id(self, voice_id):
        return self.voices_dict.get(voice_id, "Onbekende Stem")

    def create_custom_voice(self, name, description, gender, age, accent, accent_strength=1.0):
        """ Creëer een aangepast stemontwerp. """
        design = VoiceDesign(
            name=name,
            text=description,
            gender=gender,
            age=age,
            accent=accent,
            accent_strength=accent_strength,
        )
        return design
    

