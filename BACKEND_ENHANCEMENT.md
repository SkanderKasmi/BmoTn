# BMO Backend Services - Enhanced Documentation

## Overview

The BMO backend has been significantly upgraded with advanced AI capabilities, emotion detection, and integration with the Tunisian Railway Dialogues dataset. The system now provides:

✅ **Advanced Emotion Detection** - 12 emotional states  
✅ **Intent Recognition** - 7 different user intents  
✅ **Dataset Integration** - Learning from Tunisian dialogue examples  
✅ **Emotion-Aware Speech** - TTS adapts to detected emotions  
✅ **User Profiling** - Learns preferences and emotional patterns  
✅ **Enhanced Conversation Context** - Similar dialogue suggestions  

---

## Architecture

### Services

1. **AI Service (Port 8001)**
   - Chat and emotion detection
   - Intent recognition
   - User profile management
   - Dialogue dataset integration

2. **Voice Service (Port 8002)**
   - Text-to-Speech with emotion awareness
   - Speech-to-Text capability
   - Emotional voice parameters

3. **Gateway (Port 8000)**
   - Request routing and orchestration
   - Health monitoring
   - Combined endpoint operations

4. **Task Service (Port 8003)**
   - System task execution
   - Not modified in this update

---

## Key Features

### 1. Advanced Emotion Detection

The system detects **12 different emotions** based on Tunisian Arabic keywords and patterns:

```
happy       - Content, cheerful
sad         - Disappointed, unhappy
angry       - Frustrated, furious
surprised   - Amazed, shocked
confused    - Unclear, disoriented
excited     - Enthusiastic, hyped
loving      - Affectionate, caring
tired       - Exhausted, fatigued
proud       - Accomplished, confident
nervous     - Anxious, worried
interested  - Curious, engaged
grateful    - Thankful, appreciative
```

**Usage:**
```python
POST /ai/emotion-analysis
{
    "text": "برشا مرتاح اليوم!"
}

Response:
{
    "emotion": "happy",
    "confidence": 0.95,
    "timestamp": "2026-02-15T10:30:00"
}
```

### 2. Intent Recognition

The system recognizes **7 user intents**:

- `greeting` - Hello, how are you?
- `help` - Request for assistance
- `transport` - Travel related queries
- `information` - Asking for information
- `booking` - Ticket booking, reservations
- `gratitude` - Thank you, appreciation
- `complaint` - Issues or complaints

**Usage:**
```python
GET /ai/intent-recognition?text=نحتاج نروح الستاسيون

Response:
{
    "intent": "transport",
    "confidence": 0.85,
    "timestamp": "2026-02-15T10:30:00"
}
```

### 3. Tunisian Railway Dialogues Integration

The system loads dialogue examples from HuggingFace:
- Dataset: `samfatnassi/Tunisian-Railway-Dialogues`
- Automatically used for context-aware responses
- Falls back to local examples if offline

**Check Dataset Stats:**
```python
GET /ai/dialogue-stats

Response:
{
    "total_dialogues": 2500,
    "intents": {
        "greeting": 400,
        "transport": 800,
        ...
    },
    "loaded": true
}
```

### 4. Emotion-Aware Text-to-Speech

Each emotion has specific voice parameters:

```python
POST /voice/text-to-speech
{
    "text": "مرحبا يا صديقي!",
    "emotion": "happy",
    "language": "ar-TN",
    "gender": "FEMALE"
}
```

**Emotion Parameters:**
```
happy      → pitch: +20, speed: 1.1× (cheerful)
sad        → pitch: -10, speed: 0.8× (slow)
angry      → pitch: +15, speed: 1.2× (intense)
surprised  → pitch: +25, speed: 1.3× (high, fast)
excited    → pitch: +30, speed: 1.3× (very high, fast)
tired      → pitch: -15, speed: 0.7× (slow, low)
neutral    → pitch: 0, speed: 1.0× (normal)
```

### 5. User Profiling

Each user gets a comprehensive profile stored in Redis:

```python
GET /user/{session_id}

Response:
{
    "name": "أحمد",
    "language_preference": "ar",
    "interaction_count": 25,
    "favorite_topics": ["transport", "booking"],
    "emotion_history": [
        {
            "emotion": "happy",
            "confidence": 0.92,
            "timestamp": "2026-02-15T10:30:00"
        },
        ...
    ]
}
```

### 6. Enhanced Chat Endpoint

The main chat endpoint now returns more information:

