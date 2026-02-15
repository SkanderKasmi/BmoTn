import React, { useState, useEffect, useRef } from 'react';
import {
  StyleSheet,
  View,
  Text,
  TextInput,
  TouchableOpacity,
  ScrollView,
  Animated,
  Dimensions,
  PermissionsAndroid,
  Platform,
  Linking,
  Alert
} from 'react-native';
import Voice from '@react-native-voice/voice';
import RNFS from 'react-native-fs';

const { width, height } = Dimensions.get('window');
const API_BASE = 'http://YOUR_SERVER_IP:8000'; // Replace with your server IP

export default function App() {
  const [messages, setMessages] = useState([]);
  const [inputText, setInputText] = useState('');
  const [isListening, setIsListening] = useState(false);
  const [isSpeaking, setIsSpeaking] = useState(false);
  const [sessionId] = useState(`session-${Date.now()}`);
  const [userName, setUserName] = useState('');
  const [showNamePrompt, setShowNamePrompt] = useState(true);
  const [bmoMood, setBmoMood] = useState('happy');
  
  // Animation refs
  const blinkAnim = useRef(new Animated.Value(1)).current;
  const bounceAnim = useRef(new Animated.Value(0)).current;
  const scrollViewRef = useRef(null);

  useEffect(() => {
    requestPermissions();
    setupVoice();
    startBlinkAnimation();
    startBounceAnimation();
    
    return () => {
      Voice.destroy().then(Voice.removeAllListeners);
    };
  }, []);

  // Request Android permissions
  const requestPermissions = async () => {
    if (Platform.OS === 'android') {
      try {
        const granted = await PermissionsAndroid.requestMultiple([
          PermissionsAndroid.PERMISSIONS.RECORD_AUDIO,
          PermissionsAndroid.PERMISSIONS.CAMERA,
        ]);
        
        if (granted['android.permission.RECORD_AUDIO'] !== PermissionsAndroid.RESULTS.GRANTED) {
          Alert.alert('أعطيني permission للمايكروفون باش نسمعك! 🎤');
        }
      } catch (err) {
        console.warn(err);
      }
    }
  };

  // Setup voice recognition
  const setupVoice = () => {
    Voice.onSpeechStart = () => setIsListening(true);
    Voice.onSpeechEnd = () => setIsListening(false);
    Voice.onSpeechResults = (e) => {
      if (e.value && e.value[0]) {
        sendMessage(e.value[0]);
      }
    };
    Voice.onSpeechError = (e) => {
      console.error('Speech error:', e);
      setIsListening(false);
    };
  };

  // Animations
  const startBlinkAnimation = () => {
    Animated.loop(
      Animated.sequence([
        Animated.timing(blinkAnim, {
          toValue: 0,
          duration: 100,
          useNativeDriver: true,
        }),
        Animated.delay(100),
        Animated.timing(blinkAnim, {
          toValue: 1,
          duration: 100,
          useNativeDriver: true,
        }),
        Animated.delay(3000),
      ])
    ).start();
  };

  const startBounceAnimation = () => {
    Animated.loop(
      Animated.sequence([
        Animated.timing(bounceAnim, {
          toValue: -10,
          duration: 1000,
          useNativeDriver: true,
        }),
        Animated.timing(bounceAnim, {
          toValue: 0,
          duration: 1000,
          useNativeDriver: true,
        }),
      ])
    ).start();
  };

  // Set user name
  const handleSetName = async () => {
    if (userName.trim()) {
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
        Alert.alert('خطأ', 'ماقدرتش نسجّل اسمك. تأكّد من الاتصال بالإنترنت.');
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
      
      // Check for app launch intent
      handleAppIntent(text);
      
      setTimeout(() => setBmoMood('happy'), 2000);
      
    } catch (error) {
      console.error('Chat error:', error);
      Alert.alert('خطأ', 'مشكلة في الاتصال. تأكّد من الإنترنت.');
      setBmoMood('happy');
    }
  };

  // Handle app opening intents
  const handleAppIntent = async (text) => {
    const textLower = text.toLowerCase();
    
    // YouTube
    if (textLower.includes('youtube') || text.includes('يوتيوب')) {
      Linking.openURL('intent://www.youtube.com#Intent;scheme=https;package=com.google.android.youtube;end');
    }
    // Facebook
    else if (textLower.includes('facebook') || text.includes('فيسبوك')) {
      Linking.openURL('intent://www.facebook.com#Intent;scheme=https;package=com.facebook.katana;end');
    }
    // WhatsApp
    else if (textLower.includes('whatsapp') || text.includes('واتساب')) {
      Linking.openURL('whatsapp://send');
    }
    // Gmail
    else if (textLower.includes('gmail') || text.includes('بريد')) {
      Linking.openURL('intent://mail.google.com#Intent;scheme=https;package=com.google.android.gm;end');
    }
    // Maps
    else if (textLower.includes('maps') || text.includes('خرائط')) {
      Linking.openURL('intent://maps.google.com#Intent;scheme=https;package=com.google.android.apps.maps;end');
    }
    // Browser
    else if (textLower.includes('chrome') || text.includes('متصفح')) {
      Linking.openURL('intent://#Intent;package=com.android.chrome;end');
    }
  };

  // Start voice recording
  const startVoiceRecording = async () => {
    try {
      await Voice.start('ar-TN'); // Tunisian Arabic
      setBmoMood('excited');
    } catch (error) {
      console.error('Voice start error:', error);
    }
  };

  // Stop voice recording
  const stopVoiceRecording = async () => {
    try {
      await Voice.stop();
      setBmoMood('thinking');
    } catch (error) {
      console.error('Voice stop error:', error);
    }
  };

  // Name prompt screen
  if (showNamePrompt) {
    return (
      <View style={styles.namePromptContainer}>
        <BMOFace mood="happy" blinkAnim={blinkAnim} bounceAnim={bounceAnim} />
        <Text style={styles.namePromptTitle}>مرحبا! 🎮</Text>
        <Text style={styles.namePromptText}>شنوّا اسمك؟</Text>
        <TextInput
          style={styles.nameInput}
          value={userName}
          onChangeText={setUserName}
          placeholder="اكتب اسمك هوني..."
          placeholderTextColor="#999"
          autoFocus
        />
        <TouchableOpacity style={styles.nameButton} onPress={handleSetName}>
          <Text style={styles.nameButtonText}>ياسر! دخّل</Text>
        </TouchableOpacity>
      </View>
    );
  }

  // Main chat screen
  return (
    <View style={styles.container}>
      <View style={styles.bmoHeader}>
        <Animated.View style={[
          styles.bmoFaceContainer,
          { transform: [{ translateY: bounceAnim }] }
        ]}>
          <BMOFace mood={bmoMood} blinkAnim={blinkAnim} bounceAnim={bounceAnim} isSpeaking={isSpeaking} />
        </Animated.View>
      </View>

      <ScrollView
        ref={scrollViewRef}
        style={styles.messagesContainer}
        onContentSizeChange={() => scrollViewRef.current?.scrollToEnd({ animated: true })}
      >
        {messages.map((msg, idx) => (
          <View key={idx} style={[styles.message, msg.role === 'user' ? styles.userMessage : styles.assistantMessage]}>
            <Text style={[styles.messageText, msg.role === 'user' ? styles.userMessageText : styles.assistantMessageText]}>
              {msg.content}
            </Text>
          </View>
        ))}
      </ScrollView>

      <View style={styles.inputContainer}>
        <TextInput
          style={styles.input}
          value={inputText}
          onChangeText={setInputText}
          placeholder="اكتب رسالتك..."
          placeholderTextColor="#999"
          editable={!isListening}
          multiline
        />
        
        <TouchableOpacity
          style={[styles.voiceButton, isListening && styles.voiceButtonActive]}
          onPressIn={startVoiceRecording}
          onPressOut={stopVoiceRecording}
        >
          <Text style={styles.buttonText}>🎤</Text>
        </TouchableOpacity>
        
        <TouchableOpacity style={styles.sendButton} onPress={() => sendMessage(inputText)}>
          <Text style={styles.buttonText}>📤</Text>
        </TouchableOpacity>
      </View>
    </View>
  );
}

