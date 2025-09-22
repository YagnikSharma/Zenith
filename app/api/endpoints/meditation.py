"""Meditation and mindfulness endpoint"""

from fastapi import APIRouter, HTTPException, Depends, Query
from pydantic import BaseModel
from typing import Dict, Any, List, Optional
from app.services.ai_service import ai_service
from app.services.firebase_service import firebase_service
from app.core.auth import get_optional_user, get_current_user
from datetime import datetime
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

class MeditationScriptRequest(BaseModel):
    """Request for meditation script"""
    duration: int = 5  # minutes
    focus: str = "general"
    language: Optional[str] = "en"

class MeditationScriptResponse(BaseModel):
    """Meditation script response"""
    script: str
    duration: int
    focus: str
    audio_url: Optional[str] = None

class MeditationSessionLog(BaseModel):
    """Log a meditation session"""
    duration: int  # minutes
    type: str
    mood_before: Optional[int] = None  # 1-10 scale
    mood_after: Optional[int] = None  # 1-10 scale
    notes: Optional[str] = None

@router.post("/script", response_model=MeditationScriptResponse)
async def generate_meditation_script(
    request: MeditationScriptRequest,
    current_user: Optional[Dict[str, Any]] = Depends(get_optional_user)
):
    """Generate a personalized meditation script"""
    try:
        # Generate meditation script
        script = await ai_service.generate_meditation_script(
            duration_minutes=request.duration,
            focus=request.focus
        )
        
        # Translate if needed
        if request.language != "en":
            script = await ai_service.translate_text(
                script,
                target_language=request.language,
                source_language="en"
            )
        
        # Save to user's history if authenticated
        if current_user:
            await firebase_service.save_document(
                "meditation_history",
                f"script_{current_user['uid']}_{datetime.utcnow().isoformat()}",
                {
                    "user_id": current_user["uid"],
                    "script": script,
                    "duration": request.duration,
                    "focus": request.focus,
                    "language": request.language,
                    "timestamp": datetime.utcnow().isoformat()
                }
            )
        
        return MeditationScriptResponse(
            script=script,
            duration=request.duration,
            focus=request.focus,
            audio_url=None  # TODO: Generate audio using TTS
        )
        
    except Exception as e:
        logger.error(f"Error generating meditation script: {e}")
        # Return default script on error
        return MeditationScriptResponse(
            script=ai_service._get_default_meditation_script(request.duration),
            duration=request.duration,
            focus=request.focus
        )

@router.get("/breathing")
async def get_breathing_exercise(
    type: str = Query(default="4-7-8", description="Type of breathing exercise")
):
    """Get guided breathing exercises"""
    exercises = {
        "4-7-8": {
            "name": "4-7-8 Breathing",
            "description": "Calming breath technique for anxiety and sleep",
            "instructions": [
                "Exhale completely through your mouth",
                "Close your mouth and inhale through your nose for 4 counts",
                "Hold your breath for 7 counts",
                "Exhale completely through your mouth for 8 counts",
                "Repeat 3-4 times"
            ],
            "benefits": ["Reduces anxiety", "Improves sleep", "Manages cravings"],
            "duration": "2-3 minutes"
        },
        "box": {
            "name": "Box Breathing",
            "description": "Square breathing technique used by Navy SEALs",
            "instructions": [
                "Inhale for 4 counts",
                "Hold for 4 counts",
                "Exhale for 4 counts",
                "Hold empty for 4 counts",
                "Repeat 4-5 times"
            ],
            "benefits": ["Reduces stress", "Improves focus", "Regulates emotions"],
            "duration": "3-5 minutes"
        },
        "belly": {
            "name": "Diaphragmatic Breathing",
            "description": "Deep belly breathing for relaxation",
            "instructions": [
                "Place one hand on chest, one on belly",
                "Inhale slowly through nose, expanding belly",
                "Exhale slowly through mouth, contracting belly",
                "Chest should remain relatively still",
                "Continue for 5-10 breaths"
            ],
            "benefits": ["Activates relaxation response", "Lowers blood pressure", "Improves core stability"],
            "duration": "5-10 minutes"
        },
        "alternate": {
            "name": "Alternate Nostril Breathing",
            "description": "Yogic breathing technique (Nadi Shodhana)",
            "instructions": [
                "Use right thumb to close right nostril",
                "Inhale through left nostril",
                "Close left nostril with ring finger",
                "Open right nostril and exhale",
                "Inhale through right, switch, exhale through left",
                "Continue alternating for 5-10 rounds"
            ],
            "benefits": ["Balances nervous system", "Improves focus", "Reduces anxiety"],
            "duration": "5-10 minutes"
        }
    }
    
    exercise = exercises.get(type, exercises["4-7-8"])
    
    return {
        "exercise": exercise,
        "tip": "Practice in a quiet, comfortable place. Stop if you feel dizzy."
    }

