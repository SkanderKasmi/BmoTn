from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
import httpx
import os

app = FastAPI(title="BMO API Gateway")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Service URLs
AI_SERVICE = os.getenv("AI_SERVICE_URL", "http://localhost:8001")
VOICE_SERVICE = os.getenv("VOICE_SERVICE_URL", "http://localhost:8002")
TASK_SERVICE = os.getenv("TASK_SERVICE_URL", "http://localhost:8003")

# HTTP client
client = httpx.AsyncClient(timeout=60.0)

@app.get("/")
async def root():
    return {
        "service": "BMO API Gateway",
        "version": "1.0.0",
        "status": "running"
    }

# AI Service Routes
@app.post("/ai/chat")
async def ai_chat(request: Request):
    """Forward chat requests to AI service"""
    try:
        body = await request.json()
        response = await client.post(f"{AI_SERVICE}/chat", json=body)
        return response.json()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/ai/learn")
async def ai_learn(request: Request):
    """Forward learning updates to AI service"""
    try:
        body = await request.json()
        response = await client.post(f"{AI_SERVICE}/learn", json=body)
        return response.json()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/ai/set-user")
async def set_user(session_id: str, name: str):
    """Set user name in AI service"""
    try:
        response = await client.post(
            f"{AI_SERVICE}/set-user",
            params={"session_id": session_id, "name": name}
        )
        return response.json()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Voice Service Routes
@app.post("/voice/speech-to-text")
async def speech_to_text(request: Request):
    """Forward speech-to-text requests"""
    try:
        form = await request.form()
        files = {"audio": (form["audio"].filename, form["audio"].file, form["audio"].content_type)}
        response = await client.post(f"{VOICE_SERVICE}/speech-to-text", files=files)
        return response.json()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/voice/text-to-speech")
async def text_to_speech(request: Request):
    """Forward text-to-speech requests"""
    try:
        body = await request.json()
        response = await client.post(f"{VOICE_SERVICE}/text-to-speech", json=body)
        
        # Stream audio response
        return StreamingResponse(
            response.iter_bytes(),
            media_type="audio/mpeg"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Task Service Routes
@app.post("/task/execute")
async def execute_task(request: Request):
    """Forward task execution requests"""
    try:
        body = await request.json()
        response = await client.post(f"{TASK_SERVICE}/execute", json=body)
        return response.json()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/task/apps/list")
async def list_apps():
    """Get list of available apps"""
    try:
        response = await client.get(f"{TASK_SERVICE}/apps/list")
        return response.json()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/task/android/intent")
async def android_intent(request: Request):
    """Generate Android intent"""
    try:
        body = await request.json()
        response = await client.post(f"{TASK_SERVICE}/android/intent", json=body)
        return response.json()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Health check
@app.get("/health")
async def health_check():
    """Check health of all services"""
    health = {
        "gateway": "healthy",
        "services": {}
    }
    
    # Check AI service
    try:
        response = await client.get(f"{AI_SERVICE}/health", timeout=5.0)
        health["services"]["ai"] = response.json()
    except:
        health["services"]["ai"] = {"status": "unhealthy"}
    
    # Check Voice service
    try:
        response = await client.get(f"{VOICE_SERVICE}/health", timeout=5.0)
        health["services"]["voice"] = response.json()
    except:
        health["services"]["voice"] = {"status": "unhealthy"}
    
    # Check Task service
    try:
        response = await client.get(f"{TASK_SERVICE}/health", timeout=5.0)
        health["services"]["task"] = response.json()
    except:
        health["services"]["task"] = {"status": "unhealthy"}
    
    return health

@app.on_event("shutdown")
async def shutdown():
    await client.aclose()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
