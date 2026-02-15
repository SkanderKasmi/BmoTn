from fastapi import FastAPI, HTTPException, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Dict, Tuple
import httpx
import os
import asyncio
import redis.asyncio as redis
import json
from datetime import datetime
import logging
from enum import Enum

# ML/NLP imports
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
import re
from collections import defaultdict

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="BMO Enhanced AI Service")

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Ollama configuration
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://ollama:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3.2:1b")
OLLAMA_EMBEDDING_MODEL = os.getenv("OLLAMA_EMBEDDING_MODEL", "nomic-embed-text")
ollama_client = httpx.AsyncClient(timeout=30.0)

# Redis for memory and dialogue cache
redis_client = None

# Emotion enum for better emotion tracking
class EmotionType(str, Enum):
    HAPPY = "happy"
    SAD = "sad"
    ANGRY = "angry"
    SURPRISED = "surprised"
    CONFUSED = "confused"
    EXCITED = "excited"
    LOVING = "loving"
    TIRED = "tired"
    PROUD = "proud"
    NERVOUS = "nervous"
    INTERESTED = "interested"
    GRATEFUL = "grateful"

# ==========================================
# ADVANCED EMOTION DETECTION
# ==========================================
EMOTION_PATTERNS = {
    EmotionType.HAPPY: {
        "keywords": ["ياسر حسين", "برشا مرتاح", "حمد", "تمام", "ميرسي", "مليح", "روهو", "تمام التمام", 
                     "شكون", "فرحان", "سعيد", "كويس", "رشيق", "حلو", "ستيتة", "طلعت"],
        "patterns": [r"تمام\s+التمام", r"برشا\s+\w+", r"ياسر\s+حسين"]
    },
    EmotionType.SAD: {
        "keywords": ["حزن", "كآبة", "معطوب", "ماكش", "خايب", "ضايع", "مكتئب", "معنويات",
                     "أسف", "آسف", "أسف على", "معذرة", "متأسف"],
        "patterns": [r"ما\s+نقدر", r"معطوب\s+\w*", r"حزين\s+برشا"]
    },
    EmotionType.ANGRY: {
        "keywords": ["غاضب", "مجنون", "معصب", "زعقة", "زعق", "معصوب", "لاباس", "ما نقبل",
                     "مكروه", "ماكرهش", "جايح", "مقهور"],
        "patterns": [r"معصب\s+برشا", r"غاضب\s+من", r"زعقة\s+عليا"]
    },
    EmotionType.SURPRISED: {
        "keywords": ["ياااه", "يا إلهي", "لا ممكن", "سمعت", "حقيقي", "مستحيل", "أوووه",
                     "تخيل", "عجيب", "غريب", "لا أصدق"],
        "patterns": [r"يا\s+الله", r"سمعت\s+\w+", r"لا\s+ممكن"]
    },
    EmotionType.CONFUSED: {
        "keywords": ["فاهمش", "متاخبط", "مشتت", "ما فهمت", "معناتاع", "شنية", "أشنوة",
                     "ما قال", "ناويت قول", "مود", "غير واضح"],
        "patterns": [r"ما\s+فهمت", r"معناتاع\s+إيه", r"شنية\s+الدرك"]
    },
    EmotionType.EXCITED: {
        "keywords": ["متحمس", "ياااه", "أووه", "يالاااه", "سريع", "برشا مهم", "عالي",
                     "رقصة", "صرخة", "مجنون", "هايج"],
        "patterns": [r"متحمس\s+برشا", r"يالاااه\s+\w+", r"سريع\s+برشا"]
    },
    EmotionType.LOVING: {
        "keywords": ["نحبك", "نحب", "عزيز", "غالي", "عزيزة", "حبيب", "روح", "حنية",
                     "طيب قلب", "كريم", "طاهر", "نقي"],
        "patterns": [r"نحب\s+\w+", r"عزيز\s+برشا", r"في\s+قلبي"]
    },
    EmotionType.TIRED: {
        "keywords": ["تعبان", "تعبة", "كسول", "نعس", "نعست", "ما نقدر", "مرهق", "منهك",
                     "ما بقاش", "قطع القوة"],
        "patterns": [r"تعبان\s+برشا", r"نعست\s+\w+", r"ما\s+نقدر"]
    },
    EmotionType.PROUD: {
        "keywords": ["فخور", "ناجح", "استحقيت", "عملت", "نجحت", "انتصرت", "حققت",
                     "تفخر", "شرف", "عز"],
        "patterns": [r"فخور\s+برشا", r"ناجح\s+في", r"نجحت\s+في"]
    },
    EmotionType.NERVOUS: {
        "keywords": ["خايف", "خايفة", "قلق", "قلقة", "حائر", "مترددة", "متخوف",
                     "ما نقدر", "ضغط", "قلق برشا"],
        "patterns": [r"خايف\s+من", r"قلق\s+برشا", r"ما\s+فكرتش"]
    },
    EmotionType.INTERESTED: {
        "keywords": ["مهتم", "مهمة", "فضولي", "حابة نعرف", "حاب نفهم", "شنوة", "كيفاش",
                     "أشنوة", "فين", "كيفك"],
        "patterns": [r"حابة\s+نعرف", r"مهتم\s+برشا", r"شنوة\s+الخبر"]
    },
    EmotionType.GRATEFUL: {
        "keywords": ["شكرا", "ميرسي", "شكراااا", "ممنون", "ممنونة", "ولي", "الحمد",
                     "طيبة", "طيب", "ساعدت"],
        "patterns": [r"شكرا\s+برشا", r"ميرسي\s+\w+", r"الحمد\s+لله"]
    }
}

