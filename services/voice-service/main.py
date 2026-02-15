from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import Optional, List, Dict
import httpx
import os
import json
import asyncio
import logging
from datetime import datetime

# Google Cloud imports (optional)
try:
    from google.cloud import texttospeech
    GOOGLE_AVAILABLE = True
except ImportError:
    GOOGLE_AVAILABLE = False
    logging.warning("Google Cloud TTS not available")

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="BMO Voice Service")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# AI Service client
AI_SERVICE_URL = os.getenv("AI_SERVICE_URL", "http://localhost:8001")
ai_client = httpx.AsyncClient(timeout=30.0)

# Text-to-Speech configuration
TTS_PROVIDER = os.getenv("TTS_PROVIDER", "google")  # "google" or "espeak"

# Google Cloud TTS client
if GOOGLE_AVAILABLE:
    try:
        tts_client = texttospeech.TextToSpeechClient()
    except Exception as e:
        logger.warning(f"Google Cloud TTS initialization failed: {e}")
        tts_client = None
else:
    tts_client = None

# ==========================================
# DATA MODELS
# ==========================================
class TextToSpeechRequest(BaseModel):
    text: str
    language: str = "ar-TN"
    emotion: Optional[str] = "neutral"
    gender: str = "MALE"  # MALE or FEMALE

class SpeechToTextRequest(BaseModel):
    audio_base64: str
    language: str = "ar-TN"

# ==========================================
# EMOTION-AWARE TEXT-TO-SPEECH
# ==========================================
EMOTION_VOICE_PARAMS = {
    "happy": {
        "pitch": 20,
        "speaking_rate": 1.1,
        "description": "Cheerful and upbeat"
    },
    "sad": {
        "pitch": -10,
        "speaking_rate": 0.8,
        "description": "Slow and melancholic"
    },
    "angry": {
        "pitch": 15,
        "speaking_rate": 1.2,
        "description": "Intense and fast"
    },
    "surprised": {
        "pitch": 25,
        "speaking_rate": 1.3,
        "description": "High-pitched and quick"
    },
    "tired": {
        "pitch": -15,
        "speaking_rate": 0.7,
        "description": "Slow and low"
    },
    "excited": {
        "pitch": 30,
        "speaking_rate": 1.3,
        "description": "Very high and fast"
    },
    "neutral": {
        "pitch": 0,
        "speaking_rate": 1.0,
        "description": "Normal"
    }
}

