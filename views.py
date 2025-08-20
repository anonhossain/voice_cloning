from fastapi import APIRouter, UploadFile, File, HTTPException
from clone import remove_noise_and_clone_voice, clone_name  # import your function
import os
from fastapi import APIRouter, UploadFile, File, HTTPException
from stt import ElevenLabsTranscriber


router = APIRouter()

@router.post("/clone-voice/")
async def clone_voice(file: UploadFile = File(...)):
    try:
        voice_id = remove_noise_and_clone_voice(file.file, clone_name, skip_noise_reduction=True)
        return {"voice_id": voice_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    

@router.post("/transcribe/")
async def transcribe_audio(file: UploadFile = File(...)):
    """
    Upload an audio file and get back the transcription text.
    """
    try:
        # Save uploaded file temporarily
        temp_file = f"temp_{file.filename}"
        with open(temp_file, "wb") as buffer:
            buffer.write(await file.read())

        # Use transcriber from stt.py
        transcriber = ElevenLabsTranscriber()
        result = transcriber.transcribe(temp_file)

        # Cleanup
        os.remove(temp_file)

        if isinstance(result, str):
            return {"text": result}
        else:
            raise HTTPException(status_code=400, detail=result)

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