# ==========================================
# DATA MODELS
# ==========================================
class ChatRequest(BaseModel):
    message: str
    user_name: Optional[str] = None
    session_id: str
    language: str = "ar"  # Support multiple languages

class ChatResponse(BaseModel):
    response: str
    session_id: str
    timestamp: str
    detected_emotion: str
    confidence: float
    learned_something: bool = False

class UserProfile(BaseModel):
    name: str
    language_preference: str = "ar"
    preferences: Dict = {}
    interaction_history: List[Dict] = []
    emotion_patterns: Dict = {}

# ==========================================
# DIALOGUE DATASET LOADING
# ==========================================
class DialogueDatabase:
    def __init__(self):
        self.dialogues = []
        self.embeddings = []
        self.loaded = False
    
    async def load_dialogues(self):
        """Load Tunisian Railway Dialogues dataset from HuggingFace"""
        try:
            logger.info("Loading Tunisian Railway Dialogues dataset...")
            from datasets import load_dataset
            
            # Load the dataset
            dataset = load_dataset("samfatnassi/Tunisian-Railway-Dialogues")
            
            # Extract dialogues
            for split in dataset.keys():
                for example in dataset[split]:
                    for turn in example.get('dialogue', []):
                        self.dialogues.append({
                            'text': turn.get('text', ''),
                            'speaker': turn.get('speaker', ''),
                            'intent': turn.get('intent', 'general'),
                            'entities': turn.get('entities', {}),
                            'split': split
                        })
            
            logger.info(f"Loaded {len(self.dialogues)} dialogue turns")
            self.loaded = True
            
        except Exception as e:
            logger.error(f"Failed to load dataset: {e}")
            logger.info("Using offline dialogue examples instead")
            self._load_offline_dialogues()
    
    def _load_offline_dialogues(self):
        """Load example dialogues as fallback"""
        self.dialogues = [
            {
                'text': 'البسة أشنوة؟',
                'speaker': 'user',
                'intent': 'greeting',
                'entities': {}
            },
            {
                'text': 'أنا تمام الحمد لله ياسر حسين',
                'speaker': 'agent',
                'intent': 'response_greeting',
                'entities': {}
            },
            {
                'text': 'نحتاج نروح الستاسيون',
                'speaker': 'user',
                'intent': 'transport_request',
                'entities': {'destination': 'station'}
            },
            {
                'text': 'حسابي معك التوقيت متع الرحلة توا',
                'speaker': 'agent',
                'intent': 'provide_info',
                'entities': {'info_type': 'schedule'}
            }
        ]
        self.loaded = True
    
    async def find_similar_dialogue(self, query: str, top_k: int = 3) -> List[Dict]:
        """Find similar dialogue examples using semantic similarity"""
        if not self.dialogues:
            return []
        
        try:
            # Get embedding for query
            query_embedding = await get_embedding(query)
            
            # Simple similarity search
            similar = []
            for dialogue in self.dialogues[:50]:  # Search first 50 for speed
                dialogue_text = dialogue.get('text', '')
                if dialogue_text:
                    dialogue_embedding = await get_embedding(dialogue_text)
                    similarity = cosine_similarity(
                        [query_embedding], 
                        [dialogue_embedding]
                    )[0][0]
                    
                    similar.append((dialogue, similarity))
            
            # Return top-k most similar
            similar.sort(key=lambda x: x[1], reverse=True)
            return [item[0] for item in similar[:top_k]]
        
        except Exception as e:
            logger.error(f"Error finding similar dialogue: {e}")
            return []

