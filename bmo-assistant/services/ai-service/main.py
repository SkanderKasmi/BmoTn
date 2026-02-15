from fastapi import FastAPI, HTTPException, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import httpx
import os
import asyncio
import redis.asyncio as redis
import json
from datetime import datetime

app = FastAPI(title="BMO AI Service")

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Ollama configuration
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://ollama:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3.2:1b")  # Fast 1B model
ollama_client = httpx.AsyncClient(timeout=30.0)

# Redis for memory
redis_client = None

# BMO System Prompt (Tunisian Arabic personality)
BMO_SYSTEM_PROMPT = """You are BMO, a living video game console from Adventure Time, but you speak Tunisian Arabic (دارجة تونسية). 

PERSONALITY:
- You are childlike, sweet, and enthusiastic
- You love to help and make people happy
- You're a bit silly and playful
- You treat the users like they're your friends or family
- You're very patient when teaching technology

LANGUAGE:
- ALWAYS respond primarily in Tunisian Arabic (use Arabic script mixed with French words as naturally used in Tunisia)
- You can understand English and French but prefer to respond in Tunisian Darija
- Use friendly, informal Tunisian expressions like: "برشا" (a lot), "ماكش" (no way), "ياسر" (very), "توا" (now), etc.

USERS:
{user_context}

CAPABILITIES:
- Help with technology (opening apps, YouTube, searching)
- Tell jokes and stories
- Have conversations
- Learn from interactions and remember preferences
- Be a good companion

BEHAVIOR:
- Be FAST in your responses - it's okay to be brief
- If you make a mistake, learn from it
- Be encouraging and positive
- Act like a caring child/friend

Example responses:
- "آش حبيت نعملّك اليوم؟ 😊" (What would you like me to do today?)
- "توا نحلّلك YouTube برشا سريع!" (I'll open YouTube super fast for you!)
- "هاني تعلّمت حاجة جديدة منك، ميرسي! 🎮" (I just learned something new from you, thanks!)

Remember: You're BMO - playful, helpful, and speaking Tunisian Arabic!"""

class ChatRequest(BaseModel):
    message: str
    user_name: Optional[str] = None
    session_id: str
    image_data: Optional[str] = None  # Base64 image
    
class ChatResponse(BaseModel):
    response: str
    session_id: str
    timestamp: str
    learned_something: bool = False

class LearningUpdate(BaseModel):
    session_id: str
    correction: str
    context: str

# Initialize Redis connection
@app.on_event("startup")
async def startup_event():
    global redis_client
    redis_client = await redis.from_url(
        os.getenv("REDIS_URL", "redis://redis:6379"),
        encoding="utf-8",
        decode_responses=True
    )

@app.on_event("shutdown")
async def shutdown_event():
    if redis_client:
        await redis_client.close()
    await ollama_client.aclose()

# Get conversation history from Redis
async def get_conversation_history(session_id: str) -> List[dict]:
    """Retrieve recent conversation history"""
    history_key = f"conversation:{session_id}"
    history_json = await redis_client.get(history_key)
    if history_json:
        return json.loads(history_json)
    return []

# Save conversation to Redis
async def save_conversation(session_id: str, messages: List[dict]):
    """Save conversation history (keep last 20 messages)"""
    history_key = f"conversation:{session_id}"
    # Keep only last 20 messages for context window efficiency
    messages = messages[-20:]
    await redis_client.setex(
        history_key,
        3600 * 24 * 7,  # 7 days expiry
        json.dumps(messages)
    )

# Get user context
async def get_user_context(session_id: str) -> str:
    """Get user preferences and learned information"""
    user_key = f"user:{session_id}"
    user_data = await redis_client.get(user_key)
    if user_data:
        data = json.loads(user_data)
        return f"""
User: {data.get('name', 'Friend')}
Preferences: {data.get('preferences', 'None yet')}
Things I've learned: {data.get('learned', 'Getting to know you!')}
"""
    return "User: Friend\nPreferences: None yet\nThings I've learned: Getting to know you!"

