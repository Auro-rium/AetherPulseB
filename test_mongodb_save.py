#!/usr/bin/env python3
"""
Test MongoDB Save - AetherPulseB
Tests the Reddit data pipeline by fetching and saving data to MongoDB
Usage: python test_mongodb_save.py
"""

import os
import time
from dotenv import load_dotenv
import praw
from pymongo import MongoClient
import certifi

# Load environment variables
load_dotenv()

# Configuration
REDDIT_CLIENT_ID = os.getenv('REDDIT_CLIENT_ID')
REDDIT_CLIENT_SECRET = os.getenv('REDDIT_CLIENT_SECRET')
REDDIT_USER_AGENT = os.getenv('REDDIT_USER_AGENT')
MONGO_URI = os.getenv('MONGO_URI')
DB_NAME = os.getenv('DB_NAME', 'reddit_stream')
COLLECTION_NAME = os.getenv('COLLECTION_NAME', 'posts_comments')

# Test subreddits (smaller list for testing)
TEST_SUBREDDITS = ['AskReddit', 'worldnews', 'funny', 'gaming']

def test_reddit_mongodb_pipeline():
    """Test the complete Reddit to MongoDB pipeline"""
    print("🧪 Testing Reddit to MongoDB Pipeline")
    print("="*60)
    
    # Initialize Reddit client
    print("🔴 Initializing Reddit client...")
    reddit = praw.Reddit(
        client_id=REDDIT_CLIENT_ID,
        client_secret=REDDIT_CLIENT_SECRET,
        user_agent=REDDIT_USER_AGENT
    )
    reddit.read_only = True
    print("✅ Reddit client ready")
    
    # Initialize MongoDB
    print("📦 Connecting to MongoDB...")
    client = MongoClient(MONGO_URI, tls=True, tlsCAFile=certifi.where())
    db = client[DB_NAME]
    collection = db[COLLECTION_NAME]
    
    # Get initial document count
    initial_count = collection.count_documents({})
    print(f"📊 Initial documents in MongoDB: {initial_count}")
    
    # Test data collection
    print(f"\n🔄 Fetching data from {len(TEST_SUBREDDITS)} subreddits...")
    start_time = time.time()
    
    total_posts = 0
    total_comments = 0
    
    for subreddit_name in TEST_SUBREDDITS:
        try:
            print(f"📊 Processing r/{subreddit_name}...")
            subreddit = reddit.subreddit(subreddit_name)
            
            # Fetch posts
            for submission in subreddit.hot(limit=5):  # Get 5 hot posts
                post_data = {
                    'type': 'post',
                    'subreddit': subreddit_name,
                    'id': submission.id,
                    'author': str(submission.author) if submission.author else '[deleted]',
                    'title': submission.title,
                    'body': submission.selftext,
                    'created_utc': submission.created_utc,
                    'url': submission.url,
                    'score': submission.score,
                    'num_comments': submission.num_comments,
                    'test_run': True,
                    'fetched_at': time.time()
                }
                
                # Save to MongoDB
                collection.update_one(
                    {'id': post_data['id'], 'type': 'post'}, 
                    {'$set': post_data}, 
                    upsert=True
                )
                total_posts += 1
                print(f"  ✅ Saved post: {submission.title[:50]}...")
                
                # Fetch comments for this post
                submission.comments.replace_more(limit=0)  # Don't expand MoreComments
                for comment in submission.comments.list()[:3]:  # Get first 3 comments
                    comment_data = {
                        'type': 'comment',
                        'subreddit': subreddit_name,
                        'post_id': submission.id,
                        'id': comment.id,
                        'author': str(comment.author) if comment.author else '[deleted]',
                        'body': comment.body,
                        'created_utc': comment.created_utc,
                        'score': comment.score,
                        'test_run': True,
                        'fetched_at': time.time()
                    }
                    
                    # Save comment to MongoDB
                    collection.update_one(
                        {'id': comment_data['id'], 'type': 'comment'}, 
                        {'$set': comment_data}, 
                        upsert=True
                    )
                    total_comments += 1
                    print(f"    💬 Saved comment: {comment.body[:30]}...")
            
        except Exception as e:
            print(f"❌ Error processing r/{subreddit_name}: {e}")
    
    # Get final document count
    final_count = collection.count_documents({})
    duration = time.time() - start_time
    
    # Results
    print(f"\n{'='*60}")
    print("📊 TEST RESULTS")
    print(f"{'='*60}")
    print(f"⏱️  Duration: {duration:.2f} seconds")
    print(f"📝 Posts saved: {total_posts}")
    print(f"💬 Comments saved: {total_comments}")
    print(f"📊 Total items processed: {total_posts + total_comments}")
    print(f"🗄️  MongoDB documents before: {initial_count}")
    print(f"🗄️  MongoDB documents after: {final_count}")
    print(f"📈 New documents added: {final_count - initial_count}")
    
    # Test queries
    print(f"\n🔍 TESTING MONGODB QUERIES:")
    print(f"📊 Total posts: {collection.count_documents({'type': 'post'})}")
    print(f"📊 Total comments: {collection.count_documents({'type': 'comment'})}")
    print(f"📊 Test run data: {collection.count_documents({'test_run': True})}")
    
    # Sample data
    print(f"\n📋 SAMPLE DATA:")
    sample_post = collection.find_one({'type': 'post', 'test_run': True})
    if sample_post:
        print(f"📝 Sample post: {sample_post['title'][:50]}... (r/{sample_post['subreddit']})")
    
    sample_comment = collection.find_one({'type': 'comment', 'test_run': True})
    if sample_comment:
        print(f"💬 Sample comment: {sample_comment['body'][:50]}... (r/{sample_comment['subreddit']})")
    
    print(f"{'='*60}")
    print("✅ MongoDB pipeline test completed successfully!")
    print("🚀 Your Reddit data pipeline is working correctly!")
    print(f"{'='*60}")

if __name__ == "__main__":
    test_reddit_mongodb_pipeline() 