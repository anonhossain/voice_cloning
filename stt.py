import requests
from dotenv import load_dotenv
import os

load_dotenv()
# Initialize ElevenLabs client

api_key=os.getenv("ELEVENLABS_API_KEY")

# Create transcript (POST /v1/speech-to-text)
response = requests.post(
  "https://api.elevenlabs.io/v1/speech-to-text",
  headers={
    "xi-api-key": api_key
  },
  data={
    'model_id': "scribe_v1",
    'file_format': "other",
  },
  files={
    'file': ('file/Recording.m4a', open('file/Recording.m4a', 'rb')),
  },
)

# print(response.json())

# ✅ Print only the full transcribed text
result = response.json()

if "text" in result:
    print("Transcribed Text:\n")
    print(result["text"])
else:
    print("Error in transcription:", result)