# import os
# import json
# import io
# import tempfile
# import traceback
# import numpy as np
# import soundfile as sf
# from scipy.signal import butter, lfilter
# from dotenv import load_dotenv
# from elevenlabs.client import ElevenLabs
# from openai import OpenAI
# from pydub import AudioSegment
# import noisereduce as nr

# # ✅ Load environment variables
# load_dotenv()

# # Set paths
# ffmpeg_path = os.getenv("FFMPEG_PATH")
# ffprobe_path = os.getenv("FFPROBE_PATH")
# AudioSegment.converter = ffmpeg_path
# AudioSegment.ffprobe = ffprobe_path

# # Clients
# openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
# elevenlabs_client = ElevenLabs(api_key=os.getenv("ELEVENLABS_API_KEY"))
# default_voice_name = os.getenv("ELEVENLABS_VOICE_NAME")
# default_voice_id = os.getenv("ELEVENLABS_VOICE_ID")


# # ✅ Audio Conversion & Noise Reduction
# def convert_m4a_to_wav(input_path):
#     print("🔄 Converting .m4a to .wav...")
#     output_path = tempfile.mktemp(suffix=".wav")
#     audio = AudioSegment.from_file(input_path, format="m4a")
#     audio = audio.set_channels(1).set_frame_rate(16000)
#     audio.export(output_path, format="wav", parameters=["-acodec", "pcm_s16le"])
#     return output_path


# def remove_noise_and_clone_voice(input_audio_path, clone_name, skip_noise_reduction=False):
#     if not os.path.exists(input_audio_path):
#         raise Exception(f"Input file does not exist: {input_audio_path}")

#     temp_audio_path = input_audio_path
#     if input_audio_path.lower().endswith(".m4a"):
#         temp_audio_path = convert_m4a_to_wav(input_audio_path)

#     audio_data, sample_rate = sf.read(temp_audio_path)
#     duration = len(audio_data) / sample_rate
#     if duration < 10:
#         raise Exception(f"Audio too short: {duration:.2f}s")

#     if skip_noise_reduction:
#         reduced_audio = audio_data
#     else:
#         reduced_audio = nr.reduce_noise(y=audio_data, sr=sample_rate)

#     with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp_file:
#         sf.write(tmp_file.name, reduced_audio, sample_rate, subtype='PCM_16')
#         tmp_path = tmp_file.name

#     try:
#         voices_response = elevenlabs_client.voices.get_all()
#         for voice in voices_response.voices:
#             if voice.name.lower() == clone_name.lower():
#                 print(f"✅ Voice already exists: {voice.voice_id}")
#                 os.remove(tmp_path)
#                 return voice.voice_id

#         with open(tmp_path, 'rb') as f:
#             voice = elevenlabs_client.voices.ivc.create(
#                 name=clone_name,
#                 description="a person talking",
#                 files=[f],
#             )
#         print(f"✅ New voice cloned: {voice.voice_id}")
#         return voice.voice_id
#     finally:
#         os.remove(tmp_path)
#         if temp_audio_path != input_audio_path:
#             os.remove(temp_audio_path)


# # ✅ Audio Filtering
# def high_pass_filter(audio_data: np.ndarray, sample_rate: int, cutoff=80):
#     nyquist = 0.5 * sample_rate
#     normal_cutoff = cutoff / nyquist
#     b, a = butter(1, normal_cutoff, btype='high')
#     return lfilter(b, a, audio_data)


# def apply_filter_and_save_audio(mp3_bytes, output_file):
#     audio_segment = AudioSegment.from_file(io.BytesIO(mp3_bytes), format="mp3")
#     samples = np.array(audio_segment.get_array_of_samples()).astype(np.float32)
#     if audio_segment.channels == 2:
#         samples = samples.reshape((-1, 2)).mean(axis=1)
#     filtered = high_pass_filter(samples, audio_segment.frame_rate)
#     filtered_audio = AudioSegment(
#         filtered.astype(np.int16).tobytes(),
#         frame_rate=audio_segment.frame_rate,
#         sample_width=2,
#         channels=1
#     )
#     os.makedirs(os.path.dirname(output_file), exist_ok=True)
#     filtered_audio.export(output_file, format="mp3")
#     print(f"✅ Filtered audio saved: {output_file}")


# # ✅ Generate AI Response & Voice Output
# def generate_ai_response_and_stream_audio(input_data):
#     user_data = input_data.get('user_data', {})
#     cloned_voice_id = input_data.get('cloned_voice_id', default_voice_id)

#     prompt = "You are an AI assistant (user's loved one)...\n"
#     for key, value in user_data.items():
#         prompt += f"- {key.replace('_', ' ').capitalize()} is {value}.\n"
#     prompt += "\nRespond warmly and personally."

