import os
import io
import json
import uuid
from pyparsing import Union
import requests
import numpy as np
from dotenv import load_dotenv
from pydub import AudioSegment
from scipy.signal import butter, lfilter

# --- Third-party clients
from openai import OpenAI
from elevenlabs.client import ElevenLabs

# ----------------- ENV & CLIENTS -----------------
load_dotenv()

ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
VOICE_ID = os.getenv("ELEVENLABS_VOICE_ID")  # must exist

def _ensure_env():
    missing = []
    if not ELEVENLABS_API_KEY: missing.append("ELEVENLABS_API_KEY")
    if not OPENAI_API_KEY: missing.append("OPENAI_API_KEY")
    if not VOICE_ID: missing.append("ELEVENLABS_VOICE_ID")
    if missing:
        raise RuntimeError(f"Missing environment variables: {', '.join(missing)}")

_ensure_env()

openai_client = OpenAI(api_key=OPENAI_API_KEY)
elevenlabs_client = ElevenLabs(api_key=ELEVENLABS_API_KEY)

# ----------------- STT -----------------
class ElevenLabsTranscriber:
    def __init__(self):
        self.api_key = ELEVENLABS_API_KEY
        self.base_url = "https://api.elevenlabs.io/v1/speech-to-text"
        self.model_id = "scribe_v1"

    def transcribe(self, file_path: str):
        """
        Returns transcription string on success.
        Returns dict {'error': ...} on failure.
        """
        try:
            with open(file_path, "rb") as audio_file:
                resp = requests.post(
                    self.base_url,
                    headers={"xi-api-key": self.api_key},
                    data={
                        "model_id": self.model_id,
                        # Let server auto-detect; change to 'mp3'/'wav' if you know the type
                        "file_format": "other",
                    },
                    files={"file": (os.path.basename(file_path), audio_file)},
                    timeout=120,
                )
            # handle non-200 and non-json safely
            try:
                data = resp.json()
            except Exception:
                return {"error": f"STT non-JSON response, status={resp.status_code}"}

            if resp.status_code != 200:
                return {"error": data}

            text = data.get("text")
            if not text:
                return {"error": data}
            return text

        except Exception as e:
            return {"error": f"STT exception: {e}"}

# ----------------- AUDIO FILTERING -----------------
def high_pass_filter(audio_data: np.ndarray, sample_rate: int, cutoff=80):
    # Avoid invalid cutoff when sample_rate is very low
    nyquist = max(1.0, 0.5 * float(sample_rate))
    normal_cutoff = min(0.99, float(cutoff) / nyquist)
    b, a = butter(1, normal_cutoff, btype="high")
    return lfilter(b, a, audio_data)

def _float_to_int16(samples: np.ndarray) -> np.ndarray:
    # Normalize before casting to avoid clipping
    if samples.size == 0:
        return samples.astype(np.int16)
    peak = np.max(np.abs(samples))
    if peak > 0:
        samples = samples / peak
    return (samples * 32767.0).astype(np.int16)

def apply_filter_and_save_audio(mp3_bytes: bytes, output_file: str):
    """
    Takes MP3 bytes, applies a gentle high-pass filter, saves to MP3.
    NOTE: Requires ffmpeg/avlib installed for pydub export to mp3.
    """
    audio_segment = AudioSegment.from_file(io.BytesIO(mp3_bytes), format="mp3")
    samples = np.array(audio_segment.get_array_of_samples()).astype(np.float32)

    # Convert to mono
    if audio_segment.channels == 2:
        samples = samples.reshape((-1, 2)).mean(axis=1)

    # HPF
    filtered_samples = high_pass_filter(samples, audio_segment.frame_rate)
    int16_samples = _float_to_int16(filtered_samples)

    filtered_audio = AudioSegment(
        int16_samples.tobytes(),
        frame_rate=audio_segment.frame_rate,
        sample_width=2,
        channels=1,
    )

    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    filtered_audio.export(output_file, format="mp3")

