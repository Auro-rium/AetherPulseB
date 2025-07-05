from fastapi import APIRouter, HTTPException, BackgroundTasks, Query
from fastapi.responses import StreamingResponse
from typing import List, Optional
import json
import time
import os
from datetime import datetime
from dotenv import load_dotenv
import praw
from pymongo import MongoClient

from ..schemas import APIResponse, SystemStats

# Load environment variables
load_dotenv()

router = APIRouter(prefix="/api/v1", tags=["stream"])

def get_reddit_client():
    """Get Reddit client for API operations"""
    try:
        client_id = os.getenv('REDDIT_CLIENT_ID')
        client_secret = os.getenv('REDDIT_CLIENT_SECRET')
        user_agent = os.getenv('REDDIT_USER_AGENT')
        
        if not all([client_id, client_secret, user_agent]):
            raise Exception("Reddit credentials not configured")
        
        reddit = praw.Reddit(
            client_id=client_id,
            client_secret=client_secret,
            user_agent=user_agent
        )
        reddit.read_only = True
        return reddit
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Reddit client initialization failed: {str(e)}")

def get_mongodb_client():
    """Get MongoDB client for database operations"""
    try:
        mongo_uri = os.getenv('MONGO_URI')
        db_name = os.getenv('DB_NAME', 'reddit_stream')
        collection_name = os.getenv('COLLECTION_NAME', 'posts_comments')
        
        if not mongo_uri:
            raise Exception("MongoDB URI not configured")
        
        client = MongoClient(mongo_uri)
        db = client[db_name]
        return db[collection_name]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"MongoDB connection failed: {str(e)}")

@router.post("/stream/start", response_model=APIResponse)
async def start_streaming(background_tasks: BackgroundTasks):
    """Start the Reddit streaming process in the background"""
    try:
        # Lazy import to avoid loading NLP models at startup
        from app.reddit.processor import process_and_store
        
        # Get configuration
        mongo_uri = os.getenv('MONGO_URI')
        db_name = os.getenv('DB_NAME', 'reddit_stream')
        collection_name = os.getenv('COLLECTION_NAME', 'posts_comments')
        
        # Test subreddits for streaming
        test_subreddits = ['AskReddit', 'worldnews', 'funny', 'gaming']
        
        # Start background task
        background_tasks.add_task(
            process_and_store,
            test_subreddits,
            get_reddit_client(),
            mongo_uri,
            db_name,
            collection_name,
            use_redis=False
        )
        
        return APIResponse(
            success=True,
            message="Streaming started successfully",
            data={
                "status": "started",
                "subreddits": test_subreddits,
                "timestamp": datetime.now().isoformat()
            }
        )
    except Exception as e:
        return APIResponse(
            success=False,
            message=f"Failed to start streaming: {str(e)}",
            data={"status": "failed", "timestamp": datetime.now().isoformat()}
        )

@router.get("/stream/status", response_model=APIResponse)
async def get_streaming_status():
    """Get current streaming status and statistics"""
    try:
        collection = get_mongodb_client()
        
        # Get recent activity (last 1 hour)
        one_hour_ago = time.time() - 3600
        recent_count = collection.count_documents({"fetched_at": {"$gte": one_hour_ago}})
        
        # Get total counts
        total_posts = collection.count_documents({"type": "post"})
        total_comments = collection.count_documents({"type": "comment"})
        
        # Get latest fetch time
        latest_doc = collection.find_one({}, sort=[("fetched_at", -1)])
        latest_fetch = datetime.fromtimestamp(latest_doc["fetched_at"]) if latest_doc else None
        
        return APIResponse(
            success=True,
            message="Streaming status retrieved",
            data={
                "status": "active" if recent_count > 0 else "idle",
                "recent_activity": recent_count,
                "total_posts": total_posts,
                "total_comments": total_comments,
                "latest_fetch": latest_fetch.isoformat() if latest_fetch else None,
                "timestamp": datetime.now().isoformat()
            }
        )
    except Exception as e:
        return APIResponse(
            success=False,
            message=f"Failed to get streaming status: {str(e)}",
            data={"status": "error", "timestamp": datetime.now().isoformat()}
        )

@router.get("/stream/live")
async def stream_live_data():
    """Stream live Reddit data as Server-Sent Events (SSE)"""
    async def generate():
        try:
            collection = get_mongodb_client()
            last_check = time.time()
            
            while True:
                # Get new data since last check
                new_data = list(collection.find(
                    {"fetched_at": {"$gt": last_check}},
                    sort=[("fetched_at", -1)],
                    limit=10
                ))
                
                if new_data:
                    for item in new_data:
                        # Format data for SSE
                        event_data = {
                            "type": item["type"],
                            "subreddit": item["subreddit"],
                            "author": item["author"],
                            "content": item.get("title", "") + " " + (item.get("body", "") or ""),
                            "score": item["score"],
                            "emotion": item.get("emotion", {}).get("label", "unknown"),
                            "intent": item.get("intent", {}).get("label", "unknown"),
                            "timestamp": datetime.fromtimestamp(item["fetched_at"]).isoformat()
                        }
                        
                        yield f"data: {json.dumps(event_data)}\n\n"
                
                last_check = time.time()
                await asyncio.sleep(5)  # Check every 5 seconds
                
        except Exception as e:
            error_data = {"error": str(e), "timestamp": datetime.now().isoformat()}
            yield f"data: {json.dumps(error_data)}\n\n"
    
    return StreamingResponse(
        generate(),
        media_type="text/plain",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Content-Type": "text/event-stream"
        }
    )

