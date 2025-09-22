"""Spiritual wisdom and guidance endpoint"""

from fastapi import APIRouter, HTTPException, Depends, Query
from pydantic import BaseModel
from typing import Dict, Any, List, Optional
from app.services.ai_service import ai_service
from app.services.firebase_service import firebase_service
from app.core.auth import get_optional_user
from datetime import datetime
import logging
import random

logger = logging.getLogger(__name__)
router = APIRouter()

class SpiritualQuoteResponse(BaseModel):
    """Spiritual quote response model"""
    quote: str
    source: Optional[str]
    tradition: Optional[str]
    reflection: Optional[str]

class SpiritualGuidanceRequest(BaseModel):
    """Request for spiritual guidance"""
    concern: str
    tradition: Optional[str] = "universal"

class SpiritualGuidanceResponse(BaseModel):
    """Spiritual guidance response model"""
    guidance: str
    tradition: str
    practices: List[str]

@router.get("/quote", response_model=SpiritualQuoteResponse)
async def get_spiritual_quote(
    tradition: Optional[str] = Query(default="universal", description="Spiritual tradition"),
    current_user: Optional[Dict[str, Any]] = Depends(get_optional_user)
):
    """Get a daily spiritual quote or wisdom"""
    try:
        # Generate spiritual wisdom
        wisdom = await ai_service.generate_spiritual_wisdom(tradition)
        
        # Parse the response (simple parsing for now)
        lines = wisdom.split('\n')
        quote = lines[0] if lines else "Peace begins with a smile."
        source = None
        reflection = None
        
        # Try to extract source and reflection
        for line in lines:
            if '-' in line and not source:
                source = line.strip('- ')
            elif line and not quote.startswith(line) and not reflection:
                reflection = line
        
        # Save to user's history if authenticated
        if current_user:
            await firebase_service.save_document(
                "spiritual_history",
                f"quote_{current_user['uid']}_{datetime.utcnow().isoformat()}",
                {
                    "user_id": current_user["uid"],
                    "quote": quote,
                    "source": source,
                    "tradition": tradition,
                    "timestamp": datetime.utcnow().isoformat()
                }
            )
        
        return SpiritualQuoteResponse(
            quote=quote,
            source=source,
            tradition=tradition,
            reflection=reflection
        )
        
    except Exception as e:
        logger.error(f"Error getting spiritual quote: {e}")
        # Return a default quote on error
        return SpiritualQuoteResponse(
            quote="In the midst of movement and chaos, keep stillness inside of you.",
            source="Deepak Chopra",
            tradition="universal",
            reflection="Find your inner peace amidst life's challenges."
        )

@router.post("/guidance", response_model=SpiritualGuidanceResponse)
async def get_spiritual_guidance(
    request: SpiritualGuidanceRequest,
    current_user: Optional[Dict[str, Any]] = Depends(get_optional_user)
):
    """Get personalized spiritual guidance"""
    try:
        # Generate guidance using AI
        prompt = f"""Provide spiritual guidance for someone dealing with: {request.concern}
        From the {request.tradition} tradition perspective.
        Include practical spiritual practices they can follow."""
        
        if ai_service.chat_model:
            response = ai_service.chat_model.generate_content(prompt)
            guidance = response.text if response else "Seek wisdom within yourself."
        else:
            guidance = "Take time for quiet reflection and meditation on your concern."
        
        # Extract practices (simple extraction)
        practices = [
            "Daily meditation",
            "Gratitude journaling",
            "Mindful breathing",
            "Prayer or contemplation",
            "Acts of service"
        ]
        
        # Save guidance request if user is authenticated
        if current_user:
            await firebase_service.save_document(
                "spiritual_guidance",
                f"guidance_{current_user['uid']}_{datetime.utcnow().isoformat()}",
                {
                    "user_id": current_user["uid"],
                    "concern": request.concern,
                    "tradition": request.tradition,
                    "guidance": guidance,
                    "timestamp": datetime.utcnow().isoformat()
                }
            )
        
        return SpiritualGuidanceResponse(
            guidance=guidance,
            tradition=request.tradition,
            practices=practices[:3]  # Return top 3 practices
        )
        
    except Exception as e:
        logger.error(f"Error getting spiritual guidance: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate spiritual guidance"
        )

