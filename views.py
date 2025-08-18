from fastapi import APIRouter, UploadFile, File, HTTPException
from clone import remove_noise_and_clone_voice, clone_name  # import your function

router = APIRouter()

@router.post("/clone-voice/")
async def clone_voice(file: UploadFile = File(...)):
    try:
        voice_id = remove_noise_and_clone_voice(file.file, clone_name, skip_noise_reduction=True)
        return {"voice_id": voice_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))