@router.post("/stream/fetch", response_model=APIResponse)
async def fetch_single_subreddit(subreddit: str = Query(..., description="Subreddit name to fetch")):
    """Fetch data from a single subreddit"""
    try:
        reddit = get_reddit_client()
        collection = get_mongodb_client()
        
        # Get initial count
        initial_count = collection.count_documents({})
        
        # Fetch data from subreddit
        subreddit_obj = reddit.subreddit(subreddit)
        posts_processed = 0
        comments_processed = 0
        
        # Process hot posts
        for submission in subreddit_obj.hot(limit=10):
            post_data = {
                'type': 'post',
                'subreddit': subreddit,
                'id': submission.id,
                'author': str(submission.author) if submission.author else '[deleted]',
                'title': submission.title,
                'body': submission.selftext,
                'created_utc': submission.created_utc,
                'url': submission.url,
                'score': submission.score,
                'num_comments': submission.num_comments,
                'fetched_at': time.time()
            }
            
            # Save to MongoDB
            collection.update_one(
                {'id': post_data['id'], 'type': 'post'}, 
                {'$set': post_data}, 
                upsert=True
            )
            posts_processed += 1
            
            # Process comments
            submission.comments.replace_more(limit=0)
            for comment in submission.comments.list()[:5]:  # Get first 5 comments
                comment_data = {
                    'type': 'comment',
                    'subreddit': subreddit,
                    'post_id': submission.id,
                    'id': comment.id,
                    'author': str(comment.author) if comment.author else '[deleted]',
                    'body': comment.body,
                    'created_utc': comment.created_utc,
                    'score': comment.score,
                    'fetched_at': time.time()
                }
                
                collection.update_one(
                    {'id': comment_data['id'], 'type': 'comment'}, 
                    {'$set': comment_data}, 
                    upsert=True
                )
                comments_processed += 1
        
        # Get final count
        final_count = collection.count_documents({})
        
        return APIResponse(
            success=True,
            message=f"Successfully fetched data from r/{subreddit}",
            data={
                "subreddit": subreddit,
                "posts_processed": posts_processed,
                "comments_processed": comments_processed,
                "total_processed": posts_processed + comments_processed,
                "documents_added": final_count - initial_count,
                "timestamp": datetime.now().isoformat()
            }
        )
    except Exception as e:
        return APIResponse(
            success=False,
            message=f"Failed to fetch from r/{subreddit}: {str(e)}",
            data={"subreddit": subreddit, "timestamp": datetime.now().isoformat()}
        )

@router.get("/stream/analytics", response_model=APIResponse)
async def get_streaming_analytics():
    """Get analytics about the streaming data"""
    try:
        collection = get_mongodb_client()
        
        # Get time-based analytics
        now = time.time()
        one_hour_ago = now - 3600
        one_day_ago = now - 86400
        one_week_ago = now - 604800
        
        # Recent activity
        last_hour = collection.count_documents({"fetched_at": {"$gte": one_hour_ago}})
        last_day = collection.count_documents({"fetched_at": {"$gte": one_day_ago}})
        last_week = collection.count_documents({"fetched_at": {"$gte": one_week_ago}})
        
        # Top subreddits by activity
        pipeline = [
            {"$match": {"fetched_at": {"$gte": one_day_ago}}},
            {"$group": {
                "_id": "$subreddit",
                "count": {"$sum": 1}
            }},
            {"$sort": {"count": -1}},
            {"$limit": 10}
        ]
        
        top_subreddits = list(collection.aggregate(pipeline))
        
        # Emotion distribution
        emotion_pipeline = [
            {"$match": {"emotion.label": {"$exists": True}}},
            {"$group": {
                "_id": "$emotion.label",
                "count": {"$sum": 1}
            }},
            {"$sort": {"count": -1}}
        ]
        
        emotion_distribution = list(collection.aggregate(emotion_pipeline))
        
        return APIResponse(
            success=True,
            message="Streaming analytics retrieved",
            data={
                "activity": {
                    "last_hour": last_hour,
                    "last_day": last_day,
                    "last_week": last_week
                },
                "top_subreddits": [
                    {"subreddit": item["_id"], "count": item["count"]}
                    for item in top_subreddits
                ],
                "emotion_distribution": [
                    {"emotion": item["_id"], "count": item["count"]}
                    for item in emotion_distribution
                ],
                "timestamp": datetime.now().isoformat()
            }
        )
    except Exception as e:
        return APIResponse(
            success=False,
            message=f"Failed to get streaming analytics: {str(e)}",
            data={"timestamp": datetime.now().isoformat()}
        )

# Import asyncio for the streaming endpoint
import asyncio
