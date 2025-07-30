"""Main entry point for Ahrie AI application."""

import asyncio
import sys
from pathlib import Path

# Add parent directory to Python path
sys.path.append(str(Path(__file__).parent.parent))

import uvicorn
from src.api.main import app
from src.utils.config import settings
from src.utils.logger import setup_logger

logger = setup_logger(__name__)


def main():
    """Run the application."""
    logger.info(f"Starting {settings.APP_NAME} v{settings.APP_VERSION}")
    logger.info(f"Environment: {settings.ENVIRONMENT}")
    logger.info(f"Debug mode: {settings.DEBUG}")
    
    # Configure uvicorn
    config = uvicorn.Config(
        app,
        host=settings.API_HOST,
        port=settings.API_PORT,
        reload=settings.DEBUG,
        log_level=settings.LOG_LEVEL.lower(),
        access_log=settings.DEBUG,
        use_colors=True
    )
    
    # Create server
    server = uvicorn.Server(config)
    
    # Run server
    try:
        asyncio.run(server.serve())
    except KeyboardInterrupt:
        logger.info("Shutting down gracefully...")
    except Exception as e:
        logger.error(f"Fatal error: {str(e)}")
        raise


if __name__ == "__main__":
    main()