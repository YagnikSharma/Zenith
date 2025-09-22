"""Community features endpoint for peer support"""

from fastapi import APIRouter, HTTPException, Depends, Query
from pydantic import BaseModel, Field
from typing import Dict, Any, List, Optional
from app.services.firebase_service import firebase_service
from app.services.ai_service import ai_service
from app.core.auth import get_current_user, get_optional_user
from datetime import datetime
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

class PostCreate(BaseModel):
    """Create post model"""
    title: str = Field(..., min_length=1, max_length=200)
    content: str = Field(..., min_length=1, max_length=5000)
    category: str = Field(default="general")
    anonymous: bool = False

class PostResponse(BaseModel):
    """Post response model"""
    id: str
    title: str
    content: str
    category: str
    author_name: str
    author_id: Optional[str]
    created_at: str
    likes: int
    comments_count: int

class CommentCreate(BaseModel):
    """Create comment model"""
    content: str = Field(..., min_length=1, max_length=1000)
    anonymous: bool = False

class CommentResponse(BaseModel):
    """Comment response model"""
    id: str
    post_id: str
    content: str
    author_name: str
    author_id: Optional[str]
    created_at: str
    likes: int

@router.post("/posts", response_model=PostResponse)
async def create_post(
    post_data: PostCreate,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Create a new community post"""
    try:
        # Check for inappropriate content
        sentiment = await ai_service.analyze_sentiment(post_data.content)
        
        # Basic content moderation
        if await is_content_inappropriate(post_data.content):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Post contains inappropriate content"
            )
        
        # Create post
        post_id = f"post_{datetime.utcnow().isoformat()}"
        post = {
            "title": post_data.title,
            "content": post_data.content,
            "category": post_data.category,
            "author_id": current_user["uid"] if not post_data.anonymous else None,
            "author_name": "Anonymous" if post_data.anonymous else current_user.get("display_name", "User"),
            "created_at": datetime.utcnow().isoformat(),
            "likes": 0,
            "comments_count": 0,
            "sentiment": sentiment,
            "status": "active"
        }
        
        await firebase_service.save_document("community_posts", post_id, post)
        
        return PostResponse(
            id=post_id,
            **post
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating post: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create post"
        )

@router.get("/posts", response_model=List[PostResponse])
async def get_posts(
    category: Optional[str] = None,
    limit: int = Query(default=20, le=100),
    offset: int = 0,
    current_user: Optional[Dict[str, Any]] = Depends(get_optional_user)
):
    """Get community posts"""
    try:
        # Build filters
        filters = {"status": "active"}
        if category:
            filters["category"] = category
        
        # Fetch posts
        posts = await firebase_service.query_collection(
            "community_posts",
            filters=filters if category else {"status": "active"},
            limit=limit + offset
        )
        
        # Sort by created_at
        posts.sort(key=lambda x: x.get("created_at", ""), reverse=True)
        
        # Apply offset
        posts = posts[offset:offset + limit]
        
        # Convert to response model
        return [
            PostResponse(
                id=post["id"],
                title=post["title"],
                content=post["content"],
                category=post.get("category", "general"),
                author_name=post.get("author_name", "Anonymous"),
                author_id=post.get("author_id"),
                created_at=post.get("created_at", ""),
                likes=post.get("likes", 0),
                comments_count=post.get("comments_count", 0)
            )
            for post in posts
        ]
        
    except Exception as e:
        logger.error(f"Error fetching posts: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch posts"
        )

@router.get("/posts/{post_id}", response_model=PostResponse)
async def get_post(post_id: str):
    """Get a specific post"""
    try:
        post = await firebase_service.get_document("community_posts", post_id)
        
        if not post or post.get("status") != "active":
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Post not found"
            )
        
        return PostResponse(
            id=post_id,
            title=post["title"],
            content=post["content"],
            category=post.get("category", "general"),
            author_name=post.get("author_name", "Anonymous"),
            author_id=post.get("author_id"),
            created_at=post.get("created_at", ""),
            likes=post.get("likes", 0),
            comments_count=post.get("comments_count", 0)
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching post: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch post"
        )

@router.post("/posts/{post_id}/comments", response_model=CommentResponse)
async def add_comment(
    post_id: str,
    comment_data: CommentCreate,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Add a comment to a post"""
    try:
        # Verify post exists
        post = await firebase_service.get_document("community_posts", post_id)
        if not post:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Post not found"
            )
        
        # Check for inappropriate content
        if await is_content_inappropriate(comment_data.content):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Comment contains inappropriate content"
            )
        
        # Create comment
        comment_id = f"comment_{datetime.utcnow().isoformat()}"
        comment = {
            "post_id": post_id,
            "content": comment_data.content,
            "author_id": current_user["uid"] if not comment_data.anonymous else None,
            "author_name": "Anonymous" if comment_data.anonymous else current_user.get("display_name", "User"),
            "created_at": datetime.utcnow().isoformat(),
            "likes": 0,
            "status": "active"
        }
        
        await firebase_service.save_document("comments", comment_id, comment)
        
        # Update comment count on post
        post["comments_count"] = post.get("comments_count", 0) + 1
        await firebase_service.save_document("community_posts", post_id, post)
        
        return CommentResponse(
            id=comment_id,
            **comment
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error adding comment: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to add comment"
        )

