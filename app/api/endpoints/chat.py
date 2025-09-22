"""AI Chat endpoint with multilingual support"""

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Dict, Any, List, Optional
from app.services.ai_service import ai_service
from app.services.firebase_service import firebase_service
from app.core.auth import get_current_user, get_optional_user
from datetime import datetime
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

class ChatMessage(BaseModel):
    """Chat message model"""
    message: str
    language: Optional[str] = "en"

class ChatResponse(BaseModel):
    """Chat response model"""
    response: str
    original_language: str
    detected_language: Optional[str] = None
    sentiment: Optional[Dict[str, Any]] = None
    session_id: Optional[str] = None

class ChatHistory(BaseModel):
    """Chat history model"""
    messages: List[Dict[str, Any]]
    total_count: int

@router.post("/message", response_model=ChatResponse)
async def send_message(
    chat_message: ChatMessage,
    current_user: Optional[Dict[str, Any]] = Depends(get_optional_user)
):
    """Send a message to the AI chat companion"""
    try:
        # Get user's preferred language
        user_language = chat_message.language
        if current_user:
            user_doc = await firebase_service.get_document("users", current_user["uid"])
            if user_doc and user_doc.get("preferred_language"):
                user_language = user_doc["preferred_language"]
        
        # Detect language of the message
        detected_language = await ai_service.detect_language(chat_message.message)
        
        # Translate to English if needed (for AI processing)
        message_for_ai = chat_message.message
        if detected_language != "en":
            message_for_ai = await ai_service.translate_text(
                chat_message.message,
                target_language="en",
                source_language=detected_language
            )
        
        # Get conversation context if user is authenticated
        context = []
        if current_user:
            # Fetch last few messages from chat history
            chat_history = await firebase_service.query_collection(
                "chat_messages",
                filters={"user_id": current_user["uid"]},
                limit=10
            )
            
            # Format context for AI
            for msg in chat_history[-5:]:  # Last 5 messages
                context.append({
                    "user": msg.get("user_message"),
                    "assistant": msg.get("ai_response")
                })
        
        # Generate AI response
        ai_response = await ai_service.generate_chat_response(message_for_ai, context)
        
        # Translate response back to user's language if needed
        final_response = ai_response
        if user_language != "en":
            final_response = await ai_service.translate_text(
                ai_response,
                target_language=user_language,
                source_language="en"
            )
        
        # Analyze sentiment
        sentiment = await ai_service.analyze_sentiment(chat_message.message)
        
        # Save chat message if user is authenticated
        session_id = None
        if current_user:
            session_id = f"session_{current_user['uid']}_{datetime.utcnow().isoformat()}"
            await firebase_service.save_document(
                "chat_messages",
                session_id,
                {
                    "user_id": current_user["uid"],
                    "user_message": chat_message.message,
                    "ai_response": final_response,
                    "detected_language": detected_language,
                    "user_language": user_language,
                    "sentiment": sentiment,
                    "timestamp": datetime.utcnow().isoformat()
                }
            )
        
        return ChatResponse(
            response=final_response,
            original_language=user_language,
            detected_language=detected_language,
            sentiment=sentiment,
            session_id=session_id
        )
        
    except Exception as e:
        logger.error(f"Chat error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to process chat message"
        )

@router.get("/history", response_model=ChatHistory)
async def get_chat_history(
    limit: int = 50,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Get chat history for the current user"""
    try:
        # Fetch chat messages from Firestore
        messages = await firebase_service.query_collection(
            "chat_messages",
            filters={"user_id": current_user["uid"]},
            limit=limit
        )
        
        # Sort by timestamp
        messages.sort(key=lambda x: x.get("timestamp", ""), reverse=True)
        
        return ChatHistory(
            messages=messages,
            total_count=len(messages)
        )
        
    except Exception as e:
        logger.error(f"Error fetching chat history: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch chat history"
        )

@router.delete("/history/{session_id}")
async def delete_chat_message(
    session_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Delete a specific chat message"""
    try:
        # Verify the message belongs to the user
        message = await firebase_service.get_document("chat_messages", session_id)
        
        if not message or message.get("user_id") != current_user["uid"]:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Message not found"
            )
        
        # Delete the message
        await firebase_service.delete_document("chat_messages", session_id)
        
        return {"message": "Chat message deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting chat message: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete chat message"
        )

@router.delete("/history")
async def clear_chat_history(
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Clear all chat history for the current user"""
    try:
        # Fetch all user's messages
        messages = await firebase_service.query_collection(
            "chat_messages",
            filters={"user_id": current_user["uid"]},
            limit=1000  # Set a reasonable limit
        )
        
        # Delete each message
        for message in messages:
            await firebase_service.delete_document("chat_messages", message["id"])
        
        return {
            "message": "Chat history cleared successfully",
            "deleted_count": len(messages)
        }
        
    except Exception as e:
        logger.error(f"Error clearing chat history: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to clear chat history"
        )