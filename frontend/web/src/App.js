import React, { useState, useEffect, useRef } from 'react';
import './App.css';

const API_BASE = process.env.REACT_APP_API_URL || 'http://localhost:8000';

function App() {
  const [messages, setMessages] = useState([]);
  const [inputText, setInputText] = useState('');
  const [isSpeaking, setIsSpeaking] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [sessionId] = useState(() => {
    const stored = localStorage.getItem('bmo-session-id');
    if (stored) return stored;
    const newId = `session-${Date.now()}`;
    localStorage.setItem('bmo-session-id', newId);
    return newId;
  });
  const [userName, setUserName] = useState('');
  const [showNamePrompt, setShowNamePrompt] = useState(true);
  const [bmoMood, setBmoMood] = useState('happy');
  const [visibleMessages, setVisibleMessages] = useState(5); // Show last 5 messages
  const inputRef = useRef(null);
  const messagesEndRef = useRef(null);

  useEffect(() => {
    const savedName = localStorage.getItem('bmo-user-name');
    if (savedName) {
      setUserName(savedName);
      setShowNamePrompt(false);
      const stored = localStorage.getItem('bmo-messages');
      if (stored) setMessages(JSON.parse(stored));
    }
  }, []);

  useEffect(() => {
    if (messages.length > 0) {
      localStorage.setItem('bmo-messages', JSON.stringify(messages));
    }
  }, [messages]);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  // Auto-focus input when not speaking
  useEffect(() => {
    if (!isSpeaking && !isLoading && inputRef.current) {
      inputRef.current.focus();
    }
  }, [isSpeaking, isLoading]);

  const getMoodFromBackend = async (text) => {
    try {
      const res = await fetch(`${API_BASE}/ai/emotion-analysis?text=${encodeURIComponent(text)}`);
      if (res.ok) {
        const data = await res.json();
        return data.emotion || 'happy';
      }
    } catch (err) {
      console.warn('Could not get emotion from backend:', err);
    }
    return 'happy';
  };

  const sendMessage = async (text) => {
    if (!text.trim() || isLoading || isSpeaking) return;
    
    const userMsg = { role: 'user', content: text };
    setMessages(prev => [...prev, userMsg]);
    setInputText('');
    setIsLoading(true);
    setBmoMood('thinking');

    try {
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
      
      if (!response.ok) {
        throw new Error(`API Error: ${response.statusText}`);
      }
      
      const data = await response.json();
      const assistantMsg = { 
        role: 'assistant', 
        content: data.response,
        emotion: data.detected_emotion 
      };
      setMessages(prev => [...prev, assistantMsg]);
      
      // Set mood to talking
      setBmoMood('talking');
      
      // Try to speak the response
      await speakText(data.response);
      
      // Set mood based on AI's detected emotion
      const detectedMood = data.detected_emotion || 'happy';
      setBmoMood(detectedMood);
      
    } catch (err) {
      console.error('Error sending message:', err);
      setBmoMood('nervous');
      const errorMsg = { 
        role: 'assistant', 
        content: 'معذرة، لم أتمكن من الرد. الرجاء المحاولة مجددا.',
        emotion: 'nervous'
      };
      setMessages(prev => [...prev, errorMsg]);
    } finally {
      setIsLoading(false);
    }
  };

  const speakText = async (text) => {
    try {
      setIsSpeaking(true);
      const res = await fetch(`${API_BASE}/voice/text-to-speech`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ text, language: 'ar-TN' })
      });
      
      if (res.ok) {
        const blob = await res.blob();
        const audioUrl = URL.createObjectURL(blob);
        const audio = new Audio(audioUrl);
        audio.onended = () => {
          setIsSpeaking(false);
          URL.revokeObjectURL(audioUrl);
        };
        // Use playback promise handling
        const playPromise = audio.play();
        if (playPromise !== undefined) {
          playPromise.catch(err => {
            console.error('Audio playback failed:', err);
            setIsSpeaking(false);
          });
        }
      } else {
        setIsSpeaking(false);
      }
    } catch (err) {
      console.error('TTS Error:', err);
      setIsSpeaking(false);
    }
  };

  const handleNameSubmit = () => {
    if (userName.trim()) {
      localStorage.setItem('bmo-user-name', userName);
      setShowNamePrompt(false);
    }
  };

  if (showNamePrompt) {
    return (
      <div className="name-prompt-screen">
        <div className="name-prompt-container">
          <BMOFace mood="happy" isSpeaking={false} />
          <div className="name-prompt-content">
            <h1>مرحبا! 👋 🎮</h1>
            <p>ما هو اسمك؟</p>
            <input
              value={userName}
              onChange={(e) => setUserName(e.target.value)}
              onKeyPress={(e) => e.key === 'Enter' && handleNameSubmit()}
              placeholder="اكتب اسمك..."
              autoFocus
              className="name-input"
            />
            <button onClick={handleNameSubmit} className="name-submit-btn">
              ابدأ المحادثة
            </button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="app-container">
      {/* Background Blur Layer */}
      <div className="background-layer"></div>
      
      {/* Main Content */}
      <div className="main-content">
        
        {/* BMO Face - Takes up most of the screen */}
        <div className="bmo-section">
          <BMOFace mood={bmoMood} isSpeaking={isSpeaking} />
          {isSpeaking && <div className="speaking-status">جاري التحدث...</div>}
          {isLoading && <div className="speaking-status">جاري التفكير...</div>}
        </div>

        {/* Text Input - Centered Below Face */}
        {!isSpeaking && !isLoading && (
          <div className="text-input-section">
            <div className="input-wrapper">
              <input
                ref={inputRef}
                value={inputText}
                onChange={(e) => setInputText(e.target.value)}
                onKeyPress={(e) => e.key === 'Enter' && sendMessage(inputText)}
                placeholder="اكتب رسالتك..."
                className="text-input"
                disabled={isSpeaking || isLoading}
              />
              <button 
                onClick={() => sendMessage(inputText)}
                disabled={isSpeaking || isLoading || !inputText.trim()}
                className="send-btn"
              >
                إرسال
              </button>
            </div>
          </div>
        )}

        {/* Dialog Transcriptions */}
        <div className="transcription-section">
          <div className="messages-list">
            {messages.slice(-visibleMessages).map((msg, i) => (
              <div key={i} className={`message-bubble ${msg.role}`}>
                <span className="message-label">
                  {msg.role === 'user' ? `${userName || 'أنت'}:` : 'BMO:'}
                </span>
                <span className="message-text">{msg.content}</span>
              </div>
            ))}
            <div ref={messagesEndRef} />
          </div>
        </div>
      </div>
    </div>
  );
}

