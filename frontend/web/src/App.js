import React, { useState, useEffect, useRef } from 'react';
import './App.css';

const API_BASE = process.env.REACT_APP_API_URL || 'http://localhost:8000';

function App() {
  const [messages, setMessages] = useState([]);
  const [inputText, setInputText] = useState('');
  const [isListening, setIsListening] = useState(false);
  const [isSpeaking, setIsSpeaking] = useState(false);
  const [sessionId] = useState(() => `session-${Date.now()}`);
  const [userName, setUserName] = useState('');
  const [showNamePrompt, setShowNamePrompt] = useState(true);
  const [bmoMood, setBmoMood] = useState('happy'); // happy, talking, thinking, excited
  
  const messagesEndRef = useRef(null);
  const mediaRecorderRef = useRef(null);
  const audioChunksRef = useRef([]);

  // Auto-scroll to bottom
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(scrollToBottom, [messages]);

  // Set user name
  const handleSetName = async () => {
    if (userName.trim()) {
      try {
        await fetch(`${API_BASE}/ai/set-user?session_id=${sessionId}&name=${userName}`, {
          method: 'POST'
        });
        setShowNamePrompt(false);
        
        // Welcome message
        const welcomeMsg = {
          role: 'assistant',
          content: `مرحبا ${userName}! 🎮 أنا BMO، صاحبك الجديد! آش نحب نعاونك فيه اليوم؟`
        };
        setMessages([welcomeMsg]);
      } catch (error) {
        console.error('Failed to set name:', error);
      }
    }
  };

  // Send message to AI
  const sendMessage = async (text, imageData = null) => {
    if (!text.trim() && !imageData) return;

    // Add user message
    const userMsg = { role: 'user', content: text };
    setMessages(prev => [...prev, userMsg]);
    setInputText('');
    setBmoMood('thinking');

    try {
      const response = await fetch(`${API_BASE}/ai/chat`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          message: text,
          session_id: sessionId,
          user_name: userName,
          image_data: imageData
        })
      });

      const data = await response.json();
      
      // Add assistant message
      const assistantMsg = { role: 'assistant', content: data.response };
      setMessages(prev => [...prev, assistantMsg]);
      
      setBmoMood('talking');
      
      // Speak the response
      await speakText(data.response);
      
      setBmoMood('happy');

      // Check if message contains app opening intent
      if (text.includes('افتح') || text.includes('حل') || text.includes('open')) {
        handleAppIntent(text);
      }
      
    } catch (error) {
      console.error('Chat error:', error);
      setBmoMood('happy');
    }
  };

  // Handle app opening intents
  const handleAppIntent = async (text) => {
    const apps = ['youtube', 'facebook', 'whatsapp', 'gmail', 'maps'];
    const foundApp = apps.find(app => 
      text.toLowerCase().includes(app) || 
      text.includes(app)
    );

    if (foundApp) {
      try {
        await fetch(`${API_BASE}/task/execute`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            action: 'open_app',
            target: foundApp
          })
        });
      } catch (error) {
        console.error('Failed to open app:', error);
      }
    }
  };

  // Voice recording
  const startListening = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      const mediaRecorder = new MediaRecorder(stream);
      mediaRecorderRef.current = mediaRecorder;
      audioChunksRef.current = [];

      mediaRecorder.ondataavailable = (event) => {
        audioChunksRef.current.push(event.data);
      };

      mediaRecorder.onstop = async () => {
        const audioBlob = new Blob(audioChunksRef.current, { type: 'audio/webm' });
        await sendAudioToServer(audioBlob);
        stream.getTracks().forEach(track => track.stop());
      };

      mediaRecorder.start();
      setIsListening(true);
      setBmoMood('excited');
    } catch (error) {
      console.error('Microphone access denied:', error);
      alert('أعطيني permission للمايكروفون باش نسمعك! 🎤');
    }
  };

  const stopListening = () => {
    if (mediaRecorderRef.current && isListening) {
      mediaRecorderRef.current.stop();
      setIsListening(false);
      setBmoMood('thinking');
    }
  };

  // Send audio to speech-to-text service
  const sendAudioToServer = async (audioBlob) => {
    const formData = new FormData();
    formData.append('audio', audioBlob, 'recording.webm');

    try {
      const response = await fetch(`${API_BASE}/voice/speech-to-text`, {
        method: 'POST',
        body: formData
      });

      const data = await response.json();
      if (data.transcript) {
        sendMessage(data.transcript);
      }
    } catch (error) {
      console.error('Speech-to-text error:', error);
      setBmoMood('happy');
    }
  };

  // Text-to-speech
  const speakText = async (text) => {
    try {
      setIsSpeaking(true);
      
      const response = await fetch(`${API_BASE}/voice/text-to-speech`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ text, language: 'ar-TN' })
      });

      const audioBlob = await response.blob();
      const audioUrl = URL.createObjectURL(audioBlob);
      const audio = new Audio(audioUrl);
      
      audio.onended = () => {
        setIsSpeaking(false);
        URL.revokeObjectURL(audioUrl);
      };
      
      await audio.play();
    } catch (error) {
      console.error('Text-to-speech error:', error);
      setIsSpeaking(false);
    }
  };

  // Name prompt dialog
  if (showNamePrompt) {
    return (
      <div className="name-prompt">
        <BMOFace mood="happy" />
        <h2>مرحبا! 🎮</h2>
        <p>شنوّا اسمك؟</p>
        <input
          type="text"
          value={userName}
          onChange={(e) => setUserName(e.target.value)}
          onKeyPress={(e) => e.key === 'Enter' && handleSetName()}
          placeholder="اكتب اسمك هوني..."
          autoFocus
        />
        <button onClick={handleSetName}>ياسر! دخّل</button>
      </div>
    );
  }

  return (
    <div className="App">
      <div className="bmo-container">
        <BMOFace mood={bmoMood} isSpeaking={isSpeaking} />
        
        <div className="chat-container">
          <div className="messages">
            {messages.map((msg, idx) => (
              <div key={idx} className={`message ${msg.role}`}>
                <div className="message-bubble">
                  {msg.content}
                </div>
              </div>
            ))}
            <div ref={messagesEndRef} />
          </div>

          <div className="input-container">
            <input
              type="text"
              value={inputText}
              onChange={(e) => setInputText(e.target.value)}
              onKeyPress={(e) => e.key === 'Enter' && sendMessage(inputText)}
              placeholder="اكتب رسالتك..."
              disabled={isListening}
            />
            
            <button 
              className={`voice-btn ${isListening ? 'listening' : ''}`}
              onMouseDown={startListening}
              onMouseUp={stopListening}
              onTouchStart={startListening}
              onTouchEnd={stopListening}
            >
              {isListening ? '🎤 يسمع...' : '🎤'}
            </button>
            
            <button onClick={() => sendMessage(inputText)}>
              إبعث 📤
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}

