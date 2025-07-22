import time
import os
from dotenv import load_dotenv
import praw
from app.reddit.processor import process_and_store

# Load environment variables from .env file
load_dotenv()

# Load from environment variables with fallbacks
REDDIT_CLIENT_ID = os.getenv('REDDIT_CLIENT_ID', 'your_client_id')
REDDIT_CLIENT_SECRET = os.getenv('REDDIT_CLIENT_SECRET', 'your_client_secret')
REDDIT_USER_AGENT = os.getenv('REDDIT_USER_AGENT', 'AetherPulseB/0.1 by YourUsername')
MONGO_URI = os.getenv('MONGO_URI', 'mongodb://localhost:27017/')
DB_NAME = os.getenv('DB_NAME', 'reddit_stream')
COLLECTION_NAME = os.getenv('COLLECTION_NAME', 'posts_comments')

# Redis Configuration (from environment only)
REDIS_HOST = os.getenv('REDIS_HOST')
REDIS_PORT = int(os.getenv('REDIS_PORT')) if os.getenv('REDIS_PORT') else None
REDIS_DB = int(os.getenv('REDIS_DB')) if os.getenv('REDIS_DB') else None
REDIS_STREAMS = {
    'posts': os.getenv('REDIS_POSTS_STREAM'),
    'comments': os.getenv('REDIS_COMMENTS_STREAM'),
    'processed': os.getenv('REDIS_PROCESSED_STREAM')
}

TOP_SUBREDDITS = [
    'AskReddit', 'worldnews', 'funny', 'gaming', 'aww', 'pics', 'science', 'movies', 'todayilearned',
    'news', 'gifs', 'askscience', 'EarthPorn', 'books', 'television', 'Music', 'explainlikeimfive',
    'sports', 'space', 'food', 'Jokes', 'lifeprotips', 'IAmA', 'Showerthoughts', 'Futurology',
    'nottheonion', 'Documentaries', 'dataisbeautiful', 'GetMotivated', 'Art', 'DIY', 'gadgets',
    'history', 'personalfinance', 'philosophy', 'WritingPrompts', 'UpliftingNews', 'nosleep',
    'OldSchoolCool', 'InternetIsBeautiful', 'creepy', 'tifu'
]

def validate_credentials():
    """Validate that Reddit credentials are properly set"""
    if REDDIT_CLIENT_ID in ['your_client_id', ''] or REDDIT_CLIENT_SECRET in ['your_client_secret', '']:
        print("❌ REDDIT CREDENTIALS NOT CONFIGURED!")
        print("="*60)
        print("Please create a .env file with your Reddit API credentials:")
        print("")
        print("REDDIT_CLIENT_ID=your_actual_client_id")
        print("REDDIT_CLIENT_SECRET=your_actual_client_secret")
        print("REDDIT_USER_AGENT=AetherPulseB/0.1 by YourUsername")
        print("")
        print("Get your credentials from: https://www.reddit.com/prefs/apps")
        print("="*60)
        return False
    return True

if __name__ == '__main__':
    print(f"🚀 Starting AetherPulseB Reddit Streamer")
    print(f"📊 Target subreddits: {len(TOP_SUBREDDITS)}")
    print(f"🔴 Redis: {REDIS_HOST}:{REDIS_PORT}")
    print(f"📦 MongoDB: {MONGO_URI}")
    print(f"{'='*60}")
    
    # Validate credentials before starting
    if not validate_credentials():
        exit(1)
    
    print("✅ Credentials validated successfully!")
    
    reddit = praw.Reddit(
        client_id=REDDIT_CLIENT_ID,
        client_secret=REDDIT_CLIENT_SECRET,
        user_agent=REDDIT_USER_AGENT
    )
    
    cycle = 1
    while True:
        print(f"\n🔄 CYCLE {cycle} - {time.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"{'='*60}")
        
        # Set use_redis to True now that Redis is ready
        use_redis = True
        try:
            process_and_store(
                TOP_SUBREDDITS, 
                reddit, 
                MONGO_URI, 
                DB_NAME, 
                COLLECTION_NAME,
                use_redis=use_redis
            )
        except Exception as e:
            print(f"\u274c Error in cycle {cycle}: {e}")
            print("\ud83d\udd04 Retrying in 5 minutes...")
        
        print(f"⏰ Sleeping for 5 minutes... (Next cycle: {cycle + 1})")
        cycle += 1
        time.sleep(300)