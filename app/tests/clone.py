import os
import noisereduce as nr
from dotenv import load_dotenv
from elevenlabs.client import ElevenLabs
from pydub import AudioSegment

# ✅ Load environment variables
load_dotenv()

# ✅ Set ffmpeg and ffprobe paths for pydub
ffmpeg_path = os.getenv("FFMPEG_PATH")
ffprobe_path = os.getenv("FFPROBE_PATH")
AudioSegment.converter = ffmpeg_path
AudioSegment.ffprobe = ffprobe_path

class VoiceCloner:
    """Clone a voice using ElevenLabs."""
    
    def __init__(self, api_key=None):
        self.api_key = api_key or os.getenv("ELEVENLABS_API_KEY")
        if not self.api_key:
            raise Exception("❌ ELEVENLABS_API_KEY missing in .env file")
        self.client = ElevenLabs(api_key=self.api_key)
        print("🧬 VoiceCloner initialized.")

    def clone_voice(self, voice_path: str, clone_name: str, description="A person talking"):
        """
        Clone a new voice from a WAV file.
        :param voice_path: Path to input WAV audio
        :param clone_name: Name of the new voice
        :param description: Description for the voice
        :return: voice_id
        """
        if not os.path.exists(voice_path):
            raise FileNotFoundError(f"❌ Input file not found: {voice_path}")

        # Check if voice already exists
        voices_response = self.client.voices.get_all()
        voice_list = getattr(voices_response, "voices", voices_response)

        for voice in voice_list:
            if hasattr(voice, "name") and voice.name.lower() == clone_name.lower():
                print(f"✅ Voice '{clone_name}' already exists with ID: {voice.voice_id}")
                return voice.voice_id

        # Clone new voice
        with open(voice_path, "rb") as f:
            voice = self.client.voices.ivc.create(
                name=clone_name,
                description=description,
                files=[f],
            )
        print(f"✅ New voice cloned with ID: {voice.voice_id}")
        return voice.voice_id


# ---------------- Example Usage ----------------
if __name__ == "__main__":
    # Paths
    enhanced_wav = r"C:\files\voice-cloning\file\output\Tucker-[AudioTrimmer.com].mp3"

    # 2️⃣ Clone voice
    cloner = VoiceCloner()
    voice_id = cloner.clone_voice(enhanced_wav, clone_name="test_Clone", description="Cloned voice of test person")
    print(f"Cloned Voice ID: {voice_id}")

#ruvwV723wkhLMh5M1vSI