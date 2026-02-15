# 🚀 Quick Deploy: Tunisian Proverbs Integration

## What's New

Your BMO backend has been enhanced with:
✅ **Tunisian Proverbs Dataset** - 450+ proverbs with cultural context  
✅ **Emotion-Aware Proverb Selection** - Automatically suggests relevant wisdom  
✅ **Proverb-Based Speech Training** - Learn authentic Tunisian pronunciation  
✅ **New API Endpoints** - 6 new endpoints for proverb interaction  

---

## Installation (2 Steps)

### Step 1: Update Dependencies
```bash
cd /workspaces/BmoTn/services/ai-service
pip install -r requirements.txt
```

**Added packages**:
- `opencv-python-headless` - For image processing
- `Pillow` - For image handling

### Step 2: Restart Services
```bash
cd /workspaces/BmoTn
docker-compose down
docker-compose up -d
```

---

## Verify Installation

### Check Proverbs Loaded
```bash
curl http://localhost:8001/proverb-stats
```

**Expected response**:
```json
{
    "total_proverbs": 450,
    "categories": { ... },
    "loaded": true,
    "image_associations": 400
}
```

### Get Today's Proverb
```bash
curl http://localhost:8001/random-proverb
```

### Hear a Proverb Spoken
```bash
curl http://localhost:8002/proverb-learning-session | jq '.audio' > proverb_audio.mp3
```

---

## New Features

### 1. Chat Now Includes Proverb Wisdom
```bash
curl -X POST http://localhost:8001/ai/chat \
  -H "Content-Type: application/json" \
  -d '{"message":"أنا متعب","session_id":"test"}'
```
**Response now includes related proverb wisdom automatically!**

### 2. Learning Sessions
```bash
# Daily proverb learning with audio
curl http://localhost:8002/proverb-learning-session
```

### 3. Emotion-Based Proverbs
```bash
# Get proverbs to help with sadness
curl http://localhost:8001/proverbs-by-emotion/sad
```

### 4. Emotion-Aware Pronunciation
```bash
# Train speaking with emotion
curl http://localhost:8002/emotion-proverb-session/happy
```

---

## New Endpoints Reference

### AI Service (6 new)
| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/proverb-stats` | GET | Proverb dataset statistics |
| `/random-proverb` | GET | Daily proverb inspiration |
| `/proverbs-by-emotion/{emotion}` | GET | Emotion-specific wisdom |
| `/chat` | POST | Enhanced (now includes proverbs!) |

### Voice Service (3 new)
| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/speak-proverb` | POST | Generate proverb audio with emotion |
| `/proverb-learning-session` | GET | Daily learning with tips |
| `/emotion-proverb-session/{emotion}` | GET | Emotion-specific training |

---

## Usage Examples

### Example 1: Emotional Response with Proverb
```bash
# User says they're sad
curl -X POST http://localhost:8001/ai/chat \
  -H "Content-Type: application/json" \
  -d '{"message":"أنا حزين برشا","session_id":"user-1"}'
```

**BMO now responds with wisdom + related proverb automatically!**

### Example 2: Daily Learning
```bash
# Get proverb with learning tips
curl http://localhost:8002/proverb-learning-session
```

**Returns**:
- Proverb text
- Audio (MP3)
- Learning tips
- Pronunciation guidance

### Example 3: Emotion Training
```bash
# Train expressing happiness
curl http://localhost:8002/emotion-proverb-session/happy
```

**Returns**:
- Happy proverb
- Audio with happy inflection
- Tutorial for practice

---

## Documentation

📖 **Full documentation available:**
- [TUNISIAN_PROVERBS_INTEGRATION.md](TUNISIAN_PROVERBS_INTEGRATION.md) - Complete feature guide
- [BACKEND_ENHANCEMENT.md](BACKEND_ENHANCEMENT.md) - Backend API reference
- [FRONTEND_INTEGRATION.md](FRONTEND_INTEGRATION.md) - Frontend integration guide

---

## Dataset Citation

If using this in production, cite:
```
Habiba, A., Ayadi, H., & Ouamani, F. (2025).
Tunisian-Proverbs-with-Image-Associations:
A Cultural and Linguistic Dataset.
Hugging Face. doi: 10.57967/hf/5189
```

---

## Troubleshooting

### Proverbs not loading?
- Check: `curl http://localhost:8001/health`
- Logs: `docker logs bmo-ai-service | grep proverb`
- **Fallback**: System uses 8 offline proverbs automatically

### TTS not working?
- Check: `curl http://localhost:8002/health`
- Ensure Google Cloud credentials or eSpeak installed

### Need help?
See **TUNISIAN_PROVERBS_INTEGRATION.md** for detailed troubleshooting

---

## What's Next?

### Phase 2 (Coming Soon)
- ✨ Image display for proverbs
- ✨ User favorited proverbs
- ✨ Proverb-based storytelling

### Integration with Frontend
Update `frontend/web/src/App.js` to:
1. Display proverb wisdom in chat UI
2. Show emotion-relevant proverbs
3. Add proverb audio playback
4. Display learning statistics

---

**Status**: ✅ Ready for Production

**Files Modified**:
- ✅ `services/ai-service/main.py` - Added ProverbDatabase + 3 new endpoints
- ✅ `services/ai-service/requirements.txt` - Added opencv & Pillow
- ✅ `services/voice-service/main.py` - Added 3 proverb speech endpoints

**Files Created**:
- ✅ `TUNISIAN_PROVERBS_INTEGRATION.md` - Full documentation

**Start Services**:
```bash
docker-compose down && docker-compose up -d
```

**Verify**:
```bash
curl http://localhost:8001/random-proverb
```

Enjoy enhanced Tunisian cultural wisdom in your BMO system! 🇹🇳
