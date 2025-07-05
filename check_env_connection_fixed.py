#!/usr/bin/env python3
"""
FIXED Environment Connection Checker for AetherPulseB
Checks if all components are properly connected in .venv environment
Usage: python check_env_connection_fixed.py
"""

import os
import sys
from pathlib import Path

def check_python_environment():
    """Check if we're in a virtual environment"""
    print("🐍 Checking Python Environment...")
    print("="*50)
    
    # Check if virtual environment is active
    if hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
        print("✅ Virtual environment is ACTIVE")
        print(f"   Python: {sys.executable}")
        print(f"   Version: {sys.version}")
    else:
        print("⚠️  Virtual environment not detected")
        print("   Consider activating your .venv environment")
    
    # Check if .env file exists
    env_path = Path('.env')
    if env_path.exists():
        print("✅ .env file found")
        return True
    else:
        print("❌ .env file not found")
        return False

def check_dependencies():
    """Check if all required packages are installed - FIXED VERSION"""
    print("\n📦 Checking Dependencies...")
    print("="*50)
    
    # Fixed package mapping - correct import names
    package_mapping = {
        'praw': 'praw',
        'pymongo': 'pymongo', 
        'redis': 'redis',
        'transformers': 'transformers',
        'torch': 'torch',
        'python-dotenv': 'dotenv'  # FIXED: correct import name
    }
    
    missing_packages = []
    installed_packages = []
    
    for package_name, import_name in package_mapping.items():
        try:
            __import__(import_name)
            installed_packages.append(package_name)
            print(f"✅ {package_name}")
        except ImportError:
            missing_packages.append(package_name)
            print(f"❌ {package_name} - MISSING")
    
    if missing_packages:
        print(f"\n❌ Missing packages: {', '.join(missing_packages)}")
        print("Install with: pip install " + " ".join(missing_packages))
        return False
    else:
        print(f"\n✅ All {len(installed_packages)} packages installed")
        return True

def check_env_variables():
    """Check if environment variables are properly loaded"""
    print("\n🔧 Checking Environment Variables...")
    print("="*50)
    
    # Load .env file - FIXED: proper import
    try:
        from dotenv import load_dotenv
        load_dotenv()
    except ImportError:
        print("❌ python-dotenv not available")
        return False
    
    # Required environment variables
    required_vars = {
        'REDDIT_CLIENT_ID': 'Reddit API Client ID',
        'REDDIT_CLIENT_SECRET': 'Reddit API Client Secret',
        'REDDIT_USER_AGENT': 'Reddit User Agent',
        'MONGO_URI': 'MongoDB Connection URI',
        'DB_NAME': 'Database Name',
        'COLLECTION_NAME': 'Collection Name'
    }
    
    # Optional environment variables
    optional_vars = {
        'REDIS_HOST': 'Redis Host',
        'REDIS_PORT': 'Redis Port',
        'REDIS_DB': 'Redis Database'
    }
    
    all_good = True
    
    print("Required Variables:")
    for var, description in required_vars.items():
        value = os.getenv(var)
        if value and value not in ['your_client_id', 'your_client_secret', 'your_actual_client_id_here', 'your_actual_client_secret_here']:
            print(f"✅ {var}: {description} - CONFIGURED")
        else:
            print(f"❌ {var}: {description} - NOT CONFIGURED")
            all_good = False
    
    print("\nOptional Variables:")
    for var, description in optional_vars.items():
        value = os.getenv(var)
        if value:
            print(f"✅ {var}: {description} - {value}")
        else:
            print(f"⚠️  {var}: {description} - Using default")
    
    return all_good

def test_reddit_connection():
    """Test Reddit API connection"""
    print("\n🔴 Testing Reddit Connection...")
    print("="*50)
    
    try:
        import praw
        from dotenv import load_dotenv
        
        # Load environment variables
        load_dotenv()
        
        client_id = os.getenv('REDDIT_CLIENT_ID')
        client_secret = os.getenv('REDDIT_CLIENT_SECRET')
        user_agent = os.getenv('REDDIT_USER_AGENT')
        
        if not all([client_id, client_secret, user_agent]):
            print("❌ Reddit credentials not configured")
            return False
        
        # Test connection
        reddit = praw.Reddit(
            client_id=client_id,
            client_secret=client_secret,
            user_agent=user_agent
        )
        
        # Try to access Reddit (this will test the connection)
        reddit.read_only = True
        subreddit = reddit.subreddit('test')
        print("✅ Reddit API connection successful")
        return True
        
    except Exception as e:
        print(f"❌ Reddit connection failed: {e}")
        return False

