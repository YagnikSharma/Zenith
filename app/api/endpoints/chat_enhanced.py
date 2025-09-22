"""Enhanced chat endpoint with Zenith persona and wellness guidance"""

from fastapi import APIRouter, HTTPException, Depends
from typing import List, Dict, Optional
from pydantic import BaseModel
import logging
import json
import os
from pathlib import Path
from app.services.ai_service import AIService
from app.services.firebase_service import FirebaseService
from app.api.dependencies import get_current_user

router = APIRouter()
logger = logging.getLogger(__name__)

# Initialize services
ai_service = AIService()
firebase_service = FirebaseService()

# Load training data
training_data_path = Path(__file__).parent.parent.parent / "data" / "zenith_training_data.json"
try:
    with open(training_data_path, 'r', encoding='utf-8') as f:
        TRAINING_DATA = json.load(f)
        TRAINING_EXAMPLES = {ex['user_input'].lower(): ex['guide_response'] 
                           for ex in TRAINING_DATA['training_examples']}
except Exception as e:
    logger.warning(f"Could not load training data: {e}")
    TRAINING_EXAMPLES = {}

class ChatMessage(BaseModel):
    message: str
    language: str = 'en'
    context: Optional[List[Dict]] = None

class ChatResponse(BaseModel):
    response: str
    original_response: Optional[str] = None
    language: str
    is_crisis: bool = False
    crisis_resources: Optional[List[Dict]] = None
    wellness_guidance: Optional[Dict] = None
    suggested_actions: Optional[List[str]] = None

# Zenith's refined personality based on training examples
ZENITH_PERSONA = """
You are Zenith, a compassionate mental wellness guide and companion.

CORE IDENTITY:
- You are warm, nurturing, and genuinely caring
- You speak with a supportive, encouraging, and direct tone
- You validate emotions before offering guidance
- You seamlessly integrate wellness tools into conversation

COMMUNICATION STYLE:
- Use conversational language, not clinical or robotic
- Be direct yet gentle
- Use "I" statements to show personal engagement ("I hear you", "I understand")
- Include emojis occasionally for warmth (but not excessively)

WELLNESS GUIDANCE PROTOCOL:
When someone expresses distress, stress, or asks for help:

1. VALIDATE THE FEELING
   Examples:
   - "I hear you, and that sounds incredibly challenging."
   - "Thank you for sharing this with me. It takes courage."
   - "Your feelings are completely valid."

2. OFFER ONE UPLIFTING QUOTE
   Keep it short, relevant, and impactful. Examples:
   - "Remember: 'Even the darkest night will end, and the sun will rise.'"
   - "As the saying goes: 'This too shall pass.'"

3. GUIDE A SIMPLE BREATHING EXERCISE
   Provide step-by-step guidance within the chat:
   "Let's take a moment together right now. Find a comfortable position...
   - Breathe in slowly through your nose for 4 counts...
   - Hold gently for 4 counts...
   - Release through your mouth for 4 counts...
   Let's do this together two more times."

4. REFERENCE APP FEATURES NATURALLY
   - "If you'd like more guided exercises, our Meditation section has wonderful resources."
   - "The Spiritual Wisdom section has daily affirmations that many find helpful."
   - "Would you like to explore our Community section to connect with others?"

5. OFFER ALTERNATIVES & ESCALATION
   - First alternative: Suggest mood tracking or journaling
   - Second alternative: Recommend the mentorship/community section
   - If severe: Gently suggest crisis resources with care

REMEMBER:
- Never diagnose or provide medical advice
- Always prioritize safety
- Be authentic and genuinely caring
- Your goal is to be a supportive companion, not a therapist
"""

# Mood uplift quotes database
UPLIFT_QUOTES = [
    "Even the darkest night will end, and the sun will rise.",
    "You are stronger than you know, braver than you feel.",
    "Every storm runs out of rain.",
    "This too shall pass.",
    "You've survived 100% of your worst days.",
    "Healing is not linear, and that's okay.",
    "Small steps still move you forward.",
    "Your feelings are valid, and so is your strength.",
    "Tomorrow is a new canvas to paint upon.",
    "You matter, and your story isn't over yet."
]

