import os
import requests
from dotenv import load_dotenv

class ElevenLabsTranscriber:
    def __init__(self):
        load_dotenv()
        self.api_key = os.getenv("ELEVENLABS_API_KEY")
        self.base_url = "https://api.elevenlabs.io/v1/speech-to-text"
        self.model_id = "scribe_v1"

    def transcribe(self, file_path: str):
        """Transcribe the given audio file and return the text or error."""
        try:
            with open(file_path, 'rb') as audio_file:
                response = requests.post(
                    self.base_url,
                    headers={
                        "xi-api-key": self.api_key
                    },
                    data={
                        'model_id': self.model_id,
                        'file_format': "other",
                    },
                    files={
                        'file': (file_path, audio_file),
                    },
                )

            result = response.json()
            if "text" in result:
                return result["text"]
            else:
                return {"error": result}

        except Exception as e:
            return {"error": str(e)}

def main():
    file_path = "file/Recording.m4a"  # Change path if needed
    transcriber = ElevenLabsTranscriber()
    result = transcriber.transcribe(file_path)

    if isinstance(result, str):
        print("Transcribed Text:\n")
        print(result)
    else:
        print("Error in transcription:", result)

if __name__ == "__main__":
    main()
