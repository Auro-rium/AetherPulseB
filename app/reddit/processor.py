import time
import re
from pymongo import MongoClient
from app.reddit.fetcher import fetch_reddit_data, fetch_from_redis, get_redis_stats
from app.nlp import emotion, intent, sarcasm
from app.db.redis_connector import get_redis_manager

# Filtering helpers
BOT_PATTERNS = [r'bot$', r'auto', r'moderator', r'helper', r'notifier']
SPAM_PATTERNS = [r'http[s]?://', r'free', r'giveaway', r'win', r'prize']

def is_bot(author: str) -> bool:
    if not author:
        return True
    return any(re.search(pattern, author, re.IGNORECASE) for pattern in BOT_PATTERNS)

def is_spam(text: str) -> bool:
    if not text or len(text) < 5:
        return True
    return any(re.search(pattern, text, re.IGNORECASE) for pattern in SPAM_PATTERNS)

def analyze_emotion(text: str) -> str:
    return emotion.detect_emotion(text)

def analyze_intent(text: str) -> str:
    return intent.detect_intent(text)

def analyze_sarcasm(text: str) -> bool:
    return sarcasm.is_sarcastic(text)

def process_and_store(subreddits, reddit_client, mongo_uri, db_name, collection_name, use_redis=True):
    """
    Process and store Reddit data with Redis streaming support.
    """
    # Initialize connections
    mongo = MongoClient(mongo_uri)
    db = mongo[db_name]
    collection = db[collection_name]
    
    redis_manager = None
    if use_redis:
        redis_manager = get_redis_manager()
        if not redis_manager.health_check():
            print("⚠️ Redis not available, falling back to direct processing")
            use_redis = False
    
    # Track statistics
    total_processed = 0
    posts_processed = 0
    comments_processed = 0
    posts_stored = 0
    comments_stored = 0
    start_time = time.time()
    
    print(f"\n{'='*60}")
    print(f"🔄 Starting Reddit data collection at {time.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"📊 Processing {len(subreddits)} subreddits...")
    print(f"🚀 Redis streaming: {'✅ Enabled' if use_redis else '❌ Disabled'}")
    print(f"{'='*60}")
    
    # Process data
    for item in fetch_reddit_data(subreddits, reddit_client, redis_manager=redis_manager):
        total_processed += 1
        
        if item['type'] == 'post':
            posts_processed += 1
        else:
            comments_processed += 1
            
        if item['type'] == 'post':
            text = (item['title'] or '') + ' ' + (item['body'] or '')
        else:
            text = item['body'] or ''
            
        if is_bot(item['author']) or is_spam(text):
            continue
            
        # Process with NLP
        item['emotion'] = analyze_emotion(text)
        item['intent'] = analyze_intent(text)
        item['sarcasm'] = analyze_sarcasm(text)
        item['fetched_at'] = time.time()
        
        # Store in MongoDB
        try:
            result = collection.update_one(
                {'id': item['id'], 'type': item['type']}, 
                {'$set': item}, 
                upsert=True
            )
            
            if result.upserted_id:
                # New item was inserted
                if item['type'] == 'post':
                    posts_stored += 1
                    print(f"✅ NEW POST: r/{item['subreddit']} - {item['title'][:50]}...")
                else:
                    comments_stored += 1
                    print(f"💬 NEW COMMENT: r/{item['subreddit']} - {item['body'][:50]}...")
            else:
                # Item was updated (already existed)
                if item['type'] == 'post':
                    print(f"🔄 UPDATED POST: r/{item['subreddit']} - {item['title'][:50]}...")
                else:
                    print(f"🔄 UPDATED COMMENT: r/{item['subreddit']} - {item['body'][:50]}...")
                    
        except Exception as e:
            print(f"❌ Error storing {item['type']}: {e}")
    
    end_time = time.time()
    duration = end_time - start_time
    
    # Print summary
    print(f"\n{'='*60}")
    print(f"📈 COLLECTION SUMMARY ({time.strftime('%Y-%m-%d %H:%M:%S')})")
    print(f"{'='*60}")
    print(f"⏱️  Duration: {duration:.2f} seconds")
    print(f"📊 Total processed: {total_processed}")
    print(f"📝 Posts processed: {posts_processed} | stored: {posts_stored}")
    print(f"💬 Comments processed: {comments_processed} | stored: {comments_stored}")
    print(f"🗑️  Filtered out: {total_processed - posts_stored - comments_stored}")
    print(f"📊 Success rate: {((posts_stored + comments_stored) / total_processed * 100):.1f}%")
    
    # Redis stats if available
    if use_redis and redis_manager:
        redis_stats = get_redis_stats(redis_manager)
        print(f"\n🔴 REDIS STREAMS:")
        for stream_type, count in redis_stats.items():
            print(f"   📊 {stream_type}: {count} items")
    
    print(f"{'='*60}\n")

def process_from_redis(mongo_uri, db_name, collection_name, stream_type='posts', count=10):
    """
    Process data directly from Redis streams.
    Useful for separate processing pipelines.
    """
    mongo = MongoClient(mongo_uri)
    db = mongo[db_name]
    collection = db[collection_name]
    
    redis_manager = get_redis_manager()
    
    print(f"🔄 Processing {count} items from Redis stream: {stream_type}")
    
    items = fetch_from_redis(stream_type, count, redis_manager)
    
    for item in items:
        if item['type'] == 'post':
            text = (item['title'] or '') + ' ' + (item['body'] or '')
        else:
            text = item['body'] or ''
            
        if is_bot(item['author']) or is_spam(text):
            continue
            
        # Process with NLP
        item['emotion'] = analyze_emotion(text)
        item['intent'] = analyze_intent(text)
        item['sarcasm'] = analyze_sarcasm(text)
        item['fetched_at'] = time.time()
        
        # Store in MongoDB
        collection.update_one(
            {'id': item['id'], 'type': item['type']}, 
            {'$set': item}, 
            upsert=True
        )
        
        print(f"✅ Processed {item['type']} from Redis: {item['subreddit']}")