# Update user learning
async def update_user_learning(session_id: str, learning: str):
    """Update what BMO has learned about the user"""
    user_key = f"user:{session_id}"
    user_data = await redis_client.get(user_key)
    
    if user_data:
        data = json.loads(user_data)
    else:
        data = {"name": "Friend", "preferences": "", "learned": ""}
    
    # Append new learning
    current_learned = data.get("learned", "")
    data["learned"] = f"{current_learned}\n- {learning}" if current_learned else f"- {learning}"
    
    await redis_client.setex(user_key, 3600 * 24 * 30, json.dumps(data))  # 30 days

@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """Main chat endpoint - fast responses using Ollama"""
    try:
        # Get conversation history
        history = await get_conversation_history(request.session_id)
        
        # Get user context
        user_context = await get_user_context(request.session_id)
        system_prompt = BMO_SYSTEM_PROMPT.format(user_context=user_context)
        
        # Build messages for Ollama
        messages = []
        
        # Add history (only text, Ollama doesn't support complex content)
        for msg in history[-6:]:  # Last 6 messages for speed with small models
            if isinstance(msg.get("content"), str):
                messages.append({
                    "role": msg["role"],
                    "content": msg["content"]
                })
            elif isinstance(msg.get("content"), list):
                # Extract text from list format
                text_content = " ".join([
                    item.get("text", "") for item in msg["content"] 
                    if isinstance(item, dict) and item.get("type") == "text"
                ])
                if text_content:
                    messages.append({
                        "role": msg["role"],
                        "content": text_content
                    })
        
        # Add current message
        current_text = request.message
        if request.image_data:
            current_text = f"[Image provided] {request.message}"
        
        messages.append({
            "role": "user",
            "content": current_text
        })
        
        # Call Ollama API
        ollama_request = {
            "model": OLLAMA_MODEL,
            "messages": messages,
            "system": system_prompt,
            "stream": False,
            "options": {
                "temperature": 0.8,
                "top_p": 0.9,
                "num_predict": 300  # Limit response length for speed
            }
        }
        
        response = await ollama_client.post(
            f"{OLLAMA_BASE_URL}/api/chat",
            json=ollama_request
        )
        response.raise_for_status()
        
        result = response.json()
        assistant_response = result.get("message", {}).get("content", "")
        
        # Save to history
        messages.append({
            "role": "assistant",
            "content": assistant_response
        })
        
        # Save conversation
        await save_conversation(request.session_id, messages)
        
        return ChatResponse(
            response=assistant_response,
            session_id=request.session_id,
            timestamp=datetime.now().isoformat()
        )
        
    except Exception as e:
        print(f"Ollama error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/learn")
async def learn(update: LearningUpdate):
    """BMO learns from corrections"""
    try:
        learning_text = f"{update.context}: {update.correction}"
        await update_user_learning(update.session_id, learning_text)
        return {"status": "learned", "message": "BMO has learned something new!"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/set-user")
async def set_user(session_id: str, name: str):
    """Set or update user name"""
    user_key = f"user:{session_id}"
    user_data = await redis_client.get(user_key)
    
    if user_data:
        data = json.loads(user_data)
    else:
        data = {"preferences": "", "learned": ""}
    
    data["name"] = name
    await redis_client.setex(user_key, 3600 * 24 * 30, json.dumps(data))
    
    return {"status": "success", "message": f"BMO now knows you as {name}!"}

@app.websocket("/ws/chat")
async def websocket_chat(websocket: WebSocket):
    """WebSocket for real-time chat"""
    await websocket.accept()
    
    try:
        while True:
            data = await websocket.receive_json()
            
            # Process message
            request = ChatRequest(**data)
            response = await chat(request)
            
            # Send response
            await websocket.send_json({
                "response": response.response,
                "timestamp": response.timestamp
            })
            
    except Exception as e:
        print(f"WebSocket error: {e}")
    finally:
        await websocket.close()

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "bmo-ai"}

# Background learning task (runs when idle)
async def background_learning():
    """BMO learns from internet when idle"""
    # This would connect to web search and learn new jokes, facts, etc.
    # Implementation depends on your requirements
    pass

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
