from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path
from fastapi.staticfiles import StaticFiles
from api.views import api


app = FastAPI(title="Voice mate", description="Lets play with voice")

app.include_router(api)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="localhost",  # Use localhost IP address
        port=8080,
        reload=True
    )