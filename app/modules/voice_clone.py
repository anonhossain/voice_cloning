import os
import tempfile
from io import BytesIO
from dotenv import load_dotenv
from elevenlabs.client import ElevenLabs
from pydub import AudioSegment
import soundfile as sf

class VoiceCloner:
    """🎙️ Voice cloning utility using ElevenLabs API with auto-cropping."""

    def __init__(self, crop_duration_sec: int = 30):
        """
        :param crop_duration_sec: Duration of the audio clip to use for cloning (default 30s)
        """
        load_dotenv()

        self.api_key = os.getenv("ELEVENLABS_API_KEY")
        if not self.api_key:
            raise Exception("❌ ELEVENLABS_API_KEY missing in .env file")

        # Set ffmpeg paths if defined
        ffmpeg_path = os.getenv("FFMPEG_PATH")
        ffprobe_path = os.getenv("FFPROBE_PATH")
        if ffmpeg_path:
            AudioSegment.converter = ffmpeg_path
        if ffprobe_path:
            AudioSegment.ffprobe = ffprobe_path

        # Initialize ElevenLabs client
        self.client = ElevenLabs(api_key=self.api_key)
        self.crop_duration_sec = crop_duration_sec
        print("🧬 VoiceCloner initialized successfully.")

    # -------------------------------------------------------------
    # 🔄 Convert to WAV (mono, 16kHz, PCM 16-bit)
    # -------------------------------------------------------------
    def convert_to_wav(self, input_path: str) -> str:
        """Convert any audio format to .wav (mono, 16kHz, PCM 16-bit)."""
        output_path = tempfile.mktemp(suffix=".wav")
        audio = AudioSegment.from_file(input_path)
        audio = audio.set_channels(1).set_frame_rate(16000)
        audio.export(output_path, format="wav", parameters=["-acodec", "pcm_s16le"])
        return output_path

    # -------------------------------------------------------------
    # 🧬 Process and clone voice (auto-crop)
    # -------------------------------------------------------------
    def process_and_clone_voice(self, input_audio, clone_name: str) -> str:
        """
        Accepts:
        - Path string ("./file/audio.m4a")
        - File-like object (BytesIO, FastAPI UploadFile.file)
        Crops the first `crop_duration_sec` seconds, converts to WAV, and clones the voice.
        Returns: voice_id
        """

        # ✅ Prepare input file
        if isinstance(input_audio, (BytesIO,)):
            with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp:
                tmp.write(input_audio.read())
                input_audio_path = tmp.name
        elif hasattr(input_audio, "read"):  # FastAPI UploadFile.file
            with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp:
                tmp.write(input_audio.read())
                input_audio_path = tmp.name
        elif isinstance(input_audio, str):
            input_audio_path = input_audio
        else:
            raise Exception("❌ Unsupported input type. Must be path string or file-like object.")

        # ✅ Convert to WAV if not already
        if not input_audio_path.lower().endswith(".wav"):
            input_audio_path = self.convert_to_wav(input_audio_path)

        # ✅ Load audio and crop
        audio = AudioSegment.from_wav(input_audio_path)
        crop_ms = min(len(audio), self.crop_duration_sec * 1000)
        cropped_audio = audio[:crop_ms]

        # ✅ Save cropped audio as WAV
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp_file:
            cropped_audio.export(tmp_file.name, format="wav")
            final_path = tmp_file.name
            print(f"✅ Cropped audio saved for cloning: {final_path}")

        # ✅ Check existing voices
        voices_response = self.client.voices.get_all()
        voice_list = getattr(voices_response, "voices", voices_response)

        for voice in voice_list:
            if hasattr(voice, "name") and voice.name.lower() == clone_name.lower():
                print(f"✅ Voice '{clone_name}' already exists with ID: {voice.voice_id}")
                os.remove(final_path)
                return voice.voice_id

        # ✅ Clone new voice
        print("🧬 Cloning new voice...")
        with open(final_path, "rb") as f:
            voice = self.client.voices.ivc.create(
                name=clone_name,
                files=[f],
            )
        print(f"✅ New voice cloned with ID: {voice.voice_id}")

        # ✅ Cleanup
        os.remove(final_path)
        if input_audio_path != input_audio:
            os.remove(input_audio_path)

        return voice.voice_id
