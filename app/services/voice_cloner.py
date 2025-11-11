import os
import json
from pathlib import Path
from modules.voice_clone import VoiceCloner  # import your VoiceCloner class


class VoiceClonerService:
    """
    🎙️ Service layer for handling voice cloning requests.
    - Takes input voice name and audio file.
    - Returns voice_id from ElevenLabs.
    - Saves mapping of {voice_name: voice_id} in a JSON file.
    """

    def __init__(self, db_path: str = "file/database/voice.json"):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)  # ensure dir exists
        self.cloner = VoiceCloner()

        # Ensure JSON database file exists
        if not self.db_path.exists():
            with open(self.db_path, "w", encoding="utf-8") as f:
                json.dump({}, f, indent=4)

    # -------------------------------------------------------------
    # 🔍 Load and Save Helper Methods
    # -------------------------------------------------------------
    def _load_json(self):
        """Load existing voice data."""
        try:
            with open(self.db_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return {}

    def _save_json(self, data: dict):
        """Save voice data to JSON."""
        with open(self.db_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4)

    # -------------------------------------------------------------
    # 🧬 Main Function: Clone Voice and Save
    # -------------------------------------------------------------
    def create_voice(self, voice_name: str, audio_input) -> dict:
        """
        Create (or reuse) a cloned voice and save to local JSON DB.
        :param voice_name: Name for the cloned voice
        :param audio_input: Audio file path or file-like object
        :return: Dict containing {"voice_name": ..., "voice_id": ...}
        """
        # Load existing voices
        voice_data = self._load_json()

        # Reuse if exists
        if voice_name in voice_data:
            print(f"✅ Voice '{voice_name}' already exists.")
            return {"voice_name": voice_name, "voice_id": voice_data[voice_name]}

        # Clone new voice
        print("🎧 Cloning new voice via VoiceCloner module...")
        voice_id = self.cloner.process_and_clone_voice(audio_input, voice_name)

        # Save mapping
        voice_data[voice_name] = voice_id
        self._save_json(voice_data)

        print(f"✅ Voice saved: {voice_name} -> {voice_id}")
        return {"voice_name": voice_name, "voice_id": voice_id}

    # -------------------------------------------------------------
    # ❌ Optional: Delete a Voice
    # -------------------------------------------------------------
    def delete_voice(self, voice_name: str):
        """
        Delete a cloned voice both from ElevenLabs and local JSON.
        """
        from elevenlabs import ElevenLabs

        voice_data = self._load_json()
        if voice_name not in voice_data:
            print(f"⚠️ Voice '{voice_name}' not found in local DB.")
            return {"error": "Voice not found"}

        voice_id = voice_data[voice_name]
        client = ElevenLabs(base_url="https://api.elevenlabs.io/")

        try:
            client.voices.delete(voice_id=voice_id)
            del voice_data[voice_name]
            self._save_json(voice_data)
            print(f"🗑️ Deleted voice '{voice_name}' successfully.")
            return {"deleted": voice_name}
        except Exception as e:
            print(f"❌ Failed to delete voice: {e}")
            return {"error": str(e)}