function BMOFace({ mood = 'happy', isSpeaking = false }) {
  const [displayMood, setDisplayMood] = useState(mood);
  const faceRef = useRef(null);

  useEffect(() => {
    setDisplayMood(mood);
  }, [mood]);

  // Map emotions to character images
  const getMoodFaceImage = (emotion) => {
    const faceMap = {
      'happy': 'Rosto-01.png',
      'sad': 'Rosto-15.png',
      'surprised': 'Rosto-13.png',
      'angry': 'Rosto-16.png',
      'thinking': 'Rosto-02.png',
      'talking': 'Rosto-03.png',
      'confused': 'Rosto-05.png',
      'excited': 'Rosto-27.png',
      'loving': 'Rosto-21.png',
      'tired': 'Rosto-25.png',
      'proud': 'Rosto-19.png',
      'nervous': 'Rosto-23.png',
      'shocked': 'Rosto-14.png',
      'frustrated': 'Rosto-17.png',
      'laughing': 'Rosto-22.png',
      'interested': 'Rosto-11.png',
    };
    
    const imageName = faceMap[emotion] || faceMap['happy'];
    return `/assests/${imageName}`;
  };

  return (
    <div className="bmo-face-container" ref={faceRef}>
      <div className={`character-face ${displayMood} ${isSpeaking ? 'speaking' : ''}`}>
        <img 
          src={getMoodFaceImage(displayMood)} 
          alt={`BMO ${displayMood}`} 
          className="face-image"
          onError={(e) => {
            console.error('Image failed to load:', e.target.src);
            // Fallback to a simple emoji or placeholder
            e.target.style.display = 'none';
          }}
        />
        {isSpeaking && (
          <div className="speaking-indicator">
            <div className="speak-dot"></div>
            <div className="speak-dot"></div>
            <div className="speak-dot"></div>
          </div>
        )}
      </div>
    </div>
  );
}

export default App;