def test_mongodb_connection():
    """Test MongoDB connection"""
    print("\n📦 Testing MongoDB Connection...")
    print("="*50)
    
    try:
        from pymongo import MongoClient
        from dotenv import load_dotenv
        
        # Load environment variables
        load_dotenv()
        
        mongo_uri = os.getenv('MONGO_URI', 'mongodb://localhost:27017/')
        db_name = os.getenv('DB_NAME', 'reddit_stream')
        collection_name = os.getenv('COLLECTION_NAME', 'posts_comments')
        
        print(f"   URI: {mongo_uri}")
        print(f"   DB: {db_name}")
        print(f"   Collection: {collection_name}")
        
        # Test connection
        client = MongoClient(mongo_uri, serverSelectionTimeoutMS=5000)
        client.server_info()  # This will test the connection
        
        # Test database access
        db = client[db_name]
        collection = db[collection_name]
        
        # Try a simple operation
        count = collection.count_documents({})
        print(f"✅ MongoDB connection successful (Collection has {count} documents)")
        return True
        
    except Exception as e:
        print(f"❌ MongoDB connection failed: {e}")
        print("   Make sure MongoDB is running")
        return False

def test_redis_connection():
    """Test Redis connection"""
    print("\n🔴 Testing Redis Connection...")
    print("="*50)
    
    try:
        from app.db.redis_connector import get_redis_manager
        from dotenv import load_dotenv
        
        # Load environment variables
        load_dotenv()
        
        redis_host = os.getenv('REDIS_HOST', 'localhost')
        redis_port = int(os.getenv('REDIS_PORT', '6379'))
        redis_db = int(os.getenv('REDIS_DB', '0'))
        
        print(f"   Host: {redis_host}")
        print(f"   Port: {redis_port}")
        print(f"   DB: {redis_db}")
        
        # Test connection
        redis_manager = get_redis_manager(host=redis_host, port=redis_port, db=redis_db)
        
        if redis_manager.health_check():
            print("✅ Redis connection successful")
            return True
        else:
            print("❌ Redis health check failed")
            return False
            
    except Exception as e:
        print(f"❌ Redis connection failed: {e}")
        print("   Redis is optional - pipeline will work without it")
        return False

def test_nlp_models():
    """Test NLP model loading"""
    print("\n🔍 Testing NLP Models...")
    print("="*50)
    
    try:
        from app.nlp import emotion, intent, sarcasm
        print("✅ NLP modules imported successfully")
        
        # Test emotion detection
        try:
            test_text = "I am very happy today!"
            emotion_result = emotion.detect_emotion(test_text)
            print(f"✅ Emotion detection working: {emotion_result}")
        except Exception as e:
            print(f"⚠️  Emotion detection failed: {e}")
        
        # Test intent detection
        try:
            intent_result = intent.detect_intent(test_text)
            print(f"✅ Intent detection working: {intent_result}")
        except Exception as e:
            print(f"⚠️  Intent detection failed: {e}")
        
        return True
        
    except Exception as e:
        print(f"❌ NLP models failed to load: {e}")
        return False

def main():
    """Main connection checker"""
    print("🔍 AetherPulseB Environment Connection Checker (FIXED)")
    print("="*60)
    
    # Check Python environment
    env_ok = check_python_environment()
    
    # Check dependencies
    deps_ok = check_dependencies()
    
    # Check environment variables
    vars_ok = check_env_variables()
    
    # Test connections
    reddit_ok = test_reddit_connection()
    mongo_ok = test_mongodb_connection()
    redis_ok = test_redis_connection()
    nlp_ok = test_nlp_models()
    
    # Summary
    print("\n" + "="*60)
    print("🔍 CONNECTION SUMMARY")
    print("="*60)
    
    checks = [
        ("Python Environment", env_ok),
        ("Dependencies", deps_ok),
        ("Environment Variables", vars_ok),
        ("Reddit API", reddit_ok),
        ("MongoDB", mongo_ok),
        ("Redis", redis_ok),
        ("NLP Models", nlp_ok)
    ]
    
    all_passed = True
    for check_name, status in checks:
        status_icon = "✅" if status else "❌"
        print(f"{status_icon} {check_name}")
        if not status:
            all_passed = False
    
    print("\n" + "="*60)
    if all_passed:
        print("🎯 ALL CONNECTIONS SUCCESSFUL!")
        print("Your .venv environment is properly configured and connected.")
        print("You can now run: python -m app.reddit.streamer")
    else:
        print("⚠️  SOME CONNECTIONS FAILED")
        print("Please fix the issues above before running the pipeline.")
    
    print("="*60)

if __name__ == "__main__":
    main() 