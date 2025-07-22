import redis
import json
import time
from typing import Dict, List, Any, Optional
import os

class RedisStreamManager:
    """Manages Redis Streams for Reddit data pipeline"""
    
    def __init__(self, host=None, port=None, db=None, streams=None, username=None, password=None, url=None):
        if url:
            self.redis_client = redis.Redis.from_url(url, decode_responses=True)
        else:
            self.redis_client = redis.Redis(
                host=host,
                port=port,
                db=db if db is not None else 0,
                username=username,
                password=password,
                decode_responses=True
            )
        self.streams = streams or {
            'posts': 'reddit:posts',
            'comments': 'reddit:comments',
            'processed': 'reddit:processed'
        }
        
    def add_to_stream(self, stream_type: str, data: Dict[str, Any]) -> str:
        """Add data to a Redis stream"""
        try:
            stream_name = self.streams.get(stream_type)
            if not stream_name:
                raise ValueError(f"Unknown stream type: {stream_type}")
            
            # Add timestamp and data
            stream_data = {
                'data': json.dumps(data),
                'timestamp': str(time.time()),
                'type': stream_type
            }
            
            # Add to stream
            message_id = self.redis_client.xadd(stream_name, stream_data)
            print(f"✅ Added to {stream_name}: {message_id}")
            return message_id
            
        except Exception as e:
            print(f"❌ Error adding to Redis stream: {e}")
            return None
    
    def read_from_stream(self, stream_type: str, count: int = 10, block: int = 1000) -> List[Dict]:
        """Read data from a Redis stream"""
        try:
            stream_name = self.streams.get(stream_type)
            if not stream_name:
                raise ValueError(f"Unknown stream type: {stream_type}")
            
            # Read from stream
            messages = self.redis_client.xread({stream_name: '0'}, count=count, block=block)
            
            if not messages:
                return []
            
            # Parse messages
            parsed_messages = []
            for stream, message_list in messages:
                for message_id, data in message_list:
                    try:
                        parsed_data = json.loads(data['data'])
                        parsed_data['redis_id'] = message_id
                        parsed_data['redis_timestamp'] = data['timestamp']
                        parsed_messages.append(parsed_data)
                    except json.JSONDecodeError:
                        print(f"❌ Error parsing message {message_id}")
                        continue
            
            return parsed_messages
            
        except Exception as e:
            print(f"❌ Error reading from Redis stream: {e}")
            return []
    
    def get_stream_length(self, stream_type: str) -> int:
        """Get the length of a stream"""
        try:
            stream_name = self.streams.get(stream_type)
            return self.redis_client.xlen(stream_name)
        except Exception as e:
            print(f"❌ Error getting stream length: {e}")
            return 0
    
    def get_stream_info(self) -> Dict[str, int]:
        """Get info about all streams"""
        info = {}
        for stream_type, stream_name in self.streams.items():
            info[stream_type] = self.get_stream_length(stream_type)
        return info
    
    def clear_stream(self, stream_type: str) -> bool:
        """Clear a stream (for testing)"""
        try:
            stream_name = self.streams.get(stream_type)
            self.redis_client.delete(stream_name)
            print(f"🗑️ Cleared stream: {stream_name}")
            return True
        except Exception as e:
            print(f"❌ Error clearing stream: {e}")
            return False
    
    def health_check(self) -> bool:
        """Check if Redis is connected and healthy"""
        try:
            self.redis_client.ping()
            return True
        except Exception as e:
            print(f"❌ Redis health check failed: {e}")
            return False

# Convenience function
def get_redis_manager(host=None, port=None, db=None, streams=None, username=None, password=None, url=None):
    """Get a Redis Stream Manager instance using environment variables if not provided"""
    if url is None:
        url = os.getenv('REDIS_URL')
    if host is None:
        host = os.getenv('REDIS_HOST')
    if port is None:
        port = int(os.getenv('REDIS_PORT')) if os.getenv('REDIS_PORT') else None
    if db is None:
        db = int(os.getenv('REDIS_DB')) if os.getenv('REDIS_DB') else 0
    if username is None:
        username = os.getenv('REDIS_USER')
    if password is None:
        password = os.getenv('REDIS_PASSWORD')
    return RedisStreamManager(host=host, port=port, db=db, streams=streams, username=username, password=password, url=url) 