#     try:
#         response = openai_client.chat.completions.create(
#             model="gpt-4o",
#             messages=[
#                 {"role": "system", "content": "You are a warm, caring AI loved one. You must sound personal and affectionate. Use the user's data to shape your response naturally."},
#                 {"role": "system", "content": f"User data: {json.dumps(user_data)}"},
#                 {"role": "user", "content": user_data.get("distinct_greeting", "Hi there!")}
#             ],
#             max_tokens=2000,
#             temperature=0.7,
#         )
#         ai_response_text = response.choices[0].message.content
#         print(f"🧠 AI says: {ai_response_text}")

#         audio_data = elevenlabs_client.text_to_speech.convert(
#             voice_id=cloned_voice_id,
#             text=ai_response_text,
#             model_id="eleven_multilingual_v2",
#             output_format="mp3_44100_128",
#             voice_settings={
#                 "stability": 0.5,
#                 "use_speaker_boost": True,
#                 "similarity_boost": 1.0,
#                 "style": 1.0,
#                 "speed": 0.9
#             }
#         )

#         audio_bytes = b''.join(chunk for chunk in audio_data if chunk)
#         apply_filter_and_save_audio(audio_bytes, "output/output_audio_filtered2.mp3")

#     except Exception as e:
#         print(f"❌ Error generating response or speech: {e}")
#         traceback.print_exc()


# # ✅ Main Entrypoint
# if __name__ == "__main__":
#     print("🎙️ Running voice assistant pipeline...")

#     # STEP 1: Clone voice (only if needed)
#     input_audio_path = "./file/Recording.m4a"
#     skip_noise_reduction = True
#     try:
#         cloned_id = remove_noise_and_clone_voice(input_audio_path, default_voice_name, skip_noise_reduction)
#     except Exception as e:
#         print(f"❌ Voice cloning failed: {e}")
#         cloned_id = default_voice_id

#     # STEP 2: Generate personalized voice response
#     input_data = {
#         "user_data": {
#             "loved_one_name": "John",
#             "loved_one_birthday": "1990-06-15",
#             "user_birthday": "1992-11-20",
#             "distinct_greeting": "Hey there! How are you today?",
#             "distinct_goodbye": "See you soon, take care!",
#             "nickname_for_loved_one": "Johnny",
#             "favorite_food": "Pizza",
#             "special_moment": "The first time we went hiking together."
#         },
#         "cloned_voice_id": cloned_id
#     }

#     generate_ai_response_and_stream_audio(input_data)
#     print("🎙️ Voice assistant pipeline completed.")


import os
import json
import io
import tempfile
import traceback
import numpy as np
import soundfile as sf
from scipy.signal import butter, lfilter
from dotenv import load_dotenv
from elevenlabs.client import ElevenLabs
from openai import OpenAI
from pydub import AudioSegment
import noisereduce as nr

# ✅ Load environment variables
load_dotenv()

# Set paths
ffmpeg_path = os.getenv("FFMPEG_PATH")
ffprobe_path = os.getenv("FFPROBE_PATH")
AudioSegment.converter = ffmpeg_path
AudioSegment.ffprobe = ffprobe_path

# Clients
openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
elevenlabs_client = ElevenLabs(api_key=os.getenv("ELEVENLABS_API_KEY"))
default_voice_name = os.getenv("ELEVENLABS_VOICE_NAME")
default_voice_id = os.getenv("ELEVENLABS_VOICE_ID")


# ✅ Audio Conversion & Noise Reduction
def convert_m4a_to_wav(input_path):
    print("🔄 Converting .m4a to .wav...")
    output_path = tempfile.mktemp(suffix=".wav")
    audio = AudioSegment.from_file(input_path, format="m4a")
    audio = audio.set_channels(1).set_frame_rate(16000)
    audio.export(output_path, format="wav", parameters=["-acodec", "pcm_s16le"])
    return output_path


def remove_noise_and_clone_voice(input_audio_path, clone_name, skip_noise_reduction=False):
    if not os.path.exists(input_audio_path):
        raise Exception(f"Input file does not exist: {input_audio_path}")

    temp_audio_path = input_audio_path
    if input_audio_path.lower().endswith(".m4a"):
        temp_audio_path = convert_m4a_to_wav(input_audio_path)

    audio_data, sample_rate = sf.read(temp_audio_path)
    duration = len(audio_data) / sample_rate
    if duration < 10:
        raise Exception(f"Audio too short: {duration:.2f}s")

    if skip_noise_reduction:
        reduced_audio = audio_data
    else:
        reduced_audio = nr.reduce_noise(y=audio_data, sr=sample_rate)

    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp_file:
        sf.write(tmp_file.name, reduced_audio, sample_rate, subtype='PCM_16')
        tmp_path = tmp_file.name

    try:
        voices_response = elevenlabs_client.voices.get_all()
        for voice in voices_response.voices:
            if voice.name.lower() == clone_name.lower():
                print(f"✅ Voice already exists: {voice.voice_id}")
                os.remove(tmp_path)
                return voice.voice_id

        with open(tmp_path, 'rb') as f:
            voice = elevenlabs_client.voices.ivc.create(
                name=clone_name,
                description="a person talking",
                files=[f],
            )
        print(f"✅ New voice cloned: {voice.voice_id}")
        return voice.voice_id
    finally:
        os.remove(tmp_path)
        if temp_audio_path != input_audio_path:
            os.remove(temp_audio_path)


