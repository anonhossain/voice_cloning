from pydub import AudioSegment
import os

# -------------------------------------------------------------
# 🎧 Audio Croper
# -------------------------------------------------------------
class AudioCroper:
    """
    A class to handle audio conversion to WAV and cropping.
    """

    def __init__(self):
        print("🎵 AudioCroper initialized successfully.")

    # ---------------------------------------------------------
    # Convert any audio file to WAV
    # ---------------------------------------------------------
    def to_wav(self, input_path: str, output_path: str = None) -> str:
        """
        Convert audio file to WAV format.
        :param input_path: Path to input audio file
        :param output_path: Optional path to save WAV. If None, saves alongside original.
        :return: Path to WAV file
        """
        try:
            audio = AudioSegment.from_file(input_path)
            if not output_path:
                name, _ = os.path.splitext(input_path)
                output_path = f"{name}.wav"
            audio.export(output_path, format="wav")
            return output_path
        except Exception as e:
            raise RuntimeError(f"Error converting to WAV: {e}")

    # ---------------------------------------------------------
    # Crop audio
    # ---------------------------------------------------------
    def crop_audio(self, input_audio, start_time=(0, 10), end_time=(4, 30), output_path=None) -> AudioSegment:
        """
        Crop an audio clip.
        :param input_audio: AudioSegment object or path to audio file
        :param start_time: Tuple (minutes, seconds)
        :param end_time: Tuple (minutes, seconds)
        :param output_path: Optional path to save cropped audio
        :return: Cropped AudioSegment object or saved file path
        """
        # Step 1️⃣ Convert to WAV if input is a file path and not WAV
        if isinstance(input_audio, str):
            ext = os.path.splitext(input_audio)[1].lower()
            if ext != ".wav":
                input_audio = self.to_wav(input_audio)
            audio = AudioSegment.from_wav(input_audio)
        elif isinstance(input_audio, AudioSegment):
            audio = input_audio
        else:
            raise TypeError("input_audio must be a file path or AudioSegment object")

        # Step 2️⃣ Calculate crop milliseconds
        start_ms = (start_time[0] * 60 + start_time[1]) * 1000
        end_ms = (end_time[0] * 60 + end_time[1]) * 1000

        if len(audio) < start_ms:
            raise ValueError("Audio is shorter than the crop start time")

        # Step 3️⃣ Crop audio
        cropped = audio[start_ms:min(end_ms, len(audio))]

        # Step 4️⃣ Save if output path provided
        if output_path:
            cropped.export(output_path, format="wav")
            return output_path

        return cropped