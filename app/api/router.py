"""Main API router that combines all endpoint routers"""

from fastapi import APIRouter
from app.api.endpoints import auth, chat, crisis, community, spiritual, meditation

router = APIRouter()

# Include all endpoint routers
router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
router.include_router(chat.router, prefix="/chat", tags=["AI Chat"])
router.include_router(crisis.router, prefix="/crisis", tags=["Crisis Detection"])
router.include_router(community.router, prefix="/community", tags=["Community"])
router.include_router(spiritual.router, prefix="/spiritual", tags=["Spiritual Wisdom"])
router.include_router(meditation.router, prefix="/meditation", tags=["Meditation"])

@router.get("")
async def api_root():
    """API root endpoint"""
    return {
        "message": "Zenith Mental Wellness Platform API",
        "endpoints": {
            "auth": "Authentication endpoints",
            "chat": "AI chat companion",
            "crisis": "Crisis detection and support",
            "community": "Peer community features",
            "spiritual": "Spiritual wisdom and guidance",
            "meditation": "Meditation and mindfulness resources"
        }
    }