// BMO Face Component with Eye Tracking
function BMOFace({ mood, blinkAnim, bounceAnim, isSpeaking }) {
  const [eyePosition, setEyePosition] = useState({ x: 0, y: 0 });
  const faceRef = useRef(null);

  const eyeScale = blinkAnim.interpolate({
    inputRange: [0, 1],
    outputRange: [0.1, 1],
  });

  // Touch tracking - eyes follow touch
  const handleTouchMove = (event) => {
    if (!event.nativeEvent.touches[0]) return;
    
    const touch = event.nativeEvent.touches[0];
    const { pageX, pageY } = touch;
    
    // Get face position (approximate center of screen)
    const faceCenterX = width / 2;
    const faceCenterY = height / 4;
    
    const deltaX = pageX - faceCenterX;
    const deltaY = pageY - faceCenterY;
    
    const maxMove = 8;
    const x = (deltaX / width) * maxMove * 2;
    const y = (deltaY / height) * maxMove * 2;
    
    setEyePosition({ 
      x: Math.max(-maxMove, Math.min(maxMove, x)), 
      y: Math.max(-maxMove, Math.min(maxMove, y)) 
    });
  };

  // Random idle eye movements
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
    <View 
      style={styles.bmoFace} 
      ref={faceRef}
      onTouchMove={handleTouchMove}
      onTouchEnd={() => {
        // Return eyes to center when touch ends
        setTimeout(() => setEyePosition({ x: 0, y: 0 }), 300);
      }}
    >
      <View style={styles.screen}>
        <View style={styles.eyes}>
          <Animated.View style={[styles.eye, { transform: [{ scaleY: eyeScale }] }]}>
            <Animated.View 
              style={[
                styles.pupil,
                {
                  transform: [
                    { translateX: eyePosition.x },
                    { translateY: eyePosition.y }
                  ]
                }
              ]} 
            />
          </Animated.View>
          <Animated.View style={[styles.eye, { transform: [{ scaleY: eyeScale }] }]}>
            <Animated.View 
              style={[
                styles.pupil,
                {
                  transform: [
                    { translateX: eyePosition.x },
                    { translateY: eyePosition.y }
                  ]
                }
              ]} 
            />
          </Animated.View>
        </View>
        
        <View style={styles.mouth}>
          {mood === 'happy' && <View style={styles.smile} />}
          {mood === 'talking' && <View style={styles.talkMouth} />}
          {mood === 'thinking' && <View style={styles.thinkMouth} />}
          {mood === 'excited' && <View style={styles.excitedMouth} />}
        </View>
      </View>
      
      <View style={styles.buttons}>
        <View style={[styles.btn, styles.btnRed]} />
        <View style={[styles.btn, styles.btnYellow]} />
        <View style={[styles.btn, styles.btnGreen]} />
        <View style={[styles.btn, styles.btnBlue]} />
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#667eea',
  },
  namePromptContainer: {
    flex: 1,
    backgroundColor: '#667eea',
    justifyContent: 'center',
    alignItems: 'center',
    padding: 20,
  },
  namePromptTitle: {
    fontSize: 32,
    color: 'white',
    fontWeight: 'bold',
    marginTop: 20,
  },
  namePromptText: {
    fontSize: 20,
    color: 'white',
    marginTop: 10,
    marginBottom: 20,
  },
  nameInput: {
    width: '100%',
    backgroundColor: 'white',
    padding: 15,
    borderRadius: 10,
    fontSize: 18,
    textAlign: 'center',
    marginBottom: 15,
  },
  nameButton: {
    backgroundColor: '#764ba2',
    padding: 15,
    borderRadius: 10,
    width: '100%',
  },
  nameButtonText: {
    color: 'white',
    fontSize: 18,
    fontWeight: 'bold',
    textAlign: 'center',
  },
  bmoHeader: {
    backgroundColor: '#5fb3b3',
    padding: 20,
    alignItems: 'center',
    borderBottomWidth: 4,
    borderBottomColor: '#2d6666',
  },
  bmoFaceContainer: {
    width: 150,
  },
  bmoFace: {
    backgroundColor: '#5fb3b3',
    borderRadius: 15,
    padding: 15,
    borderWidth: 3,
    borderColor: '#2d6666',
  },
  screen: {
    backgroundColor: '#8fd3d3',
    borderRadius: 10,
    padding: 15,
    alignItems: 'center',
  },
  eyes: {
    flexDirection: 'row',
    justifyContent: 'space-around',
    width: '100%',
    marginBottom: 15,
  },
  eye: {
    width: 30,
    height: 30,
    backgroundColor: 'white',
    borderRadius: 15,
    justifyContent: 'center',
    alignItems: 'center',
  },
  pupil: {
    width: 12,
    height: 12,
    backgroundColor: '#2d6666',
    borderRadius: 6,
  },
  mouth: {
    width: 50,
    height: 25,
    justifyContent: 'center',
    alignItems: 'center',
  },
  smile: {
    width: 40,
    height: 20,
    borderWidth: 3,
    borderColor: '#2d6666',
    borderTopWidth: 0,
    borderRadius: 20,
  },
  talkMouth: {
    width: 25,
    height: 25,
    backgroundColor: '#2d6666',
    borderRadius: 12,
  },
  thinkMouth: {
    width: 30,
    height: 2,
    backgroundColor: '#2d6666',
  },
  excitedMouth: {
    width: 30,
    height: 30,
    backgroundColor: '#2d6666',
    borderRadius: 15,
  },
  buttons: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    justifyContent: 'space-around',
    marginTop: 10,
  },
  btn: {
    width: 25,
    height: 25,
    borderRadius: 5,
    margin: 3,
  },
  btnRed: { backgroundColor: '#ff5252' },
  btnYellow: { backgroundColor: '#ffd740' },
  btnGreen: { backgroundColor: '#69f0ae' },
  btnBlue: { backgroundColor: '#448aff' },
  messagesContainer: {
    flex: 1,
    backgroundColor: 'white',
    padding: 15,
  },
  message: {
    maxWidth: '80%',
    padding: 12,
    borderRadius: 15,
    marginBottom: 10,
  },
  userMessage: {
    alignSelf: 'flex-end',
    backgroundColor: '#667eea',
  },
  assistantMessage: {
    alignSelf: 'flex-start',
    backgroundColor: '#f0f0f0',
  },
  messageText: {
    fontSize: 16,
  },
  userMessageText: {
    color: 'white',
  },
  assistantMessageText: {
    color: '#333',
  },
  inputContainer: {
    flexDirection: 'row',
    padding: 10,
    backgroundColor: 'white',
    borderTopWidth: 1,
    borderTopColor: '#e0e0e0',
  },
  input: {
    flex: 1,
    backgroundColor: '#f5f5f5',
    padding: 12,
    borderRadius: 20,
    fontSize: 16,
    marginRight: 8,
    maxHeight: 100,
  },
  voiceButton: {
    backgroundColor: '#5fb3b3',
    width: 50,
    height: 50,
    borderRadius: 25,
    justifyContent: 'center',
    alignItems: 'center',
    marginRight: 8,
  },
  voiceButtonActive: {
    backgroundColor: '#ff5252',
  },
  sendButton: {
    backgroundColor: '#667eea',
    width: 50,
    height: 50,
    borderRadius: 25,
    justifyContent: 'center',
    alignItems: 'center',
  },
  buttonText: {
    fontSize: 24,
  },
});
