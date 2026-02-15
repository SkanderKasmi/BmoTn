import React, { useState, useEffect, useRef } from 'react';
import './App.css';

const API_BASE = process.env.REACT_APP_API_URL || 'http://localhost:8000';

// Comprehensive emotion detection with multiple emotion states
const EMOTION_KEYWORDS = {
  happy: ['happy', 'great', 'wonderful', 'excellent', 'good', 'amazing', 'awesome', 'love', 'beautiful', 'fantastic', 'haha', 'hehe', 'yay', '😊', '😄', '❤️'],
  sad: ['sad', 'sorry', 'bad', 'terrible', 'awful', 'hate', 'disappointment', 'cry', 'depressed', 'unhappy', '😢', '😭'],
  surprised: ['wow', 'amazing', 'surprised', 'really', 'seriously', 'no way', 'incredible', 'unbelievable', 'wait', 'what', '😮', '🤩'],
  angry: ['angry', 'frustrated', 'mad', 'furious', 'hate', 'terrible', 'disgusting', 'awful', '😠', '🤬'],
  confused: ['what', 'confused', 'how', 'why', 'unclear', 'don\'t understand', 'huh', 'pardon', '🤔', '😕'],
  excited: ['excited', 'yay', 'awesome', 'can\'t wait', 'amazing', 'incredible', 'awesome', '🎉', '😃', '🤩'],
  loving: ['love', 'like', 'appreciate', 'grateful', 'thank you', 'thanks', 'adore', '❤️', '💕'],
  tired: ['tired', 'tired', 'sleepy', 'exhausted', 'drain', '😴', '😪'],
  proud: ['proud', 'accomplished', 'did it', 'success', 'achieved', '🏆', '😎'],
  nervous: ['nervous', 'worried', 'anxiety', 'scared', 'afraid', 'fear', '😰', '😟'],
};

function App() {
  const [messages, setMessages] = useState([]);
  const [inputText, setInputText] = useState('');
  const [isSpeaking, setIsSpeaking] = useState(false);
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
  const [presenceTime, setPresenceTime] = useState(0);

  const messagesEndRef = useRef(null);

  // Track time with BMO for idle animations
  useEffect(() => {
    const timer = setInterval(() => {
      setPresenceTime(prev => prev + 1);
    }, 1000);
    return () => clearInterval(timer);
  }, []);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

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

  const determineMood = (text) => {
    if (!text) return 'happy';
    const lower = text.toLowerCase();
    
    // Check for emotions in order of priority
    for (const [emotion, keywords] of Object.entries(EMOTION_KEYWORDS)) {
      if (keywords.some(keyword => lower.includes(keyword))) {
        return emotion;
      }
    }
    
    // Default to happy if no keywords match
    return 'happy';
  };

  const sendMessage = async (text) => {
    if (!text.trim()) return;
    
    const userMsg = { role: 'user', content: text };
    setMessages(prev => [...prev, userMsg]);
    
    // Show mood based on user's message
    const userMood = determineMood(text);
    setBmoMood('thinking');
    setInputText('');

    try {
      const response = await fetch(`${API_BASE}/ai/chat`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: text, session_id: sessionId, user_name: userName })
      });
      
      if (!response.ok) throw new Error('API Error');
      
      const data = await response.json();
      const assistantMsg = { role: 'assistant', content: data.response };
      setMessages(prev => [...prev, assistantMsg]);
      
      // Show talking animation first
      setBmoMood('talking');
      
      // Then speak the response
      await speakText(data.response);
      
      // Finally show mood based on AI response
      const aiMood = determineMood(data.response);
      setBmoMood(aiMood);
    } catch (err) {
      console.error('Error sending message:', err);
      setBmoMood('nervous');
      const errorMsg = { role: 'assistant', content: 'معذرة، حدث خطأ. الرجاء المحاولة مجددا.' };
      setMessages(prev => [...prev, errorMsg]);
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
      const blob = await res.blob();
      const audioUrl = URL.createObjectURL(blob);
      const audio = new Audio(audioUrl);
      audio.onended = () => {
        setIsSpeaking(false);
        URL.revokeObjectURL(audioUrl);
      };
      await audio.play();
    } catch (err) {
      console.error(err);
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
      <div className="full-screen-center">
        <BMOFace mood="happy" />
        <h2>مرحبا! 🎮</h2>
        <input
          value={userName}
          onChange={(e) => setUserName(e.target.value)}
          onKeyPress={(e) => e.key === 'Enter' && handleNameSubmit()}
          placeholder="اكتب اسمك..."
          autoFocus
        />
      </div>
    );
  }

  return (
    <div className="app-fullscreen">
      <BMOFace mood={bmoMood} isSpeaking={isSpeaking} />
      <div className="chat-panel">
        <div className="messages">
          {messages.map((msg, i) => (
            <div key={i} className={`message ${msg.role}`}>
              {msg.content}
            </div>
          ))}
          <div ref={messagesEndRef} />
        </div>
        <div className="input-area">
          <input
            value={inputText}
            onChange={(e) => setInputText(e.target.value)}
            onKeyPress={(e) => e.key === 'Enter' && sendMessage(inputText)}
            placeholder="اكتب رسالتك..."
          />
          <button onClick={() => sendMessage(inputText)}>إرسال</button>
        </div>
      </div>
    </div>
  );
}

function BMOFace({ mood, isSpeaking }) {
  const faceRef = useRef(null);
  const [displayMood, setDisplayMood] = useState(mood);

  useEffect(() => {
    setDisplayMood(mood);
  }, [mood]);

  // Comprehensive emotion to image mapping
  const getMoodFaceImage = (emotion) => {
    const faceMap = {
      'happy': 'Rosto-01.png',        // Content/Happy
      'sad': 'Rosto-15.png',          // Sad/Disappointed
      'surprised': 'Rosto-13.png',    // Surprised/Amazed
      'angry': 'Rosto-16.png',        // Angry
      'thinking': 'Rosto-02.png',     // Thinking/Neutral
      'talking': 'Rosto-03.png',      // Talking/Speaking
      'confused': 'Rosto-05.png',     // Confused
      'excited': 'Rosto-27.png',      // Excited/Crazy
      'loving': 'Rosto-21.png',       // Loving/Caring
      'tired': 'Rosto-25.png',        // Tired/Sleepy
      'proud': 'Rosto-19.png',        // Confident/Proud
      'nervous': 'Rosto-23.png',      // Nervous/Embarrassed
      'shocked': 'Rosto-14.png',      // Shocked
      'frustrated': 'Rosto-17.png',   // Frustrated
      'laughing': 'Rosto-22.png',     // Laughing/Joking
      'interested': 'Rosto-11.png',   // Interested
    };
    
    return `/assests/${faceMap[emotion] || faceMap['happy']}`;
  };

  return (
    <div className="bmo-face-fullscreen" ref={faceRef}>
      {/* Character Face */}
      <div className={`character-face ${displayMood} ${isSpeaking ? 'speaking' : ''}`}>
        <img 
          src={getMoodFaceImage(displayMood)} 
          alt={`BMO ${displayMood}`} 
          className="face-image"
          onError={(e) => {
            console.error('Image failed to load:', e.target.src);
            e.target.style.display = 'none';
          }}
          onLoad={() => console.log('Image loaded:', displayMood)}
        />
        {isSpeaking && <div className="speaking-indicator"></div>}
      </div>
      
      {/* Idle animations - blinking and expressions */}
      <div className="idle-animations">
        <div className="blink-indicator" />
      </div>
    </div>
  );
}

export default App;