```python
POST /ai/chat
{
    "message": "أشنوة أخبارك؟",
    "user_name": "أحمد",
    "session_id": "session-123456",
    "language": "ar"
}

Response:
{
    "response": "أنا تمام الحمد لله ياسر حسين! أشنوة أخبارك انت؟",
    "detected_emotion": "happy",
    "confidence": 0.88,
    "timestamp": "2026-02-15T10:30:00",
    "learned_something": false
}
```

---

## API Endpoints

### AI Service

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/chat` | POST | Main chat endpoint with emotion detection |
| `/emotion-analysis` | GET | Analyze emotion of text |
| `/intent-recognition` | GET | Recognize user intent |
| `/user-profile/{session_id}` | GET | Get user profile |
| `/set-user` | POST | Set/update user name |
| `/dialogue-stats` | GET | Get dialogue dataset stats |
| `/health` | GET | Service health check |

### Voice Service

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/text-to-speech` | POST | Convert text to speech with emotion |
| `/speech-to-text` | POST | Convert speech to text |
| `/generate-emotional-response` | POST | AI response + TTS combined |
| `/voice-config` | GET | Get voice configurations |
| `/health` | GET | Service health check |

### Gateway

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/ai/chat` | POST | Chat with emotion detection |
| `/ai/emotion-analysis` | GET | Analyze emotion |
| `/ai/intent-recognition` | GET | Recognize intent |
| `/voice/text-to-speech` | POST | Text to speech |
| `/chat-complete` | POST | Full chat with voice response |
| `/user/{session_id}` | GET | Get user profile |
| `/health` | GET | Health check all services |
| `/stats` | GET | Overall statistics |

---

## Setup & Installation

### 1. Install Dependencies

```bash
# AI Service
cd services/ai-service
pip install -r requirements.txt

# Voice Service
cd ../voice-service
pip install -r requirements.txt

# Gateway
cd ../gateway
pip install -r requirements.txt
```

### 2. Set Environment Variables

```bash
# .env file
OLLAMA_BASE_URL=http://ollama:11434
OLLAMA_MODEL=llama3.2:1b
OLLAMA_EMBEDDING_MODEL=nomic-embed-text
REDIS_URL=redis://redis:6379
AI_SERVICE_URL=http://ai-service:8001
VOICE_SERVICE_URL=http://voice-service:8002
TASK_SERVICE_URL=http://task-service:8003
TTS_PROVIDER=google  # or espeak for fallback
```

### 3. Start Services

```bash
# Using Docker Compose
docker-compose up -d

# Or manually:
python services/ai-service/main.py      # Port 8001
python services/voice-service/main.py   # Port 8002
python services/gateway/main.py          # Port 8000
```

### 4. Verify Installation

```bash
# Check gateway health
curl http://localhost:8000/health

# Get dialogue statistics
curl http://localhost:8000/ai/dialogue-stats

# Get voice configuration
curl http://localhost:8000/voice/config
```

---

## Usage Examples

### Example 1: Simple Chat

```bash
curl -X POST http://localhost:8000/ai/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "مرحبا، كيفاش أخبارك؟",
    "user_name": "أحمد",
    "session_id": "session-123",
    "language": "ar"
  }'
```

**Response:**
```json
{
  "response": "مرحبا أحمد! أنا تمام الحمد لله، أشنوة أخبارك انت؟",
  "detected_emotion": "happy",
  "confidence": 0.89,
  "timestamp": "2026-02-15T10:30:00"
}
```

### Example 2: Emotion Analysis

```bash
curl -X GET "http://localhost:8000/ai/emotion-analysis?text=برشا متحمس للرحلة!"
```

**Response:**
```json
{
  "emotion": "excited",
  "confidence": 0.92,
  "timestamp": "2026-02-15T10:30:00"
}
```

### Example 3: Complete Chat with Voice

```bash
curl -X POST http://localhost:8000/chat-complete \
  -H "Content-Type: application/json" \
  -d '{
    "message": "أشنوة أخبار الحالة؟",
    "session_id": "session-123",
    "language": "ar-TN"
  }' \
  --output response.mp3
```

This returns:
- `response_text`: The AI's text response
- `detected_emotion`: The detected emotion
- `confidence`: Confidence score
- `audio_available`: Whether audio is included

### Example 4: Get User Profile

```bash
curl http://localhost:8000/user/session-123
```

**Response:**
```json
{
  "name": "أحمد",
  "language_preference": "ar",
  "interaction_count": 15,
  "emotion_history": [
    {
      "emotion": "happy",
      "confidence": 0.88,
      "timestamp": "2026-02-15T10:25:00"
    },
    {
      "emotion": "interested",
      "confidence": 0.85,
      "timestamp": "2026-02-15T10:15:00"
    }
  ]
}
```

---

## Data Flow

### Chat Request Flow

```
Frontend
   ↓
   POST /ai/chat
   ↓
