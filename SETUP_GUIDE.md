# BMO Assistant - Complete Setup Guide

## 🚀 Quick Start (5 minutes)

### Prerequisites
- Docker & Docker Compose installed
- Anthropic API key ([Get one here](https://console.anthropic.com/))
- Google Cloud account ([Setup guide](https://cloud.google.com/speech-to-text))

### Step 1: Clone & Configure

```bash
cd bmo-assistant
cp .env.example .env
```

Edit `.env` and add your keys:
```env
ANTHROPIC_API_KEY=sk-ant-your-key-here
```

### Step 2: Google Cloud Setup

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing
3. Enable APIs:
   - Cloud Speech-to-Text API
   - Cloud Text-to-Speech API
4. Create service account:
   - IAM & Admin → Service Accounts → Create
   - Grant roles: "Cloud Speech Client" and "Cloud Text-to-Speech Client"
5. Create key (JSON) and save as `credentials.json` in project root

### Step 3: Launch

```bash
docker-compose up -d
```

### Step 4: Access

- **Web Interface**: http://localhost:3000
- **API Gateway**: http://localhost:8000
- **Health Check**: http://localhost:8000/health

## 📱 Android APK Build

### Prerequisites
- Node.js 18+
- Android Studio
- JDK 11+

### Setup

1. **Install dependencies**:
```bash
cd frontend/mobile
npm install
```

2. **Install required packages**:
```bash
npm install @react-native-voice/voice react-native-fs
```

3. **Link native modules**:
```bash
npx react-native link @react-native-voice/voice
npx react-native link react-native-fs
```

4. **Update server IP in App.js**:
```javascript
const API_BASE = 'http://YOUR_SERVER_IP:8000'; // Replace with your actual IP
```

### Build Debug APK

```bash
cd android
./gradlew assembleDebug
```

Output: `android/app/build/outputs/apk/debug/app-debug.apk`

### Build Release APK

1. **Generate keystore**:
```bash
keytool -genkeypair -v -storetype PKCS12 -keystore bmo-release-key.keystore -alias bmo-key-alias -keyalg RSA -keysize 2048 -validity 10000
```

2. **Create `android/gradle.properties`**:
```properties
MYAPP_RELEASE_STORE_FILE=bmo-release-key.keystore
MYAPP_RELEASE_KEY_ALIAS=bmo-key-alias
MYAPP_RELEASE_STORE_PASSWORD=your_password
MYAPP_RELEASE_KEY_PASSWORD=your_password
```

3. **Build**:
```bash
cd android
./gradlew assembleRelease
```

Output: `android/app/build/outputs/apk/release/app-release.apk`

### Install on Device

```bash
adb install android/app/build/outputs/apk/debug/app-debug.apk
```

Or transfer APK to device and install manually.

## 🌐 Web Popup Feature (YouTube-like)

The web interface includes a floating popup that stays with you across tabs.

### Enable Popup Mode

Add to `frontend/web/src/App.js`:

```javascript
// Add this after imports
const openAsPopup = () => {
  window.open(
    window.location.href,
    'BMO Assistant',
    'width=400,height=600,popup=1,left=100,top=100'
  );
};

// Add button in UI
<button onClick={openAsPopup}>
  Open as Popup 🪟
</button>
```

The popup will:
- Float above all other windows
- Stay visible when switching tabs
- Maintain its position
- Remember conversation context

## 🧠 Continuous Learning

BMO learns from interactions and can improve over time.

### Manual Correction

When BMO makes a mistake, correct it:

```javascript
fetch(`${API_BASE}/ai/learn`, {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    session_id: sessionId,
    correction: "The correct information is...",
    context: "When I asked about..."
  })
});
```

### Background Learning (Optional)

Enable internet learning when idle:

1. Add to `ai-service/main.py`:

```python
import asyncio
from datetime import datetime, timedelta

last_interaction = {}

async def background_learning_task():
    while True:
        await asyncio.sleep(3600)  # Every hour
        
        # Check for idle sessions
        for session_id in last_interaction:
            if datetime.now() - last_interaction[session_id] > timedelta(hours=1):
                # Learn new jokes, facts, etc.
                await learn_from_web(session_id)

async def learn_from_web(session_id):
    # Fetch latest news, jokes, facts
    # Store in Redis for that session
    pass
```

2. Start background task in startup event.

## 🎮 Advanced Features

### 1. Multi-User Support

Each family member gets their own profile:

```javascript
// In App.js
const [profiles] = useState([
  { name: 'Mama', sessionId: 'session-mama' },
  { name: 'Baba', sessionId: 'session-baba' }
]);

// Switch profiles
const switchProfile = (profile) => {
  setSessionId(profile.sessionId);
  setUserName(profile.name);
};
```

### 2. Voice Wake Word

Add "Hey BMO" wake word detection:

```bash
npm install react-native-voice-wake-word
```

### 3. Scheduled Reminders

```python
# In ai-service/main.py
from apscheduler.schedulers.asyncio import AsyncIOScheduler

scheduler = AsyncIOScheduler()

@app.on_event("startup")
async def start_scheduler():
    scheduler.add_job(
        send_reminder,
        'cron',
        hour=9,  # 9 AM daily
        args=[session_id, "صباح الخير! تحب نساعدك في شيء؟"]
    )
    scheduler.start()
```

### 4. Image Recognition

Add camera support:

```javascript
import { launchCamera } from 'react-native-image-picker';

const takePhoto = async () => {
  const result = await launchCamera({ 
    mediaType: 'photo',
    includeBase64: true 
  });
  
  if (result.assets) {
    sendMessage("شوف هذي الصورة", result.assets[0].base64);
  }
};
```

## 🔧 Troubleshooting

### Docker Issues

**Services won't start**:
```bash
docker-compose down
docker-compose up --build
```

**Can't connect to services**:
```bash
docker network ls
docker network inspect bmo-network
```

### Android Build Issues

**Build fails**:
```bash
cd android
./gradlew clean
cd ..
npx react-native start --reset-cache
```

**Permission issues**:
```bash
chmod +x android/gradlew
```

### API Errors

**Anthropic API timeout**:
- Check API key is correct
- Verify network connection
- Increase timeout in `.env`

**Voice recognition not working**:
- Check microphone permissions
- Verify Google Cloud credentials
- Test with `curl` to voice service

### Web Interface Issues

**Blank screen**:
```bash
cd frontend/web
npm install
npm start
```

**CORS errors**:
- Check API_BASE URL is correct
- Verify gateway CORS settings

## 📊 Monitoring

### Check Service Health

```bash
curl http://localhost:8000/health
```

Expected response:
```json
{
  "gateway": "healthy",
  "services": {
    "ai": { "status": "healthy" },
    "voice": { "status": "healthy" },
    "task": { "status": "healthy" }
  }
}
```

### View Logs

```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f ai-service

# Last 100 lines
docker-compose logs --tail=100 ai-service
```

### Monitor Redis

```bash
docker exec -it bmo-redis redis-cli
> KEYS *
> GET conversation:session-123
```

## 🚀 Production Deployment

### Option 1: Cloud VPS (DigitalOcean, Linode, etc.)

1. **Setup server** (Ubuntu 22.04 recommended)
2. **Install Docker**:
```bash
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh
```

3. **Clone project**:
```bash
git clone your-repo
cd bmo-assistant
```

4. **Configure**:
```bash
cp .env.example .env
nano .env  # Add your keys
```

5. **Deploy**:
```bash
docker-compose up -d
```

6. **Setup domain** (optional):
- Point domain to server IP
- Install Nginx
- Setup SSL with Let's Encrypt

### Option 2: Cloud Run (Google Cloud)

Each service can be deployed individually to Cloud Run.

### Option 3: AWS ECS

Use the provided Docker containers with ECS.

## 💡 Tips & Best Practices

1. **API Keys**: Never commit `.env` or `credentials.json`
2. **Backups**: Regularly backup Redis data
3. **Updates**: Keep dependencies updated
4. **Security**: Use HTTPS in production
5. **Monitoring**: Setup uptime monitoring
6. **Scaling**: Add load balancer for multiple instances

## 📞 Support

- GitHub Issues: [your-repo]/issues
- Email: your-email@example.com

## 🎉 You're Ready!

BMO is now ready to help your parents with:
- Opening YouTube, Facebook, WhatsApp
- Answering questions in Tunisian Arabic
- Voice conversations
- Learning from interactions
- Being a friendly companion

Enjoy! 🎮
