"""Firebase service for authentication and database operations"""

import os
import json
from typing import Optional, Dict, Any
import firebase_admin
from firebase_admin import credentials, auth, firestore
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)

class FirebaseService:
    """Service for Firebase operations"""
    
    _instance = None
    _initialized = False
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if not self._initialized:
            self._initialize_firebase()
            self._initialized = True
    
    def _initialize_firebase(self):
        """Initialize Firebase Admin SDK"""
        try:
            if settings.FIREBASE_SERVICE_ACCOUNT_KEY_PATH:
                # Check if file exists
                if os.path.exists(settings.FIREBASE_SERVICE_ACCOUNT_KEY_PATH):
                    cred = credentials.Certificate(settings.FIREBASE_SERVICE_ACCOUNT_KEY_PATH)
                    firebase_admin.initialize_app(cred)
                    self.db = firestore.client()
                    logger.info("Firebase initialized successfully with service account")
                else:
                    logger.warning(f"Firebase service account file not found: {settings.FIREBASE_SERVICE_ACCOUNT_KEY_PATH}")
                    # Initialize without credentials for development
                    self._initialize_mock_firebase()
            else:
                logger.warning("Firebase service account not configured, using mock service")
                self._initialize_mock_firebase()
                
        except Exception as e:
            logger.error(f"Error initializing Firebase: {e}")
            self._initialize_mock_firebase()
    
    def _initialize_mock_firebase(self):
        """Initialize mock Firebase for development without credentials"""
        logger.info("Using mock Firebase service for development")
        self.db = None
        self._mock_users = {}
        self._mock_data = {}
    
    async def verify_id_token(self, id_token: str) -> Optional[Dict[str, Any]]:
        """Verify Firebase ID token"""
        try:
            if self.db:  # Real Firebase
                decoded_token = auth.verify_id_token(id_token)
                return decoded_token
            else:  # Mock for development
                # Simple mock verification
                if id_token.startswith("mock_token_"):
                    user_id = id_token.replace("mock_token_", "")
                    if user_id in self._mock_users:
                        return {
                            "uid": user_id,
                            "email": self._mock_users[user_id].get("email"),
                            "name": self._mock_users[user_id].get("name")
                        }
                return None
        except Exception as e:
            logger.error(f"Error verifying token: {e}")
            return None
    
    async def create_user(self, email: str, password: str, display_name: str = None) -> Optional[Dict[str, Any]]:
        """Create a new user"""
        try:
            if self.db:  # Real Firebase
                user = auth.create_user(
                    email=email,
                    password=password,
                    display_name=display_name
                )
                return {
                    "uid": user.uid,
                    "email": user.email,
                    "display_name": user.display_name
                }
            else:  # Mock for development
                user_id = f"user_{len(self._mock_users) + 1}"
                self._mock_users[user_id] = {
                    "email": email,
                    "password": password,  # In real app, never store plain passwords
                    "name": display_name
                }
                return {
                    "uid": user_id,
                    "email": email,
                    "display_name": display_name,
                    "token": f"mock_token_{user_id}"
                }
        except Exception as e:
            logger.error(f"Error creating user: {e}")
            return None
    
    async def get_user(self, uid: str) -> Optional[Dict[str, Any]]:
        """Get user by UID"""
        try:
            if self.db:  # Real Firebase
                user = auth.get_user(uid)
                return {
                    "uid": user.uid,
                    "email": user.email,
                    "display_name": user.display_name,
                    "photo_url": user.photo_url,
                    "disabled": user.disabled
                }
            else:  # Mock for development
                if uid in self._mock_users:
                    user = self._mock_users[uid]
                    return {
                        "uid": uid,
                        "email": user.get("email"),
                        "display_name": user.get("name")
                    }
                return None
        except Exception as e:
            logger.error(f"Error getting user: {e}")
            return None
    
    async def update_user(self, uid: str, **kwargs) -> bool:
        """Update user information"""
        try:
            if self.db:  # Real Firebase
                auth.update_user(uid, **kwargs)
                return True
            else:  # Mock for development
                if uid in self._mock_users:
                    self._mock_users[uid].update(kwargs)
                    return True
                return False
        except Exception as e:
            logger.error(f"Error updating user: {e}")
            return False
    
    async def delete_user(self, uid: str) -> bool:
        """Delete user"""
        try:
            if self.db:  # Real Firebase
                auth.delete_user(uid)
                return True
            else:  # Mock for development
                if uid in self._mock_users:
                    del self._mock_users[uid]
                    return True
                return False
        except Exception as e:
            logger.error(f"Error deleting user: {e}")
            return False
    
    async def save_document(self, collection: str, document_id: str, data: Dict[str, Any]) -> bool:
        """Save document to Firestore"""
        try:
            if self.db:  # Real Firestore
                doc_ref = self.db.collection(collection).document(document_id)
                doc_ref.set(data)
                return True
            else:  # Mock for development
                if collection not in self._mock_data:
                    self._mock_data[collection] = {}
                self._mock_data[collection][document_id] = data
                return True
        except Exception as e:
            logger.error(f"Error saving document: {e}")
            return False
    
    async def get_document(self, collection: str, document_id: str) -> Optional[Dict[str, Any]]:
        """Get document from Firestore"""
        try:
            if self.db:  # Real Firestore
                doc_ref = self.db.collection(collection).document(document_id)
                doc = doc_ref.get()
                if doc.exists:
                    return doc.to_dict()
                return None
            else:  # Mock for development
                if collection in self._mock_data and document_id in self._mock_data[collection]:
                    return self._mock_data[collection][document_id]
                return None
        except Exception as e:
            logger.error(f"Error getting document: {e}")
            return None
    
    async def query_collection(self, collection: str, filters: Dict[str, Any] = None, limit: int = 100) -> list:
        """Query collection with optional filters"""
        try:
            if self.db:  # Real Firestore
                query = self.db.collection(collection)
                
                if filters:
                    for field, value in filters.items():
                        query = query.where(field, "==", value)
                
                query = query.limit(limit)
                docs = query.stream()
                
                return [{"id": doc.id, **doc.to_dict()} for doc in docs]
            else:  # Mock for development
                if collection in self._mock_data:
                    results = []
                    for doc_id, doc_data in self._mock_data[collection].items():
                        if filters:
                            match = all(doc_data.get(k) == v for k, v in filters.items())
                            if match:
                                results.append({"id": doc_id, **doc_data})
                        else:
                            results.append({"id": doc_id, **doc_data})
                    return results[:limit]
                return []
        except Exception as e:
            logger.error(f"Error querying collection: {e}")
            return []
    
    async def delete_document(self, collection: str, document_id: str) -> bool:
        """Delete document from Firestore"""
        try:
            if self.db:  # Real Firestore
                self.db.collection(collection).document(document_id).delete()
                return True
            else:  # Mock for development
                if collection in self._mock_data and document_id in self._mock_data[collection]:
                    del self._mock_data[collection][document_id]
                    return True
                return False
        except Exception as e:
            logger.error(f"Error deleting document: {e}")
            return False

# Create singleton instance
firebase_service = FirebaseService()