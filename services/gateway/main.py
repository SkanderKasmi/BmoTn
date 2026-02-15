from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse, JSONResponse
import httpx
import os
import logging
from typing import Optional
import json
from datetime import datetime

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="BMO API Gateway")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Service URLs with fallbacks
AI_SERVICE = os.getenv("AI_SERVICE_URL", "http://localhost:8001")
VOICE_SERVICE = os.getenv("VOICE_SERVICE_URL", "http://localhost:8002")
TASK_SERVICE = os.getenv("TASK_SERVICE_URL", "http://localhost:8003")

# HTTP client
client = httpx.AsyncClient(timeout=60.0)

# Service health cache
service_health = {}

# ==========================================
# UTILITY FUNCTIONS
# ==========================================
async def check_service_health(service_url: str, service_name: str) -> bool:
    """Check if a service is healthy"""
    try:
        response = await client.get(f"{service_url}/health", timeout=5.0)
        return response.status_code == 200
    except Exception as e:
        logger.warning(f"{service_name} health check failed: {e}")
        return False

# ==========================================
# ROOT ENDPOINT
# ==========================================
@app.get("/")
async def root():
    return {
        "service": "BMO API Gateway",
        "version": "2.0.0",
        "status": "running",
        "timestamp": datetime.now().isoformat(),
        "endpoints": {
            "chat": "/ai/chat",
            "emotion_analysis": "/ai/emotion-analysis",
            "intent_recognition": "/ai/intent-recognition",
            "text_to_speech": "/voice/text-to-speech",
            "speech_to_text": "/voice/speech-to-text",
            "user_profile": "/user/{session_id}",
            "health": "/health"
        }
    }

# ==========================================
# AI SERVICE ROUTES (ENHANCED)
# ==========================================
@app.post("/ai/chat")
async def ai_chat(request: Request):
    """Forward chat requests to AI service with emotion detection"""
    try:
        body = await request.json()
        logger.info(f"Chat request: session={body.get('session_id', 'unknown')}")
        
        response = await client.post(f"{AI_SERVICE}/chat", json=body)
        response.raise_for_status()
        
        return response.json()
    except httpx.HTTPError as e:
        logger.error(f"AI service error: {e}")
        raise HTTPException(status_code=503, detail="AI service unavailable")
    except Exception as e:
        logger.error(f"Chat error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/ai/emotion-analysis")
async def emotion_analysis(text: str):
    """Analyze emotion of text"""
    try:
        logger.info(f"Emotion analysis: {text[:50]}...")
        
        response = await client.post(
            f"{AI_SERVICE}/emotion-analysis",
            params={"text": text}
        )
        response.raise_for_status()
        
        return response.json()
    except Exception as e:
        logger.error(f"Emotion analysis error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/ai/intent-recognition")
async def intent_recognition(text: str):
    """Recognize user intent"""
    try:
        logger.info(f"Intent recognition: {text[:50]}...")
        
        response = await client.post(
            f"{AI_SERVICE}/intent-recognition",
            params={"text": text}
        )
        response.raise_for_status()
        
        return response.json()
    except Exception as e:
        logger.error(f"Intent recognition error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/ai/set-user")
async def set_user(session_id: str, name: str):
    """Set user name in AI service"""
    try:
        logger.info(f"Setting user: session={session_id}, name={name}")
        
        response = await client.post(
            f"{AI_SERVICE}/set-user",
            params={"session_id": session_id, "name": name}
        )
        response.raise_for_status()
        
        return response.json()
    except Exception as e:
        logger.error(f"Set user error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/ai/user-profile/{session_id}")
async def get_user_profile(session_id: str):
    """Get extensive user profile with history and preferences"""
    try:
        logger.info(f"Getting user profile: session={session_id}")
        
        response = await client.get(f"{AI_SERVICE}/user-profile/{session_id}")
        response.raise_for_status()
        
        return response.json()
    except Exception as e:
        logger.error(f"Get user profile error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/ai/dialogue-stats")
