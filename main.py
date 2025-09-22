"""Main FastAPI application for Zenith Mental Wellness Platform"""

import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from app.core.config import settings, validate_settings
from app.api import router as api_router
import uvicorn

# Configure logging
logging.basicConfig(
    level=logging.INFO if settings.APP_DEBUG else logging.WARNING,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    description=settings.APP_DESCRIPTION,
    version=settings.APP_VERSION,
    debug=settings.APP_DEBUG
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routers
app.include_router(api_router.router, prefix="/api")

# Mount static files
app.mount("/static", StaticFiles(directory=str(settings.STATIC_DIR)), name="static")

@app.on_event("startup")
async def startup_event():
    """Initialize services on startup"""
    logger.info(f"Starting {settings.APP_NAME} v{settings.APP_VERSION}")
    
    # Validate settings
    warnings = validate_settings()
    if warnings:
        for warning in warnings:
            logger.warning(f"Configuration warning: {warning}")
    
    # Initialize services (they're singletons, so just importing them initializes them)
    from app.services.firebase_service import firebase_service
    from app.services.ai_service import ai_service
    
    logger.info("Services initialized successfully")

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    logger.info("Shutting down application")

@app.get("/")
async def root():
    """Serve the main application page"""
    return FileResponse(str(settings.STATIC_DIR / "index.html"))

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "environment": settings.APP_ENV
    }

@app.get("/api")
async def api_info():
    """API information endpoint"""
    return {
        "name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "description": settings.APP_DESCRIPTION,
        "endpoints": {
            "auth": "/api/auth",
            "chat": "/api/chat",
            "crisis": "/api/crisis",
            "community": "/api/community",
            "spiritual": "/api/spiritual",
            "meditation": "/api/meditation"
        },
        "supported_languages": settings.SUPPORTED_LANGUAGES
    }

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.APP_DEBUG,
        log_level="info" if settings.APP_DEBUG else "warning"
    )