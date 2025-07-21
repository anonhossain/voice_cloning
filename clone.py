import os
import tempfile
import noisereduce as nr
import soundfile as sf
from dotenv import load_dotenv
from elevenlabs.client import ElevenLabs
from pydub import AudioSegment
import traceback
from pydub import AudioSegment

# ✅ Load environment variables
load_dotenv()

# # ✅ Set your actual ffmpeg and ffprobe paths

ffmpeg_path = os.getenv("FFMPEG_PATH")
ffprobe_path = os.getenv("FFPROBE_PATH")
clone_name= os.getenv("ELEVENLABS_VOICE_NAME")

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
        # Verify if the output file exists and is playable
        if os.path.exists(output_path) and os.path.getsize(output_path) > 0:
            print(f"✅ Converted WAV file created: {output_path}")
            try:
                # Try loading the file to ensure it's not corrupted
                AudioSegment.from_file(output_path, format="wav")
                print(f"✅ Converted WAV file is playable")
            except Exception as e:
                print(f"❌ Converted WAV file is corrupted: {str(e)}")
                raise Exception("Converted WAV file is not valid")
        else:
            print(f"❌ Failed to create WAV file: {output_path}")
            raise Exception("WAV conversion failed")
        return output_path
    except Exception as e:
        print(f"❌ Error during conversion: {str(e)}")
        raise e

def remove_noise_and_clone_voice(input_audio_path, clone_name, skip_noise_reduction=False):
    """Remove noise (optional) and clone voice using ElevenLabs."""
    description = "a person talking"

    # Verify input file
    if not os.path.exists(input_audio_path):
        raise Exception(f"Input file does not exist: {input_audio_path}")

    # Convert .m4a to .wav if needed
    temp_audio_path = input_audio_path
    if input_audio_path.lower().endswith(".m4a"):
        temp_audio_path = convert_m4a_to_wav(input_audio_path)

    # Read WAV audio
    print("📥 Reading WAV audio...")
    try:
        audio_data, sample_rate = sf.read(temp_audio_path)
        print(f"🎧 Audio shape: {audio_data.shape}, Sample rate: {sample_rate}")
        # Check if audio duration is sufficient (at least 10 seconds)
        duration = len(audio_data) / sample_rate
        if duration < 10:
            raise Exception(f"Audio duration ({duration:.2f} seconds) is too short. Minimum 10 seconds required.")
        print(f"✅ Audio duration: {duration:.2f} seconds")
    except Exception as e:
        print(f"❌ Error reading WAV file: {str(e)}")
        if temp_audio_path != input_audio_path:
            os.remove(temp_audio_path)
        raise e

    # Skip noise reduction if specified
    if skip_noise_reduction:
        print("⏩ Skipping noise reduction...")
        reduced_noise_audio = audio_data
    else:
        print("🔇 Reducing background noise...")
        try:
            reduced_noise_audio = nr.reduce_noise(y=audio_data, sr=sample_rate)
        except Exception as e:
            print(f"❌ Error during noise reduction: {str(e)}")
            if temp_audio_path != input_audio_path:
                os.remove(temp_audio_path)
            raise e

    # Save processed audio to a temporary file
    with tempfile.NamedTemporaryFile(delete=False, suffix='.wav') as tmp_file:
        try:
            sf.write(tmp_file.name, reduced_noise_audio, sample_rate, subtype='PCM_16')
            tmp_path = tmp_file.name
            print(f"✅ Processed audio saved: {tmp_path}")
            # Verify the saved file
            if os.path.getsize(tmp_path) == 0:
                print(f"❌ Temporary file is empty: {tmp_path}")
                raise Exception("Processed audio file is empty")
            # Try loading the file to ensure it's not corrupted
            AudioSegment.from_file(tmp_path, format="wav")
            print(f"✅ Processed WAV file is playable")
        except Exception as e:
            print(f"❌ Error saving or verifying processed audio: {str(e)}")
            os.remove(tmp_path)
            if temp_audio_path != input_audio_path:
                os.remove(temp_audio_path)
            raise e

    # Connect to ElevenLabs
    print("🧬 Connecting to ElevenLabs...")
    try:
        client = ElevenLabs(api_key=os.getenv("ELEVENLABS_API_KEY"))
        if not os.getenv("ELEVENLABS_API_KEY"):
            raise Exception("ELEVENLABS_API_KEY is not set in .env file")
    except Exception as e:
        print(f"❌ Error initializing ElevenLabs client: {str(e)}")
        os.remove(tmp_path)
        if temp_audio_path != input_audio_path:
            os.remove(temp_audio_path)
        raise e

    # Check for existing voice
    print("🔍 Checking for existing voice...")
    try:
        voices_response = client.voices.get_all()
        voice_list = getattr(voices_response, 'voices', voices_response)

        for voice in voice_list:
            try:
                if hasattr(voice, 'name') and voice.name.lower() == clone_name.lower():
                    print(f"✅ Voice '{clone_name}' already exists with ID: {voice.voice_id}")
                    os.remove(tmp_path)
                    if temp_audio_path != input_audio_path:
                        os.remove(temp_audio_path)
                    return voice.voice_id
            except AttributeError:
                print(f"⚠️ Skipping invalid voice entry: {voice}")
                continue

        # Clone new voice
        print("🧬 Cloning new voice...")
        with open(tmp_path, 'rb') as f:
            voice = client.voices.ivc.create(
                name=clone_name,
                description=description,
                files=[f],  # Pass file object instead of path
            )
        print(f"✅ New voice cloned with ID: {voice.voice_id}")
        os.remove(tmp_path)
        if temp_audio_path != input_audio_path:
            os.remove(temp_audio_path)
        return voice.voice_id

    except Exception as e:
        print(f"❌ Error while connecting to ElevenLabs: {str(e)}")
        traceback.print_exc()
        os.remove(tmp_path)
        if temp_audio_path != input_audio_path:
            os.remove(temp_audio_path)
        raise e

if __name__ == "__main__":
    print("⏳ Processing and cloning voice...")
    input_audio_path = r"./file/Recording.m4a"
    clone_name = os.getenv("ELEVENLABS_VOICE_NAME")
    skip_noise_reduction = True

    try:
        voice_id = remove_noise_and_clone_voice(input_audio_path, clone_name, skip_noise_reduction)
        print(f"✅ Final Cloned Voice ID: {voice_id}")
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        traceback.print_exc()

