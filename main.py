# main.py
"""
FastAPI entrypoint for KisanDost backend.
Unified endpoint:
  POST /api/farmer-query
Accepts optional voice_file and/or image_file, and returns a TTS audio path.
"""

import os
import shutil
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from app.ocr import run_ocr
from app.voice import transcribe_audio, text_to_speech
from app.agent import run_query, chat_completion
from app.config import DEFAULT_LANGUAGE, OUTPUT_DIRS

app = FastAPI(title="KisanDost Backend", version="1.0")

# Allow CORS for local dev (adjust origins in production)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/ping")
def ping():
    return {"message": "Backend running"}


@app.post("/api/farmer-query")
async def farmer_query(
    voice_file: UploadFile | None = File(None),
    image_file: UploadFile | None = File(None),
    lang: str = Form(DEFAULT_LANGUAGE),
):
    """
    Unified endpoint:
    - voice_file: optional audio file (wav, mp3, ogg, webm)
    - image_file: optional image (jpg, png)
    - lang: language code (en, ur, sd)
    Returns: {"voice_response": "<relative path to mp3>"} or HTTP error.
    """

    os.makedirs("temp", exist_ok=True)
    combined_text_parts = []

    # Save and transcribe voice
    if voice_file:
        try:
            voice_path = os.path.join("temp", voice_file.filename)
            with open(voice_path, "wb") as f:
                shutil.copyfileobj(voice_file.file, f)
            transcript = transcribe_audio(voice_path, language=lang)
            if transcript:
                combined_text_parts.append(transcript)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"ASR error: {e}")

    # Save and OCR image
    if image_file:
        try:
            image_path = os.path.join("temp", image_file.filename)
            with open(image_path, "wb") as f:
                shutil.copyfileobj(image_file.file, f)
            ocr_text = run_ocr(image_path)
            if ocr_text:
                combined_text_parts.append(ocr_text)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"OCR error: {e}")

    if not combined_text_parts:
        raise HTTPException(status_code=400, detail="No valid input provided (voice or image).")

    combined_query = "\n\n".join(combined_text_parts)
    print(f"[Main] Combined query length: {len(combined_query)} chars")

    # Build messages for agent
    messages = [
        {
            "role": "system",
            "content": (
                "You are an agricultural assistant for farmers in Pakistan. "
                "Explain usage, safety, and compatibility of agricultural chemicals. "
                "Keep answers short and practical. If needed, use the web search tool once."
            ),
        },
        {"role": "user", "content": combined_query},
    ]

    # Run agent
    agent_text = run_query(chat_completion(combined_query))

    if not agent_text:
        raise HTTPException(status_code=500, detail="Agent produced no response.")

    # Convert to speech
    tts_path = text_to_speech(agent_text, language=lang)
    if not tts_path:
        raise HTTPException(status_code=500, detail="TTS generation failed.")

    # Return path relative to server root (frontend will fetch /outputs/...)
    return {"voice_response": tts_path}

