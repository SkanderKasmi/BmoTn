# 👀 BMO Eye Tracking Feature

BMO can now **follow you with his eyes**! This makes him feel alive and interactive.

## 🎯 Three Tracking Modes

### 1. 🖱️ Mouse Tracking (Default - Always On)
**Web Only**

BMO's eyes follow your mouse cursor around the screen!

- ✅ **No setup needed** - works immediately
- ✅ Smooth, natural eye movement
- ✅ Eyes return to center when idle
- ✅ Perfect for desktop use

**How it works:**
- Move your mouse around the screen
- BMO's pupils follow the cursor
- Maximum movement range: 8 pixels in each direction
- Smooth transition animations

### 2. 📱 Touch Tracking (Default - Always On)
**Mobile Only**

On Android, BMO follows your finger!

- ✅ **No setup needed** - works immediately
- ✅ Touch and drag to move eyes
- ✅ Eyes return to center when you lift finger
- ✅ Perfect for mobile interaction

**How it works:**
- Touch anywhere on screen
- Move your finger around
- BMO watches your finger
- Release to return eyes to center

### 3. 🎥 Camera Face Tracking (Optional)
**Web Only - Advanced Feature**

BMO can track your actual face using your webcam!

- ⚠️ Requires browser support
- ⚠️ Needs camera permission
- ✅ Most realistic interaction
- ✅ Follows you as you move

## 🚀 Quick Demo

### Test Mouse Tracking (Web)
1. Open http://localhost:3000
2. Move your mouse around the screen
3. Watch BMO's eyes follow you! 👀

### Test Touch Tracking (Mobile)
1. Open app on Android
2. Touch and drag anywhere
3. BMO watches your finger! 👀

## 🎥 Enable Camera Face Tracking

By default, camera tracking is **disabled** to avoid requesting camera permissions.

### To Enable:

**Edit:** `frontend/web/src/App.js`

**Find this line (~line 135):**
```javascript
// Uncomment to enable face tracking:
// startFaceDetection();
```

**Change to:**
```javascript
// Enable face tracking:
startFaceDetection();
```

**Save and rebuild:**
```bash
docker-compose restart web
```

### What Happens:
1. Browser asks for camera permission
2. BMO activates webcam (small light turns on)
3. Detects your face in real-time
4. Eyes follow you as you move!
5. Shows "👁️ Watching you!" indicator

### Requirements:
- Modern browser (Chrome, Edge, Firefox)
- Webcam/camera
- User permission granted
- Good lighting

### Browser Support:
| Browser | Support |
|---------|---------|
| Chrome 90+ | ✅ Full support |
| Edge 90+ | ✅ Full support |
| Firefox | ⚠️ Partial (needs flag) |
| Safari | ❌ Not supported |

## 🎨 How It Works

### Eye Movement Calculation

```javascript
// Get mouse/face position
const deltaX = targetX - faceCenterX;
const deltaY = targetY - faceCenterY;

// Limit range (8 pixels max)
const maxMove = 8;
const x = (deltaX / 200) * maxMove;
const y = (deltaY / 200) * maxMove;

// Smooth animation
transition: transform 0.2s ease-out
```

### Random Idle Movements

When BMO isn't actively tracking:
- Every 5 seconds: random small eye movement
- Duration: 500ms
- Returns to center
- Makes BMO feel "alive"

### Natural Blinking

- Blinks every ~3 seconds randomly
- 150ms blink duration
- Both eyes blink together
- Continues during tracking

## ⚙️ Customization

### Change Tracking Sensitivity

**Edit:** `frontend/web/src/App.js`

```javascript
// Find this line:
const maxMove = 8; // pixels

// Increase for more dramatic eyes:
const maxMove = 12; // more expressive

// Decrease for subtle eyes:
const maxMove = 5; // more reserved
```

### Change Tracking Speed

```javascript
// Find this style:
transition: 'transform 0.2s ease-out'

// Slower (more lazy):
transition: 'transform 0.5s ease-out'

// Faster (more alert):
transition: 'transform 0.1s ease-out'
```

### Change Idle Movement Frequency

```javascript
// Find this interval:
setInterval(() => { /* ... */ }, 5000); // 5 seconds

// More frequent:
setInterval(() => { /* ... */ }, 3000); // 3 seconds

// Less frequent:
setInterval(() => { /* ... */ }, 10000); // 10 seconds
```

## 📊 Performance

### Impact:
- **Mouse tracking**: Negligible (~0.1% CPU)
- **Touch tracking**: Negligible (~0.1% CPU)
- **Camera tracking**: Low (~2-5% CPU)

