from fastapi import APIRouter, HTTPException, Query, Depends
from typing import List, Optional
from datetime import datetime, timedelta
import os
from pymongo import MongoClient
from pymongo.collection import Collection
from dotenv import load_dotenv

from ..schemas import (
    RedditPost, RedditComment, RedditContent, SystemStats, 
    EmotionStats, IntentStats, SubredditStats, SearchQuery, APIResponse
)
from app.api.deps.auth import get_current_user

# Load environment variables
load_dotenv()

router = APIRouter(prefix="/api/v1", tags=["query"])

def get_mongodb_collection() -> Collection:
    """Get MongoDB collection for database operations"""
    try:
        mongo_uri = os.getenv('MONGO_URI')
        db_name = os.getenv('DB_NAME', 'reddit_stream')
        collection_name = os.getenv('COLLECTION_NAME', 'posts_comments')
        
        client = MongoClient(mongo_uri)
        db = client[db_name]
        collection = db[collection_name]
        
        # Ensure text index exists for search functionality
        try:
            collection.create_index([("title", "text"), ("body", "text")])
        except:
            pass  # Index might already exist
        
        return collection
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database connection failed: {str(e)}")

@router.get("/health", response_model=APIResponse)
async def health_check():
    """Check system health and connectivity"""
    try:
        collection = get_mongodb_collection()
        # Test database connection
        collection.find_one()
        
        return APIResponse(
            success=True,
            message="System is healthy",
            data={"status": "healthy", "timestamp": datetime.now().isoformat()}
        )
    except Exception as e:
        return APIResponse(
            success=False,
            message=f"System health check failed: {str(e)}",
            data={"status": "unhealthy", "timestamp": datetime.now().isoformat()}
        )

