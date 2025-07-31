# 🗣️ Voice Clone App

A simple voice cloning application using [ElevenLabs](https://www.elevenlabs.io/) API and OpenAI. This tool allows you to generate speech using cloned voices.

---

## Features

- Clone voice using ElevenLabs API
- Convert input text into high-quality speech
- Local audio processing with FFMPEG

---

## Setup Instructions

### 1. Clone the Repository

```bash
git clone https://github.com/anonhossain/voice_cloning
cd voice_cloning
```
 
## 2. Install the requirements

```bash
pip install -r requirements.txt
```
## 4. Create .env file and put the credentials

Install FFMPEG and set the variable path.

## 4. Create .env file and put the credentials

```bash
ELEVENLABS_API_KEY='your_elevenlabs_api_key'
OPENAI_API_KEY='your_openai_api_key'

FFMPEG_PATH='C:\\path\\to\\ffmpeg.exe'
FFPROBE_PATH='C:\\path\\to\\ffprobe.exe'

ELEVENLABS_VOICE_ID='your_voice_id'
ELEVENLABS_VOICE_NAME='your_voice_name'

```

## 5. Once setup is complete, you can run the app

``` bash
python app.py
```