async def text_to_speech_google(
    text: str,
    language: str = "ar-TN",
    emotion: str = "neutral",
    gender: str = "FEMALE"
) -> bytes:
    """Convert text to speech using Google Cloud TTS"""
    
    if not tts_client:
        raise HTTPException(
            status_code=503,
            detail="Google Cloud TTS not available"
        )
    
    try:
        # Get emotion parameters
        emotion_params = EMOTION_VOICE_PARAMS.get(emotion, EMOTION_VOICE_PARAMS["neutral"])
        
        # Map language to voice name
        voice_map = {
            "ar-TN": ("ar-TN-Standard-A" if gender == "MALE" else "ar-TN-Standard-D"),
            "ar": ("ar-XA-Standard-B" if gender == "MALE" else "ar-XA-Standard-C"),
            "en": ("en-US-Standard-A" if gender == "MALE" else "en-US-Standard-C"),
            "fr": ("fr-FR-Standard-A" if gender == "MALE" else "fr-FR-Standard-C"),
        }
        
        voice_name = voice_map.get(language, "ar-TN-Standard-D")
        
        # Build TTS request
        synthesis_input = texttospeech.SynthesisInput(text=text)
        
        voice = texttospeech.VoiceSelectionParams(
            language_code=language,
            name=voice_name,
            ssml_gender=texttospeech.SsmlVoiceGender.FEMALE
        )
        
        audio_config = texttospeech.AudioConfig(
            audio_encoding=texttospeech.AudioEncoding.MP3,
            pitch=emotion_params["pitch"],
            speaking_rate=emotion_params["speaking_rate"]
        )
        
        # Synthesize speech
        response = tts_client.synthesize_speech(
            input=synthesis_input,
            voice=voice,
            audio_config=audio_config
        )
        
        logger.info(f"Generated audio for emotion: {emotion}")
        return response.audio_content
        
    except Exception as e:
        logger.error(f"Google TTS error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

async def text_to_speech_espeak(
    text: str,
    language: str = "ar-TN",
    emotion: str = "neutral"
) -> bytes:
    """Fallback: Convert text to speech using eSpeak"""
    
    try:
        import subprocess
        
        # eSpeak doesn't support Arabic well, but we can try
        emotion_params = EMOTION_VOICE_PARAMS.get(emotion, EMOTION_VOICE_PARAMS["neutral"])
        
        # Map language codes for espeak
        lang_map = {
            "ar-TN": "ar",
            "ar": "ar",
            "en": "en",
            "fr": "fr"
        }
        
        lang = lang_map.get(language, "ar")
        
        # Calculate speed from speaking rate
        speed = int(150 * emotion_params["speaking_rate"])
        pitch = 50 + (emotion_params["pitch"] // 2)
        
        # Run espeak command
        process = await asyncio.create_subprocess_exec(
            "espeak",
            f"-l{lang}",
            f"-s{speed}",
            f"-p{pitch}",
            "-mmp3",
            text,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        
        stdout, stderr = await process.communicate()
        
        if process.returncode != 0:
            logger.error(f"eSpeak error: {stderr}")
            raise Exception(f"eSpeak failed: {stderr}")
        
        logger.info(f"Generated audio with eSpeak for emotion: {emotion}")
        return stdout
        
    except Exception as e:
        logger.error(f"eSpeak TTS error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ==========================================
# TEXT-TO-SPEECH ENDPOINT
# ==========================================
@app.post("/text-to-speech")
async def tts(request: TextToSpeechRequest):
    """Convert text to speech with emotion awareness"""
    
    try:
        logger.info(f"TTS Request: text='{request.text[:50]}...', emotion={request.emotion}")
        
        # Use Google TTS if available, otherwise fallback to eSpeak
        if tts_client:
            audio_content = await text_to_speech_google(
                text=request.text,
                language=request.language,
                emotion=request.emotion,
                gender=request.gender
            )
        else:
            audio_content = await text_to_speech_espeak(
                text=request.text,
                language=request.language,
                emotion=request.emotion
            )
        
        # Return audio as MP3
        return StreamingResponse(
            iter([audio_content]),
            media_type="audio/mpeg",
            headers={
                "Content-Disposition": "attachment; filename=bmo_response.mp3",
                "Cache-Control": "no-cache"
            }
        )
        
    except Exception as e:
        logger.error(f"TTS error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ==========================================
# SPEECH-TO-TEXT ENDPOINT
# ==========================================
@app.post("/speech-to-text")
async def stt(request: SpeechToTextRequest):
    """Convert speech to text"""
    
    try:
        from google.cloud import speech_v1 as speech
        
        # Decode base64 audio
        import base64
        audio_content = base64.b64decode(request.audio_base64)
        
        # Initialize speech client
        speech_client = speech.SpeechClient()
        
        # Create audio config
        config = speech.RecognitionConfig(
            encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
            language_code=request.language,
            sample_rate_hertz=16000,
        )
        
        audio = speech.RecognitionAudio(content=audio_content)
        
        # Recognize speech
        response = speech_client.recognize(config=config, audio=audio)
        
        # Extract text
        transcript = ""
        confidence = 0.0
        
        for result in response.results:
            if result.alternatives:
                transcript = result.alternatives[0].transcript
                confidence = result.alternatives[0].confidence
        
        logger.info(f"Speech recognized: {transcript[:50]}... (confidence: {confidence})")
        
        return {
            "text": transcript,
            "confidence": confidence,
            "language": request.language
        }
        
    except Exception as e:
        logger.error(f"Speech-to-text error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ==========================================
# EMOTION-AWARE RESPONSE GENERATION
# ==========================================
@app.post("/generate-emotional-response")
async def generate_emotional_response(
    text: str,
    session_id: str,
    emotion: Optional[str] = None
):
    """Generate an emotional response to text"""
    
    try:
        # Call AI service to get response with emotion
        ai_response = await ai_client.post(
            f"{AI_SERVICE_URL}/chat",
            json={
                "message": text,
                "session_id": session_id,
                "language": "ar"
            }
        )
        
        response_data = ai_response.json()
        ai_text = response_data.get("response", "")
        detected_emotion = response_data.get("detected_emotion", "neutral")
        
        # Generate TTS with detected emotion
        audio_response = await text_to_speech_google(
            text=ai_text,
            language="ar-TN",
            emotion=detected_emotion,
            gender="FEMALE"
        )
        
        return {
            "response_text": ai_text,
            "detected_emotion": detected_emotion,
            "audio": audio_response.hex()  # Convert to hex for JSON serialization
        }
        
    except Exception as e:
        logger.error(f"Emotional response generation error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ==========================================
# TUNISIAN PROVERB SPEECH TRAINING
# ==========================================
@app.post("/speak-proverb")
async def speak_proverb(
    proverb_text: str,
    emotion: Optional[str] = "grateful",
    language: str = "ar-TN"
):
    """
    Generate audio for a Tunisian proverb with emotion-aware pronunciation.
    Great for learning authentic Tunisian Arabic speech patterns.
    """
    try:
        logger.info(f"Generating audio for proverb: {proverb_text[:50]}...")
        
        # Generate TTS with emotion for proper inflection
        audio_response = await text_to_speech_google(
            text=proverb_text,
            language=language,
            emotion=emotion,
            gender="FEMALE"  # Female voice for better proverb delivery
        )
        
        return {
            "proverb": proverb_text,
            "emotion": emotion,
            "language": language,
            "audio": audio_response.hex(),
            "timestamp": datetime.now().isoformat(),
            "description": f"Tunisian proverb spoken with {emotion} emotion"
        }
        
    except Exception as e:
        logger.error(f"Proverb speech error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/proverb-learning-session")
async def proverb_learning_session():
    """
    Get a guided learning session with Tunisian proverbs and audio.
    Returns a daily proverb for pronunciation training.
    """
    try:
        # Get random proverb from AI service
        proverb_response = await ai_client.get(
            f"{AI_SERVICE_URL}/random-proverb"
        )
        
        proverb_data = proverb_response.json()
        proverb_text = proverb_data.get("proverb", "")
        category = proverb_data.get("category", "General")
        
        if not proverb_text:
            return {
                "error": "No proverbs available",
                "message": "Proverbs dataset not loaded yet"
            }
        
        # Generate audio with contemplative emotion
        audio_response = await text_to_speech_google(
            text=proverb_text,
            language="ar-TN",
            emotion="grateful",
            gender="FEMALE"
        )
        
        return {
            "proverb": proverb_text,
            "category": category,
            "audio": audio_response.hex(),
            "learning_tips": [
                "Listen to the proverb carefully",
                "Notice the pronunciation patterns",
                "Repeat with same emotion and intonation",
                "Practice daily for authentic Tunisian accent"
            ],
            "timestamp": datetime.now().isoformat(),
            "language": "ar-TN",
            "difficulty": "beginner"
        }
        
    except Exception as e:
        logger.error(f"Proverb learning session error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/emotion-proverb-session/{emotion}")
async def emotion_proverb_session(emotion: str):
    """
    Get proverbs related to a specific emotion with proper voice inflection.
    Uses emotion-aware TTS to learn authentic emotional expression.
    """
    try:
        # Get proverbs for this emotion from AI service
        proverb_response = await ai_client.get(
            f"{AI_SERVICE_URL}/proverbs-by-emotion/{emotion}"
        )
        
        proverb_data = proverb_response.json()
        proverbs = proverb_data.get("proverbs", [])
        
        if not proverbs:
            return {
                "error": "No proverbs available for this emotion",
                "emotion": emotion
            }
        
        # Convert first proverb to speech with emotion
        selected_proverb = proverbs[0]
        proverb_text = selected_proverb.get("text", "")
        
        audio_response = await text_to_speech_google(
            text=proverb_text,
            language="ar-TN",
            emotion=emotion,
            gender="FEMALE"
        )
        
        return {
            "emotion": emotion,
            "selected_proverb": proverb_text,
            "category": selected_proverb.get("prompt", ""),
            "audio": audio_response.hex(),
            "recommended_practice": f"Use this proverb to practice {emotion} emotion with authentic Tunisian pronunciation",
            "total_available": proverb_data.get("count", 0),
            "tutorial_steps": [
                f"1. Listen to how {emotion} emotion changes voice pitch and speed",
                "2. Note the emotional inflection in Tunisian Arabic",
                "3. Repeat after the speaker",
                f"4. Practice expressing the same emotion in other sentences"
            ],
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Emotion proverb session error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ==========================================
# HEALTH CHECK
# ==========================================
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "bmo-voice",
        "google_tts_available": GOOGLE_AVAILABLE and tts_client is not None,
        "tts_provider": TTS_PROVIDER
    }

@app.get("/voice-config")
async def get_voice_config():
    """Get available voice configurations"""
    return {
        "emotions": list(EMOTION_VOICE_PARAMS.keys()),
        "languages": ["ar-TN", "ar", "en", "fr"],
        "genders": ["MALE", "FEMALE"],
        "tts_provider": TTS_PROVIDER,
        "emotion_voice_params": EMOTION_VOICE_PARAMS
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8002)
