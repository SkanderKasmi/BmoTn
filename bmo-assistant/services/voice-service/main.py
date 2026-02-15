from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from google.cloud import speech_v1 as speech
from google.cloud import texttospeech
import io
import os
from pydantic import BaseModel

app = FastAPI(title="BMO Voice Service")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize Google Cloud clients
speech_client = speech.SpeechClient()
tts_client = texttospeech.TextToSpeechClient()

class TTSRequest(BaseModel):
    text: str
    language: str = "ar-TN"  # Tunisian Arabic
    voice_type: str = "childlike"  # BMO's voice

@app.post("/speech-to-text")
async def speech_to_text(audio: UploadFile = File(...)):
    """Convert speech to text (supports Arabic and French)"""
    try:
        # Read audio file
        content = await audio.read()
        
        # Configure recognition
        audio_config = speech.RecognitionAudio(content=content)
        config = speech.RecognitionConfig(
            encoding=speech.RecognitionConfig.AudioEncoding.WEBM_OPUS,
            sample_rate_hertz=48000,
            language_code="ar-TN",  # Tunisian Arabic
            alternative_language_codes=["fr-FR", "ar"],  # Fallback languages
            enable_automatic_punctuation=True,
            model="default"
        )
        
        # Perform recognition
        response = speech_client.recognize(config=config, audio=audio_config)
        
        # Extract transcript
        if response.results:
            transcript = response.results[0].alternatives[0].transcript
            confidence = response.results[0].alternatives[0].confidence
            
            return {
                "transcript": transcript,
                "confidence": confidence,
                "language": "ar-TN"
            }
        else:
            return {
                "transcript": "",
                "confidence": 0.0,
                "error": "No speech detected"
            }
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/text-to-speech")
async def text_to_speech(request: TTSRequest):
    """Convert text to speech with BMO-like voice"""
    try:
        # Configure voice (childlike, playful)
        if request.language.startswith("ar"):
            # Arabic voice
            voice = texttospeech.VoiceSelectionParams(
                language_code="ar-XA",  # Arabic
                name="ar-XA-Wavenet-D",  # Female voice (more childlike)
                ssml_gender=texttospeech.SsmlVoiceGender.FEMALE
            )
        else:
            # French fallback
            voice = texttospeech.VoiceSelectionParams(
                language_code="fr-FR",
                name="fr-FR-Wavenet-B",
                ssml_gender=texttospeech.SsmlVoiceGender.FEMALE
            )
        
        # Configure audio
        audio_config = texttospeech.AudioConfig(
            audio_encoding=texttospeech.AudioEncoding.MP3,
            speaking_rate=1.15,  # Slightly faster (energetic)
            pitch=4.0  # Higher pitch (childlike)
        )
        
        # Synthesize speech
        synthesis_input = texttospeech.SynthesisInput(text=request.text)
        response = tts_client.synthesize_speech(
            input=synthesis_input,
            voice=voice,
            audio_config=audio_config
        )
        
        # Return audio stream
        return StreamingResponse(
            io.BytesIO(response.audio_content),
            media_type="audio/mpeg"
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "bmo-voice"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8002)
