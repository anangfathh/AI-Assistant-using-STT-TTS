import os
import uuid
from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
import google.generativeai as genai
import speech_recognition as sr
from gtts import gTTS
from pydantic import BaseModel
from dotenv import load_dotenv
from pydub import AudioSegment
import io

load_dotenv()
try:
    GOOGLE_API_KEY = os.environ.get("GEMINI_API_KEY")
    if not GOOGLE_API_KEY:
        raise ValueError("GEMINI_API_KEY environment variable not set.")
    genai.configure(api_key=GOOGLE_API_KEY)
except ValueError as e:
    print(f"Error: {e}")
    print("Please set the GEMINI_API_KEY environment variable.")
    exit()

app = FastAPI()

os.makedirs("static/audio", exist_ok=True)
app.mount("/static", StaticFiles(directory="static"), name="static")

class ChatRequest(BaseModel):
    message: str

model = genai.GenerativeModel('gemini-2.5-flash')
chat_session = model.start_chat(history=[])

def text_to_speech(text: str) -> str:
    try:
        tts = gTTS(text=text, lang='en')
        filename = f"response_{uuid.uuid4()}.mp3"
        filepath = os.path.join("static/audio", filename)
        tts.save(filepath)
        return f"/static/audio/{filename}"
    except Exception as e:
        print(f"Error in text-to-speech conversion: {e}")
        raise HTTPException(status_code=500, detail="Failed to convert text to speech.")

def speech_to_text(audio_file_path: str) -> str:
    recognizer = sr.Recognizer()
    try:
        with sr.AudioFile(audio_file_path) as source:
            recognizer.adjust_for_ambient_noise(source)
            audio_data = recognizer.record(source)
            text = recognizer.recognize_google(audio_data)
            return text
    except sr.UnknownValueError:
        raise HTTPException(status_code=400, detail="Could not understand the audio. Please speak more clearly.")
    except sr.RequestError as e:
        raise HTTPException(status_code=500, detail=f"Speech recognition service error: {e}")
    except Exception as e:
        print(f"Error in speech-to-text conversion: {e}")
        raise HTTPException(status_code=500, detail="Failed to process audio file.")

@app.get("/", response_class=HTMLResponse)
async def get_root():
    with open("index.html") as f:
        return HTMLResponse(content=f.read(), status_code=200)

@app.post("/chat")
async def chat_handler(request: ChatRequest):
    try:
        response = chat_session.send_message(request.message)
        gemini_response_text = response.text

        audio_url = text_to_speech(gemini_response_text)

        return JSONResponse(content={
            "user_message": request.message,
            "gemini_response": gemini_response_text,
            "audio_url": audio_url
        })
    except Exception as e:
        print(f"An error occurred in /chat: {e}")
        raise HTTPException(status_code=500, detail="An internal error occurred.")

@app.post("/voice")
async def voice_handler(audio: UploadFile = File(...)):
    if not audio.content_type.startswith("audio/"):
        raise HTTPException(status_code=400, detail="Invalid file type. Please upload an audio file.")

    temp_wav_path = f"temp_{uuid.uuid4()}.wav"
    
    try:
        audio_content = await audio.read()

        try:
            audio_segment = AudioSegment.from_file(io.BytesIO(audio_content))
            
            audio_segment = audio_segment.set_channels(1).set_frame_rate(16000).set_sample_width(2)

            audio_segment.export(temp_wav_path, format="wav")
            
            print(f"Audio converted successfully. Duration: {len(audio_segment)/1000:.2f} seconds")
            
        except Exception as conversion_error:
            print(f"Audio conversion failed: {conversion_error}")
            raise HTTPException(
                status_code=500, 
                detail=f"Failed to convert audio format: {str(conversion_error)}"
            )

        transcribed_text = speech_to_text(temp_wav_path)

        response = chat_session.send_message(transcribed_text)
        gemini_response_text = response.text

        audio_url = text_to_speech(gemini_response_text)

        return JSONResponse(content={
            "user_transcription": transcribed_text,
            "gemini_response": gemini_response_text,
            "audio_url": audio_url
        })

    except HTTPException as e:
        raise e
    except Exception as e:
        print(f"An error occurred in /voice: {e}")
        raise HTTPException(status_code=500, detail=f"Voice processing failed: {str(e)}")
    finally:
        if os.path.exists(temp_wav_path):
            try:
                os.remove(temp_wav_path)
            except Exception as e:
                print(f"Failed to remove temp file: {e}")

@app.get("/health")
async def health_check():
    try:
        test_audio = AudioSegment.silent(duration=100)
        return JSONResponse(content={
            "status": "healthy",
            "ffmpeg_working": True,
            "pydub_working": True
        })
    except Exception as e:
        return JSONResponse(content={
            "status": "error",
            "ffmpeg_working": False,
            "error": str(e)
        })

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)