# Breathing exercises
BREATHING_EXERCISES = {
    "quick_calm": {
        "name": "Quick Calm",
        "steps": [
            "Find a comfortable position and relax your shoulders",
            "Breathe in slowly through your nose for 4 counts",
            "Hold your breath gently for 4 counts",
            "Exhale slowly through your mouth for 4 counts",
            "Repeat 3 times"
        ]
    },
    "stress_relief": {
        "name": "Stress Relief Breathing",
        "steps": [
            "Place one hand on your chest, one on your belly",
            "Take a deep breath through your nose, feeling your belly expand",
            "Hold for 2 counts",
            "Exhale slowly, feeling your belly fall",
            "Continue for 5 breaths"
        ]
    }
}

def detect_mood_keywords(message: str) -> bool:
    """Detect if user needs mood uplift guidance"""
    mood_keywords = [
        'stressed', 'anxious', 'down', 'sad', 'depressed', 'upset', 
        'worried', 'overwhelmed', 'help', 'struggling', 'tired',
        'scared', 'lonely', 'lost', 'frustrated', 'angry', 'hopeless',
        'can\'t', 'difficult', 'hard', 'pain', 'hurt', 'crying'
    ]
    message_lower = message.lower()
    return any(keyword in message_lower for keyword in mood_keywords)

def generate_wellness_guidance(needs_support: bool) -> Dict:
    """Generate contextual wellness guidance"""
    if not needs_support:
        return None
    
    import random
    quote = random.choice(UPLIFT_QUOTES)
    exercise = random.choice(list(BREATHING_EXERCISES.values()))
    
    return {
        "quote": quote,
        "breathing_exercise": exercise,
        "app_resources": [
            "Meditation section for guided sessions",
            "Spiritual Wisdom for daily affirmations",
            "Community to connect with others",
            "Mood tracking in your profile"
        ],
        "suggested_actions": [
            "Try the breathing exercise above",
            "Explore our Meditation section",
            "Read today's affirmations",
            "Connect with our community"
        ]
    }

def find_best_training_response(user_input: str) -> Optional[str]:
    """Find the best matching response from training data"""
    # First check for exact match
    user_input_lower = user_input.lower().strip()
    if user_input_lower in TRAINING_EXAMPLES:
        return TRAINING_EXAMPLES[user_input_lower]
    
    # Check for partial matches
    for trained_input, response in TRAINING_EXAMPLES.items():
        # Check if the core content matches (ignoring punctuation differences)
        if user_input_lower.replace('.', '').replace('?', '').replace('!', '') == \
           trained_input.replace('.', '').replace('?', '').replace('!', ''):
            return response
    
    # Check for keyword similarity
    user_words = set(user_input_lower.split())
    best_match = None
    best_score = 0
    
    for trained_input, response in TRAINING_EXAMPLES.items():
        trained_words = set(trained_input.split())
        common_words = user_words.intersection(trained_words)
        score = len(common_words) / max(len(user_words), 1)
        
        if score > best_score and score > 0.6:  # At least 60% word match
            best_score = score
            best_match = response
    
    return best_match

