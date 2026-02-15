# Frontend Integration Guide - Enhanced BMO

## Overview

The frontend now integrates with an advanced backend that provides emotion detection, intent recognition, and emotion-aware speech synthesis.

---

## Key Integration Points

### 1. Enhanced Chat Response

**Old Implementation:**
```javascript
const response = await fetch(`${API_BASE}/ai/chat`, {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ message: text, session_id: sessionId })
});
const data = await response.json();
// response.response - text only
```

**New Implementation:**
```javascript
const response = await fetch(`${API_BASE}/ai/chat`, {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ 
    message: text, 
    session_id: sessionId,
    user_name: userName,
    language: 'ar'
  })
});
const data = await response.json();

// Now you get:
// - data.response (text)
// - data.detected_emotion (emotion from AI response)
// - data.confidence (0-1 confidence score)
// - data.timestamp (ISO timestamp)
```

### 2. Emotion-Based Character Animation

The frontend [App.js](frontend/web/src/App.js) now uses the `detected_emotion` field:

```javascript
// Get AI response
const aiMood = determineMood(data.response);
setBmoMood(aiMood);

// Even better - use the backend's detected emotion:
setBmoMood(data.detected_emotion);  // From backend
```

The backend detects emotions based on content analysis, not just keywords, making it more accurate.

### 3. User Profile Integration

Get comprehensive user information:

```javascript
// Fetch user profile
const response = await fetch(`${API_BASE}/user/${sessionId}`);
const profile = await response.json();

console.log(profile);
// {
//   "name": "أحمد",
//   "interaction_count": 15,
//   "emotion_history": [...],
//   "favorite_topics": ["transport"]
// }
```

### 4. Intent Recognition

Know what the user is trying to do:

```javascript
// Check user intent
const intentResponse = await fetch(
  `${API_BASE}/ai/intent-recognition?text=${encodeURIComponent(text)}`
);
const intentData = await intentResponse.json();

if (intentData.intent === 'transport') {
  // User is asking about transport - show relevant options
  showTransportOptions();
} else if (intentData.intent === 'booking') {
  // User wants to book - show booking interface
  showBookingInterface();
}
```

### 5. Complete Chat with Emotion-Aware Voice

Get both AI response AND emotion-aware audio:

```javascript
// If using complete chat endpoint
const response = await fetch(`${API_BASE}/chat-complete`, {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ 
    message: text,
    session_id: sessionId,
    language: 'ar-TN'
  })
});

const data = await response.json();
// {
//   "response_text": "...",
//   "detected_emotion": "happy",
//   "confidence": 0.92,
//   "audio_available": true
// }
```

---

## Updated App.js Features

### Emotion Keywords from Backend

The backend now recognizes **12 emotions**:

```javascript
// These are now detected by backend:
happy, sad, angry, surprised, confused, excited,
loving, tired, proud, nervous, interested, grateful
```

### Emotion Detection Logic

