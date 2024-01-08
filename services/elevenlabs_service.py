
from elevenlabs import voices, Voice, VoiceSettings, generate, clone, stream, set_api_key, play, save
import threading
from elevenlabs.api import User, Models, History
import os
import datetime
import random
from pydub import AudioSegment
from elevenlabs import VoiceDesign, Gender, Age, Accent, play
from flask import url_for


set_api_key(os.getenv('ELEVENLABS_API_KEY'))
elevenlabs_model="eleven_multilingual_v2"

class ElevenLabsService:

    def get_user_info(self):
        user = User.from_api()
        return user

    #List all available voices.
    def list_voices(self):
        return voices()
        
    # Get all available voices with a specific label.
    def list_voices_with_label(self,label_key, label_value):
        voices = self.list_voices()
        return [voice for voice in voices if voice.category == 'cloned' and voice.labels.get(label_key) == label_value]
    
    def generate_speech(self, text, voice_id, settings):
        # Generate speech from text with customized settings.
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
    
    def generate_multiple_voices_bgvoice(self, text_voice_bgvoice_pairs, intro, outro, bgaudio, settings):
        voices = self.list_voices()
        if not voices:
            raise Exception("No voices available")

        audio_segments = self.generate_voice_segments(text_voice_bgvoice_pairs, settings)
        combined_audio = self.combine_audio_segments(audio_segments)

        if bgaudio:
            combined_audio = self.add_background_audio(combined_audio, bgaudio)

        if intro:
            combined_audio = self.add_intro_audio(combined_audio, intro)

        if outro:
            combined_audio = self.add_outro_audio(combined_audio, outro)

        return self.save_and_return_url(combined_audio)

    def generate_voice_segments(self, text_voice_bgvoice_pairs, settings):
        audio_segments = []
        for pair in text_voice_bgvoice_pairs:
            audio_segment = self.process_pair(pair, settings)
            if audio_segment:
                audio_segments.append(audio_segment)
        return audio_segments

    def process_pair(self, pair, settings):
        try:
            audio_data = self.generate_speech(pair['text'], pair['voiceId'], settings)
            speech_segment = self.create_audio_segment(audio_data)

            if pair.get('bgVoiceId'):
                speech_segment = self.add_background_to_segment(speech_segment, pair['bgVoiceId'])

            return speech_segment
        except Exception as e:
            print(f"Error generating speech for text '{pair['text']}': {e}")
            return None

    def create_audio_segment(self, audio_data):
        speech_filename = f"{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}.mp3"
        with open(speech_filename, 'wb') as f:
            f.write(audio_data)
        speech_segment = AudioSegment.from_file(speech_filename, format="mp3")
        os.remove(speech_filename)
        return speech_segment

    def add_background_to_segment(self, segment, bgvoice_filename):
        bgvoice_path = os.path.join('static','media', bgvoice_filename)
        bg_segment = AudioSegment.from_file(bgvoice_path, format="mp3")
        bg_segment = bg_segment * (len(segment) // len(bg_segment) + 1)
        return segment.overlay(bg_segment[:len(segment)])

    def add_background_audio(self, audio, bgaudio):
        bgaudio_path = os.path.join('static','media', bgaudio)
        bg_segment = AudioSegment.from_file(bgaudio_path, format="mp3")
        bg_segment = bg_segment * (len(audio) // len(bg_segment) + 1)
        return audio.overlay(bg_segment[:len(audio)])

    def add_intro_audio(self, audio, intro):
        intro_audio = AudioSegment.from_file(os.path.join('static','media', intro), format="mp3")
        return intro_audio + audio

    def add_outro_audio(self, audio, outro):
        outro_audio = AudioSegment.from_file(os.path.join('static','media', outro), format="mp3")
        return audio + outro_audio

    def combine_audio_segments(self, segments):
        return sum(segments)

    def save_and_return_url(self, audio):
        directory = os.path.join('static','media', 'output')
        if not os.path.exists(directory):
            os.makedirs(directory)

        filename = f"{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}_combined.mp3"
        combined_filename = os.path.join(directory, filename)
        audio.export(combined_filename, format='mp3')
        return url_for('static', filename='media/output/' + filename, _external=True)

    def generate_multiple_voices_bgvoice_backup(self, text_voice_bgvoice_pairs, intro, outro, bgaudio, settings):
        voices = self.list_voices()
        voices = [voice for voice in voices if voice.category == 'cloned']
        if not voices:
            raise Exception("No voices available")

        audio_segments = []
        
        if intro:
            intro_audio = AudioSegment.from_file(os.path.join('static','media', intro), format="mp3")
        pair_counter = 0
        for pair in text_voice_bgvoice_pairs:
            text = pair['text']
            voice_id = pair['voiceId']
            bgvoice_filename = pair.get('bgVoiceId')
            try:
                audio_data = self.generate_speech(text, voice_id, settings)
                speech_filename = f"{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}_{voice_id}.mp3"
                with open(speech_filename, 'wb') as f:
                    f.write(audio_data)

                speech_segment = AudioSegment.from_file(speech_filename, format="mp3")
                os.remove(speech_filename)

                if bgvoice_filename:
                    bgvoice_filename = os.path.join('static','media', bgvoice_filename)
                    bg_segment = AudioSegment.from_file(bgvoice_filename, format="mp3")
                    bg_segment = bg_segment * (len(speech_segment) // len(bg_segment) + 1)  # Herhaal het achtergrondgeluid
                    speech_segment = speech_segment.overlay(bg_segment[:len(speech_segment)])  # Overlay met spraak

                audio_segments.append(speech_segment)
                
                # Add intro audio before every sentence if provided - testing
                if intro_audio:
                    if pair_counter % 2 == 1 and pair_counter != len(text_voice_bgvoice_pairs) - 1:
                        audio_segments.append(intro_audio)

                    # Increment the pair counter
                    pair_counter += 1

            except Exception as e:
                print(f"Error generating speech for text '{text}': {e}")
                continue

        if not audio_segments:
            raise Exception("No audio segments were successfully processed")

        combined_audio = sum(audio_segments)
        print(f"Combined audio length: {combined_audio.duration_seconds}")
        if bgaudio:
            bgaudio = os.path.join('static','media', bgaudio)
            print(f"Processing Background audio: {bgaudio}")
            bg_segment = AudioSegment.from_file(bgaudio, format="mp3")
            bg_segment = bg_segment * (len(combined_audio) // len(bg_segment) + 1)  # Herhaal het achtergrondgeluid
            combined_audio = combined_audio.overlay(bg_segment[:len(combined_audio)])

        if intro:
            intro_audio = AudioSegment.from_file(os.path.join('static','media', intro), format="mp3")
            print(f"Processing Intro audio: {intro}")
            combined_audio = intro_audio + combined_audio

        if outro:
            outro_audio = AudioSegment.from_file(os.path.join('static','media', outro), format="mp3")
            print(f"Processing Outro audio: {outro}")
            combined_audio += outro_audio

        print(f"Combined audio length: {combined_audio.duration_seconds}")
        directory = os.path.join('static', 'media', 'output')
        if not os.path.exists(directory):
            os.makedirs(directory)

        filename = f"{datetime.datetime.now().strftime('%d%m%Y')}_intro_outro_combined.mp3"
        print(f"Filename: {filename}")
        combined_filename = os.path.join(directory, filename)
        print(f"Full path audio filename: {combined_filename}")
        combined_audio.export(combined_filename, format='mp3')
        audio_file_url = url_for('static', filename='media/output/' + filename, _external=True)
        return audio_file_url


    def generate_multiple_voices(self, text_voice_pairs, settings):
        voices = self.list_voices()
        voices = [voice for voice in voices if voice.category == 'cloned']
        #print(f"Available voices: {voices}")
        if not voices:
            raise Exception("No voices available")

        audio_segments = []

        for pair in text_voice_pairs:
            text = pair['text']
            #voice_id = pair.get('voiceId', random.choice(voices).get('voice_id')) - didn't work
            voice_id = pair['voiceId']
            #print(f"Generating speech for text '{text}' with voice '{voice_id}'")
            try:
                audio_data = self.generate_speech(text, voice_id, settings)
                filename = f"{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}_{voice_id}.mp3"
                with open(filename, 'wb') as f:
                    f.write(audio_data)

                audio_segment = AudioSegment.from_file(filename, format="mp3")
                os.remove(filename)
                audio_segments.append(audio_segment)

            except Exception as e:
                print(f"Error generating speech for text '{text}': {e}")
                continue

        if not audio_segments:
            raise Exception("No audio segments were successfully processed")

        combined_audio = sum(audio_segments)

        directory = os.path.join('static','media', 'output')
        if not os.path.exists(directory):
            os.makedirs(directory)

        filename = f"{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}_combined.mp3"
        combined_filename = os.path.join(directory, filename)
        combined_audio.export(combined_filename, format='mp3')

        # Genereer de toegankelijke URL voor het audiobestand
        audio_url = url_for('static', filename=f'media/output/{filename}', _external=True)

        return audio_url

    # Multiple voices overlayed on each other
    def generate_multiple_voices_overlay(self, sentences,first_voice_id, settings):
        voices = self.list_voices()
        voices = [voice for voice in voices if voice.category == 'cloned']
        if not voices:
            raise Exception("No voices available")

        longest_duration = 0
        audio_segments = []

        for i, sentence in enumerate(sentences):
            if i == 0:
                voice_id = first_voice_id
            else:
                voice = random.choice(voices)
                voice_id = voice.voice_id
            voice = random.choice(voices)
            try:
                audio_data = self.generate_speech(sentence, voice_id, settings)
                filename = f"{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}_{voice.voice_id}.mp3"
                with open(filename, 'wb') as f:
                    f.write(audio_data)

                audio_segment = AudioSegment.from_file(filename, format="mp3")
                os.remove(filename)

                audio_segments.append(audio_segment)
                longest_duration = max(longest_duration, len(audio_segment))
            except Exception as e:
                print(f"Error: {e}")
                continue

        # Gebruik het langste segment als basis
        combined_audio = AudioSegment.silent(duration=longest_duration)

        # Bereken starttijden voor elk segment
        num_segments = len(audio_segments)
        segment_spacing = longest_duration / max(1, num_segments - 1)

        for i, segment in enumerate(audio_segments):
            start_time = int(i * segment_spacing)  # Rond af naar het dichtstbijzijnde geheel getal
            fade_duration = int(min(1000, segment_spacing / 2))  # Fade-duur, maximaal 1 seconde

            # Fade in en fade out
            segment = segment.fade_in(fade_duration).fade_out(fade_duration)

            # Overlay het segment op de berekende starttijd
            combined_audio = combined_audio.overlay(segment, position=start_time)

        if combined_audio.duration_seconds == 0:
            raise Exception("No audio segments were successfully processed")

        directory = os.path.join('static','media', 'output')
        if not os.path.exists(directory):
            os.makedirs(directory)

        filename = f"{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}_combined.mp3"
        combined_filename = os.path.join(directory, filename)
        combined_audio.export(combined_filename, format='mp3')

        return combined_filename

    def generate_multiple_voices_bgaudio_overlay(self, sentences, first_voice_id, settings, background_audio_file):
        voices = self.list_voices()
        voices = [voice for voice in voices if voice.category == 'cloned']
        if not voices:
            raise Exception("No voices available")

        longest_duration = 0
        audio_segments = []

        for i, sentence in enumerate(sentences):
            if i == 0:
                voice_id = first_voice_id
            else:
                voice = random.choice(voices)
                voice_id = voice.voice_id
            voice = random.choice(voices)
            try:
                audio_data = self.generate_speech(sentence, voice_id, settings)
                filename = f"{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}_{voice.voice_id}.mp3"
                with open(filename, 'wb') as f:
                    f.write(audio_data)

                audio_segment = AudioSegment.from_file(filename, format="mp3")
                os.remove(filename)

                audio_segments.append(audio_segment)
                longest_duration = max(longest_duration, len(audio_segment))
            except Exception as e:
                print(f"Error: {e}")
                continue

        # Load the background audio file
        background_audio_file = os.path.join('static','media', 'bgaudio', background_audio_file)
        background_audio = AudioSegment.from_file(background_audio_file, format="mp3")

        # Use the background audio as the base
        combined_audio = background_audio[:longest_duration]

        # Overlay the segments on the combined audio
        for i, segment in enumerate(audio_segments):
            start_time = int(i * longest_duration / len(audio_segments))  # Calculate the start time for each segment
            combined_audio = combined_audio.overlay(segment, position=start_time)

        # Save the combined audio to a .mp3 file
        directory = os.path.join('static','media', 'output')
        filename = f"{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}_combined.mp3"
        combined_filename = os.path.join(directory, filename)
        combined_audio.export(combined_filename, format='mp3')

        return combined_filename

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
    
    

