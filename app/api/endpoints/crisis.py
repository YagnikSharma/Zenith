"""Crisis detection and support endpoint"""

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Dict, Any, List, Optional
from app.services.ai_service import ai_service
from app.services.firebase_service import firebase_service
from app.core.auth import get_optional_user
from datetime import datetime
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

class CrisisCheckRequest(BaseModel):
    """Crisis check request model"""
    message: str
    user_context: Optional[Dict[str, Any]] = None

class CrisisResponse(BaseModel):
    """Crisis response model"""
    is_crisis: bool
    confidence: float
    type: str
    recommended_action: str
    support_resources: List[Dict[str, Any]]
    emergency_contacts: List[Dict[str, Any]]

class CrisisAlert(BaseModel):
    """Crisis alert model for logging"""
    user_id: Optional[str]
    message: str
    detection_result: Dict[str, Any]
    timestamp: str

@router.post("/check", response_model=CrisisResponse)
async def check_for_crisis(
    request: CrisisCheckRequest,
    current_user: Optional[Dict[str, Any]] = Depends(get_optional_user)
):
    """Check if a message indicates a crisis situation"""
    try:
        # Perform crisis detection
        detection_result = await ai_service.detect_crisis(request.message)
        
        # Log crisis detection if it's positive
        if detection_result["is_crisis"] and detection_result["confidence"] > 0.7:
            alert_id = f"alert_{datetime.utcnow().isoformat()}"
            await firebase_service.save_document(
                "crisis_alerts",
                alert_id,
                {
                    "user_id": current_user["uid"] if current_user else None,
                    "message": request.message[:500],  # Truncate for privacy
                    "detection_result": detection_result,
                    "timestamp": datetime.utcnow().isoformat(),
                    "handled": False
                }
            )
        
        # Get appropriate support resources
        support_resources = await get_support_resources(
            detection_result["is_crisis"],
            current_user
        )
        
        # Get emergency contacts
        emergency_contacts = await get_emergency_contacts(current_user)
        
        return CrisisResponse(
            is_crisis=detection_result["is_crisis"],
            confidence=detection_result["confidence"],
            type=detection_result["type"],
            recommended_action=detection_result["recommended_action"],
            support_resources=support_resources,
            emergency_contacts=emergency_contacts
        )
        
    except Exception as e:
        logger.error(f"Crisis detection error: {e}")
        # In case of error, provide default support resources
        return CrisisResponse(
            is_crisis=False,
            confidence=0.0,
            type="error",
            recommended_action="seek_support",
            support_resources=await get_default_resources(),
            emergency_contacts=await get_default_emergency_contacts()
        )

@router.get("/resources")
async def get_crisis_resources(
    current_user: Optional[Dict[str, Any]] = Depends(get_optional_user)
):
    """Get crisis support resources"""
    try:
        resources = {
            "helplines": await get_helplines(current_user),
            "support_groups": await get_support_groups(),
            "self_help": await get_self_help_resources(),
            "professional_help": await get_professional_resources()
        }
        
        return resources
        
    except Exception as e:
        logger.error(f"Error fetching crisis resources: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch crisis resources"
        )

@router.post("/report")
async def report_crisis(
    message: str,
    current_user: Optional[Dict[str, Any]] = Depends(get_optional_user)
):
    """Allow users to self-report a crisis situation"""
    try:
        # Create crisis report
        report_id = f"report_{datetime.utcnow().isoformat()}"
        await firebase_service.save_document(
            "crisis_reports",
            report_id,
            {
                "user_id": current_user["uid"] if current_user else None,
                "message": message,
                "timestamp": datetime.utcnow().isoformat(),
                "status": "pending",
                "self_reported": True
            }
        )
        
        # Get immediate support resources
        resources = await get_immediate_support()
        
        return {
            "message": "Your report has been received. Help is available.",
            "report_id": report_id,
            "immediate_support": resources
        }
        
    except Exception as e:
        logger.error(f"Error reporting crisis: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to report crisis"
        )

# Helper functions