async def get_dialogue_stats():
    """Get statistics about available dialogue dataset"""
    try:
        response = await client.get(f"{AI_SERVICE}/dialogue-stats")
        response.raise_for_status()
        
        return response.json()
    except Exception as e:
        logger.error(f"Dialogue stats error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ==========================================
# VOICE SERVICE ROUTES (ENHANCED)
# ==========================================
@app.post("/voice/text-to-speech")
async def text_to_speech(request: Request):
    """Convert text to speech with emotion awareness"""
    try:
        body = await request.json()
        text = body.get("text", "")
        emotion = body.get("emotion", "neutral")
        language = body.get("language", "ar-TN")
        
        logger.info(f"TTS request: text='{text[:30]}...', emotion={emotion}")
        
        response = await client.post(
            f"{VOICE_SERVICE}/text-to-speech",
            json=body,
            timeout=30.0
        )
        response.raise_for_status()
        
        # Stream audio response
        return StreamingResponse(
            response.iter_bytes(),
            media_type="audio/mpeg",
            headers={
                "Content-Disposition": "attachment; filename=bmo_response.mp3",
                "Cache-Control": "no-cache"
            }
        )
    except Exception as e:
        logger.error(f"TTS error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/voice/speech-to-text")
async def speech_to_text(request: Request):
    """Convert speech to text"""
    try:
        body = await request.json()
        logger.info(f"STT request")
        
        response = await client.post(
            f"{VOICE_SERVICE}/speech-to-text",
            json=body
        )
        response.raise_for_status()
        
        return response.json()
    except Exception as e:
        logger.error(f"STT error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/voice/generate-emotional-response")
async def generate_emotional_response(text: str, session_id: str):
    """Generate AI response and convert to speech with emotion"""
    try:
        logger.info(f"Generating emotional response for session={session_id}")
        
        response = await client.post(
            f"{VOICE_SERVICE}/generate-emotional-response",
            params={"text": text, "session_id": session_id}
        )
        response.raise_for_status()
        
        return response.json()
    except Exception as e:
        logger.error(f"Emotional response error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/voice/config")
async def get_voice_config():
    """Get voice service configuration"""
    try:
        response = await client.get(f"{VOICE_SERVICE}/voice-config")
        response.raise_for_status()
        
        return response.json()
    except Exception as e:
        logger.error(f"Voice config error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ==========================================
# COMBINED ENDPOINTS
# ==========================================
@app.post("/chat-complete")
async def full_chat_with_voice(request: Request):
    """Complete chat interaction: text -> AI -> TTS"""
    try:
        body = await request.json()
        message = body.get("message", "")
        session_id = body.get("session_id", "")
        
        logger.info(f"Full chat with voice: session={session_id}")
        
        # Step 1: Get AI response with emotion
        ai_response = await client.post(
            f"{AI_SERVICE}/chat",
            json=body
        )
        ai_response.raise_for_status()
        ai_data = ai_response.json()
        
        # Step 2: Generate TTS with detected emotion
        tts_request = {
            "text": ai_data.get("response", ""),
            "language": body.get("language", "ar-TN"),
            "emotion": ai_data.get("detected_emotion", "neutral")
        }
        
        tts_response = await client.post(
            f"{VOICE_SERVICE}/text-to-speech",
            json=tts_request,
            timeout=30.0
        )
        tts_response.raise_for_status()
        
        # Return combined response
        return {
            "response_text": ai_data.get("response", ""),
            "detected_emotion": ai_data.get("detected_emotion", "neutral"),
            "confidence": ai_data.get("confidence", 0),
            "audio_available": True,
            "timestamp": ai_data.get("timestamp", datetime.now().isoformat())
        }
        
    except Exception as e:
        logger.error(f"Full chat error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ==========================================
# TASK SERVICE ROUTES
# ==========================================
@app.post("/task/execute")
async def execute_task(request: Request):
    """Execute a system task"""
    try:
        body = await request.json()
        logger.info(f"Executing task: {body.get('task_type', 'unknown')}")
        
        response = await client.post(f"{TASK_SERVICE}/execute", json=body)
        response.raise_for_status()
        
        return response.json()
    except Exception as e:
        logger.error(f"Task execution error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/task/apps/list")
async def list_apps():
    """Get list of available apps"""
    try:
        response = await client.get(f"{TASK_SERVICE}/apps/list")
        response.raise_for_status()
        
        return response.json()
    except Exception as e:
        logger.error(f"List apps error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ==========================================
# USER MANAGEMENT
# ==========================================
@app.get("/user/{session_id}")
async def get_user(session_id: str):
    """Get comprehensive user information"""
    try:
        profile = await client.get(f"{AI_SERVICE}/user-profile/{session_id}")
        profile.raise_for_status()
        
        return profile.json()
    except Exception as e:
        logger.error(f"Get user error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/user/{session_id}/name")
async def update_user_name(session_id: str, name: str):
    """Update user name"""
    try:
        response = await client.post(
            f"{AI_SERVICE}/set-user",
            params={"session_id": session_id, "name": name}
        )
        response.raise_for_status()
        
        return response.json()
    except Exception as e:
        logger.error(f"Update user name error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ==========================================
# HEALTH CHECK
# ==========================================
@app.get("/health")
async def health_check():
    """Comprehensive health check of all services"""
    try:
        health = {
            "gateway": "healthy",
            "timestamp": datetime.now().isoformat(),
            "services": {}
        }
        
        # Check AI service
        try:
            response = await client.get(f"{AI_SERVICE}/health", timeout=5.0)
            health["services"]["ai"] = response.json()
        except Exception as e:
            logger.warning(f"AI service health check failed: {e}")
            health["services"]["ai"] = {
                "status": "unhealthy",
                "error": str(e)
            }
        
        # Check Voice service
        try:
            response = await client.get(f"{VOICE_SERVICE}/health", timeout=5.0)
            health["services"]["voice"] = response.json()
        except Exception as e:
            logger.warning(f"Voice service health check failed: {e}")
            health["services"]["voice"] = {
                "status": "unhealthy",
                "error": str(e)
            }
        
        # Check Task service
        try:
            response = await client.get(f"{TASK_SERVICE}/health", timeout=5.0)
            health["services"]["task"] = response.json()
        except Exception as e:
            logger.warning(f"Task service health check failed: {e}")
            health["services"]["task"] = {
                "status": "unhealthy",
                "error": str(e)
            }
        
        # Overall status
        all_healthy = all(
            service.get("status") == "healthy"
            for service in health["services"].values()
        )
        health["overall_status"] = "healthy" if all_healthy else "degraded"
        
        return health
        
    except Exception as e:
        logger.error(f"Health check error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ==========================================
# ANALYTICS
# ==========================================
@app.get("/stats")
async def get_stats():
    """Get overall statistics"""
    try:
        ai_stats = await client.get(f"{AI_SERVICE}/dialogue-stats")
        voice_config = await client.get(f"{VOICE_SERVICE}/voice-config")
        
        return {
            "dialogues": ai_stats.json() if ai_stats.status_code == 200 else {},
            "voice": voice_config.json() if voice_config.status_code == 200 else {},
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Get stats error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ==========================================
# CLEANUP
# ==========================================
@app.on_event("shutdown")
async def shutdown():
    """Cleanup on shutdown"""
    await client.aclose()
    logger.info("Gateway shutdown")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