# ----------------- AI RESPONSE + TTS -----------------
def _build_personal_prompt(user_data: dict) -> tuple[str, str]:
    """
    Recreates your previous 'loved one' style prompt.
    We will inject the STT output as the 'distinct_greeting'.
    Returns (system_prompt, user_message)
    """
    sys = (
        "You are a warm, caring AI loved one. "
        "Sound personal and affectionate. Use the user's data naturally."
    )

    # Build readable context bullets
    bullets = []
    for k, v in user_data.items():
        k2 = k.replace("_", " ").capitalize()
        bullets.append(f"- {k2}: {v}")

    context = "Here is some information about the user:\n" + "\n".join(bullets) if bullets else ""
    user_msg = user_data.get("distinct_greeting", "Hi there! I’m here to chat.")

    system_full = f"{sys}\n{context}".strip()
    return system_full, user_msg

def _elevenlabs_tts_bytes(text: str) -> bytes:
    """
    Handles both generator and bytes responses for different ElevenLabs SDK versions.
    """
    # Primary path (newer SDK method)
    try:
        audio = elevenlabs_client.text_to_speech.convert(
            voice_id=VOICE_ID,
            text=text,
            model_id="eleven_multilingual_v2",
            output_format="mp3_44100_128",
            voice_settings={
                "stability": 0.5,
                "use_speaker_boost": True,
                "similarity_boost": 1.0,
                "style": 1.0,
                "speed": 0.9,
            },
        )
        if isinstance(audio, (bytes, bytearray)):
            return bytes(audio)
        # some SDKs return an iterator of chunks
        return b"".join(chunk for chunk in audio if chunk)
    except AttributeError:
        # Fallback older-style API
        audio = elevenlabs_client.generate(
            text=text,
            voice=VOICE_ID,
            model="eleven_multilingual_v2",
            stream=False,
        )
        if isinstance(audio, (bytes, bytearray)):
            return bytes(audio)
        return b"".join(chunk for chunk in audio if chunk)

def generate_ai_response_audio_from_user_data(user_data: dict) -> Union[str, dict]:
    """
    Creates an AI reply and returns the saved MP3 path.
    """
    try:
        system_prompt, user_message = _build_personal_prompt(user_data)

        # --- OpenAI chat ---
        resp = openai_client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message},
            ],
            max_tokens=1000,
            temperature=0.7,
        )
        ai_text = resp.choices[0].message.content
        if not ai_text:
            return {"error": "OpenAI returned empty content."}

        # --- TTS ---
        tts_bytes = _elevenlabs_tts_bytes(ai_text)

        # --- Save filtered output to unique file ---
        out_dir = "output2/"
        out_path = os.path.join(out_dir, f"output_{uuid.uuid4().hex}.mp3")
        output_path = os.path.dirname(out_path)
        if not os.path.exists(output_path):
            os.makedirs(output_path)
        print(f"Saving audio to {out_path}")

        apply_filter_and_save_audio(tts_bytes, out_path)
        return out_path

    except Exception as e:
        return {"error": f"AI/TTS exception: {e}"}

# ----------------- PUBLIC PIPELINE -----------------
def process_voice_chat(file_path: str) -> Union[str, dict]:
    """
    Full pipeline:
      1) Transcribe audio with ElevenLabs STT
      2) Feed transcription into 'user_data' as distinct_greeting
      3) Generate an AI reply
      4) Synthesize reply to MP3 (filtered)
      5) Return path to MP3

    Returns:
      str path to mp3 on success
      dict {'error': ...} on failure
    """
    transcriber = ElevenLabsTranscriber()
    transcription = transcriber.transcribe(file_path)
    if isinstance(transcription, dict):  # error
        return transcription

    # connect STT -> user_data, as requested
    user_data = {
        "distinct_greeting": transcription
        # you can add other fields here if desired
    }
    return generate_ai_response_audio_from_user_data(user_data)
