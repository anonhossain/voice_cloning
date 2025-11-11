from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from api.audio_api import AudioAPI
from services.voice_cloner import VoiceClonerService

api = APIRouter()
audio_api = AudioAPI()
voice_service = VoiceClonerService()

@api.post("/summarize_audio/")
async def summarize_audio(file: UploadFile = File(...), pdf_name: str = Form(...)):
    """
    Complete Endpoint to summarize audio.
    """
    return await audio_api.summarize_audio(file, pdf_name)

@api.post("/voice-clone/")
async def create_voice_clone(
    voice_name: str = Form(...),
    audio_file: UploadFile = File(...),
):
    """
    API Endpoint:
    Clone a voice using a 4.5-minute audio clip and return the voice_id.
    - Input: voice_name, audio_file
    """
    try:
        result = voice_service.create_voice(voice_name, audio_file.file)
        return {"status": "success", **result}

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@api.delete("/voice-clone/")
async def delete_voice_clone(voice_name: str = Form(...)):
    """
    Delete a cloned voice by name (locally + ElevenLabs).
    """
    try:
        result = voice_service.delete_voice(voice_name)
        return {"status": "success", **result}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
