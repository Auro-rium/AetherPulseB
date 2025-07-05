import time
from datetime import datetime, timedelta
from pymongo import MongoClient
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

MONGO_URI = os.getenv('MONGO_URI', 'mongodb://localhost:27017/')
DB_NAME = os.getenv('DB_NAME', 'reddit_stream')
COLLECTION_NAME = os.getenv('COLLECTION_NAME', 'posts_comments')

def get_db_stats():
    """Get current database statistics"""
    try:
        client = MongoClient(MONGO_URI)
        db = client[DB_NAME]
        collection = db[COLLECTION_NAME]
        
        # Total counts
        total_posts = collection.count_documents({'type': 'post'})
        total_comments = collection.count_documents({'type': 'comment'})
        total_items = total_posts + total_comments
        
        # Recent activity (last 10 minutes)
        ten_minutes_ago = time.time() - (10 * 60)
        recent_posts = collection.count_documents({
            'type': 'post', 
            'fetched_at': {'$gte': ten_minutes_ago}
        })
        recent_comments = collection.count_documents({
            'type': 'comment', 
            'fetched_at': {'$gte': ten_minutes_ago}
        })
        
        # Last 5 minutes activity
        five_minutes_ago = time.time() - (5 * 60)
        very_recent_posts = collection.count_documents({
            'type': 'post', 
            'fetched_at': {'$gte': five_minutes_ago}
        })
        very_recent_comments = collection.count_documents({
            'type': 'comment', 
            'fetched_at': {'$gte': five_minutes_ago}
        })
        
        # Latest items
        latest_items = list(collection.find().sort('fetched_at', -1).limit(5))
        
        print(f"\n{'='*70}")
        print(f"📊 MONGODB MONITOR - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"{'='*70}")
        print(f"📈 TOTAL DATABASE:")
        print(f"   📝 Posts: {total_posts:,}")
        print(f"   💬 Comments: {total_comments:,}")
        print(f"   📊 Total: {total_items:,}")
        print(f"\n⏰ RECENT ACTIVITY:")
        print(f"   📝 Last 10 min - Posts: {recent_posts} | Comments: {recent_comments}")
        print(f"   📝 Last 5 min  - Posts: {very_recent_posts} | Comments: {very_recent_comments}")
        print(f"\n🆕 LATEST ITEMS:")
        for item in latest_items:
            timestamp = datetime.fromtimestamp(item['fetched_at']).strftime('%H:%M:%S')
            if item['type'] == 'post':
                print(f"   📝 [{timestamp}] r/{item['subreddit']} - {item['title'][:60]}...")
            else:
                print(f"   💬 [{timestamp}] r/{item['subreddit']} - {item['body'][:60]}...")
        print(f"{'='*70}\n")
        
        return {
            'total_posts': total_posts,
            'total_comments': total_comments,
            'recent_posts': recent_posts,
            'recent_comments': recent_comments,
            'very_recent_posts': very_recent_posts,
            'very_recent_comments': very_recent_comments
        }
        
    except Exception as e:
        print(f"❌ Error connecting to MongoDB: {e}")
        return None

def monitor_continuously(interval=60):
    """Monitor database continuously"""
    print(f"🔍 Starting continuous monitoring (checking every {interval} seconds)...")
    print("Press Ctrl+C to stop\n")
    
    try:
        while True:
            get_db_stats()
            time.sleep(interval)
    except KeyboardInterrupt:
        print("\n🛑 Monitoring stopped by user")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "continuous":
        monitor_continuously()
    else:
        get_db_stats() 