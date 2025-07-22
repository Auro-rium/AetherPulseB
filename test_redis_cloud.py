import os
from dotenv import load_dotenv
import redis

load_dotenv()

r = redis.Redis(
    host=os.getenv('REDIS_HOST'),
    port=int(os.getenv('REDIS_PORT')),
    username=os.getenv('REDIS_USER'),
    password=os.getenv('REDIS_PASSWORD'),
    db=int(os.getenv('REDIS_DB', 0)),
    ssl=True
)

try:
    r.set('foo', 'bar')
    value = r.get('foo')
    print('Redis connection successful! Value:', value.decode())
except Exception as e:
    print('Redis connection failed:', e) 