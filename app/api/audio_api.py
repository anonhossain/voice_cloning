# api/audio_api.py

import os
import tempfile
from fastapi import UploadFile
from fastapi.responses import FileResponse
from services.audio_summarizer import AudioSummarizerService
import shutil

class AudioAPI:
    """Class to handle audio-related API logic."""

    def __init__(self):
        self.audio_service = AudioSummarizerService()

    async def summarize_audio(self, file: UploadFile, pdf_name: str) -> FileResponse:
        """
        Process uploaded audio and return summarized audio.
        """
        # Save uploaded file temporarily
        suffix = os.path.splitext(file.filename)[1]
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as temp_input:
            shutil.copyfileobj(file.file, temp_input)
            temp_input_path = temp_input.name

        temp_output = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
        temp_output.close()  # Close to allow writing later

        try:
            output_path, _summary_text = self.audio_service.process_audio(
                audio_path=temp_input_path,
                pdf_name=pdf_name,
                output_path=temp_output.name
            )
            return FileResponse(
                output_path,
                media_type="audio/mpeg",
                filename=f"summarized_{file.filename}"
            )

        finally:
            # Cleanup input file
            if os.path.exists(temp_input_path):
                os.remove(temp_input_path)