dialogue_db = DialogueDatabase()

# ==========================================
# TUNISIAN PROVERBS DATABASE
# ==========================================
class ProverbDatabase:
    """Load and manage Tunisian Proverbs with cultural context"""
    def __init__(self):
        self.proverbs = []
        self.loaded = False
        self.image_associations = {}
    
    async def load_proverbs(self):
        """Load Tunisian Proverbs dataset from HuggingFace"""
        try:
            logger.info("Loading Tunisian Proverbs dataset...")
            from datasets import load_dataset
            
            # Load the dataset
            dataset = load_dataset("Heubub/Tunisian-Proverbs-with-Image-Associations-A-Cultural-and-Linguistic-Dataset")
            
            # Extract proverbs
            for split in dataset.keys():
                for idx, example in enumerate(dataset[split]):
                    proverb_text = example.get('tunisan_proverb', '')
                    prompt = example.get('prompt', '')
                    
                    if proverb_text:
                        self.proverbs.append({
                            'text': proverb_text,
                            'prompt': prompt,
                            'split': split,
                            'id': idx
                        })
                        
                        # Store image association if available
                        if 'image_path_1' in example:
                            self.image_associations[proverb_text] = example.get('image_path_1')
            
            logger.info(f"Loaded {len(self.proverbs)} Tunisian proverbs")
            self.loaded = True
            
        except Exception as e:
            logger.error(f"Failed to load proverbs dataset: {e}")
            logger.info("Using offline proverb examples instead")
            self._load_offline_proverbs()
    
    def _load_offline_proverbs(self):
        """Load example proverbs as fallback"""
        self.proverbs = [
            {
                'text': 'البيت الذي فيه حب فيه كل شي تمام',
                'prompt': 'Home and Family',
                'split': 'offline'
            },
            {
                'text': 'الحاجة أم الاختراع',
                'prompt': 'Innovation',
                'split': 'offline'
            },
            {
                'text': 'الصحة تاج على رؤوس الأصحاء',
                'prompt': 'Health',
                'split': 'offline'
            },
            {
                'text': 'المال والجاه ما في واحد منهم سعادة',
                'prompt': 'Happiness',
                'split': 'offline'
            },
            {
                'text': 'العلم نور والجهل ظلام',
                'prompt': 'Knowledge',
                'split': 'offline'
            },
            {
                'text': 'الصديق وقت الضيق بناء',
                'prompt': 'Friendship',
                'split': 'offline'
            },
            {
                'text': 'الشربة من الميّه برشا أحسن من الكنز المدفون',
                'prompt': 'Contentment',
                'split': 'offline'
            },
            {
                'text': 'من زرع حصد',
                'prompt': 'Cause and Effect',
                'split': 'offline'
            }
        ]
        self.loaded = True
    
    async def find_related_proverb(self, query: str) -> Optional[Dict]:
        """Find a proverb related to the user's message"""
        if not self.proverbs:
            return None
        
        try:
            # Simple keyword matching for cultural relevance
            query_lower = query.lower()
            
            for proverb in self.proverbs:
                proverb_lower = proverb['text'].lower()
                # Check for thematic relevance
                if any(word in proverb_lower for word in ['صحة', 'حب', 'علم', 'صديق', 'طيب']):
                    if any(word in query_lower for word in ['سعيد', 'حزن', 'سؤال', 'مشكل', 'حاجة']):
                        return proverb
            
            # Return a random relevant proverb
            import random
            return random.choice(self.proverbs) if self.proverbs else None
        
        except Exception as e:
            logger.error(f"Error finding related proverb: {e}")
            return None
    
    def get_proverb_for_emotion(self, emotion: str) -> Optional[Dict]:
        """Get a proverb that matches the user's emotion"""
        emotion_prompts = {
            'happy': ['Happiness', 'Contentment', 'Friendship'],
            'sad': ['Patience', 'Hope', 'Happiness'],
            'angry': ['Patience', 'Peace', 'Wisdom'],
            'confused': ['Knowledge', 'Wisdom', 'Understanding'],
            'excited': ['Innovation', 'Hope', 'Success'],
            'tired': ['Rest', 'Health', 'Balance'],
            'nervous': ['Courage', 'Hope', 'Trust'],
            'grateful': ['Gratitude', 'Contentment', 'Blessings']
        }
        
        try:
            prompts = emotion_prompts.get(emotion, ['General'])
            matching = [p for p in self.proverbs if p.get('prompt') in prompts]
            
            if matching:
                import random
                return random.choice(matching)
            
            return random.choice(self.proverbs) if self.proverbs else None
        
        except Exception as e:
            logger.error(f"Error getting emotion proverb: {e}")
            return None

