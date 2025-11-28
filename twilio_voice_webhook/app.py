import os
from fastapi import FastAPI, Request
from fastapi.responses import Response
from twilio.twiml.voice_response import VoiceResponse
from dotenv import load_dotenv
import requests  # Add to imports

load_dotenv()

TWILIO_FORWARD_NUMBER = os.getenv("TWILIO_FORWARD_NUMBER", "+1XXXXXXXXXX")

app = FastAPI()


# --- Incoming Call ---
@app.post("/voice")
async def incoming_call():
    vr = VoiceResponse()
    vr.say("Hello! Thanks for calling Munimji. Connecting your call now.", voice="alice")

    # Record the call
    vr.record(
        action="/voice/recording",  # Callback URL for recording
        method="POST",
        max_length=3600,  # Max 1 hour (adjust as needed)
        play_beep=True,   # Optional beep before recording
        trim="trim-silence"  # Trim silence
    )

    # Forward call after recording
    vr.dial(TWILIO_FORWARD_NUMBER)

    return Response(content=str(vr), media_type="text/xml")


# --- Optional: Recording callback ---
@app.post("/voice/recording")
async def recording_callback(request: Request):
    form_data = await request.form()
    recording_url = form_data.get("RecordingUrl")
    call_sid = form_data.get("CallSid")

    if recording_url:
        # Download the recording (Twilio provides MP3/WAV)
        response = requests.get(recording_url)
        filename = f"recording_{call_sid}.mp3"
        with open(f"recordings/{filename}", "wb") as f:  # Save to 'recordings/' folder
            f.write(response.content)
        print(f"Recording saved: {filename}")
    
    return {"status": "recording saved"}


# --- Optional: Call status callback ---
@app.post("/voice/status")
async def status_callback():
    return {"status": "received"}


# Local dev server
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)