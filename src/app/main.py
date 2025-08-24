from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from loguru import logger
import os

# Import routers
from .routers.resume_router import router as resume_router

# create the Fast API app instance with simple metadata
app = FastAPI(
    title="Resume Tailor API", 
    version="0.0.1",
    description="AI-powered resume tailoring service that optimizes resumes for specific job descriptions",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify your frontend domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
app.mount("/static", StaticFiles(directory="src/app/static"), name="static")

# Include routers
app.include_router(resume_router)

# health check endpoint
# open http://127.0.0.1:8000/health in a browser once the server is running
@app.get("/health")
def health():
    logger.info("Health check called")
    return {"status": "ok", "service": "Resume Tailor API"}

@app.get("/")
def root():
    return {
        "message": "Welcome to Resume Tailor API",
        "version": "0.0.1",
        "docs": "/docs",
        "endpoints": {
            "health": "/health",
            "resume_analysis": "/resume/analyze",
            "file_analysis": "/resume/analyze-file",
            "detailed_analysis": "/resume/detailed-analysis",
            "keywords": "/resume/keywords"
        }
    }