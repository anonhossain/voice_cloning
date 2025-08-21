from fastapi import APIRouter, BackgroundTasks, UploadFile, File, HTTPException
from fastapi.responses import FileResponse
from clone import remove_noise_and_clone_voice, clone_name  # import your function
import os
from fastapi import APIRouter, UploadFile, File, HTTPException
from stt import ElevenLabsTranscriber
from voice_chat import process_voice_chat


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


@router.post("/voice_chat/")
async def voice_chat(file: UploadFile = File(...), background_tasks: BackgroundTasks = None):
    """
    Accepts an audio file, returns an MP3 response speaking back like a loved one.
    """
    try:
        temp_path = f"temp_{file.filename}"
        with open(temp_path, "wb") as f:
            f.write(await file.read())

        result = process_voice_chat(temp_path)

        # Clean temp upload immediately
        try:
            os.remove(temp_path)
        except Exception:
            pass

        if isinstance(result, dict) and "error" in result:
            raise HTTPException(status_code=400, detail=result["error"])

        # Schedule deletion of generated output after response is sent
        if background_tasks is None:
            # FastAPI will provide one normally; this is just a guard.
            return FileResponse(result, media_type="audio/mpeg", filename="ai_response.mp3")

        background_tasks.add_task(lambda p=result: os.remove(p) if os.path.exists(p) else None)
        return FileResponse(result, media_type="audio/mpeg", filename="ai_response.mp3")

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))