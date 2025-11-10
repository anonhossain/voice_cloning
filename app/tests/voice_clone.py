import os
import tempfile
import noisereduce as nr
import soundfile as sf
from dotenv import load_dotenv
from elevenlabs.client import ElevenLabs
from pydub import AudioSegment
import traceback
from io import BytesIO


# ✅ Load environment variables
load_dotenv()

# ✅ Set ffmpeg and ffprobe paths
ffmpeg_path = os.getenv("FFMPEG_PATH")
ffprobe_path = os.getenv("FFPROBE_PATH")
clone_name = os.getenv("ELEVENLABS_VOICE_NAME")

AudioSegment.converter = ffmpeg_path
AudioSegment.ffprobe = ffprobe_path


def convert_m4a_to_wav(input_path):
    """Convert .m4a to .wav (mono, 16kHz, PCM 16-bit) and verify the output file."""
    print("🔄 Converting .m4a to .wav (mono, 16kHz, PCM 16-bit)...")
    output_path = tempfile.mktemp(suffix=".wav")
    try:
        audio = AudioSegment.from_file(input_path, format="m4a")
        audio = audio.set_channels(1).set_frame_rate(16000)
        # Ensure PCM 16-bit encoding
        audio.export(output_path, format="wav", parameters=["-acodec", "pcm_s16le"])

        # Verify output
        if os.path.exists(output_path) and os.path.getsize(output_path) > 0:
            AudioSegment.from_file(output_path, format="wav")
            print(f"✅ Converted WAV file created: {output_path}")
        else:
            raise Exception("❌ WAV conversion failed")

        return output_path
    except Exception as e:
        print(f"❌ Error during conversion: {str(e)}")
        raise e


def remove_noise_and_clone_voice(input_audio, clone_name, skip_noise_reduction=False):
    """
    Accepts either:
    - path string ("./file/audio.m4a")
    - file-like object (BytesIO, FastAPI UploadFile.file, etc.)
    """
    # Handle input: convert file object -> temp file
    if isinstance(input_audio, (BytesIO, )):
        with tempfile.NamedTemporaryFile(delete=False, suffix=".m4a") as tmp:
            tmp.write(input_audio.read())
            input_audio_path = tmp.name
    elif hasattr(input_audio, "read"):  # e.g. FastAPI UploadFile.file
        with tempfile.NamedTemporaryFile(delete=False, suffix=".m4a") as tmp:
            tmp.write(input_audio.read())
            input_audio_path = tmp.name
    elif isinstance(input_audio, str):
        input_audio_path = input_audio
    else:
        raise Exception("❌ Unsupported input type. Must be path string or file-like object.")

    description = "a person talking"

    # Convert .m4a to .wav if needed
    temp_audio_path = input_audio_path
    if input_audio_path.lower().endswith(".m4a"):
        temp_audio_path = convert_m4a_to_wav(input_audio_path)

    # Read WAV audio
    print("📥 Reading WAV audio...")
    try:
        audio_data, sample_rate = sf.read(temp_audio_path)
        duration = len(audio_data) / sample_rate
        if duration > 300:
            raise Exception(f"Audio duration ({duration:.2f}s) too long. Max 5 minutes required.")
        print(f"✅ Audio duration: {duration:.2f} seconds")
    except Exception as e:
        if temp_audio_path != input_audio_path:
            os.remove(temp_audio_path)
        raise e

    # Noise reduction
    if skip_noise_reduction:
        print("⏩ Skipping noise reduction...")
        reduced_noise_audio = audio_data
    else:
        print("🔇 Reducing background noise...")
        reduced_noise_audio = nr.reduce_noise(y=audio_data, sr=sample_rate)

    # Save processed audio to temp WAV
    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp_file:
        sf.write(tmp_file.name, reduced_noise_audio, sample_rate, subtype="PCM_16")
        tmp_path = tmp_file.name
        print(f"✅ Processed audio saved: {tmp_path}")

        # Verify
        if os.path.getsize(tmp_path) == 0:
            raise Exception("❌ Processed audio file is empty")
        AudioSegment.from_file(tmp_path, format="wav")

    # Connect to ElevenLabs
    print("🧬 Connecting to ElevenLabs...")
    if not os.getenv("ELEVENLABS_API_KEY"):
        raise Exception("❌ ELEVENLABS_API_KEY missing in .env file")
    client = ElevenLabs(api_key=os.getenv("ELEVENLABS_API_KEY"))

    # Check for existing voice
    print("🔍 Checking for existing voice...")
    voices_response = client.voices.get_all()
    voice_list = getattr(voices_response, "voices", voices_response)

    for voice in voice_list:
        if hasattr(voice, "name") and voice.name.lower() == clone_name.lower():
            print(f"✅ Voice '{clone_name}' already exists with ID: {voice.voice_id}")
            os.remove(tmp_path)
            if temp_audio_path != input_audio_path:
                os.remove(temp_audio_path)
            return voice.voice_id

    # Clone new voice
    print("🧬 Cloning new voice...")
    with open(tmp_path, "rb") as f:
        voice = client.voices.ivc.create(
            name=clone_name,
            description=description,
            files=[f],
        )
    print(f"✅ New voice cloned with ID: {voice.voice_id}")

    # Cleanup
    os.remove(tmp_path)
    if temp_audio_path != input_audio_path:
        os.remove(temp_audio_path)

    return voice.voice_id
    

if __name__ == "__main__":
    try:
        # Example usage with a local .m4a file
        input_file_path = "file/assets/voice_samples/sample_voice.m4a"  # Change to your input file path
        voice_id = remove_noise_and_clone_voice(input_file_path, clone_name, skip_noise_reduction=False)
        print(f"Cloned Voice ID: {voice_id}")
    except Exception as e:
        print("❌ An error occurred during voice cloning:")
        traceback.print_exc()