@router.post("/chat", response_model=ChatResponse)
async def enhanced_chat(
    request: ChatMessage,
    current_user: dict = Depends(get_current_user)
):
    """Enhanced chat endpoint with Zenith persona"""
    try:
        # First check if we have a trained response
        trained_response = find_best_training_response(request.message)
        
        if trained_response:
            # Use the trained response directly
            response_text = trained_response
            needs_support = detect_mood_keywords(request.message)
            wellness_guidance = generate_wellness_guidance(needs_support) if needs_support else None
        else:
            # Detect if user needs support
            needs_support = detect_mood_keywords(request.message)
            
            # Build enhanced prompt with Zenith persona and training examples
            system_prompt = ZENITH_PERSONA + "\n\nHere are some example responses that show your communication style:\n"
            
            # Add relevant training examples to the prompt
            import random
            relevant_examples = random.sample(list(TRAINING_EXAMPLES.items())[:20], min(5, len(TRAINING_EXAMPLES)))
            for input_ex, response_ex in relevant_examples:
                system_prompt += f"\nUser: {input_ex}\nZenith: {response_ex}\n"
            
            if needs_support:
                # Add specific guidance for support scenarios
                wellness_guidance = generate_wellness_guidance(True)
                
                enhanced_message = f"""
                {system_prompt}
                
                The user appears to need support. Their message: "{request.message}"
                
                Remember to:
                1. Validate their feelings first
                2. Sit with their emotions without rushing to fix
                3. Ask open-ended questions to explore
                4. Gently mention app resources only if appropriate
                
                Respond as Zenith with genuine care and presence.
                """
            else:
                enhanced_message = f"{system_prompt}\n\nUser message: {request.message}"
                wellness_guidance = None
            
            # Generate response with Zenith persona
            response_text = await ai_service.generate_chat_response(
                enhanced_message,
                request.context
            )
        
        # Check for crisis indicators
        crisis_check = await ai_service.detect_crisis(request.message)
        
        # Prepare crisis resources if needed
        crisis_resources = None
        if crisis_check['is_crisis']:
            crisis_resources = [
                {"name": "NIMHANS", "number": "080-46110007", "available": "24/7"},
                {"name": "Vandrevala Foundation", "number": "9999666555", "available": "24/7"},
                {"name": "AASRA", "number": "91-9820466726", "available": "24/7"}
            ]
            
            # Add crisis response to Zenith's message
            response_text += "\n\n💝 I want you to know that you don't have to go through this alone. "
            response_text += "If you need immediate support, these helplines have caring professionals ready to help:"
            for resource in crisis_resources[:2]:
                response_text += f"\n• {resource['name']}: {resource['number']} ({resource['available']})"
        
        # Translate response if needed
        if request.language != 'en':
            translated_response = await ai_service.translate_text(
                response_text, 
                request.language, 
                'en'
            )
        else:
            translated_response = response_text
        
        # Store conversation in Firebase (if user is authenticated)
        if current_user and current_user.get('uid'):
            conversation_data = {
                'user_id': current_user['uid'],
                'message': request.message,
                'response': response_text,
                'language': request.language,
                'is_crisis': crisis_check['is_crisis'],
                'needs_support': needs_support,
                'timestamp': firebase_service.SERVER_TIMESTAMP
            }
            
            firebase_service.db.collection('conversations').add(conversation_data)
        
        return ChatResponse(
            response=translated_response if request.language != 'en' else response_text,
            original_response=response_text if request.language != 'en' else None,
            language=request.language,
            is_crisis=crisis_check['is_crisis'],
            crisis_resources=crisis_resources,
            wellness_guidance=wellness_guidance,
            suggested_actions=wellness_guidance['suggested_actions'] if wellness_guidance else None
        )
        
    except Exception as e:
        logger.error(f"Chat error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/chat/feedback")
async def chat_feedback(
    message_id: str,
    helpful: bool,
    feedback: Optional[str] = None,
    current_user: dict = Depends(get_current_user)
):
    """Store feedback about chat responses"""
    try:
        feedback_data = {
            'user_id': current_user.get('uid') if current_user else 'anonymous',
            'message_id': message_id,
            'helpful': helpful,
            'feedback': feedback,
            'timestamp': firebase_service.SERVER_TIMESTAMP
        }
        
        firebase_service.db.collection('chat_feedback').add(feedback_data)
        
        return {"status": "success", "message": "Thank you for your feedback!"}
        
    except Exception as e:
        logger.error(f"Feedback error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/chat/suggestions")
async def get_suggestions():
    """Get conversation starter suggestions"""
    return {
        "suggestions": [
            "I'm feeling overwhelmed with work",
            "How can I manage my anxiety?",
            "I need help sleeping better",
            "I'm having relationship troubles",
            "Can you help me feel more positive?",
            "I want to practice mindfulness",
            "Tell me something uplifting",
            "Guide me through a breathing exercise"
        ]
    }