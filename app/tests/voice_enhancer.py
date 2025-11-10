import os
import soundfile as sf
import noisereduce as nr
from pydub import AudioSegment

# ✅ Set ffmpeg and ffprobe paths for pydub (required for some conversions)
ffmpeg_path = os.getenv("FFMPEG_PATH")
ffprobe_path = os.getenv("FFPROBE_PATH")
AudioSegment.converter = ffmpeg_path
AudioSegment.ffprobe = ffprobe_path


class VoiceEnhancer:
    """Enhance audio files by reducing background noise."""

    def __init__(self):
        print("🎧 VoiceEnhancer initialized.")

    @staticmethod
    def remove_noise(input_path: str, output_path: str, skip_noise_reduction: bool = False) -> str:
        """
        Reduce noise in a WAV audio file.
        
        Args:
            input_path (str): Path to the input WAV audio file.
            output_path (str): Path where the processed WAV will be saved.
            skip_noise_reduction (bool): If True, noise reduction will be skipped.
        
        Returns:
            str: Path to the enhanced audio file.
        """
        if not os.path.exists(input_path):
            raise FileNotFoundError(f"❌ Input file not found: {input_path}")

        # Load audio
        audio_data, sample_rate = sf.read(input_path)
        duration = len(audio_data) / sample_rate
        print(f"📥 Audio duration: {duration:.2f} seconds")

        # Noise reduction
        if skip_noise_reduction:
            print("⏩ Skipping noise reduction...")
            reduced_audio = audio_data
        else:
            print("🔇 Reducing background noise...")
            reduced_audio = nr.reduce_noise(y=audio_data, sr=sample_rate)

        # Save enhanced audio
        sf.write(output_path, reduced_audio, sample_rate, subtype="PCM_16")
        print(f"✅ Enhanced audio saved: {output_path}")

        # Verify the output file
        if os.path.getsize(output_path) == 0:
            raise Exception("❌ Enhanced audio file is empty")

        return output_path


# ---------------- Main Execution ----------------
if __name__ == "__main__":
    # Example paths
    input_wav = r"C:\files\voice-cloning\file\assets\output\summary_audio35.wav"
    output_wav = r"C:\files\voice-cloning\file\output\summary_audio35_enhanced.wav"

    # Ensure output directory exists
    os.makedirs(os.path.dirname(output_wav), exist_ok=True)

    # Initialize enhancer and process the audio
    enhancer = VoiceEnhancer()
    try:
        enhanced_path = enhancer.remove_noise(input_wav, output_wav)
        print(f"\n🎉 Processing complete. Enhanced file saved at:\n{enhanced_path}")
    except Exception as e:
        print(f"❌ Error during enhancement: {e}")
