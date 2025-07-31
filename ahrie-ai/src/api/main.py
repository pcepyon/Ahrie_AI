"""Main FastAPI application for Ahrie AI."""

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging
from typing import Dict, Any

from src.utils.config import settings
from src.utils.logger import setup_logger
from src.database.connection import init_db, close_db
from .routes import webhook, health
from .middleware import LoggingMiddleware, ErrorHandlerMiddleware

logger = setup_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan manager for startup and shutdown events.
    """
    # Startup
    logger.info("Starting Ahrie AI API server...")
    
    # Initialize database
    await init_db()
    
    # Initialize Enhanced Team-based orchestrator V2
    from src.agents.team_orchestrator_v2 import AhrieTeamOrchestratorV2
    
    # Initialize the enhanced team orchestrator
    team_orchestrator = AhrieTeamOrchestratorV2()
    
    # Store in app state
    app.state.team_orchestrator = team_orchestrator
    
    # For backward compatibility, also store as orchestrator
    app.state.orchestrator = team_orchestrator
    
    logger.info("All systems initialized successfully")
    
    yield
    
    # Shutdown
    logger.info("Shutting down Ahrie AI API server...")
    await close_db()
    logger.info("Shutdown complete")


app = FastAPI(
    title="Ahrie AI - K-Beauty Medical Tourism Chatbot",
    description="AI-powered chatbot for Saudi and UAE clients seeking K-Beauty medical procedures",
    version="1.0.0",
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add custom middleware
app.add_middleware(LoggingMiddleware)
app.add_middleware(ErrorHandlerMiddleware)

# Include routers
app.include_router(webhook.router, prefix="/api/v1/webhook", tags=["webhook"])
app.include_router(health.router, prefix="/api/v1/health", tags=["health"])


@app.get("/")
async def root() -> Dict[str, str]:
    """Root endpoint."""
    return {
        "message": "Welcome to Ahrie AI API",
        "version": "1.0.0",
        "status": "operational"
    }


@app.get("/api/v1/info")
async def api_info() -> Dict[str, Any]:
    """Get API information."""
    return {
        "name": "Ahrie AI",
        "description": "K-Beauty Medical Tourism Chatbot",
        "version": "1.0.0",
        "features": [
            "Multi-agent system with Agno framework",
            "Telegram bot integration",
            "Medical procedure consultation",
            "YouTube review analysis",
            "Cultural and halal guidance",
            "Multi-language support (AR, EN, KO)"
        ],
        "agents": [
            "Orchestrator Agent (Master Conductor)",
            "Coordinator Agent (General Conversation)",
            "Medical Expert Agent",
            "Review Analyst Agent",
            "Cultural Advisor Agent"
        ]
    }


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "src.api.main:app",
        host=settings.API_HOST,
        port=settings.API_PORT,
        reload=settings.DEBUG,
        log_level="info"
    )