@router.get("/scriptures")
async def get_scripture_references(
    topic: str = Query(..., description="Topic to find scriptures about"),
    tradition: Optional[str] = Query(default="all", description="Religious tradition")
):
    """Get scripture references for a topic"""
    try:
        scriptures = {
            "bhagavad_gita": [
                {
                    "verse": "2.47",
                    "text": "You have the right to perform your prescribed duty, but you are not entitled to the fruits of action.",
                    "topic": ["duty", "detachment", "karma"]
                },
                {
                    "verse": "6.5",
                    "text": "One must elevate, not degrade, oneself with one's own mind.",
                    "topic": ["self-improvement", "mind", "discipline"]
                }
            ],
            "bible": [
                {
                    "verse": "Philippians 4:13",
                    "text": "I can do all things through Christ who strengthens me.",
                    "topic": ["strength", "faith", "perseverance"]
                },
                {
                    "verse": "Psalm 23:4",
                    "text": "Even though I walk through the valley of the shadow of death, I will fear no evil.",
                    "topic": ["courage", "faith", "protection"]
                }
            ],
            "quran": [
                {
                    "verse": "2:286",
                    "text": "Allah does not burden a soul beyond that it can bear.",
                    "topic": ["strength", "trials", "faith"]
                },
                {
                    "verse": "94:5-6",
                    "text": "Indeed, with hardship comes ease.",
                    "topic": ["hope", "perseverance", "patience"]
                }
            ],
            "buddhist": [
                {
                    "text": "Thousands of candles can be lighted from a single candle, and the life of the candle will not be shortened. Happiness never decreases by being shared.",
                    "source": "Buddha",
                    "topic": ["happiness", "sharing", "compassion"]
                },
                {
                    "text": "Peace comes from within. Do not seek it without.",
                    "source": "Buddha",
                    "topic": ["peace", "inner-peace", "mindfulness"]
                }
            ]
        }
        
        # Filter by topic
        relevant_scriptures = []
        topic_lower = topic.lower()
        
        for trad, verses in scriptures.items():
            if tradition == "all" or tradition.lower() in trad:
                for verse in verses:
                    if any(t in topic_lower or topic_lower in t for t in verse.get("topic", [])):
                        verse["tradition"] = trad
                        relevant_scriptures.append(verse)
        
        return {
            "topic": topic,
            "tradition": tradition,
            "scriptures": relevant_scriptures[:5]  # Limit to 5 results
        }
        
    except Exception as e:
        logger.error(f"Error getting scriptures: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch scripture references"
        )

