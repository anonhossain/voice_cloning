import os
from dotenv import load_dotenv
from elevenlabs import ElevenLabs

# Load environment variables from .env file
load_dotenv()

class TextToSpeechGenerator:
    def __init__(self, api_key: str = None, voice_id: str = None):
        """
        Initializes the ElevenLabs client and configures voice settings.
        :param api_key: ElevenLabs API key (loads from environment if not provided)
        :param voice_id: Voice ID for text-to-speech conversion (must be provided)
        """
        self.api_key = api_key or os.getenv("ELEVENLABS_API_KEY")
        self.voice_id = voice_id  # The voice_id will now be provided explicitly in the main function
        
        if not self.api_key:
            raise ValueError("❌ ELEVENLABS_API_KEY not found in environment or provided.")
        if not self.voice_id:
            raise ValueError("❌ voice_id must be provided.")

        # Initialize ElevenLabs client
        self.client = ElevenLabs(api_key=self.api_key, base_url="https://api.elevenlabs.io/")

    def text_to_speech(self, text: str, output_path: str):
        """
        Converts text to speech using ElevenLabs API and saves as MP3.
        :param text: The text to be converted to speech.
        :param output_path: The path where the generated audio will be saved.
        """
        print(f"Generating speech using voice: {self.voice_id}...")

        # Request speech conversion from ElevenLabs API
        response_stream = self.client.text_to_speech.convert(
            voice_id=self.voice_id,
            model_id="eleven_multilingual_v2",
            text=text,
            output_format="mp3_44100_128",
            voice_settings={
                "stability": 0.5,
                "similarity_boost": 0.9,
                "style": 1.0,
                "use_speaker_boost": True,
                "speed": 0.75

            }
        )

        # Combine audio chunks from the response stream
        audio_bytes = b"".join(chunk for chunk in response_stream if chunk)

        # Ensure the output directory exists
        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        # Save the audio to the specified path
        with open(output_path, "wb") as audio_file:
            audio_file.write(audio_bytes)

        print(f"✅ Audio saved to: {output_path}")

def main():
    # Set the path for the text file and output directory
    text_file_path = "file/assets/output/Tucker_summarizer.txt"  # Path to the text file to be converted to speech
    output_directory = "file/assets/output/"         # Directory where the audio file will be saved
    output_file_path = os.path.join(output_directory, "Tucker_summarized2.mp3")  # Full path for the MP3 file
    voice_id = "x98xhnTaTuiJIQ6Kxz7D"
    #voice_id = "UgBBYS2sOqTuMpoF3BR0"  # Example voice ID, you can replace this with the desired voice ID

    # Initialize TextToSpeechGenerator with API key and voice ID
    tts_generator = TextToSpeechGenerator(voice_id=voice_id)

    # Read the text from the file to convert to speech
    with open(text_file_path, "r", encoding="utf-8") as file:
        sample_text = file.read()

    # Convert text to speech and save as MP3
    tts_generator.text_to_speech(sample_text, output_file_path)

if __name__ == "__main__":
    main()