@router.get("/stats", response_model=SystemStats)
async def get_system_stats(current_user=Depends(get_current_user)):
    """Get overall system statistics"""
    try:
        collection = get_mongodb_collection()
        
        # Get counts
        total_posts = collection.count_documents({"type": "post"})
        total_comments = collection.count_documents({"type": "comment"})
        total_documents = collection.count_documents({})
        
        # Get unique subreddits
        subreddits = collection.distinct("subreddit")
        subreddits_count = len(subreddits)
        
        # Get latest fetch time
        latest_doc = collection.find_one({}, sort=[("fetched_at", -1)])
        latest_fetch = datetime.fromtimestamp(latest_doc["fetched_at"]) if latest_doc else None
        
        return SystemStats(
            total_posts=total_posts,
            total_comments=total_comments,
            total_documents=total_documents,
            subreddits_count=subreddits_count,
            latest_fetch=latest_fetch,
            system_status="operational"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get system stats: {str(e)}")

@router.get("/posts", response_model=List[dict])
async def get_posts(
    subreddit: Optional[str] = Query(None, description="Filter by subreddit"),
    limit: int = Query(50, description="Number of posts to return", ge=1, le=100),
    skip: int = Query(0, description="Number of posts to skip", ge=0),
    emotion: Optional[str] = Query(None, description="Filter by emotion"),
    sort_by: str = Query("fetched_at", description="Sort field"),
    sort_order: int = Query(-1, description="Sort order (1=asc, -1=desc)")
):
    """Get Reddit posts with optional filtering"""
    try:
        collection = get_mongodb_collection()
        
        # Build filter
        filter_query = {"type": "post"}
        if subreddit:
            filter_query["subreddit"] = subreddit
        if emotion:
            filter_query["emotion.label"] = emotion
        
        # Execute query
        posts = list(collection.find(
            filter_query,
            sort=[(sort_by, sort_order)],
            limit=limit,
            skip=skip
        ))
        
        # Convert ObjectId to string for JSON serialization
        for post in posts:
            if '_id' in post:
                post['_id'] = str(post['_id'])
        
        return posts
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get posts: {str(e)}")

@router.get("/comments", response_model=List[dict])
async def get_comments(
    subreddit: Optional[str] = Query(None, description="Filter by subreddit"),
    post_id: Optional[str] = Query(None, description="Filter by parent post ID"),
    limit: int = Query(50, description="Number of comments to return", ge=1, le=100),
    skip: int = Query(0, description="Number of comments to skip", ge=0),
    emotion: Optional[str] = Query(None, description="Filter by emotion"),
    sort_by: str = Query("fetched_at", description="Sort field"),
    sort_order: int = Query(-1, description="Sort order (1=asc, -1=desc)")
):
    """Get Reddit comments with optional filtering"""
    try:
        collection = get_mongodb_collection()
        
        # Build filter
        filter_query = {"type": "comment"}
        if subreddit:
            filter_query["subreddit"] = subreddit
        if post_id:
            filter_query["post_id"] = post_id
        if emotion:
            filter_query["emotion.label"] = emotion
        
        # Execute query
        comments = list(collection.find(
            filter_query,
            sort=[(sort_by, sort_order)],
            limit=limit,
            skip=skip
        ))
        
        # Convert ObjectId to string for JSON serialization
        for comment in comments:
            if '_id' in comment:
                comment['_id'] = str(comment['_id'])
        
        return comments
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get comments: {str(e)}")

@router.get("/search", response_model=List[dict])
async def search_content(
    query: str = Query(..., description="Search query"),
    subreddit: Optional[str] = Query(None, description="Filter by subreddit"),
    content_type: Optional[str] = Query(None, description="Filter by content type (post/comment)"),
    emotion: Optional[str] = Query(None, description="Filter by emotion"),
    intent: Optional[str] = Query(None, description="Filter by intent"),
    limit: int = Query(50, description="Number of results to return", ge=1, le=100),
    skip: int = Query(0, description="Number of results to skip", ge=0)
):
    """Search Reddit content by text"""
    try:
        collection = get_mongodb_collection()
        
        # Build filter query (simpler than text search for now)
        filter_query = {}
        if subreddit:
            filter_query["subreddit"] = subreddit
        if content_type:
            filter_query["type"] = content_type
        if emotion:
            filter_query["emotion.label"] = emotion
        if intent:
            filter_query["intent.label"] = intent
        
        # Simple text search using regex
        text_query = {
            "$or": [
                {"title": {"$regex": query, "$options": "i"}},
                {"body": {"$regex": query, "$options": "i"}}
            ]
        }
        
        # Combine queries
        if filter_query:
            search_query = {"$and": [text_query, filter_query]}
        else:
            search_query = text_query
        
        # Execute search
        results = list(collection.find(
            search_query,
            sort=[("fetched_at", -1)],
            limit=limit,
            skip=skip
        ))
        
        # Convert ObjectId to string for JSON serialization
        for result in results:
            if '_id' in result:
                result['_id'] = str(result['_id'])
        
        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")

@router.get("/emotions", response_model=List[EmotionStats])
async def get_emotion_stats():
    """Get emotion distribution statistics"""
    try:
        collection = get_mongodb_collection()
        
        # Aggregate emotion statistics
        pipeline = [
            {"$match": {"emotion.label": {"$exists": True}}},
            {"$group": {
                "_id": "$emotion.label",
                "count": {"$sum": 1}
            }},
            {"$sort": {"count": -1}}
        ]
        
        emotion_stats = list(collection.aggregate(pipeline))
        
        # Calculate total for percentages
        total = sum(stat["count"] for stat in emotion_stats)
        
        # Format results
        results = []
        for stat in emotion_stats:
            percentage = (stat["count"] / total * 100) if total > 0 else 0
            results.append(EmotionStats(
                emotion=stat["_id"],
                count=stat["count"],
                percentage=round(percentage, 2)
            ))
        
        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get emotion stats: {str(e)}")

@router.get("/intents", response_model=List[IntentStats])
async def get_intent_stats():
    """Get intent distribution statistics"""
    try:
        collection = get_mongodb_collection()
        
        # Aggregate intent statistics
        pipeline = [
            {"$match": {"intent.label": {"$exists": True}}},
            {"$group": {
                "_id": "$intent.label",
                "count": {"$sum": 1}
            }},
            {"$sort": {"count": -1}}
        ]
        
        intent_stats = list(collection.aggregate(pipeline))
        
        # Calculate total for percentages
        total = sum(stat["count"] for stat in intent_stats)
        
        # Format results
        results = []
        for stat in intent_stats:
            percentage = (stat["count"] / total * 100) if total > 0 else 0
            results.append(IntentStats(
                intent=stat["_id"],
                count=stat["count"],
                percentage=round(percentage, 2)
            ))
        
        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get intent stats: {str(e)}")

@router.get("/subreddits", response_model=List[SubredditStats])
async def get_subreddit_stats():
    """Get subreddit statistics"""
    try:
        collection = get_mongodb_collection()
        
        # Aggregate subreddit statistics
        pipeline = [
            {"$group": {
                "_id": "$subreddit",
                "posts_count": {"$sum": {"$cond": [{"$eq": ["$type", "post"]}, 1, 0]}},
                "comments_count": {"$sum": {"$cond": [{"$eq": ["$type", "comment"]}, 1, 0]}},
                "total_score": {"$sum": "$score"}
            }},
            {"$sort": {"posts_count": -1}}
        ]
        
        subreddit_stats = list(collection.aggregate(pipeline))
        
        # Format results
        results = []
        for stat in subreddit_stats:
            results.append(SubredditStats(
                subreddit=stat["_id"],
                posts_count=stat["posts_count"],
                comments_count=stat["comments_count"],
                total_score=stat["total_score"]
            ))
        
        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get subreddit stats: {str(e)}")

@router.get("/recent", response_model=List[dict])
async def get_recent_content(
    hours: int = Query(24, description="Hours to look back", ge=1, le=168),
    limit: int = Query(50, description="Number of results to return", ge=1, le=100)
):
    """Get recent content from the last N hours"""
    try:
        collection = get_mongodb_collection()
        
        # Calculate time threshold
        time_threshold = datetime.now() - timedelta(hours=hours)
        timestamp_threshold = time_threshold.timestamp()
        
        # Query recent content
        recent_content = list(collection.find(
            {"fetched_at": {"$gte": timestamp_threshold}},
            sort=[("fetched_at", -1)],
            limit=limit
        ))
        
        # Convert ObjectId to string for JSON serialization
        for content in recent_content:
            if '_id' in content:
                content['_id'] = str(content['_id'])
        
        return recent_content
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get recent content: {str(e)}")
