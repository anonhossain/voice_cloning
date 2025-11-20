# # module/text_to_speech.py
# import os
# from dotenv import load_dotenv
# from elevenlabs import ElevenLabs

# # Load environment variables
# load_dotenv()

# class TextToSpeech:
#     """Generate speech from text using ElevenLabs API and return as byte stream."""

#     def __init__(self, api_key: str = None):
#         """
#         Initialize the ElevenLabs client.
#         :param api_key: ElevenLabs API key (optional, falls back to .env)
#         """
#         self.api_key = api_key or os.getenv("ELEVENLABS_API_KEY")
#         if not self.api_key:
#             raise ValueError("❌ ELEVENLABS_API_KEY not found in environment or provided.")
        
#         self.client = ElevenLabs(api_key=self.api_key, base_url="https://api.elevenlabs.io/")

#     def text_to_speech(self, text: str, voice_id: str) -> bytes:
#         """
#         Convert text to speech using ElevenLabs and return as bytes.
#         :param text: Text to convert
#         :param voice_id: Voice ID to use
#         :return: Audio bytes (MP3 format)
#         """
#         if not voice_id:
#             raise ValueError("❌ voice_id must be provided.")
#         if not text:
#             raise ValueError("❌ text cannot be empty.")

#         print(f"Generating speech using voice: {voice_id}...")

#         # Request speech conversion
#         response_stream = self.client.text_to_speech.convert(
#             voice_id=voice_id,
#             model_id="eleven_multilingual_v2",
#             text=text,
#             output_format="mp3_44100_128",
#             voice_settings={
#                 "stability": 0.5,
#                 "similarity_boost": 0.9,
#                 "style": 1.0,
#                 "speed": 0.75,
#                 "use_speaker_boost": True
#             }
#         )

#         # Combine audio chunks
#         audio_bytes = b"".join(chunk for chunk in response_stream if chunk)

#         print(f"✅ Speech generation complete. Audio length: {len(audio_bytes)} bytes")
#         return audio_bytes
    
#         print("Deleting voice id")



# module/text_to_speech.py
import os
from dotenv import load_dotenv
from elevenlabs import ElevenLabs
from elevenlabs.core import ApiError

# Load environment variables
load_dotenv()

class TextToSpeech:
    """Generate speech from text using ElevenLabs API and optionally delete the voice afterwards."""

    def __init__(self, api_key: str = None):
        """
        Initialize the ElevenLabs client.
        :param api_key: ElevenLabs API key (optional, falls back to .env)
        """
        self.api_key = api_key or os.getenv("ELEVENLABS_API_KEY")
        if not self.api_key:
            raise ValueError("ELEVENLABS_API_KEY not found in environment or provided.")
        
        # Correct client initialization (official SDK uses `api_key` directly)
        self.client = ElevenLabs(api_key=self.api_key)

    def text_to_speech(
        self,
        text: str,
        voice_id: str,
        delete_after_use: bool = False
    ) -> bytes:
        """
        Convert text to speech using ElevenLabs and return as bytes.
        Optionally deletes the voice immediately after generation.

        :param text: Text to convert
        :param voice_id: Voice ID to use
        :param delete_after_use: If True, deletes the voice from ElevenLabs after generating audio
        :return: Audio bytes (MP3 format)
        """
        if not voice_id:
            raise ValueError("voice_id must be provided.")
        if not text:
            raise ValueError("text cannot be empty.")

        print(f"Generating speech using voice: {voice_id}...")

        try:
            # Generate speech
            response_stream = self.client.text_to_speech.convert(
                voice_id=voice_id,
                model_id="eleven_multilingual_v2",
                text=text,
                output_format="mp3_44100_128",
                voice_settings={
                    "stability": 0.5,
                    "similarity_boost": 0.9,
                    "style": 1.0,
                    "speed": 0.75,
                    "use_speaker_boost": True
                }
            )

            # Combine streamed chunks
            audio_bytes = b"".join(chunk for chunk in response_stream if chunk)
            print(f"Speech generation complete. Audio length: {len(audio_bytes)} bytes")

            # Optionally delete the voice right after use
            if delete_after_use:
                self.delete_voice(voice_id)
                print(f"Voice {voice_id} deleted successfully.")

            return audio_bytes

        except ApiError as e:
            if e.status_code == 403 and "detected_captcha_voice" in str(e):
                print("Voice is blocked by ElevenLabs (captcha/protected voice). Cannot generate or delete.")
            else:
                print(f"ElevenLabs API Error: {e}")
            raise

    def delete_voice(self, voice_id: str) -> bool:
        """
        Permanently delete a voice from your ElevenLabs account.
        :param voice_id: The voice ID to delete
        :return: True if deleted, False if already gone or error
        """
        if not voice_id:
            raise ValueError("voice_id is required to delete a voice.")

        try:
            print(f"Attempting to delete voice ID: {voice_id}...")
            self.client.voices.delete(voice_id=voice_id)
            print(f"Successfully deleted voice {voice_id}")
            return True
        except ApiError as e:
            if e.status_code == 404:
                print(f"Voice {voice_id} not found (already deleted or never existed).")
            elif e.status_code == 403:
                print(f"Forbidden: You don't have permission to delete voice {voice_id} (might be protected).")
            else:
                print(f"Failed to delete voice {voice_id}: {e}")
            return False
        except Exception as e:
            print(f"Unexpected error while deleting voice {voice_id}: {e}")
            return False


# Example usage (uncomment to test):
# if __name__ == "__main__":
#     tts = TextToSpeech()
#     audio = tts.text_to_speech(
#         text="Hello, this is a test. The voice will be deleted immediately after.",
#         voice_id="NyD6ahwP6Kp8tu3kNrgY",
#         delete_after_use=True  # Automatically deletes after use
#     )
#     with open("output.mp3", "wb") as f:
#         f.write(audio)