// BMO Face Component with Eye Tracking
function BMOFace({ mood, isSpeaking }) {
  const [blinkLeft, setBlinkLeft] = useState(false);
  const [blinkRight, setBlinkRight] = useState(false);
  const [eyePosition, setEyePosition] = useState({ x: 0, y: 0 });
  const [faceDetected, setFaceDetected] = useState(null);
  const faceRef = useRef(null);
  const videoRef = useRef(null);
  const canvasRef = useRef(null);

  // Random blinking
  useEffect(() => {
    const blinkInterval = setInterval(() => {
      if (Math.random() > 0.7) {
        setBlinkLeft(true);
        setBlinkRight(true);
        setTimeout(() => {
          setBlinkLeft(false);
          setBlinkRight(false);
        }, 150);
      }
    }, 3000);

    return () => clearInterval(blinkInterval);
  }, []);

  // Mouse tracking - eyes follow cursor
  useEffect(() => {
    const handleMouseMove = (e) => {
      if (!faceRef.current) return;
      
      const rect = faceRef.current.getBoundingClientRect();
      const faceCenterX = rect.left + rect.width / 2;
      const faceCenterY = rect.top + rect.height / 2;
      
      // Calculate angle and distance
      const deltaX = e.clientX - faceCenterX;
      const deltaY = e.clientY - faceCenterY;
      
      // Limit eye movement range
      const maxMove = 8; // pixels
      const distance = Math.sqrt(deltaX * deltaX + deltaY * deltaY);
      const limitedDistance = Math.min(distance, 200);
      
      const x = (deltaX / 200) * maxMove;
      const y = (deltaY / 200) * maxMove;
      
      setEyePosition({ x: Math.max(-maxMove, Math.min(maxMove, x)), 
                       y: Math.max(-maxMove, Math.min(maxMove, y)) });
    };

    window.addEventListener('mousemove', handleMouseMove);
    return () => window.removeEventListener('mousemove', handleMouseMove);
  }, []);

  // Camera face detection (optional)
  useEffect(() => {
    let animationFrame;
    let faceDetector;

    const startFaceDetection = async () => {
      try {
        // Check if Face Detection API is available
        if (!('FaceDetector' in window)) {
          console.log('Face Detection API not available - using mouse tracking only');
          return;
        }

        // Request camera access
        const stream = await navigator.mediaDevices.getUserMedia({ 
          video: { facingMode: 'user', width: 320, height: 240 } 
        });
        
        if (videoRef.current) {
          videoRef.current.srcObject = stream;
          videoRef.current.play();
        }

        // Initialize face detector
        faceDetector = new window.FaceDetector({ 
          maxDetectedFaces: 1,
          fastMode: true 
        });

        const detectFaces = async () => {
          if (videoRef.current && videoRef.current.readyState === 4) {
            try {
              const faces = await faceDetector.detect(videoRef.current);
              
              if (faces.length > 0) {
                const face = faces[0];
                const boundingBox = face.boundingBox;
                
                // Calculate face center relative to video
                const faceCenterX = boundingBox.x + boundingBox.width / 2;
                const faceCenterY = boundingBox.y + boundingBox.height / 2;
                
                // Video center
                const videoCenterX = videoRef.current.videoWidth / 2;
                const videoCenterY = videoRef.current.videoHeight / 2;
                
                // Calculate eye movement
                const deltaX = (faceCenterX - videoCenterX) / videoCenterX;
                const deltaY = (faceCenterY - videoCenterY) / videoCenterY;
                
                const maxMove = 8;
                setEyePosition({
                  x: -deltaX * maxMove, // Negative for correct direction
                  y: deltaY * maxMove
                });
                
                setFaceDetected(true);
              } else {
                setFaceDetected(false);
              }
            } catch (err) {
              console.error('Face detection error:', err);
            }
          }
          
          animationFrame = requestAnimationFrame(detectFaces);
        };

        detectFaces();
      } catch (err) {
        console.log('Camera not available - using mouse tracking only');
      }
    };

    // Uncomment to enable face tracking:
    // startFaceDetection();

    return () => {
      if (animationFrame) {
        cancelAnimationFrame(animationFrame);
      }
      if (videoRef.current && videoRef.current.srcObject) {
        videoRef.current.srcObject.getTracks().forEach(track => track.stop());
      }
    };
  }, []);

  // Random idle eye movements
  useEffect(() => {
    const idleMovement = setInterval(() => {
      // Only do idle movements if not following mouse actively
      if (Math.abs(eyePosition.x) < 1 && Math.abs(eyePosition.y) < 1) {
        const randomX = (Math.random() - 0.5) * 6;
        const randomY = (Math.random() - 0.5) * 6;
        setEyePosition({ x: randomX, y: randomY });
        
        // Return to center after a moment
        setTimeout(() => {
          setEyePosition({ x: 0, y: 0 });
        }, 500);
      }
    }, 5000); // Every 5 seconds

    return () => clearInterval(idleMovement);
  }, [eyePosition]);

  return (
    <div className={`bmo-face ${mood}`} ref={faceRef}>
      {/* Hidden video for face detection */}
      <video 
        ref={videoRef} 
        style={{ display: 'none' }} 
        width="320" 
        height="240"
      />
      <canvas 
        ref={canvasRef} 
        style={{ display: 'none' }} 
        width="320" 
        height="240"
      />
      
      {/* Face detection indicator */}
      {faceDetected && (
        <div className="face-detected-indicator">
          👁️ Watching you!
        </div>
      )}
      
      <div className="screen">
        <div className={`eyes ${isSpeaking ? 'talking' : ''}`}>
          <div className={`eye left ${blinkLeft ? 'blink' : ''}`}>
            <div 
              className="pupil" 
              style={{
                transform: `translate(${eyePosition.x}px, ${eyePosition.y}px)`,
                transition: 'transform 0.2s ease-out'
              }}
            ></div>
          </div>
          <div className={`eye right ${blinkRight ? 'blink' : ''}`}>
            <div 
              className="pupil"
              style={{
                transform: `translate(${eyePosition.x}px, ${eyePosition.y}px)`,
                transition: 'transform 0.2s ease-out'
              }}
            ></div>
          </div>
        </div>
        
        <div className={`mouth ${mood}`}>
          {mood === 'happy' && <div className="smile"></div>}
          {mood === 'talking' && <div className="talk-mouth"></div>}
          {mood === 'thinking' && <div className="think-mouth"></div>}
          {mood === 'excited' && <div className="excited-mouth"></div>}
        </div>
      </div>
      
      <div className="bmo-body">
        <div className="buttons">
          <div className="btn red"></div>
          <div className="btn yellow"></div>
          <div className="btn green"></div>
          <div className="btn blue"></div>
        </div>
      </div>
    </div>
  );
}

export default App;
