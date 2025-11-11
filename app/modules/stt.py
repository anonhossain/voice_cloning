# module/elevenlabs_transcriber.py
import os
import requests
from dotenv import load_dotenv
from io import BytesIO

# Load environment variables
load_dotenv()


class SpeechToText:
    """Transcribe audio files using ElevenLabs Speech-to-Text API."""

    def __init__(self, api_key: str = None, model_id: str = None, base_url: str = None):
        """
        Initialize the transcriber.
        :param api_key: ElevenLabs API key (falls back to .env if not provided)
        :param model_id: Transcription model ID
        :param base_url: ElevenLabs Speech-to-Text API URL
        """
        self.api_key = api_key or os.getenv("ELEVENLABS_API_KEY")
        self.model_id = model_id or os.getenv("TRANSCRIPTION_MODEL")
        self.base_url = base_url or os.getenv("URL_SPEECH_TO_TEXT")

        if not all([self.api_key, self.model_id, self.base_url]):
            raise ValueError("❌ Missing ElevenLabs API configuration.")

    def transcribe(self, file) -> str:
        """
        Transcribe an audio file and return the text.
        :param file: Either a file path (str) or a file-like object (BytesIO, UploadFile, etc.)
        :return: Transcribed text
        """
        # Determine if the input is a path or file-like object
        if isinstance(file, str):
            if not os.path.exists(file):
                raise FileNotFoundError(f"Audio file not found: {file}")
            file_name = os.path.basename(file)
            file_data = open(file, "rb")
            close_file = True
        elif isinstance(file, BytesIO) or hasattr(file, "read"):
            file_name = getattr(file, "name", "uploaded_audio")
            file_data = file
            close_file = False
        else:
            raise TypeError("File must be a path string or a file-like object.")

        try:
            response = requests.post(
                self.base_url,
                headers={"xi-api-key": self.api_key},
                data={"model_id": self.model_id, "file_format": "other"},
                files={"file": (file_name, file_data)},
            )
            response.raise_for_status()
            result = response.json()

            if "text" in result:
                return result["text"]
            else:
                raise Exception(f"Transcription failed: {result}")

        finally:
            if close_file:
                file_data.close()