@router.get("/practices")
async def get_spiritual_practices(
    goal: Optional[str] = Query(default="peace", description="Spiritual goal")
):
    """Get spiritual practices for specific goals"""
    practices_db = {
        "peace": [
            {
                "name": "Centering Prayer",
                "duration": "20 minutes",
                "description": "Sit quietly and let go of thoughts, returning to a sacred word",
                "tradition": "Christian Contemplative"
            },
            {
                "name": "Vipassana Meditation",
                "duration": "10-60 minutes",
                "description": "Observe sensations and thoughts without attachment",
                "tradition": "Buddhist"
            },
            {
                "name": "Pranayama",
                "duration": "15 minutes",
                "description": "Controlled breathing exercises to calm the mind",
                "tradition": "Yoga/Hindu"
            }
        ],
        "gratitude": [
            {
                "name": "Gratitude Journal",
                "duration": "10 minutes",
                "description": "Write three things you're grateful for each day",
                "tradition": "Universal"
            },
            {
                "name": "Shukr Practice",
                "duration": "Throughout the day",
                "description": "Express thankfulness to Allah for blessings",
                "tradition": "Islamic"
            }
        ],
        "compassion": [
            {
                "name": "Metta Meditation",
                "duration": "20 minutes",
                "description": "Send loving-kindness to yourself and others",
                "tradition": "Buddhist"
            },
            {
                "name": "Seva",
                "duration": "Varies",
                "description": "Selfless service to others",
                "tradition": "Hindu/Sikh"
            }
        ],
        "focus": [
            {
                "name": "Trataka",
                "duration": "10-15 minutes",
                "description": "Candle gazing meditation for concentration",
                "tradition": "Yoga"
            },
            {
                "name": "Dhikr",
                "duration": "15-30 minutes",
                "description": "Remembrance of Allah through repetition",
                "tradition": "Islamic/Sufi"
            }
        ]
    }
    
    # Get practices for the goal
    goal_lower = goal.lower()
    practices = practices_db.get(goal_lower, practices_db["peace"])
    
    return {
        "goal": goal,
        "practices": practices,
        "tip": "Start with shorter durations and gradually increase as you build your practice."
    }

@router.get("/affirmations")
async def get_daily_affirmations(
    count: int = Query(default=5, le=10),
    focus: Optional[str] = Query(default="general", description="Focus area for affirmations")
):
    """Get daily positive affirmations"""
    affirmations_db = {
        "general": [
            "I am worthy of love and respect",
            "I choose peace over worry",
            "I am growing stronger every day",
            "I trust the journey of my life",
            "I am exactly where I need to be",
            "I release what no longer serves me",
            "I am grateful for this moment",
            "I have the power to create change"
        ],
        "anxiety": [
            "I am safe in this moment",
            "I release the need to control everything",
            "My breath anchors me to the present",
            "This too shall pass",
            "I choose calm over chaos",
            "I am stronger than my anxious thoughts"
        ],
        "self-love": [
            "I am enough just as I am",
            "I deserve kindness and compassion",
            "I honor my journey and growth",
            "I am learning to love myself more each day",
            "My imperfections make me unique",
            "I am worthy of my own love"
        ],
        "strength": [
            "I have overcome challenges before and I will again",
            "I am resilient and can handle life's challenges",
            "My strength comes from within",
            "I choose courage over comfort",
            "I am capable of amazing things",
            "Every challenge is an opportunity to grow"
        ]
    }
    
    # Get affirmations for the focus area
    focus_lower = focus.lower()
    affirmation_list = affirmations_db.get(focus_lower, affirmations_db["general"])
    
    # Randomly select requested number
    selected = random.sample(affirmation_list, min(count, len(affirmation_list)))
    
    return {
        "focus": focus,
        "affirmations": selected,
        "suggestion": "Repeat these affirmations in the morning or whenever you need encouragement."
    }

@router.get("/videos")
async def get_spiritual_videos():
    """Get curated spiritual guidance videos"""
    # In a real implementation, these would be actual video URLs or embedded content
    videos = [
        {
            "title": "Finding Inner Peace",
            "description": "A guided meditation for inner calm",
            "duration": "15 minutes",
            "type": "meditation",
            "url": "/static/videos/inner-peace.mp4"  # Placeholder
        },
        {
            "title": "Understanding Your Purpose",
            "description": "Spiritual talk on finding life's meaning",
            "duration": "30 minutes",
            "type": "teaching",
            "url": "/static/videos/purpose.mp4"  # Placeholder
        },
        {
            "title": "Healing Through Faith",
            "description": "Stories of spiritual healing and hope",
            "duration": "20 minutes",
            "type": "inspiration",
            "url": "/static/videos/healing.mp4"  # Placeholder
        }
    ]
    
    return {
        "videos": videos,
        "message": "AI-generated spiritual content coming soon"
    }