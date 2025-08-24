#!/usr/bin/env python3
"""
Startup script for Resume Tailor API
"""
import uvicorn
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

if __name__ == "__main__":
    # Check if OpenAI API key is set
    if not os.getenv("OPENAI_API_KEY"):
        print("⚠️  Warning: OPENAI_API_KEY not found in environment variables.")
        print("   Please create a .env file with your OpenAI API key:")
        print("   OPENAI_API_KEY=your_api_key_here")
        print()
    
    # Run the application
    print("🚀 Starting Resume Tailor API...")
    print("📖 API Documentation: http://localhost:8000/docs")
    print("🌐 Web Interface: http://localhost:8000/static/index.html")
    print("💚 Health Check: http://localhost:8000/health")
    print()
    
    uvicorn.run(
        "src.app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )

