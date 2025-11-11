# module/text_to_speech.py
import os
from dotenv import load_dotenv
from elevenlabs import ElevenLabs

# Load environment variables
load_dotenv()

class TextToSpeech:
    """Generate speech from text using ElevenLabs API and return as byte stream."""

    def __init__(self, api_key: str = None):
        """
        Initialize the ElevenLabs client.
        :param api_key: ElevenLabs API key (optional, falls back to .env)
        """
        self.api_key = api_key or os.getenv("ELEVENLABS_API_KEY")
        if not self.api_key:
            raise ValueError("❌ ELEVENLABS_API_KEY not found in environment or provided.")
        
        self.client = ElevenLabs(api_key=self.api_key, base_url="https://api.elevenlabs.io/")

    def text_to_speech(self, text: str, voice_id: str) -> bytes:
        """
        Convert text to speech using ElevenLabs and return as bytes.
        :param text: Text to convert
        :param voice_id: Voice ID to use
        :return: Audio bytes (MP3 format)
        """
        if not voice_id:
            raise ValueError("❌ voice_id must be provided.")
        if not text:
            raise ValueError("❌ text cannot be empty.")

        print(f"Generating speech using voice: {voice_id}...")

        # Request speech conversion
        response_stream = self.client.text_to_speech.convert(
            voice_id=voice_id,
            model_id="eleven_multilingual_v2",
            text=text,
            output_format="mp3_44100_128",
            voice_settings={
                "stability": 0.5,
                "similarity_boost": 0.9,
                "style": 1.0,
                "use_speaker_boost": True
            }
        )

        # Combine audio chunks
        audio_bytes = b"".join(chunk for chunk in response_stream if chunk)

        print(f"✅ Speech generation complete. Audio length: {len(audio_bytes)} bytes")
        return audio_bytes
