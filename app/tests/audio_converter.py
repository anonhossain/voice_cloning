from pydub import AudioSegment

class AudioConverter:
    """A simple audio conversion utility using PyDub."""

    def __init__(self):
        print("🎵 AudioConverter initialized successfully.")

    def to_mp3(self, src_path: str, dst_path: str):
        """
        Convert an MP3 file to WAV format.
        :param src_path: Path to the input MP3 file.
        :param dst_path: Path where the converted WAV file will be saved.
        """
        try:
            audio = AudioSegment.from_mp3(src_path)
            audio.export(dst_path, format="mp3")
            print(f"✅ Conversion successful! File saved as: {dst_path}")
        except Exception as e:
            print(f"❌ Error converting MP3 to WAV: {e}")

    def to_m4a(self, src_path: str, dst_path: str):
        """
        Convert any audio file to M4A format.
        :param input_file: Path to the input audio file.
        :param output_file: Path where the converted M4A file will be saved.
        """
        try:
            audio = AudioSegment.from_file(src_path)
            audio.export(dst_path, format="mp4")
            print(f"✅ Conversion successful! File saved as: {dst_path}")
        except Exception as e:
            print(f"❌ Error converting to M4A: {e}")


    def to_wav(self, src_path:str, dst_path:str):
        """
        Convert any audio file to WAV format.
        :param input_file: Path to the input audio file.
        :param output_file: Path where the converted WAV file will be saved.
        """
        try:
            audio = AudioSegment.from_file(src_path)
            audio.export(dst_path, format="wav")
            print(f"✅ Conversion successful! File saved as: {dst_path}")
        except Exception as e:
            print(f"❌ Error converting to WAV: {e}")


if __name__ == "__main__":
    # Initialize converter
    converter = AudioConverter()

    converter.to_wav(
        input_file=r"C:\files\voice-cloning\file\assets\output\summary_audio35.m4a",
        output_file=r"C:\files\voice-cloning\file\assets\output\summary_audio35.wav"
    )

    # ======================================================
    # converter.to_m4a(
    #     input_file=r"C:\files\voice-cloning\file\assets\output\summary_audio35.mp3",
    #     output_file=r"C:\files\voice-cloning\file\assets\output\summary_audio35.m4a"
    # )
