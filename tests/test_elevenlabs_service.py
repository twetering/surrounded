import unittest
from unittest.mock import patch
from services.elevenlabs_service import ElevenLabsService
from elevenlabs import Voice, VoiceSettings


class ElevenLabsServiceTests(unittest.TestCase):

    def setUp(self):
        self.service = ElevenLabsService()

    def test_list_voices(self):
        # Mock the voices() method
        with patch('services.elevenlabs_service.voices') as mock_voices:
            mock_voices.return_value = ['voice1', 'voice2', 'voice3']
            voice_list = self.service.list_voices()
            self.assertEqual(voice_list, ['voice1', 'voice2', 'voice3'])

    def test_generate_speech_with_settings(self):
        # Mock the generate() method
        with patch('services.elevenlabs_service.generate') as mock_generate:
            mock_generate.return_value = 'audio_data'
            text = 'Hello, world!'
            voice_id = 'voice1'
            settings = {'stability': 0.8, 'clarity': 0.6, 'style': 0.2, 'speakerBoost': False}
            audio = self.service.generate_speech(text, voice_id, settings)
            self.assertEqual(audio, 'audio_data')
            mock_generate.assert_called_with(text=text, voice=Voice(voice_id=voice_id, settings=VoiceSettings(stability=0.8, clarity=0.6, style=0.2, use_speaker_boost=False)), model="eleven_multilingual_v2")

    def test_generate_speech_without_settings(self):
        # Mock the generate() method
        with patch('services.elevenlabs_service.generate') as mock_generate:
            mock_generate.return_value = 'audio_data'
            text = 'Hello, world!'
            voice_id = 'voice1'
            audio = self.service.generate_speech(text, voice_id, None)
            self.assertEqual(audio, 'audio_data')
            mock_generate.assert_called_with(text=text, voice=Voice(voice_id=voice_id), model="eleven_multilingual_v2")

    # Add more test cases for other methods

if __name__ == '__main__':
    unittest.main()