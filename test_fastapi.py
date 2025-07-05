#!/usr/bin/env python3
"""
Simple FastAPI test to check for import errors
"""

import sys
import traceback

def test_imports():
    """Test all imports"""
    print("Testing imports...")
    
    try:
        print("✓ Importing FastAPI...")
        from fastapi import FastAPI
        print("✓ FastAPI imported successfully")
    except Exception as e:
        print(f"❌ FastAPI import failed: {e}")
        return False
    
    try:
        print("✓ Importing app.api.endpoints.query...")
        from app.api.endpoints import query
        print("✓ Query endpoints imported successfully")
    except Exception as e:
        print(f"❌ Query endpoints import failed: {e}")
        traceback.print_exc()
        return False
    
    try:
        print("✓ Importing app.api.endpoints.stream...")
        from app.api.endpoints import stream
        print("✓ Stream endpoints imported successfully")
    except Exception as e:
        print(f"❌ Stream endpoints import failed: {e}")
        traceback.print_exc()
        return False
    
    try:
        print("✓ Importing app.api.schemas...")
        from app.api import schemas
        print("✓ Schemas imported successfully")
    except Exception as e:
        print(f"❌ Schemas import failed: {e}")
        traceback.print_exc()
        return False
    
    return True

def test_main_app():
    """Test creating the main app"""
    try:
        print("✓ Creating FastAPI app...")
        from app.main import app
        print("✓ FastAPI app created successfully")
        return True
    except Exception as e:
        print(f"❌ FastAPI app creation failed: {e}")
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🧪 Testing AetherPulseB FastAPI Setup")
    print("="*50)
    
    if test_imports():
        print("\n✅ All imports successful!")
        
        if test_main_app():
            print("✅ FastAPI app creation successful!")
            print("\n🚀 Ready to start the server!")
            print("Run: python -m app.main")
        else:
            print("❌ FastAPI app creation failed!")
    else:
        print("❌ Import tests failed!") 