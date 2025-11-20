import os
import requests
from dotenv import load_dotenv

# ✅ Load API key
load_dotenv()
ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY")
TRANSCRIPTION_MODEL = os.getenv("TRANSCRIPTION_MODEL")
URL_SPEECH_TO_TEXT = os.getenv("URL_SPEECH_TO_TEXT")
OUTPUT_DIRECTORY = os.getenv("OUTPUT_DIRECTORY")


class ElevenLabsTranscriber:
    def __init__(self):
        self.api_key = ELEVENLABS_API_KEY
        self.base_url = URL_SPEECH_TO_TEXT
        self.model_id = TRANSCRIPTION_MODEL

    def transcribe(self, file_path: str, save_directory: str = OUTPUT_DIRECTORY):
        """Send audio file to ElevenLabs and return transcription, then save the text to a file."""
        try:
            with open(file_path, 'rb') as audio_file:
                response = requests.post(
                    self.base_url,
                    headers={"xi-api-key": self.api_key},
                    data={
                        "model_id": self.model_id,
                        "file_format": "other",
                    },
                    files={"file": (os.path.basename(file_path), audio_file)},
                )

            result = response.json()
            if "text" in result:
                transcription = result["text"]
                self.save_transcription(transcription, file_path, save_directory)
                return transcription
            else:
                return {"error": result}

        except Exception as e:
            return {"error": str(e)}

    def save_transcription(self, transcription: str, file_path: str, save_directory: str):
        """Save the transcription to a text file in the specified directory."""
        try:
            # Extract file name from the path and change extension to .txt
            file_name = os.path.splitext(os.path.basename(file_path))[0] + ".txt"
            save_path = os.path.join(save_directory, file_name)

            # Ensure the directory exists
            os.makedirs(save_directory, exist_ok=True)

            # Write the transcription to the file
            with open(save_path, 'w') as file:
                file.write(transcription)

            print(f"Transcription saved at: {save_path}")

        except Exception as e:
            print(f"Error saving transcription: {str(e)}")
        

def main():
    file_path = "file/assets/Tucker.mp3"  # Change path if needed
    save_directory = 'file/assets/output/'   # Directory to save the transcription file
    transcriber = ElevenLabsTranscriber()
    result = transcriber.transcribe(file_path, save_directory)
    print(result)


if __name__ == "__main__":
    main()
