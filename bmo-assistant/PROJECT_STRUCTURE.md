# BMO Assistant - Project Structure

```
bmo-assistant/
│
├── 📄 README.md                    # Main project documentation
├── 📄 SETUP_GUIDE.md              # Detailed setup instructions
├── 📄 FEATURES.md                 # Complete features list
├── 📄 docker-compose.yml          # Docker orchestration
├── 📄 .env.example                # Environment variables template
├── 📄 .env                        # Your API keys (create from .env.example)
├── 📄 credentials.json            # Google Cloud credentials (you provide)
├── 🚀 start.sh                    # Quick start script
│
├── 📁 services/                   # Backend microservices
│   │
│   ├── 📁 ai-service/            # AI/LLM service
│   │   ├── main.py               # FastAPI app with Anthropic Claude
│   │   ├── requirements.txt      # Python dependencies
│   │   └── Dockerfile           # Container definition
│   │
│   ├── 📁 voice-service/         # Speech recognition & TTS
│   │   ├── main.py               # FastAPI app with Google Cloud
│   │   ├── requirements.txt      # Python dependencies
│   │   └── Dockerfile           # Container definition
│   │
│   ├── 📁 task-service/          # App launching & automation
│   │   ├── main.py               # FastAPI app for system tasks
│   │   ├── requirements.txt      # Python dependencies
│   │   └── Dockerfile           # Container definition
│   │
│   └── 📁 gateway/               # API Gateway
│       ├── main.py               # Request routing
│       ├── requirements.txt      # Python dependencies
│       └── Dockerfile           # Container definition
│
├── 📁 frontend/                   # Frontend applications
│   │
│   ├── 📁 web/                   # Web interface (React)
│   │   ├── 📁 src/
│   │   │   ├── App.js           # Main web app
│   │   │   ├── AppWithPopup.js  # Enhanced app with popup
│   │   │   ├── App.css          # BMO face styling
│   │   │   └── index.js         # Entry point
│   │   ├── 📁 public/
│   │   ├── package.json         # NPM dependencies
│   │   └── Dockerfile          # Container definition
│   │
│   └── 📁 mobile/                # Android app (React Native)
│       ├── App.js                # Mobile app with BMO face
│       ├── ANDROID_BUILD.md      # APK build instructions
│       └── package.json          # NPM dependencies
│
└── 📁 docs/                       # Additional documentation
    ├── API.md                     # API reference (if needed)
    ├── ARCHITECTURE.md            # System architecture
    └── CONTRIBUTING.md            # Contribution guidelines
```

## 📦 Key Components

### Backend Services (Python/FastAPI)

1. **AI Service** (`services/ai-service/`)
   - Handles all LLM interactions
   - Uses Anthropic Claude Haiku for speed
   - Manages conversation history
   - Implements learning/correction
   - Stores user preferences in Redis

2. **Voice Service** (`services/voice-service/`)
   - Speech-to-text (Google Cloud)
   - Text-to-speech with childlike voice
   - Supports Tunisian Arabic
   - Handles audio streaming

3. **Task Service** (`services/task-service/`)
   - Opens applications (YouTube, etc.)
   - Performs web searches
   - Generates Android intents
   - System automation

4. **API Gateway** (`services/gateway/`)
   - Routes requests to services
   - Handles CORS
   - Health monitoring
   - Load balancing ready

### Frontend Applications

1. **Web Interface** (`frontend/web/`)
   - React-based SPA
   - BMO animated face
   - Voice chat interface
   - Popup window mode
   - RTL Arabic support

2. **Mobile App** (`frontend/mobile/`)
   - React Native for Android
   - Floating bubble widget
   - Background service
   - Native app launching
   - Push-to-talk voice

## 🔧 Configuration Files

### Docker & Deployment
- `docker-compose.yml` - Service orchestration
- `Dockerfile` (multiple) - Container definitions
- `start.sh` - Quick deployment script

### Environment
- `.env.example` - Template for API keys
- `.env` - Your actual configuration (not in git)
- `credentials.json` - Google Cloud credentials

