from fastapi import FastAPI
from loguru import logger

# create the Fast API app instance with simple metadata
app = FastAPI(title="Resume Tailor API", version="0.0.1")

# heath check endpoint
# open http://127.0.0.1:8000/health in a browser once the server is running
@app.get("/health")
def health():
    logger.info("Health check called")
    return {"status": "ok"}