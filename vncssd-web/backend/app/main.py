"""
VNCSSDetector Web Service - Main Application
"""
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.config import get_settings
from app.database import init_db
from app.routers import auth, nodes, recordings, alerts, dashboard, users, mobile

settings = get_settings()

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.log_level.upper()),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler."""
    logger.info("Starting VNCSSDetector Web Service...")
    
    # Initialize database
    await init_db()
    logger.info("Database initialized")
    
    yield
    
    logger.info("Shutting down VNCSSDetector Web Service...")


# Create FastAPI application
app = FastAPI(
    title="VNCSSDetector Web Service",
    description="Centralized management service for VNCSSDetector nodes",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs" if settings.debug else None,
    redoc_url="/redoc" if settings.debug else None,
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(users.router, prefix="/api/users", tags=["Users"])
app.include_router(nodes.router, prefix="/api/nodes", tags=["Nodes"])
app.include_router(recordings.router, prefix="/api/recordings", tags=["Recordings"])
app.include_router(alerts.router, prefix="/api/alerts", tags=["Alerts"])
app.include_router(dashboard.router, prefix="/api/dashboard", tags=["Dashboard"])
app.include_router(mobile.router, prefix="/api/mobile", tags=["Mobile"])


@app.get("/api/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": "vncssd-web"}


@app.get("/")
async def root():
    """Root endpoint redirect info."""
    return {
        "message": "VNCSSDetector Web Service",
        "docs": "/docs",
        "health": "/api/health"
    }
