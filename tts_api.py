from fastapi import FastAPI, Form, BackgroundTasks
from fastapi.responses import FileResponse
from kittentts import TTS
import tempfile
import os
from asyncio import to_thread

app = FastAPI(title="KittenTTS API")
tts = TTS()

@app.post("/speak")
async def speak(background_tasks: BackgroundTasks, text: str = Form(...)):
    audio_bytes = await to_thread(tts.speak, text)

    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as tmp:
        tmp.write(audio_bytes)
        tmp_path = tmp.name

    background_tasks.add_task(os.remove, tmp_path)

    return FileResponse(
        path=tmp_path,
        media_type="audio/mpeg",
        filename="speech.mp3"
    )

@app.get("/health")
def health():
    return {"status": "ok"}