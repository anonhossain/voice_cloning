from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path
from fastapi.staticfiles import StaticFiles
from api.views import api


app = FastAPI(title="Voice mate", description="Lets play with voice")

app.include_router(api)

# Allow frontend to communicate with backend (adjust origin if needed)
origins = ["*"]
# Set up CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,      # <- This allows all origins
    allow_credentials=True,
    allow_methods=["*"],      # Allow all HTTP methods (GET, POST, etc.)
    allow_headers=["*"],      # Allow all headers
)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="localhost",  # Use localhost IP address
        port=8080,
        reload=True
    )