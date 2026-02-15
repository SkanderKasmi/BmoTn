import React, { useState, useEffect, useRef } from 'react';
import './App.css';

const API_BASE = process.env.REACT_APP_API_URL || 'http://localhost:8000';
const IS_POPUP = window.opener !== null;

function App() {
  const [messages, setMessages] = useState([]);
  const [inputText, setInputText] = useState('');
  const [isListening, setIsListening] = useState(false);
  const [isSpeaking, setIsSpeaking] = useState(false);
  const [sessionId] = useState(() => {
    // Persist session across popup and main window
    const stored = localStorage.getItem('bmo-session-id');
    if (stored) return stored;
    const newId = `session-${Date.now()}`;
    localStorage.setItem('bmo-session-id', newId);
    return newId;
  });
  const [userName, setUserName] = useState('');
  const [showNamePrompt, setShowNamePrompt] = useState(true);
  const [bmoMood, setBmoMood] = useState('happy');
  const [isMinimized, setIsMinimized] = useState(false);
  
  const messagesEndRef = useRef(null);
  const mediaRecorderRef = useRef(null);
  const audioChunksRef = useRef([]);

  // Auto-scroll to bottom
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(scrollToBottom, [messages]);

  // Load saved session
  useEffect(() => {
    const savedName = localStorage.getItem('bmo-user-name');
    if (savedName) {
      setUserName(savedName);
      setShowNamePrompt(false);
      loadConversationHistory();
    }
  }, []);

  // Load conversation history
  const loadConversationHistory = async () => {
    // In production, fetch from server
    const stored = localStorage.getItem('bmo-messages');
    if (stored) {
      setMessages(JSON.parse(stored));
    }
  };

  // Save messages to localStorage
  useEffect(() => {
    if (messages.length > 0) {
      localStorage.setItem('bmo-messages', JSON.stringify(messages));
    }
  }, [messages]);

  // Open as popup window
  const openAsPopup = () => {
    const width = 400;
    const height = 600;
    const left = window.screen.width - width - 50;
    const top = 50;
    
    window.open(
      window.location.href + '?popup=true',
      'BMO Assistant',
      `width=${width},height=${height},left=${left},top=${top},resizable=yes,scrollbars=yes`
    );
  };

  // Set user name
  const handleSetName = async () => {
    if (userName.trim()) {
      localStorage.setItem('bmo-user-name', userName);
      
      try {
        await fetch(`${API_BASE}/ai/set-user?session_id=${sessionId}&name=${userName}`, {
          method: 'POST'
        });
        setShowNamePrompt(false);
        
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
      const errorMsg = {
        role: 'assistant',
        content: 'عندي مشكلة توا... ممكن تعاود السؤال؟ 😅'
      };
      setMessages(prev => [...prev, errorMsg]);
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

  // Clear conversation
  const clearConversation = () => {
    if (window.confirm('تحب تمسح المحادثة الكل؟')) {
      setMessages([]);
      localStorage.removeItem('bmo-messages');
    }
  };

  // Logout
  const logout = () => {
    if (window.confirm('تحب تخرج؟')) {
      localStorage.removeItem('bmo-user-name');
      localStorage.removeItem('bmo-messages');
      setUserName('');
      setMessages([]);
      setShowNamePrompt(true);
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
    <div className={`App ${IS_POPUP ? 'popup-mode' : ''} ${isMinimized ? 'minimized' : ''}`}>
      {/* Popup controls */}
      {IS_POPUP && (
        <div className="popup-controls">
          <button onClick={() => setIsMinimized(!isMinimized)} className="minimize-btn">
            {isMinimized ? '▲' : '▼'}
          </button>
          <button onClick={() => window.close()} className="close-btn">
            ✕
          </button>
        </div>
      )}

      <div className="bmo-container">
        {!isMinimized && (
          <>
            <div className="bmo-sidebar">
              <BMOFace mood={bmoMood} isSpeaking={isSpeaking} />
              
              <div className="user-info">
                <p className="welcome-text">مرحبا {userName}! 👋</p>
              </div>

              {!IS_POPUP && (
                <button onClick={openAsPopup} className="popup-button">
                  فتح في نافذة طافية 🪟
                </button>
              )}

              <div className="action-buttons">
                <button onClick={clearConversation} className="action-btn">
                  مسح المحادثة 🗑️
                </button>
                <button onClick={logout} className="action-btn">
                  خروج 🚪
                </button>
              </div>
            </div>
            
            <div className="chat-container">
              <div className="messages">
                {messages.map((msg, idx) => (
                  <div key={idx} className={`message ${msg.role}`}>
                    <div className="message-bubble">
                      {msg.content}
                    </div>
                  </div>
                ))}
                {isListening && (
                  <div className="message assistant">
                    <div className="message-bubble listening-indicator">
                      🎤 يسمع...
                    </div>
                  </div>
                )}
                <div ref={messagesEndRef} />
              </div>

              <div className="input-container">
                <input
                  type="text"
                  value={inputText}
                  onChange={(e) => setInputText(e.target.value)}
                  onKeyPress={(e) => e.key === 'Enter' && !e.shiftKey && sendMessage(inputText)}
                  placeholder="اكتب رسالتك..."
                  disabled={isListening}
                />
                
                <button 
                  className={`voice-btn ${isListening ? 'listening' : ''}`}
                  onMouseDown={startListening}
                  onMouseUp={stopListening}
                  onTouchStart={startListening}
                  onTouchEnd={stopListening}
                  title="اضغط وحكي"
                >
                  {isListening ? '🔴' : '🎤'}
                </button>
                
                <button onClick={() => sendMessage(inputText)} disabled={!inputText.trim()}>
                  إبعث 📤
                </button>
              </div>
            </div>
          </>
        )}

        {isMinimized && (
          <div className="minimized-view" onClick={() => setIsMinimized(false)}>
            <BMOFace mood="happy" isSpeaking={false} />
            <p>اضغط لفتح BMO</p>
          </div>
        )}
      </div>
    </div>
  );
}

// BMO Face Component with Eye Tracking
function BMOFace({ mood, isSpeaking }) {
  const [blinkLeft, setBlinkLeft] = useState(false);
  const [blinkRight, setBlinkRight] = useState(false);
  const [eyePosition, setEyePosition] = useState({ x: 0, y: 0 });
  const faceRef = useRef(null);

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

  // Mouse tracking
  useEffect(() => {
    const handleMouseMove = (e) => {
      if (!faceRef.current) return;
      
      const rect = faceRef.current.getBoundingClientRect();
      const faceCenterX = rect.left + rect.width / 2;
      const faceCenterY = rect.top + rect.height / 2;
      
      const deltaX = e.clientX - faceCenterX;
      const deltaY = e.clientY - faceCenterY;
      
      const maxMove = 8;
      const x = (deltaX / 200) * maxMove;
      const y = (deltaY / 200) * maxMove;
      
      setEyePosition({ x: Math.max(-maxMove, Math.min(maxMove, x)), 
                       y: Math.max(-maxMove, Math.min(maxMove, y)) });
    };

    window.addEventListener('mousemove', handleMouseMove);
    return () => window.removeEventListener('mousemove', handleMouseMove);
  }, []);

  // Random idle movements
  useEffect(() => {
    const idleMovement = setInterval(() => {
      if (Math.abs(eyePosition.x) < 1 && Math.abs(eyePosition.y) < 1) {
        const randomX = (Math.random() - 0.5) * 6;
        const randomY = (Math.random() - 0.5) * 6;
        setEyePosition({ x: randomX, y: randomY });
        
        setTimeout(() => {
          setEyePosition({ x: 0, y: 0 });
        }, 500);
      }
    }, 5000);

    return () => clearInterval(idleMovement);
  }, [eyePosition]);

  return (
    <div className={`bmo-face ${mood}`} ref={faceRef}>
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