### Dependencies
- `requirements.txt` (multiple) - Python packages
- `package.json` (multiple) - JavaScript packages

## 🗄️ Data Storage

### Redis (In-Memory)
- Conversation history
- User preferences
- Learning data
- Session management
- Auto-expiry (7 days)

### Local Storage (Web)
- Session persistence
- User name
- Recent messages
- Popup state

### Android Storage
- User profile
- Conversation cache
- App preferences

## 🌐 Network Architecture

```
Internet
    ↓
[API Gateway :8000]
    ↓
    ├──→ [AI Service :8001] ──→ Anthropic API
    ├──→ [Voice Service :8002] ──→ Google Cloud
    ├──→ [Task Service :8003] ──→ System
    └──→ [Redis :6379]
    ↑
[Web Frontend :3000]
[Mobile App]
```

## 📊 Data Flow

### Text Message Flow
1. User types message → Frontend
2. Frontend → API Gateway
3. Gateway → AI Service
4. AI Service → Anthropic Claude
5. Response → Redis (cache)
6. Response → Frontend
7. Frontend displays BMO's response

### Voice Message Flow
1. User speaks → Frontend captures audio
2. Audio → API Gateway → Voice Service
3. Voice Service → Google STT
4. Transcript → AI Service (same as text)
5. AI response → Voice Service → Google TTS
6. Audio → Frontend → Plays to user

### App Launch Flow
1. User requests app → Frontend
2. Request → API Gateway → Task Service
3. Task Service detects OS
4. Executes appropriate command/intent
5. App opens on user's device

## 🔐 Security Layers

1. **API Keys**: Stored in `.env`, never committed
2. **CORS**: Configured in all services
3. **Rate Limiting**: Can be added to gateway
4. **HTTPS**: Required for production
5. **Input Validation**: All services validate inputs

## 🚀 Deployment Paths

### Local Development
```
1. Edit .env
2. ./start.sh
3. Access http://localhost:3000
```

### Cloud Deployment
```
1. Push to VPS
2. Configure domain
3. Setup SSL (Let's Encrypt)
4. docker-compose up -d
```

### Mobile Distribution
```
1. cd frontend/mobile
2. Update API_BASE URL
3. ./gradlew assembleRelease
4. Distribute APK
```

## 📝 File Ownership & Git

### Included in Git
- All source code
- Documentation
- Dockerfiles
- docker-compose.yml
- .env.example
- start.sh

### Not in Git (.gitignore)
- .env (secrets)
- credentials.json (secrets)
- node_modules/
- __pycache__/
- *.pyc
- build/
- dist/

## 🔄 Update Process

### Code Updates
```bash
git pull
docker-compose down
docker-compose up -d --build
```

### Dependency Updates
```bash
# Python
pip install --upgrade -r requirements.txt

# JavaScript
npm update
```

## 📈 Scaling Considerations

### Horizontal Scaling
- Add multiple instances of each service
- Use load balancer
- Share Redis instance

### Vertical Scaling
- Increase container resources
- Optimize database queries
- Add caching layers

### Cost Optimization
- Use serverless (Cloud Run)
- Implement auto-scaling
- Monitor API usage

## 🎯 Development Workflow

1. **Local Testing**: Use docker-compose
2. **Code Changes**: Edit relevant service
3. **Rebuild**: `docker-compose up -d --build`
4. **Test**: Verify changes work
5. **Commit**: Push to repository
6. **Deploy**: Update production

## 📚 Additional Resources

- **Anthropic Docs**: https://docs.anthropic.com/
- **Google Cloud Speech**: https://cloud.google.com/speech-to-text
- **React Docs**: https://react.dev/
- **React Native**: https://reactnative.dev/
- **FastAPI**: https://fastapi.tiangolo.com/
- **Docker**: https://docs.docker.com/

---

This structure is designed for:
- ✅ Easy maintenance
- ✅ Clear separation of concerns
- ✅ Simple deployment
- ✅ Future scalability
- ✅ Team collaboration