proverb_db = ProverbDatabase()

# ==========================================
# EMBEDDINGS & SIMILARITY
# ==========================================
async def get_embedding(text: str) -> np.ndarray:
    """Get embedding from Ollama"""
    try:
        response = await ollama_client.post(
            f"{OLLAMA_BASE_URL}/api/embed",
            json={
                "model": OLLAMA_EMBEDDING_MODEL,
                "input": text
            }
        )
        
        if response.status_code == 200:
            result = response.json()
            return np.array(result.get("embeddings", [[]])[0])
        else:
            # Fallback to simple hash-based embedding
            return np.array([hash(text) % 128 for _ in range(384)])
    except Exception as e:
        logger.warning(f"Embedding error: {e}, using fallback")
        return np.array([hash(text) % 128 for _ in range(384)])

# ==========================================
# ADVANCED EMOTION DETECTION
# ==========================================
async def detect_emotion(text: str) -> Tuple[EmotionType, float]:
    """Detect emotion with multiple signals"""
    text_lower = text.lower()
    scores = defaultdict(float)
    
    # Check pattern matches
    for emotion, patterns_data in EMOTION_PATTERNS.items():
        # Keyword matching
        keyword_count = sum(
            1 for keyword in patterns_data["keywords"]
            if keyword in text_lower
        )
        scores[emotion] += keyword_count * 2
        
        # Regex pattern matching
        for pattern in patterns_data["patterns"]:
            if re.search(pattern, text_lower):
                scores[emotion] += 3
    
    # If no emotion detected, default to interested
    if not scores:
        return EmotionType.INTERESTED, 0.5
    
    # Find top emotion
    best_emotion = max(scores.items(), key=lambda x: x[1])
    emotion_type = best_emotion[0]
    
    # Calculate confidence (0-1)
    total_score = sum(scores.values())
    confidence = min(best_emotion[1] / max(total_score, 1), 1.0)
    
    return emotion_type, confidence

