# BMO Assistant - AI Companion for Parents

A BMO-inspired AI assistant designed to help your parents with technology, speak Tunisian Arabic, and provide companionship.

## Features

- 🎮 **BMO-like Personality**: Childlike, friendly, and helpful
- 🗣️ **Tunisian Arabic**: Native language support
- 👤 **Personal Recognition**: Recognizes your parents by name
- 🎤 **Voice Interaction**: Speech-to-text and text-to-speech
- 📸 **Image Recognition**: Can see and understand images
- ⚡ **Fast Responses**: Optimized for speed with Ollama (< 1 second)
- 🧠 **Self-Learning**: Corrects mistakes and improves over time
- 📱 **Cross-Platform**: Web + Android APK
- 🎭 **Simple Face Interface**: Animated BMO-like face
- 💰 **100% FREE**: No API costs - runs locally with Ollama
- 👀 **Eye Tracking**: Eyes follow your mouse/touch/face!

## Architecture

### Microservices Structure

```
bmo-assistant/
├── services/
│   ├── ai-service/          # LLM interactions (Ollama - Free!)
│   ├── voice-service/       # Speech recognition & synthesis
│   ├── task-service/        # App launching & automation
│   └── gateway/             # API Gateway
├── frontend/
│   ├── web/                 # React web interface
│   └── mobile/              # React Native for Android
└── docker-compose.yml       # Orchestration
```

## Quick Start

### Prerequisites
- Docker & Docker Compose
- ~~Node.js 18+~~ (handled by Docker)
- ~~Anthropic API key~~ **NOT NEEDED!** Using free Ollama
- Google Cloud account (optional - only for voice features)

### Setup

1. Clone and configure:
```bash
cd bmo-assistant
cp .env.example .env
# No API keys required! Ollama is free
```

2. Start services:
```bash
docker-compose up -d
```

3. Download AI model (choose one):
```bash
# Fastest (RECOMMENDED for parents)
docker exec -it bmo-ollama ollama pull llama3.2:1b

# OR better quality
docker exec -it bmo-ollama ollama pull phi3:mini
```

4. Access:
- Web: http://localhost:3000
- API Gateway: http://localhost:8000

**💰 Total cost: $0.00** - Completely free!

📖 See [OLLAMA_SETUP.md](OLLAMA_SETUP.md) for model recommendations and optimization.

## Technology Stack

- **AI**: Ollama (Llama 3.2, Phi-3, Gemma 2 - runs locally, 100% free)
- **Voice**: Google Speech-to-Text & TTS (optional)
- **Backend**: Python (FastAPI)
- **Frontend**: React, React Native
- **Database**: Redis (memory)
- **Containerization**: Docker
