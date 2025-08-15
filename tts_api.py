from fastapi import FastAPI, Form, BackgroundTasks, HTTPException
from fastapi.responses import FileResponse
from kittentts import KittenTTS
import tempfile
import os
from asyncio import to_thread

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
        audio = await to_thread(tts.generate, text, voice=voice)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"TTS engine error: {str(e)}")

    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp:
        tmp.write(audio)
        tmp_path = tmp.name

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