@router.get("/guided")
async def get_guided_meditations():
    """Get list of guided meditation options"""
    meditations = [
        {
            "id": "body-scan",
            "name": "Body Scan Meditation",
            "description": "Progressive relaxation through body awareness",
            "duration": 15,
            "difficulty": "beginner",
            "benefits": ["Reduces tension", "Improves body awareness", "Promotes relaxation"]
        },
        {
            "id": "loving-kindness",
            "name": "Loving-Kindness Meditation",
            "description": "Cultivate compassion for self and others",
            "duration": 20,
            "difficulty": "intermediate",
            "benefits": ["Increases empathy", "Reduces negative emotions", "Improves relationships"]
        },
        {
            "id": "mindfulness",
            "name": "Mindfulness of Breath",
            "description": "Focus on the breath to anchor in the present",
            "duration": 10,
            "difficulty": "beginner",
            "benefits": ["Improves focus", "Reduces anxiety", "Increases awareness"]
        },
        {
            "id": "sleep",
            "name": "Sleep Meditation",
            "description": "Gentle meditation to prepare for restful sleep",
            "duration": 25,
            "difficulty": "beginner",
            "benefits": ["Improves sleep quality", "Reduces insomnia", "Calms racing thoughts"]
        },
        {
            "id": "anxiety-relief",
            "name": "Anxiety Relief Meditation",
            "description": "Specific techniques to manage anxiety",
            "duration": 12,
            "difficulty": "beginner",
            "benefits": ["Reduces anxiety", "Calms nervous system", "Improves emotional regulation"]
        },
        {
            "id": "focus",
            "name": "Concentration Meditation",
            "description": "Train the mind to maintain focus",
            "duration": 15,
            "difficulty": "intermediate",
            "benefits": ["Improves concentration", "Enhances productivity", "Strengthens mental discipline"]
        }
    ]
    
    return {
        "meditations": meditations,
        "recommendation": "Start with shorter sessions and gradually increase duration as you build your practice."
    }

@router.get("/music")
async def get_meditation_music():
    """Get therapeutic music recommendations"""
    music_tracks = [
        {
            "title": "Ocean Waves",
            "type": "nature",
            "duration": "30 minutes",
            "description": "Calming ocean sounds for deep relaxation",
            "url": "/static/music/ocean-waves.mp3"  # Placeholder
        },
        {
            "title": "Tibetan Singing Bowls",
            "type": "instrumental",
            "duration": "20 minutes",
            "description": "Traditional healing sounds for meditation",
            "url": "/static/music/singing-bowls.mp3"  # Placeholder
        },
        {
            "title": "Rain Forest",
            "type": "nature",
            "duration": "45 minutes",
            "description": "Peaceful rain and forest sounds",
            "url": "/static/music/rain-forest.mp3"  # Placeholder
        },
        {
            "title": "432 Hz Healing",
            "type": "frequency",
            "duration": "15 minutes",
            "description": "Healing frequency music for balance",
            "url": "/static/music/432hz.mp3"  # Placeholder
        },
        {
            "title": "Indian Classical - Raag Yaman",
            "type": "classical",
            "duration": "25 minutes",
            "description": "Evening raag for peace and tranquility",
            "url": "/static/music/raag-yaman.mp3"  # Placeholder
        }
    ]
    
    return {
        "tracks": music_tracks,
        "message": "AI-generated therapeutic music coming soon with Lyria integration"
    }