**Frontend (User's message):**
```javascript
const determineMood = (text) => {
  // Simple keyword matching for user's message
  const lower = text.toLowerCase();
  // Returns: happy, sad, angry, surprised, confused, etc.
};
```

**Backend (AI's response):**
Uses advanced pattern matching + keyword analysis to detect emotion from AI's generated response.

### Updated CSS Animations

The [App.css](frontend/web/src/App.css) includes emotion-specific transforms:

```css
/* For each emotion */
.character-face.happy { transform: scale(1) translateY(0); }
.character-face.excited { animation: bounce-excited 0.5s infinite; }
.character-face.sad { transform: scale(0.92) translateY(10px); }
.character-face.nervous { animation: shake 0.4s infinite; }
/* ... and 8 more */
```

---

## Emotion-Aware Speech

### Audio Parameters by Emotion

The backend adjusts voice parameters based on detected emotion:

```javascript
const EMOTION_VOICE_PARAMS = {
  happy: { pitch: 20, speaking_rate: 1.1 },      // Cheerful & upbeat
  sad: { pitch: -10, speaking_rate: 0.8 },       // Slow & melancholic
  angry: { pitch: 15, speaking_rate: 1.2 },      // Intense & fast
  surprised: { pitch: 25, speaking_rate: 1.3 },  // High-pitched & quick
  excited: { pitch: 30, speaking_rate: 1.3 },    // Very high & fast
  tired: { pitch: -15, speaking_rate: 0.7 },     // Slow & low
  // ... etc
};
```

When you call TTS, the emotion affects:
- **Pitch**: How high or low the voice is
- **Speaking Rate**: How fast or slow the speech is

### Example: Emotion-Aware TTS

```javascript
async function speakWithEmotion(text, emotion = 'neutral') {
  const response = await fetch(`${API_BASE}/voice/text-to-speech`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      text: text,
      emotion: emotion,        // Use detected emotion!
      language: 'ar-TN',
      gender: 'FEMALE'
    })
  });
  
  const audioBlob = await response.blob();
  const audio = new Audio(URL.createObjectURL(audioBlob));
  await audio.play();
}

// Usage with backend emotion detection:
speakWithEmotion(
  "تمام التمام!",
  data.detected_emotion  // "happy" from backend
);
```

---

## Updated App.js Example Code

Here's how to integrate the new features:

```javascript
// ==========================================
// Enhanced Chat with Backend Emotion
// ==========================================
const sendMessage = async (text) => {
  if (!text.trim()) return;
  
  const userMsg = { role: 'user', content: text };
  setMessages(prev => [...prev, userMsg]);
  setInputText('');
  setBmoMood('thinking');
  
  try {
    // Call enhanced AI chat
    const response = await fetch(`${API_BASE}/ai/chat`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        message: text,
        session_id: sessionId,
        user_name: userName,
        language: 'ar'
      })
    });
    
    if (!response.ok) throw new Error('AI Error');
    
    const data = await response.json();
    
    // Add to messages
    const assistantMsg = { role: 'assistant', content: data.response };
    setMessages(prev => [...prev, assistantMsg]);
    
    // Use backend-detected emotion (more accurate!)
    setBmoMood(data.detected_emotion);
    
    // Play audio with emotion-aware voice
    await speakTextWithEmotion(
      data.response,
      data.detected_emotion  // Emotion-aware TTS!
    );
    
  } catch (err) {
    console.error('Error:', err);
    setBmoMood('nervous');
  }
};

// ==========================================
// Emotion-Aware Speech Synthesis
// ==========================================
const speakTextWithEmotion = async (text, emotion = 'neutral') => {
  try {
    setIsSpeaking(true);
    
    const res = await fetch(`${API_BASE}/voice/text-to-speech`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        text: text,
        emotion: emotion,    // Use detected emotion!
        language: 'ar-TN',
        gender: 'FEMALE'
      })
    });
    
    const blob = await res.blob();
    const audioUrl = URL.createObjectURL(blob);
    const audio = new Audio(audioUrl);
    
    audio.onended = () => {
      setIsSpeaking(false);
      URL.revokeObjectURL(audioUrl);
    };
    
    await audio.play();
    
  } catch (err) {
    console.error('TTS Error:', err);
    setIsSpeaking(false);
  }
};

// ==========================================
// Get User Profile & Emotion History
// ==========================================
const loadUserProfile = async () => {
  try {
    const response = await fetch(`${API_BASE}/user/${sessionId}`);
    const profile = await response.json();
    
    console.log('User Profile:', profile);
    // {
    //   "name": "أحمد",
    //   "interaction_count": 15,
    //   "emotion_history": [
    //     { "emotion": "happy", "confidence": 0.92, ... },
    //     { "emotion": "interested", "confidence": 0.85, ... }
    //   ]
    // }
    
    // Show emotion trends
    showEmotionTrends(profile.emotion_history);
    
  } catch (err) {
    console.error('Profile Error:', err);
  }
};

// ==========================================
// Intent-Based UI Changes
// ==========================================
const handleUserMessage = async (text) => {
  // Detect what user is trying to do
  const intentResponse = await fetch(
    `${API_BASE}/ai/intent-recognition?text=${encodeURIComponent(text)}`
  );
  const intentData = await intentResponse.json();
  
  // React based on intent
  switch(intentData.intent) {
    case 'greeting':
      showGreetingAnimation();
      break;
    case 'help':
      showHelpPanel();
      break;
    case 'transport':
      showTransportOptions();
      break;
    case 'booking':
      showBookingInterface();
      break;
    case 'complaint':
      showSupportOptions();
      break;
    case 'gratitude':
      playSpecialAnimation();
      break;
    default:
      // General conversation
      break;
  }
  
  // Then process normally
  sendMessage(text);
};
```

---

## Visualization: Emotion Confidence

Show user how confident the emotion detection is:

```javascript
// In the UI, display confidence as a visual indicator
<div className="emotion-confidence">
  <span className="emotion">{data.detected_emotion}</span>
  <div className="confidence-bar">
    <div 
      className="confidence-fill" 
      style={{width: `${data.confidence * 100}%`}}
    />
  </div>
  <span className="percentage">{Math.round(data.confidence * 100)}%</span>
</div>
```

---

## API Response Structure

### Chat Endpoint

```json
{
  "response": "تمام برشا! أشنوة أخبارك؟",
  "detected_emotion": "happy",
  "confidence": 0.92,
  "timestamp": "2026-02-15T10:30:00.123456",
  "session_id": "session-12345",
  "learned_something": false
}
```

### User Profile Endpoint

```json
{
  "name": "أحمد",
  "language_preference": "ar",
  "interaction_count": 15,
  "favorite_topics": ["transport", "booking"],
  "emotion_history": [
    {
      "emotion": "happy",
      "confidence": 0.92,
      "timestamp": "2026-02-15T10:30:00"
    },
    {
      "emotion": "interested",
      "confidence": 0.85,
      "timestamp": "2026-02-15T10:20:00"
    }
  ]
}
```

### Intent Recognition

```json
{
  "intent": "transport",
  "confidence": 0.85,
  "timestamp": "2026-02-15T10:30:00"
}
```

---

## Best Practices

### 1. Always Use Backend Emotion

```javascript
// ❌ Don't use frontend emotion alone
const frontendMood = determineMood(aiResponse);
setBmoMood(frontendMood);

// ✅ Use backend's more accurate emotion
setBmoMood(data.detected_emotion);
```

### 2. Show Confidence Levels

```javascript
// ✅ Display confidence to user
if (data.confidence < 0.6) {
  console.warn('Low emotion confidence - may not be accurate');
}
```

### 3. Cache User Profiles

```javascript
// ✅ Load once and update on changes
const [userProfile, setUserProfile] = useState(null);

useEffect(() => {
  loadUserProfile();  // Once on mount
}, [sessionId]);

// Update on specific interactions
```

### 4. Handle Intent-Based Logic

```javascript
// ✅ Check intent and adapt UI
if (intent === 'booking') {
  showBookingFlow();
} else if (intent === 'help') {
  showFAQPanel();
}
```

### 5. Emotion-Aware Animations

```javascript
// ✅ Different animations per emotion
const getAnimationClass = (emotion) => {
  const animations = {
    happy: 'spin-happy',
    sad: 'droop-sad',
    excited: 'bounce-excited',
    nervous: 'shake',
    // ...
  };
  return animations[emotion] || 'default';
};
```

---

## Testing the Integration

### 1. Test Emotion Detection

```bash
# In browser console
fetch('http://localhost:8000/ai/emotion-analysis?text=برشا متحمس!').then(r => r.json()).then(console.log)
```

### 2. Test Intent Recognition

```bash
fetch('http://localhost:8000/ai/intent-recognition?text=نحتاج نروح الستاسيون').then(r => r.json()).then(console.log)
```

### 3. Test Full Chat

```bash
fetch('http://localhost:8000/ai/chat', {
  method: 'POST',
  headers: {'Content-Type': 'application/json'},
  body: JSON.stringify({message: 'أشنوة؟', session_id: 'test'})
}).then(r => r.json()).then(console.log)
```

---

## Summary of Changes

| Feature | Before | After |
|---------|--------|-------|
| Emotion Detection | 6 emotions (keywords) | 12 emotions (backend) |
| Confidence Score | Not available | 0-1 confidence included |
| Intent Recognition | Not available | 7 different intents |
| User Profiling | Basic | Comprehensive (emotions, history) |
| Voice Synthesis | Single voice | Emotion-adaptive voice |
| Dataset Learning | Not available | Tunisian Railway Dialogues |
| Response Context | No | Similar dialogue suggestions |

---

## Next Steps

1. Update [frontend/web/src/App.js](frontend/web/src/App.js) to use `data.detected_emotion` instead of calculating emotion locally
2. Add emotion confidence visualization
3. Implement intent-based UI logic
4. Display user emotion history/trends
5. Test with various Tunisian Arabic inputs
6. Optimize character animations per emotion

All new files are ready to deploy! The backend is now ready for the enhanced frontend integration.
