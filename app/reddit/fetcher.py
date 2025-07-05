# fetcher.py
import praw
from app.db.redis_connector import get_redis_manager

def fetch_reddit_data(subreddits, reddit_client, post_limit=10, comment_limit=20, redis_manager=None):
    """
    Fetch posts and comments from subreddits and stream to Redis.
    Returns generator for backward compatibility.
    """
    if redis_manager is None:
        redis_manager = get_redis_manager()
    
    print(f"🔄 Fetching data from {len(subreddits)} subreddits...")
    
    for subreddit_name in subreddits:
        try:
            subreddit = reddit_client.subreddit(subreddit_name)
            print(f"📊 Processing r/{subreddit_name}...")
            
            # Fetch new posts
            for submission in subreddit.new(limit=post_limit):
                post_data = {
                    'type': 'post',
                    'subreddit': subreddit_name,
                    'id': submission.id,
                    'author': str(submission.author),
                    'title': submission.title,
                    'body': submission.selftext,
                    'created_utc': submission.created_utc,
                    'url': submission.url,
                    'score': submission.score,
                    'num_comments': submission.num_comments
                }
                
                # Stream to Redis
                redis_manager.add_to_stream('posts', post_data)
                yield post_data
            
            # Fetch new comments
            for comment in subreddit.comments(limit=comment_limit):
                comment_data = {
                    'type': 'comment',
                    'subreddit': subreddit_name,
                    'id': comment.id,
                    'author': str(comment.author),
                    'body': comment.body,
                    'created_utc': comment.created_utc,
                    'score': comment.score,
                    'parent_id': comment.parent_id,
                    'link_id': comment.link_id
                }
                
                # Stream to Redis
                redis_manager.add_to_stream('comments', comment_data)
                yield comment_data
                
        except Exception as e:
            print(f"❌ Error processing r/{subreddit_name}: {e}")
            continue

def fetch_from_redis(stream_type='posts', count=10, redis_manager=None):
    """
    Fetch data from Redis streams.
    Useful for consumers that want to process from Redis.
    """
    if redis_manager is None:
        redis_manager = get_redis_manager()
    
    return redis_manager.read_from_stream(stream_type, count=count)

def get_redis_stats(redis_manager=None):
    """
    Get statistics about Redis streams.
    """
    if redis_manager is None:
        redis_manager = get_redis_manager()
    
    return redis_manager.get_stream_info()