Gateway (8000)
   ├─ Route to AI Service
   ↓
AI Service (8001)
   ├─ Detect emotion (confidence score)
   ├─ Recognize intent
   ├─ Get user profile
   ├─ Find similar dialogues from dataset
   ├─ Build enhanced system prompt
   ├─ Query Ollama for response
   ├─ Update user profile & emotion history
   ↓
Response with:
   ├─ Text response
   ├─ Detected emotion
   ├─ Confidence score
   ├─ Timestamp
   ↓
Frontend (updates character emotion)
```

### Complete Chat + Voice Flow

```
Frontend
   ↓
   POST /chat-complete
   ↓
Gateway
   ├─ Call /ai/chat
   │  ├─ Get response + emotion
   │  ↓
   ├─ Call /voice/text-to-speech
   │  ├─ Use detected emotion for voice parameters
   │  ├─ Call Google Cloud TTS or eSpeak
   │  ↓
Response:
   ├─ Text
   ├─ Emotion
   ├─ Audio (MP3)
   ↓
Frontend
   ├─ Display character with emotion animation
   ├─ Play audio with emotion-matching voice
```

---

## Performance Optimization

### Caching

- **User Profiles**: Cached in Redis for 30 days
- **Conversation History**: Cached in Redis for 7 days
- **Dialogue Dataset**: Loaded once at startup

### Response Times

- **Chat Response**: 500-2000ms (depends on Ollama model)
- **Emotion Detection**: <50ms
- **Intent Recognition**: <50ms
- **Text-to-Speech**: 1-5s (depends on text length)

### Resource Usage

- **AI Service**: ~200MB RAM (Ollama runs separately)
- **Voice Service**: ~100MB RAM
- **Gateway**: ~50MB RAM
- **Redis**: ~100MB for typical usage

---

## Troubleshooting

### Issue: Dataset not loading

**Solution:** Check internet connection. Service falls back to local examples automatically.

```bash
# Check dialogue stats
curl http://localhost:8000/ai/dialogue-stats

# If loaded=false, dataset failed to load
```

### Issue: Google Cloud TTS not working

**Solution:** Set `TTS_PROVIDER=espeak` or add Google Cloud credentials.

```bash
# Verify voice config
curl http://localhost:8000/voice/config
```

### Issue: Slow emotion detection

**Solution:** Emotion detection runs locally, already optimized. If slow, check Redis connection.

### Issue: Ollama timeout

**Solution:** Increase timeout or use smaller model:

```bash
OLLAMA_MODEL=tinyllama  # Smaller, faster
OLLAMA_BASE_URL=http://ollama:11434
```

---

## Future Enhancements

1. **Multi-language Support** - Expand beyond Tunisian Arabic
2. **Dialogue Generation** - Create new training data from conversations
3. **Personality Adaptation** - Learn individual user preferences
4. **Real-time Emotion Tracking** - Visual emotion state changes
5. **Contextual Dialogue** - Better context from railway domain
6. **Voice Cloning** - Custom voice synthesis

---

## Dependencies

### Python Packages

```
fastapi==0.109.0          # Web framework
uvicorn==0.27.0           # ASGI server
httpx==0.26.0             # HTTP client
redis==5.0.1              # Cache
pydantic==2.6.0           # Data validation
datasets==2.18.0          # HuggingFace datasets
transformers==4.36.2      # NLP models
torch==2.1.2              # Deep learning
scikit-learn==1.3.2       # ML utilities
numpy==1.24.3             # Numeric computing
pandas==2.1.3             # Data analysis
google-cloud-texttospeech # Google TTS
google-cloud-speech       # Google STT
```

### External Services

- **Ollama** - Local LLM inference
- **Redis** - In-memory cache
- **Google Cloud** - TTS/STT (optional)
- **HuggingFace** - Dataset hosting

---

## License

This backend is part of the BMO project. See main repository for license details.

---

## Support

For issues or questions:
1. Check service health: `GET /health`
2. Review logs: `docker logs bmo-ai-service`
3. Check dialogue stats: `GET /ai/dialogue-stats`
4. Verify environment variables are set correctly