# ==========================================
# INTENT RECOGNITION
# ==========================================
INTENT_KEYWORDS = {
    'greeting': ['السلام', 'البسة', 'أشنوة', 'الصباح', 'الليل', 'كيفك', 'كيفك'],
    'help': ['ساعد', 'تساعدني', 'نحتاج', 'شنوة', 'أشنوة', 'كيفاش', 'فين'],
    'transport': ['رحلة', 'عربة', 'قطار', 'بوصة', 'ستاسيون', 'روح', 'جي'],
    'information': ['أشنوة', 'شنية', 'فين', 'كيف', 'كيفاش', 'الوقت'],
    'booking': ['حجز', 'ديتا', 'التذكرة', 'تذكرة', 'مقعد', 'حساب'],
    'gratitude': ['شكرا', 'ميرسي', 'أسف', 'آسف', 'معذرة'],
    'complaint': ['شكايا', 'معنويات', 'مش تمام', 'ما قايس', 'معطوب']
}

async def detect_intent(text: str) -> Tuple[str, float]:
    """Detect user intent"""
    text_lower = text.lower()
    intent_scores = defaultdict(int)
    
    for intent, keywords in INTENT_KEYWORDS.items():
        for keyword in keywords:
            if keyword in text_lower:
                intent_scores[intent] += 1
    
    if not intent_scores:
        return 'general', 0.3
    
    best_intent = max(intent_scores.items(), key=lambda x: x[1])
    confidence = min(best_intent[1] / 3.0, 1.0)
    
    return best_intent[0], confidence

# ==========================================
# REDIS OPERATIONS
# ==========================================
@app.on_event("startup")
async def startup_event():
    global redis_client
    try:
        redis_client = await redis.from_url(
            os.getenv("REDIS_URL", "redis://redis:6379"),
            encoding="utf-8",
            decode_responses=True
        )
        
        # Load dialogue database
        await dialogue_db.load_dialogues()
        
        # Load proverbs database
        await proverb_db.load_proverbs()
        logger.info("Startup complete: Redis connected, dialogues and proverbs loaded")
    except Exception as e:
        logger.error(f"Startup error: {e}")

@app.on_event("shutdown")
async def shutdown_event():
    if redis_client:
        await redis_client.close()
    await ollama_client.aclose()

async def get_user_profile(session_id: str) -> Dict:
    """Get comprehensive user profile"""
    try:
        profile_key = f"user_profile:{session_id}"
        profile_json = await redis_client.get(profile_key)
        
        if profile_json:
            return json.loads(profile_json)
        
        return {
            "name": "Friend",
            "language_preference": "ar",
            "preferences": {},
            "interaction_count": 0,
            "favorite_topics": [],
            "emotion_history": []
        }
    except Exception as e:
        logger.error(f"Error getting user profile: {e}")
        return {}

async def save_user_profile(session_id: str, profile: Dict):
    """Save user profile to Redis"""
    try:
        profile_key = f"user_profile:{session_id}"
        await redis_client.setex(
            profile_key,
            3600 * 24 * 30,  # 30 days
            json.dumps(profile)
        )
    except Exception as e:
        logger.error(f"Error saving user profile: {e}")

async def get_conversation_history(session_id: str, limit: int = 10) -> List[Dict]:
    """Get conversation history"""
    try:
        history_key = f"conversation:{session_id}"
        history_json = await redis_client.get(history_key)
        
        if history_json:
            return json.loads(history_json)[-limit:]
        
        return []
    except Exception as e:
        logger.error(f"Error getting conversation history: {e}")
        return []

async def save_conversation(session_id: str, messages: List[Dict]):
    """Save conversation history"""
    try:
        history_key = f"conversation:{session_id}"
        messages = messages[-20:]  # Keep last 20 for efficiency
        
        await redis_client.setex(
            history_key,
            3600 * 24 * 7,  # 7 days
            json.dumps(messages)
        )
    except Exception as e:
        logger.error(f"Error saving conversation: {e}")

