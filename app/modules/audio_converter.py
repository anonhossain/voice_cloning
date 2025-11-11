# module/audio_converter.py
from pydub import AudioSegment
import os
from io import BytesIO

class AudioConverter:
    """A reusable audio conversion utility using PyDub."""

    def __init__(self):
        print("🎵 AudioConverter initialized successfully.")

    def to_wav(self, src, dst_path: str):
        """Convert audio to WAV."""
        self._convert(src, dst_path, format="wav")

    def to_mp3(self, src, dst_path: str):
        """Convert audio to MP3."""
        self._convert(src, dst_path, format="mp3")

    def to_m4a(self, src, dst_path: str):
        """Convert audio to M4A."""
        self._convert(src, dst_path, format="mp4")

    def _convert(self, src, dst_path: str, format: str):
        """
        Internal helper for conversion.
        :param src: Path to file or file-like object (BytesIO)
        :param dst_path: Output file path
        :param format: Format string for export
        """
        try:
            if isinstance(src, (str, os.PathLike)):
                if not os.path.exists(src):
                    raise FileNotFoundError(f"Input file not found: {src}")
                audio = AudioSegment.from_file(src)
            elif isinstance(src, BytesIO):
                src.seek(0)
                audio = AudioSegment.from_file(src)
            else:
                raise TypeError("Input must be a file path or BytesIO object")

            # Export to desired format
            audio.export(dst_path, format=format)
            print(f"✅ Conversion successful! File saved as: {dst_path}")

        except Exception as e:
            print(f"❌ Error converting to {format.upper()}: {e}")
            raise e
