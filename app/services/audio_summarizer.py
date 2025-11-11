# # services/audio_summarizer.py

# import os
# import tempfile
# from modules.audio_converter import AudioConverter
# from modules.stt import SpeechToText
# from modules.summarizer import Summarizer
# from modules.tts import TextToSpeech
# from modules.voice_clone import VoiceCloner
# from elevenlabs import ElevenLabs
# from pydub import AudioSegment

# class AudioSummarizerService:
#     """Service to process long audio, summarize, clone voice, and produce output speech."""

#     def __init__(self):
#         self.audio_converter = AudioConverter()
#         self.transcriber = SpeechToText()
#         self.summarizer = Summarizer()
#         self.tts = TextToSpeech()
#         self.voice_cloner = VoiceCloner()
#         self.eleven_client = ElevenLabs(base_url="https://api.elevenlabs.io/")

#     def process_audio(self, audio_path: str, pdf_name: str, output_path: str):
#         """
#         Full pipeline:
#         1. Clip 4:30 min section for voice cloning
#         2. Clone voice
#         3. Transcribe full audio
#         4. Summarize transcription
#         5. Generate summarized speech using cloned voice
#         6. Delete cloned voice
#         7. Save final audio
#         """
#         # ------------------------------
#         # 1️⃣ Cut 4:30 section for cloning
#         # ------------------------------
#         audio = AudioSegment.from_file(audio_path)
#         clip_duration_ms = 4 * 60 * 1000 + 30 * 1000  # 4 mins 30 seconds
#         clip = audio[:clip_duration_ms]  # take first 4:30
#         with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp_clip:
#             clip.export(tmp_clip.name, format="wav")
#             clip_path = tmp_clip.name

#         # ------------------------------
#         # 2️⃣ Create voice_id
#         # ------------------------------
#         voice_id = self.voice_cloner.process_and_clone_voice(
#             input_audio=clip_path,
#             clone_name=pdf_name
#         )
#         print(f"✅ Voice cloned: {voice_id}")
#         os.remove(clip_path)  # cleanup clip file

#         # ------------------------------
#         # 3️⃣ Transcribe full audio
#         # ------------------------------
#         print("📥 Transcribing full audio...")
#         transcription = self.transcriber.transcribe(audio_path)
#         print(f"✅ Transcription complete. Length: {len(transcription)} chars")

#         # ------------------------------
#         # 4️⃣ Summarize transcription
#         # ------------------------------
#         print("📝 Summarizing transcription...")
#         summary_text = self.summarizer.summarize(transcription)
#         print("✅ Summarization complete")

#         # ------------------------------
#         # 5️⃣ Convert summary to speech
#         # ------------------------------
#         print("🔊 Generating summarized speech...")
#         speech_bytes = self.tts.text_to_speech(summary_text, voice_id=voice_id)

#         # Save final audio
#         with open(output_path, "wb") as f:
#             f.write(speech_bytes)
#         print(f"✅ Final summarized audio saved: {output_path}")

#         # ------------------------------
#         # 6️⃣ Delete cloned voice
#         # ------------------------------
#         print(f"🗑️ Deleting temporary voice: {voice_id}")
#         self.eleven_client.voices.delete(voice_id=voice_id)
#         print("✅ Voice deleted successfully")

#         return output_path, summary_text


# services/audio_summarizer.py

import os
import tempfile
from modules.audio_converter import AudioConverter
from modules.stt import SpeechToText
from modules.summarizer import Summarizer
from modules.tts import TextToSpeech
from modules.voice_clone import VoiceCloner
from modules.audio_crop import AudioCroper
from elevenlabs import ElevenLabs

class AudioSummarizerService:
    """Service to process long audio, summarize, clone voice, and produce output speech."""

    def __init__(self):
        self.audio_converter = AudioConverter()
        self.transcriber = SpeechToText()
        self.summarizer = Summarizer()
        self.tts = TextToSpeech()
        self.voice_cloner = VoiceCloner()
        self.audio_croper = AudioCroper()
        self.eleven_client = ElevenLabs(base_url="https://api.elevenlabs.io/")

    def process_audio(self, audio_path: str, pdf_name: str, output_path: str):
        """
        Full pipeline:
        1. Crop 4:30 min section and clean for voice cloning
        2. Clone voice and get voice_id
        3. Transcribe full audio
        4. Summarize transcription
        5. Generate summarized speech using cloned voice
        6. Delete cloned voice
        7. Save final audio
        """
        # ------------------------------
        # 1️⃣ Crop first 4:30 min for voice clone
        # ------------------------------
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp_clip:
            clip_path = self.audio_croper.crop_audio(
                input_audio=audio_path,
                start_time=(0, 0),
                end_time=(4, 30),
                output_path=tmp_clip.name
            )

        # ------------------------------
        # 2️⃣ Create voice_id
        # ------------------------------
        voice_id = self.voice_cloner.process_and_clone_voice(
            input_audio=clip_path,
            clone_name=pdf_name
        )
        print(f"✅ Voice cloned: {voice_id}")
        os.remove(clip_path)  # cleanup temp clip

        # ------------------------------
        # 3️⃣ Transcribe full audio
        # ------------------------------
        print("📥 Transcribing full audio...")
        transcription = self.transcriber.transcribe(audio_path)
        print(f"✅ Transcription complete. Length: {len(transcription)} chars")

        # ------------------------------
        # 4️⃣ Summarize transcription
        # ------------------------------
        print("📝 Summarizing transcription...")
        summary_text = self.summarizer.summarize(transcription)
        print("✅ Summarization complete")

        # ------------------------------
        # 5️⃣ Convert summary to speech
        # ------------------------------
        print("🔊 Generating summarized speech...")
        speech_bytes = self.tts.text_to_speech(summary_text, voice_id=voice_id)

        # Save final audio
        with open(output_path, "wb") as f:
            f.write(speech_bytes)
        print(f"✅ Final summarized audio saved: {output_path}")

        # ------------------------------
        # 6️⃣ Delete cloned voice
        # ------------------------------
        print(f"🗑️ Deleting temporary voice: {voice_id}")
        self.eleven_client.voices.delete(voice_id=voice_id)
        print("✅ Voice deleted successfully")

        return output_path, summary_text