@router.post("/log")
async def log_meditation_session(
    session: MeditationSessionLog,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Log a completed meditation session"""
    try:
        # Calculate mood improvement
        mood_improvement = None
        if session.mood_before and session.mood_after:
            mood_improvement = session.mood_after - session.mood_before
        
        # Save session log
        session_id = f"session_{current_user['uid']}_{datetime.utcnow().isoformat()}"
        await firebase_service.save_document(
            "meditation_sessions",
            session_id,
            {
                "user_id": current_user["uid"],
                "duration": session.duration,
                "type": session.type,
                "mood_before": session.mood_before,
                "mood_after": session.mood_after,
                "mood_improvement": mood_improvement,
                "notes": session.notes,
                "timestamp": datetime.utcnow().isoformat()
            }
        )
        
        # Update user statistics
        user_stats = await firebase_service.get_document("user_stats", current_user["uid"])
        if not user_stats:
            user_stats = {
                "total_sessions": 0,
                "total_minutes": 0,
                "streak_days": 0,
                "last_session": None
            }
        
        user_stats["total_sessions"] = user_stats.get("total_sessions", 0) + 1
        user_stats["total_minutes"] = user_stats.get("total_minutes", 0) + session.duration
        user_stats["last_session"] = datetime.utcnow().isoformat()
        
        # Calculate streak (simplified)
        if user_stats.get("last_session"):
            last_date = datetime.fromisoformat(user_stats["last_session"]).date()
            today = datetime.utcnow().date()
            if (today - last_date).days <= 1:
                user_stats["streak_days"] = user_stats.get("streak_days", 0) + 1
            else:
                user_stats["streak_days"] = 1
        else:
            user_stats["streak_days"] = 1
        
        await firebase_service.save_document("user_stats", current_user["uid"], user_stats)
        
        return {
            "message": "Session logged successfully",
            "session_id": session_id,
            "stats": {
                "total_sessions": user_stats["total_sessions"],
                "total_minutes": user_stats["total_minutes"],
                "streak_days": user_stats["streak_days"],
                "mood_improvement": mood_improvement
            }
        }
        
    except Exception as e:
        logger.error(f"Error logging meditation session: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to log meditation session"
        )

@router.get("/stats")
async def get_meditation_stats(
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Get user's meditation statistics"""
    try:
        # Get user stats
        user_stats = await firebase_service.get_document("user_stats", current_user["uid"])
        
        if not user_stats:
            return {
                "total_sessions": 0,
                "total_minutes": 0,
                "streak_days": 0,
                "average_session_length": 0,
                "favorite_type": None,
                "mood_improvement_average": 0
            }
        
        # Get recent sessions for additional stats
        recent_sessions = await firebase_service.query_collection(
            "meditation_sessions",
            filters={"user_id": current_user["uid"]},
            limit=30
        )
        
        # Calculate additional statistics
        avg_session_length = user_stats["total_minutes"] / user_stats["total_sessions"] if user_stats["total_sessions"] > 0 else 0
        
        # Find favorite type
        type_counts = {}
        mood_improvements = []
        for session in recent_sessions:
            session_type = session.get("type", "unknown")
            type_counts[session_type] = type_counts.get(session_type, 0) + 1
            if session.get("mood_improvement") is not None:
                mood_improvements.append(session["mood_improvement"])
        
        favorite_type = max(type_counts, key=type_counts.get) if type_counts else None
        avg_mood_improvement = sum(mood_improvements) / len(mood_improvements) if mood_improvements else 0
        
        return {
            "total_sessions": user_stats.get("total_sessions", 0),
            "total_minutes": user_stats.get("total_minutes", 0),
            "streak_days": user_stats.get("streak_days", 0),
            "average_session_length": round(avg_session_length, 1),
            "favorite_type": favorite_type,
            "mood_improvement_average": round(avg_mood_improvement, 1),
            "last_session": user_stats.get("last_session")
        }
        
    except Exception as e:
        logger.error(f"Error fetching meditation stats: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch meditation statistics"
        )

@router.get("/reminders")
async def get_meditation_reminders(
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Get or set meditation reminders"""
    try:
        # Get user's reminder preferences
        reminders = await firebase_service.get_document("meditation_reminders", current_user["uid"])
        
        if not reminders:
            # Default reminders
            reminders = {
                "enabled": False,
                "times": ["08:00", "20:00"],
                "days": ["mon", "tue", "wed", "thu", "fri", "sat", "sun"],
                "message": "Time for your daily meditation practice 🧘"
            }
        
        return reminders
        
    except Exception as e:
        logger.error(f"Error fetching reminders: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch meditation reminders"
        )