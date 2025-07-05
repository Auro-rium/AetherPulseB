import time
from datetime import datetime
from app.db.redis_connector import get_redis_manager

def monitor_redis_streams():
    """Monitor Redis streams activity"""
    redis_manager = get_redis_manager()
    
    if not redis_manager.health_check():
        print("❌ Redis is not available")
        return
    
    print(f"\n{'='*70}")
    print(f"🔴 REDIS STREAMS MONITOR - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*70}")
    
    # Get stream info
    stream_info = redis_manager.get_stream_info()
    
    print(f"📊 STREAM STATISTICS:")
    for stream_type, count in stream_info.items():
        print(f"   📈 {stream_type}: {count:,} items")
    
    # Get recent activity
    print(f"\n⏰ RECENT ACTIVITY (last 5 minutes):")
    five_minutes_ago = time.time() - (5 * 60)
    
    for stream_type in ['posts', 'comments']:
        recent_items = redis_manager.read_from_stream(stream_type, count=50)
        recent_count = 0
        
        for item in recent_items:
            if float(item.get('redis_timestamp', 0)) >= five_minutes_ago:
                recent_count += 1
        
        print(f"   📝 {stream_type}: {recent_count} items in last 5 min")
    
    print(f"{'='*70}\n")

def continuous_redis_monitor(interval=30):
    """Continuously monitor Redis streams"""
    print(f"🔍 Starting continuous Redis monitoring (checking every {interval} seconds)...")
    print("Press Ctrl+C to stop\n")
    
    try:
        while True:
            monitor_redis_streams()
            time.sleep(interval)
    except KeyboardInterrupt:
        print("\n🛑 Redis monitoring stopped by user")

def get_redis_performance():
    """Get Redis performance metrics"""
    redis_manager = get_redis_manager()
    
    if not redis_manager.health_check():
        return None
    
    try:
        # Get Redis info
        info = redis_manager.redis_client.info()
        
        print(f"\n{'='*50}")
        print(f"🔴 REDIS PERFORMANCE METRICS")
        print(f"{'='*50}")
        print(f"📊 Connected clients: {info.get('connected_clients', 'N/A')}")
        print(f"📊 Used memory: {info.get('used_memory_human', 'N/A')}")
        print(f"📊 Total commands: {info.get('total_commands_processed', 'N/A')}")
        print(f"📊 Keyspace hits: {info.get('keyspace_hits', 'N/A')}")
        print(f"📊 Keyspace misses: {info.get('keyspace_misses', 'N/A')}")
        
        # Calculate hit rate
        hits = info.get('keyspace_hits', 0)
        misses = info.get('keyspace_misses', 0)
        if hits + misses > 0:
            hit_rate = (hits / (hits + misses)) * 100
            print(f"📊 Hit rate: {hit_rate:.2f}%")
        
        print(f"{'='*50}\n")
        
    except Exception as e:
        print(f"❌ Error getting Redis performance: {e}")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        if sys.argv[1] == "continuous":
            continuous_redis_monitor()
        elif sys.argv[1] == "performance":
            get_redis_performance()
        else:
            monitor_redis_streams()
    else:
        monitor_redis_streams() 