@router.get("/posts/{post_id}/comments", response_model=List[CommentResponse])
async def get_comments(
    post_id: str,
    limit: int = Query(default=20, le=100),
    offset: int = 0
):
    """Get comments for a post"""
    try:
        # Fetch comments
        comments = await firebase_service.query_collection(
            "comments",
            filters={"post_id": post_id, "status": "active"},
            limit=limit + offset
        )
        
        # Sort by created_at
        comments.sort(key=lambda x: x.get("created_at", ""))
        
        # Apply offset
        comments = comments[offset:offset + limit]
        
        return [
            CommentResponse(
                id=comment["id"],
                post_id=comment["post_id"],
                content=comment["content"],
                author_name=comment.get("author_name", "Anonymous"),
                author_id=comment.get("author_id"),
                created_at=comment.get("created_at", ""),
                likes=comment.get("likes", 0)
            )
            for comment in comments
        ]
        
    except Exception as e:
        logger.error(f"Error fetching comments: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch comments"
        )

@router.post("/posts/{post_id}/like")
async def like_post(
    post_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Like a post"""
    try:
        post = await firebase_service.get_document("community_posts", post_id)
        
        if not post:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Post not found"
            )
        
        # Check if already liked
        like_id = f"like_{current_user['uid']}_{post_id}"
        existing_like = await firebase_service.get_document("likes", like_id)
        
        if existing_like:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Already liked this post"
            )
        
        # Add like
        await firebase_service.save_document("likes", like_id, {
            "user_id": current_user["uid"],
            "post_id": post_id,
            "created_at": datetime.utcnow().isoformat()
        })
        
        # Update like count
        post["likes"] = post.get("likes", 0) + 1
        await firebase_service.save_document("community_posts", post_id, post)
        
        return {"message": "Post liked successfully", "likes": post["likes"]}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error liking post: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to like post"
        )

@router.delete("/posts/{post_id}/like")
async def unlike_post(
    post_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Unlike a post"""
    try:
        post = await firebase_service.get_document("community_posts", post_id)
        
        if not post:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Post not found"
            )
        
        # Check if liked
        like_id = f"like_{current_user['uid']}_{post_id}"
        existing_like = await firebase_service.get_document("likes", like_id)
        
        if not existing_like:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Post not liked"
            )
        
        # Remove like
        await firebase_service.delete_document("likes", like_id)
        
        # Update like count
        post["likes"] = max(0, post.get("likes", 0) - 1)
        await firebase_service.save_document("community_posts", post_id, post)
        
        return {"message": "Post unliked successfully", "likes": post["likes"]}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error unliking post: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to unlike post"
        )

@router.delete("/posts/{post_id}")
async def delete_post(
    post_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Delete a post (soft delete)"""
    try:
        post = await firebase_service.get_document("community_posts", post_id)
        
        if not post:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Post not found"
            )
        
        # Verify ownership
        if post.get("author_id") != current_user["uid"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can only delete your own posts"
            )
        
        # Soft delete
        post["status"] = "deleted"
        post["deleted_at"] = datetime.utcnow().isoformat()
        await firebase_service.save_document("community_posts", post_id, post)
        
        return {"message": "Post deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting post: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete post"
        )

# Helper functions

async def is_content_inappropriate(content: str) -> bool:
    """Check if content contains inappropriate material"""
    # Simple keyword-based moderation
    inappropriate_keywords = [
        "hate", "violence", "abuse", "harassment",
        # Add more keywords as needed
    ]
    
    content_lower = content.lower()
    for keyword in inappropriate_keywords:
        if keyword in content_lower:
            # Use AI for more nuanced detection
            sentiment = await ai_service.analyze_sentiment(content)
            if sentiment.get("sentiment") == "negative" and sentiment.get("magnitude", 0) > 0.8:
                return True
    
    return False