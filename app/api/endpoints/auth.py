"""Authentication endpoints"""

from fastapi import APIRouter, HTTPException, status, Depends
from app.models.auth import UserSignup, UserLogin, UserResponse, TokenResponse, UserUpdate
from app.services.firebase_service import firebase_service
from app.core.auth import get_password_hash, verify_password, create_token_for_user, get_current_user
from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

@router.post("/signup", response_model=TokenResponse)
async def signup(user_data: UserSignup):
    """Create a new user account"""
    try:
        # Check if user already exists (mock implementation)
        existing_user = await firebase_service.get_document("users", user_data.email)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User with this email already exists"
            )
        
        # Create user in Firebase
        user = await firebase_service.create_user(
            email=user_data.email,
            password=user_data.password,
            display_name=user_data.display_name
        )
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create user"
            )
        
        # Store additional user data
        await firebase_service.save_document("users", user["uid"], {
            "email": user_data.email,
            "display_name": user_data.display_name,
            "preferred_language": user_data.preferred_language,
            "created_at": "2024-01-01T00:00:00Z"  # Use proper timestamp in production
        })
        
        # Create access token
        access_token = create_token_for_user(user)
        
        return TokenResponse(
            access_token=user.get("token", access_token),  # Use mock token if available
            user=UserResponse(
                uid=user["uid"],
                email=user["email"],
                display_name=user.get("display_name"),
                preferred_language=user_data.preferred_language
            )
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Signup error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred during signup"
        )

@router.post("/login", response_model=TokenResponse)
async def login(user_data: UserLogin):
    """Login with email and password"""
    try:
        # For development, check mock users
        # In production, this would use Firebase Auth
        
        # Mock implementation for development
        mock_users = firebase_service._mock_users if hasattr(firebase_service, '_mock_users') else {}
        
        user = None
        for uid, user_info in mock_users.items():
            if user_info.get("email") == user_data.email:
                # In production, verify password properly
                if user_info.get("password") == user_data.password:
                    user = {
                        "uid": uid,
                        "email": user_info["email"],
                        "display_name": user_info.get("name")
                    }
                break
        
        if not user:
            # Try to create a test user for development
            if user_data.email == "test@example.com" and user_data.password == "test123":
                user = {
                    "uid": "test_user_1",
                    "email": "test@example.com",
                    "display_name": "Test User"
                }
                # Store in mock users
                if hasattr(firebase_service, '_mock_users'):
                    firebase_service._mock_users["test_user_1"] = {
                        "email": "test@example.com",
                        "password": "test123",
                        "name": "Test User"
                    }
            else:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid email or password"
                )
        
        # Get user data from Firestore
        user_doc = await firebase_service.get_document("users", user["uid"])
        if user_doc:
            user.update(user_doc)
        
        # Create access token
        access_token = create_token_for_user(user)
        
        return TokenResponse(
            access_token=access_token,
            user=UserResponse(
                uid=user["uid"],
                email=user["email"],
                display_name=user.get("display_name"),
                preferred_language=user.get("preferred_language", "en")
            )
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Login error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred during login"
        )

@router.get("/me", response_model=UserResponse)
async def get_current_user_profile(current_user: Dict[str, Any] = Depends(get_current_user)):
    """Get current user profile"""
    try:
        # Get additional user data from Firestore
        user_doc = await firebase_service.get_document("users", current_user["uid"])
        
        if user_doc:
            current_user.update(user_doc)
        
        return UserResponse(
            uid=current_user["uid"],
            email=current_user["email"],
            display_name=current_user.get("display_name"),
            preferred_language=current_user.get("preferred_language", "en")
        )
        
    except Exception as e:
        logger.error(f"Error getting user profile: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get user profile"
        )

@router.put("/me", response_model=UserResponse)
async def update_user_profile(
    user_update: UserUpdate,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Update current user profile"""
    try:
        # Prepare update data
        update_data = {}
        if user_update.display_name is not None:
            update_data["display_name"] = user_update.display_name
        if user_update.preferred_language is not None:
            update_data["preferred_language"] = user_update.preferred_language
        
        # Update in Firestore
        if update_data:
            await firebase_service.save_document("users", current_user["uid"], update_data)
        
        # Update Firebase Auth profile if needed
        if user_update.display_name:
            await firebase_service.update_user(
                current_user["uid"],
                display_name=user_update.display_name
            )
        
        # Return updated user
        current_user.update(update_data)
        
        return UserResponse(
            uid=current_user["uid"],
            email=current_user["email"],
            display_name=current_user.get("display_name"),
            preferred_language=current_user.get("preferred_language", "en")
        )
        
    except Exception as e:
        logger.error(f"Error updating user profile: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update user profile"
        )

@router.post("/logout")
async def logout(current_user: Dict[str, Any] = Depends(get_current_user)):
    """Logout current user"""
    # In a stateless JWT system, logout is handled client-side by removing the token
    # Here we can add any server-side cleanup if needed
    return {"message": "Logged out successfully"}

@router.delete("/me")
async def delete_account(current_user: Dict[str, Any] = Depends(get_current_user)):
    """Delete current user account"""
    try:
        # Delete user data from Firestore
        await firebase_service.delete_document("users", current_user["uid"])
        
        # Delete from Firebase Auth
        await firebase_service.delete_user(current_user["uid"])
        
        return {"message": "Account deleted successfully"}
        
    except Exception as e:
        logger.error(f"Error deleting account: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete account"
        )