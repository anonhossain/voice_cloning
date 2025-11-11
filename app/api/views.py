from fastapi import APIRouter, UploadFile, File, Form
from api.audio_api import AudioAPI

api = APIRouter()
audio_api = AudioAPI()

@api.post("/summarize_audio/")
async def summarize_audio(file: UploadFile = File(...), pdf_name: str = Form(...)):
    """
    Endpoint to summarize audio.
    """
    return await audio_api.summarize_audio(file, pdf_name)