async def get_support_resources(is_crisis: bool, user: Optional[Dict] = None) -> List[Dict[str, Any]]:
    """Get appropriate support resources based on crisis level"""
    if is_crisis:
        return [
            {
                "type": "immediate",
                "name": "National Suicide Prevention Lifeline",
                "contact": "988",
                "available": "24/7",
                "description": "Free, confidential crisis support"
            },
            {
                "type": "immediate",
                "name": "Crisis Text Line",
                "contact": "Text HOME to 741741",
                "available": "24/7",
                "description": "Text-based crisis support"
            },
            {
                "type": "immediate",
                "name": "NIMHANS 24x7 Helpline",
                "contact": "080-46110007",
                "available": "24/7",
                "description": "Mental health support in India"
            }
        ]
    else:
        return [
            {
                "type": "preventive",
                "name": "Mental Health Resources",
                "url": "https://www.nimh.nih.gov/health/find-help",
                "description": "Find mental health resources and information"
            },
            {
                "type": "preventive",
                "name": "Mindfulness Exercises",
                "url": "/api/meditation",
                "description": "Practice mindfulness and meditation"
            }
        ]

async def get_emergency_contacts(user: Optional[Dict] = None) -> List[Dict[str, Any]]:
    """Get emergency contacts for the user's region"""
    # Default emergency contacts (India-focused)
    return [
        {
            "name": "Emergency Services",
            "number": "112",
            "type": "emergency"
        },
        {
            "name": "NIMHANS Helpline",
            "number": "080-46110007",
            "type": "mental_health"
        },
        {
            "name": "Vandrevala Foundation",
            "number": "9999666555",
            "type": "mental_health"
        },
        {
            "name": "AASRA",
            "number": "91-9820466726",
            "type": "suicide_prevention"
        }
    ]

async def get_default_resources() -> List[Dict[str, Any]]:
    """Get default support resources"""
    return [
        {
            "type": "general",
            "name": "Mental Health Support",
            "description": "Professional help is available"
        }
    ]

async def get_default_emergency_contacts() -> List[Dict[str, Any]]:
    """Get default emergency contacts"""
    return [
        {
            "name": "Emergency",
            "number": "112",
            "type": "emergency"
        }
    ]

async def get_helplines(user: Optional[Dict] = None) -> List[Dict[str, Any]]:
    """Get helpline numbers"""
    return [
        {
            "name": "NIMHANS",
            "number": "080-46110007",
            "hours": "24/7",
            "languages": ["English", "Hindi", "Kannada"]
        },
        {
            "name": "Vandrevala Foundation",
            "number": "9999666555",
            "hours": "24/7",
            "languages": ["English", "Hindi", "Multiple Regional Languages"]
        },
        {
            "name": "iCALL",
            "number": "9152987821",
            "hours": "Mon-Sat: 10 AM - 8 PM",
            "languages": ["English", "Hindi", "Marathi", "Tamil", "Telugu", "Gujarati"]
        }
    ]

async def get_support_groups() -> List[Dict[str, Any]]:
    """Get support group information"""
    return [
        {
            "name": "Youth Mental Health Support",
            "type": "online",
            "platform": "Discord/WhatsApp",
            "description": "Peer support for young adults"
        },
        {
            "name": "Depression and Anxiety Support Group",
            "type": "online",
            "platform": "Zoom",
            "schedule": "Weekly meetings"
        }
    ]

async def get_self_help_resources() -> List[Dict[str, Any]]:
    """Get self-help resources"""
    return [
        {
            "name": "Breathing Exercises",
            "type": "technique",
            "duration": "5 minutes",
            "link": "/api/meditation/breathing"
        },
        {
            "name": "Grounding Techniques",
            "type": "technique",
            "description": "5-4-3-2-1 sensory grounding"
        },
        {
            "name": "Journaling Prompts",
            "type": "activity",
            "description": "Express your feelings through writing"
        }
    ]

async def get_professional_resources() -> List[Dict[str, Any]]:
    """Get professional help resources"""
    return [
        {
            "name": "Find a Therapist",
            "type": "directory",
            "url": "https://www.psychologytoday.com/in",
            "description": "Directory of mental health professionals in India"
        },
        {
            "name": "Online Therapy Platforms",
            "type": "service",
            "options": ["BetterHelp", "Talkspace", "Manastha"],
            "description": "Connect with licensed therapists online"
        }
    ]

async def get_immediate_support() -> Dict[str, Any]:
    """Get immediate support information"""
    return {
        "message": "You are not alone. Help is available.",
        "immediate_actions": [
            "Call a trusted friend or family member",
            "Contact a crisis helpline: 080-46110007",
            "Go to the nearest emergency room if in immediate danger",
            "Use grounding techniques to calm yourself"
        ],
        "helplines": await get_helplines()
    }