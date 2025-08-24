#!/usr/bin/env python3
"""
Simple test script to verify the Resume Tailor setup
"""
import sys
import os
from pathlib import Path

def test_imports():
    """Test that all required modules can be imported"""
    print("🔍 Testing imports...")
    
    try:
        from src.app.main import app
        print("✅ FastAPI app imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import FastAPI app: {e}")
        return False
    
    try:
        from src.app.models import ResumeAnalysisRequest
        print("✅ Pydantic models imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import models: {e}")
        return False
    
    try:
        from src.app.services import AIService, FileService
        print("✅ Services imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import services: {e}")
        return False
    
    return True

def test_environment():
    """Test environment configuration"""
    print("\n🔍 Testing environment...")
    
    # Check if .env file exists
    env_file = Path(".env")
    if env_file.exists():
        print("✅ .env file found")
    else:
        print("⚠️  .env file not found - you'll need to create one with your OpenAI API key")
    
    # Check OpenAI API key
    from dotenv import load_dotenv
    load_dotenv()
    
    api_key = os.getenv("OPENAI_API_KEY")
    if api_key and api_key != "your_openai_api_key_here":
        print("✅ OpenAI API key found")
    else:
        print("⚠️  OpenAI API key not configured - set OPENAI_API_KEY in your .env file")
    
    return True

def test_file_structure():
    """Test that all required files exist"""
    print("\n🔍 Testing file structure...")
    
    required_files = [
        "src/app/main.py",
        "src/app/models.py",
        "src/app/routers/resume_router.py",
        "src/app/services/ai_service.py",
        "src/app/services/file_service.py",
        "src/app/static/index.html",
        "src/app/static/script.js",
        "requirements.txt",
        "README.md"
    ]
    
    all_exist = True
    for file_path in required_files:
        if Path(file_path).exists():
            print(f"✅ {file_path}")
        else:
            print(f"❌ {file_path} - missing")
            all_exist = False
    
    return all_exist

def test_dependencies():
    """Test that required dependencies are available"""
    print("\n🔍 Testing dependencies...")
    
    required_packages = [
        "fastapi",
        "uvicorn",
        "openai",
        "pydantic",
        "loguru",
        "multipart",
        "dotenv"
    ]
    
    all_available = True
    for package in required_packages:
        try:
            __import__(package)
            print(f"✅ {package}")
        except ImportError:
            print(f"❌ {package} - not installed")
            all_available = False
    
    return all_available

def main():
    """Run all tests"""
    print("🧪 Resume Tailor Setup Test")
    print("=" * 40)
    
    tests = [
        test_imports,
        test_environment,
        test_file_structure,
        test_dependencies
    ]
    
    results = []
    for test in tests:
        try:
            result = test()
            results.append(result)
        except Exception as e:
            print(f"❌ Test failed with error: {e}")
            results.append(False)
    
    print("\n" + "=" * 40)
    print("📊 Test Results Summary")
    print("=" * 40)
    
    if all(results):
        print("🎉 All tests passed! Your setup is ready.")
        print("\n🚀 To start the application, run:")
        print("   python run.py")
        print("\n📖 Or with uvicorn directly:")
        print("   uvicorn src.app.main:app --reload --host 0.0.0.0 --port 8000")
    else:
        print("⚠️  Some tests failed. Please check the issues above.")
        print("\n📋 Next steps:")
        print("   1. Install missing dependencies: pip install -r requirements.txt")
        print("   2. Create a .env file with your OpenAI API key")
        print("   3. Run this test again")
    
    return all(results)

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

