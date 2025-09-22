from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import logging
from pathlib import Path

# Import main router
from app.api.router import router as api_router

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="Zenith Mental Wellness Platform",
    description="AI-powered mental wellness platform with multilingual support",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify allowed origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
static_path = Path(__file__).parent.parent / "static"
app.mount("/static", StaticFiles(directory=static_path), name="static")

# Include main API router
app.include_router(api_router, prefix="/api")

# Root endpoint - serve the main HTML
@app.get("/")
async def root():
    return FileResponse(static_path / "index.html")

# Health check endpoint
@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "service": "Zenith Mental Wellness Platform",
        "version": "1.0.0"
    }

# API documentation redirect
@app.get("/api")
async def api_docs():
    return {
        "message": "Zenith Mental Wellness Platform API",
        "documentation": "/docs",
        "redoc": "/redoc",
        "endpoints": {
            "auth": "/api/auth",
            "chat": "/api/chat",
            "crisis": "/api/crisis",
            "community": "/api/community",
            "spiritual": "/api/spiritual",
            "meditation": "/api/meditation"
        }
    }

@app.on_event("startup")
async def startup_event():
    logger.info("🚀 Zenith Mental Wellness Platform is starting up...")
    logger.info(f"📁 Static files served from: {static_path}")
    logger.info("✨ All systems initialized successfully!")

@app.on_event("shutdown")
async def shutdown_event():
    logger.info("👋 Zenith Mental Wellness Platform is shutting down...")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)