### Battery Impact:
- **Mouse/Touch**: None
- **Camera**: Moderate (webcam active)

## 🐛 Troubleshooting

### Eyes don't move
1. Check browser console for errors
2. Refresh the page
3. Make sure you're moving mouse over BMO
4. Try clicking on BMO first

### Camera not working
1. Check browser permissions
2. Allow camera access when prompted
3. Check if camera is being used by another app
4. Try Chrome/Edge instead of Firefox/Safari
5. Check webcam light is on

### Eyes move too much/little
- Adjust `maxMove` value (see Customization)
- Default: 8 pixels
- Range: 3-15 pixels recommended

### Camera face detection fails
- Ensure good lighting
- Face camera directly
- Not too close/far (30-100cm ideal)
- One person at a time
- Check Face Detection API support

## 🎭 Feature Combinations

### Watching + Speaking
When BMO speaks, eyes still track!
- Mouth animates (talking)
- Eyes continue following
- Very lifelike effect

### Watching + Voice Chat
Perfect combo for conversations!
- Parents speak to BMO
- BMO tracks their face
- Feels like real interaction

### Watching + Mood Changes
Eyes track in all moods:
- Happy: Wide eyes following
- Thinking: Focused tracking
- Talking: Animated while watching
- Excited: Energetic tracking

## 💡 Creative Uses

### 1. Attention Checker
See if parents are looking at screen:
- Eyes follow their face
- Good for tutorials
- Engagement indicator

### 2. Privacy Mode
Disable camera tracking:
- Comment out `startFaceDetection()`
- Only use mouse tracking
- No webcam activation

### 3. Presentation Mode
BMO watches audience:
- Enable camera tracking
- BMO "presents" content
- Follows speaker

### 4. Gaming
Interactive games:
- "Follow the eyes" game
- Eye movement challenges
- Engagement activities

## 🔐 Privacy Notes

### Camera Tracking:
- **Only runs if you enable it**
- **Browser asks permission first**
- **Video never saved or sent**
- **Processed locally in browser**
- **You control when it's active**

### Mouse/Touch Tracking:
- **No privacy concerns**
- **No data collected**
- **Purely visual effect**
- **Local only**

## 🎯 Best Practices

### For Web (Desktop):
1. Use **mouse tracking** (default)
2. Enable **camera tracking** for demos
3. Disable camera for daily use
4. Adjust sensitivity if needed

### For Mobile:
1. Use **touch tracking** (default)
2. Great for interactions
3. Show parents how to play

### For Both:
1. Keep lighting good
2. Don't cover camera
3. Position face/pointer naturally
4. Enjoy the interaction!

## 📱 Mobile-Specific Notes

### Android
- Touch tracking works perfectly
- Smooth animations
- No lag
- Great for parents

### iOS (if you build for it)
- Same touch tracking
- Identical behavior
- No special setup

## 🔄 Fallback Behavior

If tracking fails:
1. **Mouse/Touch unavailable**: Random idle movements
2. **Camera blocked**: Falls back to mouse tracking
3. **API not supported**: Uses mouse/touch only
4. **Performance issues**: Automatically disabled

## 🎨 Visual Feedback

### Currently Tracking:
- Eyes smoothly follow target
- Natural movement
- Smooth transitions

### Idle State:
- Small random movements
- Eyes mostly centered
- Occasional glances

### Camera Active:
- "👁️ Watching you!" indicator
- Webcam light on
- Real-time tracking

## ✨ Future Enhancements (Ideas)

- [ ] Multi-person tracking
- [ ] Gesture recognition
- [ ] Emotion detection
- [ ] Distance-based eye size
- [ ] Blink patterns based on mood
- [ ] Eye color customization
- [ ] Wink animations
- [ ] Sleep mode (eyes closed)

## 🎬 Demo Ideas

### Show Parents:
1. "Look, BMO watches you!"
2. Move around screen
3. Wave at camera
4. BMO follows you!

### Fun Activities:
- Play peek-a-boo
- "Where's mama/baba?"
- Follow the pointer game
- Eye contact exercises

## 📝 Summary

| Feature | Platform | Setup | Privacy |
|---------|----------|-------|---------|
| Mouse Tracking | Web | ✅ Auto | ✅ Safe |
| Touch Tracking | Mobile | ✅ Auto | ✅ Safe |
| Camera Tracking | Web | ⚙️ Manual | ⚠️ Permission |

**Default:** Mouse/Touch tracking (no setup, private, fun!)
**Optional:** Camera tracking (advanced, requires permission)

---

**Enjoy making BMO come alive! 👀🎮**
