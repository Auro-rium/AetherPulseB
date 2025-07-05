#!/usr/bin/env python3
"""
AetherPulseB Setup Script
Helps users configure their environment for Reddit streaming
"""

import os
import sys
from pathlib import Path

def create_env_file():
    """Create a .env file with template values"""
    env_content = """# Reddit API Credentials
# Get these from https://www.reddit.com/prefs/apps
REDDIT_CLIENT_ID=your_actual_client_id_here
REDDIT_CLIENT_SECRET=your_actual_client_secret_here
REDDIT_USER_AGENT=AetherPulseB/0.1 by YourUsername

# MongoDB Configuration
MONGO_URI=mongodb://localhost:27017/
DB_NAME=reddit_stream
COLLECTION_NAME=posts_comments

# Redis Configuration
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0
REDIS_POSTS_STREAM=reddit:posts
REDIS_COMMENTS_STREAM=reddit:comments
REDIS_PROCESSED_STREAM=reddit:processed
"""
    
    env_path = Path('.env')
    if env_path.exists():
        print("⚠️  .env file already exists!")
        response = input("Do you want to overwrite it? (y/N): ")
        if response.lower() != 'y':
            print("Setup cancelled.")
            return False
    
    try:
        with open('.env', 'w') as f:
            f.write(env_content)
        print("✅ Created .env file with template values")
        return True
    except Exception as e:
        print(f"❌ Error creating .env file: {e}")
        return False

def check_requirements():
    """Check if required packages are installed"""
    required_packages = [
        'praw', 'pymongo', 'redis', 'transformers', 
        'torch', 'python-dotenv'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print("❌ Missing required packages:")
        for package in missing_packages:
            print(f"   - {package}")
        print("\nInstall them with:")
        print(f"pip install {' '.join(missing_packages)}")
        return False
    else:
        print("✅ All required packages are installed")
        return True

def validate_setup():
    """Validate the current setup"""
    print("\n🔍 Validating setup...")
    
    # Check if .env exists
    if not Path('.env').exists():
        print("❌ .env file not found")
        return False
    
    # Load environment variables
    from dotenv import load_dotenv
    load_dotenv()
    
    # Check Reddit credentials
    client_id = os.getenv('REDDIT_CLIENT_ID')
    client_secret = os.getenv('REDDIT_CLIENT_SECRET')
    
    if client_id in ['your_actual_client_id_here', None, '']:
        print("❌ Reddit credentials not configured")
        return False
    
    if client_secret in ['your_actual_client_secret_here', None, '']:
        print("❌ Reddit credentials not configured")
        return False
    
    print("✅ Reddit credentials configured")
    
    # Test MongoDB connection
    try:
        from pymongo import MongoClient
        mongo_uri = os.getenv('MONGO_URI', 'mongodb://localhost:27017/')
        client = MongoClient(mongo_uri, serverSelectionTimeoutMS=5000)
        client.server_info()
        print("✅ MongoDB connection successful")
    except Exception as e:
        print(f"⚠️  MongoDB connection failed: {e}")
        print("   Make sure MongoDB is running")
    
    # Test Redis connection
    try:
        from app.db.redis_connector import get_redis_manager
        redis_manager = get_redis_manager()
        if redis_manager.health_check():
            print("✅ Redis connection successful")
        else:
            print("⚠️  Redis not available (will use fallback mode)")
    except Exception as e:
        print(f"⚠️  Redis connection failed: {e}")
        print("   Redis is optional - pipeline will work without it")
    
    return True

def main():
    """Main setup function"""
    print("🚀 AetherPulseB Setup")
    print("="*50)
    
    # Check requirements
    if not check_requirements():
        print("\n❌ Please install missing packages and run setup again")
        return
    
    # Create .env file if needed
    if not Path('.env').exists():
        print("\n📝 Creating .env file...")
        if not create_env_file():
            return
        print("\n📋 Next steps:")
        print("1. Edit the .env file with your Reddit API credentials")
        print("2. Get credentials from: https://www.reddit.com/prefs/apps")
        print("3. Run this setup script again to validate")
        return
    
    # Validate setup
    if validate_setup():
        print("\n🎉 Setup is complete!")
        print("You can now run: python -m app.reddit.streamer")
    else:
        print("\n❌ Setup validation failed")
        print("Please check the issues above and try again")

if __name__ == "__main__":
    main() 