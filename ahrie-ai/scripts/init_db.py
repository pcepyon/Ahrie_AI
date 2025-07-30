#!/usr/bin/env python3
"""Initialize database with tables and sample data."""

import asyncio
import sys
from pathlib import Path

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from src.database.connection import init_db, close_db, create_tables
from src.utils.logger import setup_logger

logger = setup_logger(__name__)


async def initialize_database():
    """Initialize database with tables and sample data."""
    try:
        logger.info("Initializing database...")
        
        # Initialize connection pool
        await init_db()
        
        # Create tables
        logger.info("Creating tables...")
        await create_tables()
        
        logger.info("Database initialization complete!")
        
    except Exception as e:
        logger.error(f"Error initializing database: {str(e)}")
        raise
    finally:
        await close_db()


if __name__ == "__main__":
    asyncio.run(initialize_database())