from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime

class RedditPost(BaseModel):
    """Schema for Reddit post data"""
    id: str = Field(..., description="Reddit post ID")
    type: str = Field(default="post", description="Content type")
    subreddit: str = Field(..., description="Subreddit name")
    author: str = Field(..., description="Post author")
    title: str = Field(..., description="Post title")
    body: Optional[str] = Field(None, description="Post body text")
    created_utc: float = Field(..., description="Creation timestamp")
    url: str = Field(..., description="Post URL")
    score: int = Field(..., description="Post score (upvotes - downvotes)")
    num_comments: int = Field(..., description="Number of comments")
    fetched_at: float = Field(..., description="When data was fetched")
    
    # NLP Analysis Results
    emotion: Optional[Dict[str, Any]] = Field(None, description="Emotion analysis results")
    intent: Optional[Dict[str, Any]] = Field(None, description="Intent classification results")
    sarcasm: Optional[Dict[str, Any]] = Field(None, description="Sarcasm detection results")

class RedditComment(BaseModel):
    """Schema for Reddit comment data"""
    id: str = Field(..., description="Reddit comment ID")
    type: str = Field(default="comment", description="Content type")
    subreddit: str = Field(..., description="Subreddit name")
    post_id: str = Field(..., description="Parent post ID")
    author: str = Field(..., description="Comment author")
    body: str = Field(..., description="Comment text")
    created_utc: float = Field(..., description="Creation timestamp")
    score: int = Field(..., description="Comment score")
    fetched_at: float = Field(..., description="When data was fetched")
    
    # NLP Analysis Results
    emotion: Optional[Dict[str, Any]] = Field(None, description="Emotion analysis results")
    intent: Optional[Dict[str, Any]] = Field(None, description="Intent classification results")
    sarcasm: Optional[Dict[str, Any]] = Field(None, description="Sarcasm detection results")

class RedditContent(BaseModel):
    """Schema for generic Reddit content (post or comment)"""
    id: str = Field(..., description="Reddit content ID")
    type: str = Field(..., description="Content type (post or comment)")
    subreddit: str = Field(..., description="Subreddit name")
    author: str = Field(..., description="Author username")
    body: Optional[str] = Field(None, description="Content text")
    title: Optional[str] = Field(None, description="Post title (only for posts)")
    created_utc: float = Field(..., description="Creation timestamp")
    score: int = Field(..., description="Score")
    fetched_at: float = Field(..., description="When data was fetched")
    
    # NLP Analysis Results
    emotion: Optional[Dict[str, Any]] = Field(None, description="Emotion analysis results")
    intent: Optional[Dict[str, Any]] = Field(None, description="Intent classification results")
    sarcasm: Optional[Dict[str, Any]] = Field(None, description="Sarcasm detection results")

class SystemStats(BaseModel):
    """Schema for system statistics"""
    total_posts: int = Field(..., description="Total number of posts")
    total_comments: int = Field(..., description="Total number of comments")
    total_documents: int = Field(..., description="Total documents in database")
    subreddits_count: int = Field(..., description="Number of unique subreddits")
    latest_fetch: Optional[datetime] = Field(None, description="Latest data fetch time")
    system_status: str = Field(..., description="System status")

class EmotionStats(BaseModel):
    """Schema for emotion statistics"""
    emotion: str = Field(..., description="Emotion label")
    count: int = Field(..., description="Number of occurrences")
    percentage: float = Field(..., description="Percentage of total")

class IntentStats(BaseModel):
    """Schema for intent statistics"""
    intent: str = Field(..., description="Intent label")
    count: int = Field(..., description="Number of occurrences")
    percentage: float = Field(..., description="Percentage of total")

class SubredditStats(BaseModel):
    """Schema for subreddit statistics"""
    subreddit: str = Field(..., description="Subreddit name")
    posts_count: int = Field(..., description="Number of posts")
    comments_count: int = Field(..., description="Number of comments")
    total_score: int = Field(..., description="Total score")

class SearchQuery(BaseModel):
    """Schema for search queries"""
    query: str = Field(..., description="Search query")
    subreddit: Optional[str] = Field(None, description="Filter by subreddit")
    emotion: Optional[str] = Field(None, description="Filter by emotion")
    intent: Optional[str] = Field(None, description="Filter by intent")
    content_type: Optional[str] = Field(None, description="Filter by content type (post/comment)")
    limit: int = Field(default=100, description="Number of results to return")
    skip: int = Field(default=0, description="Number of results to skip")

class APIResponse(BaseModel):
    """Schema for API responses"""
    success: bool = Field(..., description="Request success status")
    message: str = Field(..., description="Response message")
    data: Optional[Any] = Field(None, description="Response data")
    count: Optional[int] = Field(None, description="Number of items returned")
    total: Optional[int] = Field(None, description="Total number of items available")

class HealthCheck(BaseModel):
    """Schema for health check response"""
    status: str = Field(..., description="System status")
    timestamp: datetime = Field(..., description="Check timestamp")
    reddit_api: bool = Field(..., description="Reddit API status")
    mongodb: bool = Field(..., description="MongoDB connection status")
    nlp_models: bool = Field(..., description="NLP models status")
    redis: Optional[bool] = Field(None, description="Redis connection status")