# ✅ Audio Filtering
def high_pass_filter(audio_data: np.ndarray, sample_rate: int, cutoff=80):
    nyquist = 0.5 * sample_rate
    normal_cutoff = cutoff / nyquist
    b, a = butter(1, normal_cutoff, btype='high')
    return lfilter(b, a, audio_data)


def apply_filter_and_save_audio(mp3_bytes, output_file):
    audio_segment = AudioSegment.from_file(io.BytesIO(mp3_bytes), format="mp3")
    samples = np.array(audio_segment.get_array_of_samples()).astype(np.float32)
    if audio_segment.channels == 2:
        samples = samples.reshape((-1, 2)).mean(axis=1)
    filtered = high_pass_filter(samples, audio_segment.frame_rate)
    filtered_audio = AudioSegment(
        filtered.astype(np.int16).tobytes(),
        frame_rate=audio_segment.frame_rate,
        sample_width=2,
        channels=1
    )
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    filtered_audio.export(output_file, format="mp3")
    print(f"✅ Filtered audio saved: {output_file}")


# ✅ Main Pipeline Function
def run_voice_assistant_pipeline(audio_path: str, user_data: dict, skip_noise_reduction=True) -> str:
    """
    Complete voice assistant pipeline.

    Args:
        audio_path (str): Path to the uploaded voice recording (.m4a or .wav).
        user_data (dict): Dictionary of user preferences and metadata.
        skip_noise_reduction (bool): Whether to skip noise reduction.

    Returns:
        str: Path to the generated and filtered MP3 file.
    """
    print("🎙️ Running voice assistant pipeline...")

    try:
        # Step 1: Clone voice
        voice_id = remove_noise_and_clone_voice(audio_path, default_voice_name, skip_noise_reduction)
    except Exception as e:
        print(f"❌ Voice cloning failed: {e}")
        voice_id = default_voice_id

    # Step 2: Prepare prompt
    prompt = "You are an AI assistant (user's loved one)...\n"
    for key, value in user_data.items():
        prompt += f"- {key.replace('_', ' ').capitalize()} is {value}.\n"
    prompt += "\nRespond warmly and personally."

    try:
        # Step 3: Get AI response
        response = openai_client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are a warm, caring AI loved one. You must sound personal and affectionate. Use the user's data to shape your response naturally."},
                {"role": "system", "content": f"User data: {json.dumps(user_data)}"},
                {"role": "user", "content": user_data.get("distinct_greeting", "Hi there!")}
            ],
            max_tokens=2000,
            temperature=0.7,
        )
        ai_response_text = response.choices[0].message.content
        print(f"🧠 AI says: {ai_response_text}")

        # Step 4: Convert response to voice
        audio_data = elevenlabs_client.text_to_speech.convert(
            voice_id=voice_id,
            text=ai_response_text,
            model_id="eleven_multilingual_v2",
            output_format="mp3_44100_128",
            voice_settings={
                "stability": 0.5,
                "use_speaker_boost": True,
                "similarity_boost": 1.0,
                "style": 1.0,
                "speed": 0.9
            }
        )

        audio_bytes = b''.join(chunk for chunk in audio_data if chunk)

        output_path = "output/output_audio_filtered2.mp3"
        apply_filter_and_save_audio(audio_bytes, output_path)
        print("🎙️ Voice assistant pipeline completed.")
        return output_path

    except Exception as e:
        print(f"❌ Error generating response or speech: {e}")
        traceback.print_exc()
        return ""


# ✅ Example usage (for testing only)
if __name__ == "__main__":
    input_audio = "./file/Recording.m4a"
    user_info = {
        "loved_one_name": "John",
        "loved_one_birthday": "1990-06-15",
        "user_birthday": "1992-11-20",
        "distinct_greeting": "Hey there! How are you today?",
        "distinct_goodbye": "See you soon, take care!",
        "nickname_for_loved_one": "Johnny",
        "favorite_food": "Pizza",
        "special_moment": "The first time we went hiking together."
    }

    output_file = run_voice_assistant_pipeline(input_audio, user_info)
    print(f"🎧 Final output file: {output_file}")
