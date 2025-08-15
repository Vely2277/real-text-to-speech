from fastapi import FastAPI, Form, BackgroundTasks, HTTPException
from fastapi.responses import FileResponse
from kittentts import KittenTTS
import tempfile
import os
from asyncio import to_thread
import numpy as np
import soundfile as sf

app = FastAPI(title="KittenTTS API")

# Load model once at startup
tts = KittenTTS("KittenML/kitten-tts-nano-0.1")

@app.post("/speak")
async def speak(
    background_tasks: BackgroundTasks,
    text: str = Form(...),
    voice: str = Form("expr-voice-2-f")  # default voice
):
    if not text.strip():
        raise HTTPException(status_code=400, detail="Text input cannot be empty.")

    try:
        raw_audio = await to_thread(tts.generate, text, voice=voice)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"TTS engine error: {str(e)}")

    # Detect format and convert safely
    if isinstance(raw_audio, np.ndarray):
        pcm_array = raw_audio
    elif isinstance(raw_audio, bytes):
        # Assuming float32 PCM from KittenTTS; update if model changes
        pcm_array = np.frombuffer(raw_audio, dtype=np.float32)
    else:
        raise HTTPException(status_code=500, detail="Unknown audio format")

    # Convert float32 to int16 if needed
    if pcm_array.dtype == np.float32:
        pcm_array = (pcm_array * 32767).astype(np.int16)

    # Get sample rate from model metadata (if available)
    sample_rate = getattr(tts, "sample_rate", 24000)  # fallback to 24000

    # Save as proper WAV
    tmp_path = tempfile.NamedTemporaryFile(delete=False, suffix=".wav").name
    sf.write(tmp_path, pcm_array, samplerate=sample_rate)

    background_tasks.add_task(os.remove, tmp_path)

    return FileResponse(
        path=tmp_path,
        media_type="audio/wav",
        filename="speech.wav"
    )

@app.get("/voices")
def voices():
    return {
        "available_voices": [
            "expr-voice-2-m", "expr-voice-2-f",
            "expr-voice-3-m", "expr-voice-3-f",
            "expr-voice-4-m", "expr-voice-4-f",
            "expr-voice-5-m", "expr-voice-5-f"
        ]
    }

@app.get("/health")
def health():
    return {"status": "ok"}