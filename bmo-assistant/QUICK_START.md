# 🚀 BMO Assistant - Quick Reference

## 🎯 One-Command Setup

```bash
cd bmo-assistant
./start.sh
```

The script will:
1. Start all services
2. Let you choose an AI model
3. Download the model (1-3 min)
4. Open BMO at http://localhost:3000

**Total cost: $0.00** - Completely FREE with Ollama!

## 📋 What You Need

### Required
1. **Docker & Docker Compose** - That's it!
   - No API keys needed
   - No subscriptions
   - No credit card

### Optional
- **Google Cloud Credentials** - Only if you want voice features
  - Create project → Enable Speech APIs
  - Create service account → Download JSON
  - Save as `credentials.json`
  - BMO works fine without it!

## 🤖 Choose Your Model

The `./start.sh` script will ask you to choose:

1. **llama3.2:1b** - RECOMMENDED
   - Size: 1.3 GB
   - Speed: ⚡⚡⚡⚡ Very Fast
   - Quality: ⭐⭐⭐⭐ Good
   - Perfect for parents

2. **qwen2.5:0.5b** - Ultra Fast
   - Size: 400 MB  
   - Speed: ⚡⚡⚡⚡⚡ Fastest
   - Quality: ⭐⭐⭐ Decent
   - If you want instant responses

3. **phi3:mini** - Best Quality
   - Size: 2.3 GB
   - Speed: ⚡⚡⚡ Fast
   - Quality: ⭐⭐⭐⭐⭐ Excellent
   - If you have good hardware

Can switch models anytime - see OLLAMA_SETUP.md

## 🎮 Key Features

- ✅ **100% FREE** - No API costs, ever!
- ✅ Speaks Tunisian Arabic
- ✅ Voice chat (push to talk)
- ✅ Opens apps (YouTube, Facebook, etc.)
- ✅ BMO animated face
- ✅ Learns from mistakes
- ✅ Remembers conversations
- ✅ Fast responses (< 1 second)
- ✅ Works offline (after model download)
- ✅ Privacy-first (data stays local)

## 🔧 Common Commands

```bash
# Start services
docker-compose up -d

# Stop services
docker-compose down

# View logs
docker-compose logs -f

# Restart a service
docker-compose restart ai-service

# Check health
curl http://localhost:8000/health

# Rebuild after code changes
docker-compose up -d --build

# Ollama-specific commands
docker exec -it bmo-ollama ollama list                    # List models
docker exec -it bmo-ollama ollama pull llama3.2:3b        # Download new model  
docker exec -it bmo-ollama ollama rm old-model           # Remove model
```

## 📱 Build Android APK

```bash
cd frontend/mobile
npm install
cd android
./gradlew assembleDebug
```

APK location: `android/app/build/outputs/apk/debug/app-debug.apk`

Transfer to phone and install!

## 🌐 Access Points

- **Web**: http://localhost:3000
- **API**: http://localhost:8000
- **Health**: http://localhost:8000/health

## 📝 File Locations

```
bmo-assistant/
├── .env                  # Your API keys (create from .env.example)
├── credentials.json      # Google Cloud credentials
├── docker-compose.yml    # Service configuration
└── start.sh             # Quick start script
```

## 🎨 Customization

### Change BMO's Voice
Edit `services/voice-service/main.py`:
```python
audio_config = texttospeech.AudioConfig(
    speaking_rate=1.15,  # Speed (0.5-2.0)
    pitch=4.0           # Pitch (-20 to 20)
)
```

### Change AI Model
Edit `.env`:
```env
# Choose based on your needs:
OLLAMA_MODEL=llama3.2:1b    # Fastest (recommended)
OLLAMA_MODEL=phi3:mini      # Best quality
OLLAMA_MODEL=qwen2.5:0.5b   # Ultra fast
```

Then download model and restart:
```bash
docker exec -it bmo-ollama ollama pull phi3:mini
docker-compose restart ai-service
```

### Add New Apps
Edit `services/task-service/main.py`:
```python
APP_MAPPINGS = {
    "your_app": {
        "android": "intent://...",
        "windows": "start your_app"
    }
}
```

## 🐛 Troubleshooting

### Services won't start
```bash
docker-compose down
docker system prune
docker-compose up -d --build
```

### Ollama not responding
```bash
# Check Ollama is running
docker ps | grep ollama

# Restart Ollama
docker-compose restart ollama

# Check model is downloaded
docker exec -it bmo-ollama ollama list
```

### No model downloaded
```bash
# Download recommended model
docker exec -it bmo-ollama ollama pull llama3.2:1b

# Update .env
echo "OLLAMA_MODEL=llama3.2:1b" >> .env

# Restart AI service
docker-compose restart ai-service
```

### Slow responses
1. Use smaller model (llama3.2:1b or qwen2.5:0.5b)
2. Check CPU usage with `docker stats`
3. Enable GPU if you have NVIDIA card (see OLLAMA_SETUP.md)
4. Close other heavy applications

### Voice not working
1. Check `credentials.json` exists
2. Verify Google Cloud APIs are enabled
3. Check microphone permissions
4. Voice is optional - BMO works without it!

## 🔐 Security

### Production Checklist
- [ ] Use HTTPS (SSL certificate)
- [ ] Change default Redis password
- [ ] Enable rate limiting
- [ ] Setup firewall rules
- [ ] Use environment secrets management
- [ ] Regular backups

## 📚 Documentation

- `README.md` - Overview
- `SETUP_GUIDE.md` - Detailed setup
- `FEATURES.md` - Complete features
- `PROJECT_STRUCTURE.md` - Code organization
- `frontend/mobile/ANDROID_BUILD.md` - APK build

## 🎁 Pre-configured For

- **Users**: Parents who need tech help
- **Language**: Tunisian Arabic primary
- **Speed**: Fast responses (Haiku model)
- **Privacy**: Local-first, data expires
- **Deployment**: Docker-based, cloud-ready

## 💡 Tips

1. **Test locally first** before deploying
2. **Use popup mode** for always-available BMO
3. **Enable voice** for easier parent interaction
4. **Customize personality** in `ai-service/main.py`
5. **Add reminders** for medication, appointments

## 🆘 Get Help

- Check logs: `docker-compose logs -f`
- View health: http://localhost:8000/health
- Test services individually
- Read error messages carefully

## 🎉 Quick Test

```bash
# After starting services
curl -X POST http://localhost:8000/ai/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "مرحبا",
    "session_id": "test-123"
  }'
```

Should return: BMO's greeting in Tunisian Arabic

---

**Need more help?** Check the full `SETUP_GUIDE.md`
