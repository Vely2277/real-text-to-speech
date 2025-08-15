from fastapi import FastAPI, Form, BackgroundTasks, HTTPException
from fastapi.responses import FileResponse
from kittentts import TTS
import tempfile
import os
from asyncio import to_thread

app = FastAPI(title="KittenTTS API")
tts = TTS()

@app.post("/speak")
async def speak(background_tasks: BackgroundTasks, text: str = Form(...)):
    if not text.strip():
        raise HTTPException(status_code=400, detail="Text input cannot be empty.")

    try:
        audio_bytes = await to_thread(tts.speak, text)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"TTS engine error: {str(e)}")

    if not isinstance(audio_bytes, bytes):
        raise HTTPException(status_code=500, detail="Invalid audio output.")

    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as tmp:
        tmp.write(audio_bytes)
        tmp_path = tmp.name

    background_tasks.add_task(os.remove, tmp_path)

    try:
        return FileResponse(
            path=tmp_path,
            media_type="audio/mpeg",
            filename="speech.mp3"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"File response error: {str(e)}")

@app.get("/health")
def health():
    return {"status": "ok"}