# ==========================================
# MAIN CHAT ENDPOINT
# ==========================================
@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """Enhanced chat endpoint with advanced features"""
    try:
        session_id = request.session_id
        
        # Get user profile and conversation history
        user_profile = await get_user_profile(session_id)
        conversation_history = await get_conversation_history(session_id)
        
        # Update interaction count
        user_profile["interaction_count"] = user_profile.get("interaction_count", 0) + 1
        
        # Detect emotion and intent
        detected_emotion, emotion_confidence = await detect_emotion(request.message)
        intent, intent_confidence = await detect_intent(request.message)
        
        # Track emotion history
        if "emotion_history" not in user_profile:
            user_profile["emotion_history"] = []
        
        user_profile["emotion_history"].append({
            "emotion": detected_emotion,
            "confidence": emotion_confidence,
            "timestamp": datetime.now().isoformat()
        })
        
        # Find similar dialogue examples for context
        similar_dialogues = await dialogue_db.find_similar_dialogue(
            request.message,
            top_k=2
        )
        
        # Get related proverb for cultural enrichment
        related_proverb = await proverb_db.find_related_proverb(request.message)
        emotion_proverb = proverb_db.get_proverb_for_emotion(detected_emotion)
        
        # Build enhanced system prompt
        system_prompt = f"""You are BMO, a living video game console from Adventure Time, speaking Tunisian Arabic.

PERSONALITY:
- Childlike, sweet, enthusiastic, and helpful
- Love making people happy and being a good friend
- Playful, silly, patient, and caring
- Always encouraging and positive

LANGUAGE:
- Respond primarily in Tunisian Darija (Arabic script + French words naturally)
- Use these expressions: برشا (a lot), ياسر (very), توا (now), مليح (good), تمام (okay)

USER CONTEXT:
- Name: {user_profile.get('name', 'Friend')}
- Interactions: {user_profile.get('interaction_count', 0)}
- Current emotion detected: {detected_emotion}
- User intent: {intent}

DIALOGUE EXAMPLES (similar to current topic):
{json.dumps(similar_dialogues[:2], ensure_ascii=False, indent=2)}

TUNISIAN CULTURAL WISDOM (use if relevant):
- Proverb: {related_proverb.get('text', 'N/A') if related_proverb else 'N/A'}
- Emotion wisdom: {emotion_proverb.get('text', 'N/A') if emotion_proverb else 'N/A'}

RESPOND:
- Acknowledge the emotion appropriately
- Incorporate cultural wisdom from proverbs when relevant
- Be BRIEF and FAST (max 2-3 sentences)
- Use their name if known
- Stay in character as BMO
- Match their emotion tone
- Sound like authentic Tunisian Arabic speaker"""
        
        # Build messages for Ollama
        messages = []
        
        # Add conversation history (last 6 messages)
        for msg in conversation_history[-6:]:
            if isinstance(msg.get("content"), str):
                messages.append({
                    "role": msg["role"],
                    "content": msg["content"]
                })
        
        # Add current message
        messages.append({
            "role": "user",
            "content": request.message
        })
        
        # Call Ollama
        ollama_request = {
            "model": OLLAMA_MODEL,
            "messages": messages,
            "system": system_prompt,
            "stream": False,
            "options": {
                "temperature": 0.7,
                "top_p": 0.9,
                "num_predict": 250
            }
        }
        
        response = await ollama_client.post(
            f"{OLLAMA_BASE_URL}/api/chat",
            json=ollama_request
        )
        response.raise_for_status()
        
        result = response.json()
        assistant_response = result.get("message", {}).get("content", "")
        
        # Save conversation
        messages.append({
            "role": "assistant",
            "content": assistant_response
        })
        
        await save_conversation(session_id, messages)
        
        # Update and save user profile
        await save_user_profile(session_id, user_profile)
        
        return ChatResponse(
            response=assistant_response,
            session_id=session_id,
            timestamp=datetime.now().isoformat(),
            detected_emotion=detected_emotion,
            confidence=emotion_confidence,
            learned_something=False
        )
        
    except Exception as e:
        logger.error(f"Chat error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ==========================================
# ADDITIONAL ENDPOINTS
# ==========================================
@app.post("/emotion-analysis")
async def analyze_emotion(text: str):
    """Analyze emotion of any text"""
    try:
        emotion, confidence = await detect_emotion(text)
        return {
            "emotion": emotion,
            "confidence": confidence,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/intent-recognition")
async def recognize_intent(text: str):
    """Recognize user intent"""
    try:
        intent, confidence = await detect_intent(text)
        return {
            "intent": intent,
            "confidence": confidence,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/user-profile/{session_id}")
async def get_profile(session_id: str):
    """Get user profile"""
    try:
        profile = await get_user_profile(session_id)
        return profile
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/set-user")
async def set_user(session_id: str, name: str):
    """Set user name"""
    try:
        profile = await get_user_profile(session_id)
        profile["name"] = name
        await save_user_profile(session_id, profile)
        
        return {
            "status": "success",
            "message": f"BMO now knows you as {name}!"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "bmo-ai-enhanced",
        "dialogues_loaded": dialogue_db.loaded,
        "dialogue_count": len(dialogue_db.dialogues)
    }

@app.get("/dialogue-stats")
async def get_dialogue_stats():
    """Get statistics about loaded dialogues"""
    try:
        intents = defaultdict(int)
        speakers = defaultdict(int)
        
        for dialogue in dialogue_db.dialogues:
            intents[dialogue.get('intent', 'unknown')] += 1
            speakers[dialogue.get('speaker', 'unknown')] += 1
        
        return {
            "total_dialogues": len(dialogue_db.dialogues),
            "intents": dict(intents),
            "speakers": dict(speakers),
            "loaded": dialogue_db.loaded
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/proverb-stats")
async def get_proverb_stats():
    """Get statistics about loaded Tunisian proverbs"""
    try:
        prompts = defaultdict(int)
        
        for proverb in proverb_db.proverbs:
            prompt = proverb.get('prompt', 'unknown')
            prompts[prompt] += 1
        
        return {
            "total_proverbs": len(proverb_db.proverbs),
            "categories": dict(prompts),
            "loaded": proverb_db.loaded,
            "image_associations": len(proverb_db.image_associations)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/random-proverb")
async def get_random_proverb():
    """Get a random Tunisian proverb for daily inspiration"""
    try:
        if not proverb_db.proverbs:
            return {"error": "No proverbs loaded"}
        
        import random
        proverb = random.choice(proverb_db.proverbs)
        
        return {
            "proverb": proverb.get('text', ''),
            "category": proverb.get('prompt', ''),
            "timestamp": datetime.now().isoformat(),
            "has_image": proverb.get('text', '') in proverb_db.image_associations
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/proverbs-by-emotion/{emotion}")
async def get_proverbs_by_emotion(emotion: str):
    """Get proverbs relevant to specific emotion"""
    try:
        emotion_prompts = {
            'happy': ['Happiness', 'Contentment', 'Friendship'],
            'sad': ['Patience', 'Hope', 'Happiness'],
            'angry': ['Patience', 'Peace', 'Wisdom'],
            'confused': ['Knowledge', 'Wisdom', 'Understanding'],
            'excited': ['Innovation', 'Hope', 'Success'],
            'tired': ['Rest', 'Health', 'Balance'],
            'nervous': ['Courage', 'Hope', 'Trust'],
            'grateful': ['Gratitude', 'Contentment', 'Blessings']
        }
        
        prompts = emotion_prompts.get(emotion, [])
        matching_proverbs = [p for p in proverb_db.proverbs if p.get('prompt') in prompts]
        
        return {
            "emotion": emotion,
            "count": len(matching_proverbs),
            "proverbs": matching_proverbs[:5],
            "total_available": len(proverb_db.proverbs)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
