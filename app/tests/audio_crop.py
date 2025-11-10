from pydub import AudioSegment
import os

# -------------------------------------------------------------
# 🎧 Audio Converter Class
# -------------------------------------------------------------
class AudioConverter:
    """A simple audio conversion utility using PyDub."""

    def __init__(self):
        print("🎵 AudioConverter initialized successfully.")

    def to_wav(self, src_path: str, dst_path: str):
        """
        Convert any audio file to WAV format.
        :param src_path: Path to the input audio file.
        :param dst_path: Path where the converted WAV file will be saved.
        """
        try:
            audio = AudioSegment.from_file(src_path)
            audio.export(dst_path, format="wav")
            print(f"✅ Converted to WAV: {dst_path}")
        except Exception as e:
            print(f"❌ Error converting to WAV: {e}")


# -------------------------------------------------------------
# ✂️ Audio Cropper Class
# -------------------------------------------------------------
class AudioCropper:
    """Crop audio files (any format) by converting to WAV first."""

    def __init__(self, input_dir, output_dir, start_time=(0, 10), end_time=(4, 30)):
        self.input_dir = input_dir
        self.output_dir = output_dir
        self.start_ms = ((start_time[0] * 60) + start_time[1]) * 1000
        self.end_ms = ((end_time[0] * 60) + end_time[1]) * 1000
        self.converter = AudioConverter()

        os.makedirs(self.output_dir, exist_ok=True)
        print(f"\n🎧 AudioCropper ready. Output folder: {self.output_dir}\n")

    def crop_audio_files(self):
        supported_exts = (".mp3", ".wav", ".m4a")
        files = [f for f in os.listdir(self.input_dir) if f.lower().endswith(supported_exts)]

        if not files:
            print("⚠️ No supported audio files found in the input directory.")
            return

        for filename in files:
            try:
                input_path = os.path.join(self.input_dir, filename)
                name, ext = os.path.splitext(filename)
                ext = ext.lower()

                print(f"🎵 Processing: {filename}")

                # Step 1️⃣ Convert to WAV
                wav_temp_path = os.path.join(self.output_dir, f"{name}_temp.wav")
                self.converter.to_wav(input_path, wav_temp_path)

                # Step 2️⃣ Load WAV
                song = AudioSegment.from_wav(wav_temp_path)

                # Step 3️⃣ Crop
                if len(song) < self.start_ms:
                    print(f"⏩ Skipping {filename} — shorter than crop start time.\n")
                    os.remove(wav_temp_path)
                    continue

                cropped = song[self.start_ms:min(self.end_ms, len(song))]

                # Step 4️⃣ Save cropped WAV
                cropped_output_path = os.path.join(self.output_dir, f"{name}_cropped.wav")
                cropped.export(cropped_output_path, format="wav")

                # Step 5️⃣ Cleanup temporary WAV
                os.remove(wav_temp_path)

                print(f"✅ Cropped and saved as: {cropped_output_path}\n")

            except Exception as e:
                print(f"❌ Error processing {filename}: {e}\n")

        print("🎉 All valid audio files cropped successfully!\n")


# -------------------------------------------------------------
# 🏁 Run Script
# -------------------------------------------------------------
if __name__ == "__main__":
    input_dir = r"C:\files\voice-cloning\file\assets"
    output_dir = r"C:\files\voice-cloning\file\output"

    cropper = AudioCropper(input_dir, output_dir, start_time=(0, 10), end_time=(4, 30))
    cropper.crop_audio_files()
