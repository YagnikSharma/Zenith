"""Google AI services wrapper for Gemini models and translation"""

import os
import logging
from typing import Optional, Dict, Any, List
import google.generativeai as genai
from google.cloud import translate_v2 as translate
from google.cloud import language_v1
from app.core.config import settings

logger = logging.getLogger(__name__)

class AIService:
    """Service for AI operations using Google's Gemini and other APIs"""
    
    def __init__(self):
        self._initialize_services()
    
    def _initialize_services(self):
        """Initialize Google AI services"""
        try:
            # Configure Gemini
            if settings.GOOGLE_API_KEY:
                genai.configure(api_key=settings.GOOGLE_API_KEY)
                
                # Initialize the custom fine-tuned model
                if settings.GEMINI_CUSTOM_MODEL_ID:
                    try:
                        self.chat_model = genai.GenerativeModel(settings.GEMINI_CUSTOM_MODEL_ID)
                    except:
                        # Fallback if custom model fails
                        self.chat_model = genai.GenerativeModel('gemini-1.5-flash')
                        logger.warning("Using gemini-1.5-flash as fallback")
                else:
                    # Fallback to base model if custom model not configured
                    self.chat_model = genai.GenerativeModel('gemini-1.5-flash')
                    logger.warning("Custom Gemini model ID not configured, using base gemini-1.5-flash")
                
                # Initialize crisis detection model
                self.crisis_model = genai.GenerativeModel('gemini-1.5-flash')
                
                logger.info("Gemini models initialized successfully")
            else:
                logger.warning("Google API key not configured")
                self.chat_model = None
                self.crisis_model = None
            
            # Initialize Translation client
            if settings.GOOGLE_APPLICATION_CREDENTIALS and os.path.exists(settings.GOOGLE_APPLICATION_CREDENTIALS):
                self.translate_client = translate.Client()
                logger.info("Translation service initialized")
            else:
                self.translate_client = None
                logger.warning("Translation service not configured")
            
            # Initialize Natural Language client
            if settings.GOOGLE_APPLICATION_CREDENTIALS and os.path.exists(settings.GOOGLE_APPLICATION_CREDENTIALS):
                self.language_client = language_v1.LanguageServiceClient()
                logger.info("Natural Language service initialized")
            else:
                self.language_client = None
                logger.warning("Natural Language service not configured")
                
        except Exception as e:
            logger.error(f"Error initializing AI services: {e}")
            self.chat_model = None
            self.crisis_model = None
            self.translate_client = None
            self.language_client = None
    
    async def generate_chat_response(self, message: str, context: List[Dict] = None) -> str:
        """Generate response using the fine-tuned Gemini model"""
        try:
            if not self.chat_model:
                return "I apologize, but the AI service is currently unavailable. Please try again later."
            
            # Build conversation history if context is provided
            prompt = message
            if context:
                conversation = "\n".join([
                    f"User: {msg['user']}\nAssistant: {msg['assistant']}" 
                    for msg in context[-5:]  # Last 5 messages for context
                ])
                prompt = f"Previous conversation:\n{conversation}\n\nUser: {message}\nAssistant:"
            
            # Generate response
            response = self.chat_model.generate_content(prompt)
            
            if response and response.text:
                return response.text
            else:
                return "I'm here to help. Could you please rephrase your question?"
                
        except Exception as e:
            logger.error(f"Error generating chat response: {e}")
            return "I apologize for the inconvenience. There was an error processing your message. Please try again."
    
    async def detect_crisis(self, message: str) -> Dict[str, Any]:
        """Detect if the message indicates a crisis situation"""
        try:
            # First check for explicit crisis keywords
            message_lower = message.lower()
            for keyword in settings.CRISIS_KEYWORDS:
                if keyword in message_lower:
                    return {
                        "is_crisis": True,
                        "confidence": 0.95,
                        "type": "explicit_keyword",
                        "recommended_action": "immediate_support"
                    }
            
            # Use AI model for more nuanced detection
            if self.crisis_model:
                prompt = f"""Analyze the following message for signs of mental health crisis or suicidal ideation.
                Respond with JSON format: {{"is_crisis": boolean, "confidence": float (0-1), "indicators": list}}
                
                Message: {message}
                """
                
                response = self.crisis_model.generate_content(prompt)
                
                if response and response.text:
                    try:
                        # Parse the response as JSON-like structure
                        result_text = response.text.strip()
                        # Simple parsing (in production, use proper JSON parsing)
                        is_crisis = "\"is_crisis\": true" in result_text.lower()
                        
                        return {
                            "is_crisis": is_crisis,
                            "confidence": 0.8 if is_crisis else 0.2,
                            "type": "ai_detection",
                            "recommended_action": "immediate_support" if is_crisis else "monitor"
                        }
                    except:
                        pass
            
            return {
                "is_crisis": False,
                "confidence": 0.1,
                "type": "no_indicators",
                "recommended_action": "continue_conversation"
            }
            
        except Exception as e:
            logger.error(f"Error in crisis detection: {e}")
            # Err on the side of caution
            return {
                "is_crisis": False,
                "confidence": 0.0,
                "type": "error",
                "recommended_action": "monitor"
            }
    
    async def translate_text(self, text: str, target_language: str, source_language: str = None) -> str:
        """Translate text to target language"""
        try:
            if not self.translate_client:
                logger.warning("Translation service not available")
                return text
            
            # Validate target language
            if target_language not in settings.SUPPORTED_LANGUAGES:
                logger.warning(f"Unsupported target language: {target_language}")
                return text
            
            # Don't translate if already in target language
            if source_language == target_language:
                return text
            
            # Perform translation
            result = self.translate_client.translate(
                text,
                target_language=target_language,
                source_language=source_language
            )
            
            return result['translatedText']
            
        except Exception as e:
            logger.error(f"Error translating text: {e}")
            return text  # Return original text if translation fails
    
    async def detect_language(self, text: str) -> str:
        """Detect the language of the text"""
        try:
            if not self.translate_client:
                return "en"  # Default to English
            
            result = self.translate_client.detect_language(text)
            
            if result and result['language']:
                detected_lang = result['language']
                # Return only if it's a supported language
                if detected_lang in settings.SUPPORTED_LANGUAGES:
                    return detected_lang
            
            return "en"  # Default to English
            
        except Exception as e:
            logger.error(f"Error detecting language: {e}")
            return "en"
    
    async def analyze_sentiment(self, text: str) -> Dict[str, Any]:
        """Analyze sentiment of the text"""
        try:
            if not self.language_client:
                return {
                    "sentiment": "neutral",
                    "score": 0.0,
                    "magnitude": 0.0
                }
            
            document = language_v1.Document(
                content=text,
                type_=language_v1.Document.Type.PLAIN_TEXT,
            )
            
            # Analyze sentiment
            sentiment = self.language_client.analyze_sentiment(
                request={'document': document}
            ).document_sentiment
            
            # Categorize sentiment
            if sentiment.score < -0.25:
                category = "negative"
            elif sentiment.score > 0.25:
                category = "positive"
            else:
                category = "neutral"
            
            return {
                "sentiment": category,
                "score": sentiment.score,
                "magnitude": sentiment.magnitude
            }
            
        except Exception as e:
            logger.error(f"Error analyzing sentiment: {e}")
            return {
                "sentiment": "neutral",
                "score": 0.0,
                "magnitude": 0.0
            }
    
    async def generate_meditation_script(self, duration_minutes: int = 5, focus: str = "general") -> str:
        """Generate a personalized meditation script"""
        try:
            if not self.chat_model:
                return self._get_default_meditation_script(duration_minutes)
            
            prompt = f"""Create a {duration_minutes}-minute guided meditation script focused on {focus}.
            Include:
            - Opening breathing exercise
            - Body relaxation
            - Visualization or mindfulness practice
            - Closing affirmations
            
            Make it suitable for young adults dealing with stress and anxiety.
            Format it as a script that can be read aloud."""
            
            response = self.chat_model.generate_content(prompt)
            
            if response and response.text:
                return response.text
            else:
                return self._get_default_meditation_script(duration_minutes)
                
        except Exception as e:
            logger.error(f"Error generating meditation script: {e}")
            return self._get_default_meditation_script(duration_minutes)
    
    def _get_default_meditation_script(self, duration_minutes: int) -> str:
        """Get a default meditation script"""
        return f"""Welcome to this {duration_minutes}-minute meditation session.
        
Find a comfortable position and gently close your eyes.
        
Begin by taking three deep breaths:
- Breathe in slowly through your nose... hold... and exhale through your mouth.
- Again, breathe in... hold... and release.
- One more time, deep breath in... and let it all go.

Now, let your breathing return to its natural rhythm.

Notice how your body feels right now. Starting from the top of your head, 
slowly scan down through your body, releasing any tension you find.

Your forehead... your jaw... your shoulders... let them all soften.

Continue breathing naturally, knowing that in this moment, you are safe and at peace.

[Continue for {duration_minutes} minutes with gentle guidance]

When you're ready, slowly bring your awareness back to the room.
Wiggle your fingers and toes.
Take a deep breath and open your eyes.

Thank you for taking this time for yourself."""
    
    async def generate_spiritual_wisdom(self, tradition: str = "universal") -> str:
        """Generate spiritual wisdom or quotes"""
        try:
            if not self.chat_model:
                return self._get_default_spiritual_quote()
            
            prompt = f"""Provide an inspiring spiritual quote or wisdom from {tradition} tradition 
            that would help a young person dealing with life challenges. 
            Include the source if applicable and a brief reflection on how to apply this wisdom."""
            
            response = self.chat_model.generate_content(prompt)
            
            if response and response.text:
                return response.text
            else:
                return self._get_default_spiritual_quote()
                
        except Exception as e:
            logger.error(f"Error generating spiritual wisdom: {e}")
            return self._get_default_spiritual_quote()
    
    def _get_default_spiritual_quote(self) -> str:
        """Get a default spiritual quote"""
        return """\"The best way to find yourself is to lose yourself in the service of others.\" 
        - Mahatma Gandhi

This timeless wisdom reminds us that when we focus on helping others, 
we often discover our own strength and purpose. In moments of difficulty, 
reaching out to support someone else can bring unexpected healing to our own hearts."""

# Create singleton instance
ai_service = AIService()