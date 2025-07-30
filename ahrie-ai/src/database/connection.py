"""Database connection and pool management."""

import asyncpg
from asyncpg import Pool
from typing import Optional
import logging
from contextlib import asynccontextmanager

from src.utils.config import settings

logger = logging.getLogger(__name__)

# Global database pool
_db_pool: Optional[Pool] = None


async def init_db() -> None:
    """
    Initialize database connection pool.
    
    This should be called once during application startup.
    """
    global _db_pool
    
    if _db_pool is not None:
        logger.warning("Database pool already initialized")
        return
    
    try:
        logger.info("Initializing database connection pool...")
        
        # Create connection pool
        _db_pool = await asyncpg.create_pool(
            settings.DATABASE_URL,
            min_size=settings.DB_POOL_MIN_SIZE,
            max_size=settings.DB_POOL_MAX_SIZE,
            max_queries=settings.DB_POOL_MAX_QUERIES,
            max_inactive_connection_lifetime=settings.DB_POOL_MAX_INACTIVE_LIFETIME,
            command_timeout=settings.DB_COMMAND_TIMEOUT,
            server_settings={
                'application_name': 'ahrie_ai',
                'jit': 'off'
            }
        )
        
        # Test connection
        async with _db_pool.acquire() as connection:
            version = await connection.fetchval('SELECT version()')
            logger.info(f"Connected to PostgreSQL: {version}")
        
        logger.info("Database connection pool initialized successfully")
        
    except Exception as e:
        logger.error(f"Failed to initialize database pool: {str(e)}")
        raise


async def close_db() -> None:
    """
    Close database connection pool.
    
    This should be called once during application shutdown.
    """
    global _db_pool
    
    if _db_pool is None:
        logger.warning("Database pool not initialized")
        return
    
    try:
        logger.info("Closing database connection pool...")
        await _db_pool.close()
        _db_pool = None
        logger.info("Database connection pool closed successfully")
        
    except Exception as e:
        logger.error(f"Error closing database pool: {str(e)}")
        raise


async def get_db_pool() -> Pool:
    """
    Get the database connection pool.
    
    Returns:
        asyncpg.Pool: Database connection pool
        
    Raises:
        RuntimeError: If pool is not initialized
    """
    if _db_pool is None:
        raise RuntimeError("Database pool not initialized. Call init_db() first.")
    
    return _db_pool


@asynccontextmanager
async def get_db_connection():
    """
    Context manager for getting a database connection from the pool.
    
    Usage:
        async with get_db_connection() as conn:
            result = await conn.fetch("SELECT * FROM users")
    """
    pool = await get_db_pool()
    
    async with pool.acquire() as connection:
        yield connection


async def execute_query(query: str, *args, timeout: Optional[float] = None):
    """
    Execute a query and return the result.
    
    Args:
        query: SQL query to execute
        *args: Query parameters
        timeout: Query timeout in seconds
        
    Returns:
        Query result
    """
    async with get_db_connection() as conn:
        return await conn.fetch(query, *args, timeout=timeout)


async def execute_many(query: str, args_list: list, timeout: Optional[float] = None):
    """
    Execute a query multiple times with different parameters.
    
    Args:
        query: SQL query to execute
        args_list: List of parameter tuples
        timeout: Query timeout in seconds
    """
    async with get_db_connection() as conn:
        await conn.executemany(query, args_list, timeout=timeout)


async def create_tables() -> None:
    """
    Create database tables if they don't exist.
    
    This is a simple alternative to using Alembic migrations for development.
    """
    create_statements = [
        # Users table
        """
        CREATE TABLE IF NOT EXISTS users (
            id SERIAL PRIMARY KEY,
            telegram_id INTEGER UNIQUE NOT NULL,
            username VARCHAR(255),
            first_name VARCHAR(255),
            last_name VARCHAR(255),
            language_code VARCHAR(10) DEFAULT 'en',
            phone_number VARCHAR(50),
            email VARCHAR(255),
            country VARCHAR(100),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            is_active BOOLEAN DEFAULT TRUE,
            preferences JSONB DEFAULT '{}'::jsonb
        );
        CREATE INDEX IF NOT EXISTS idx_users_telegram_id ON users(telegram_id);
        """,
        
        # Conversations table
        """
        CREATE TABLE IF NOT EXISTS conversations (
            id SERIAL PRIMARY KEY,
            user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
            chat_id INTEGER NOT NULL,
            title VARCHAR(255),
            context JSONB DEFAULT '{}'::jsonb,
            status VARCHAR(50) DEFAULT 'active',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        CREATE INDEX IF NOT EXISTS idx_conversations_user_chat ON conversations(user_id, chat_id);
        """,
        
        # Messages table
        """
        CREATE TABLE IF NOT EXISTS messages (
            id SERIAL PRIMARY KEY,
            conversation_id INTEGER NOT NULL REFERENCES conversations(id) ON DELETE CASCADE,
            role VARCHAR(50) NOT NULL,
            content TEXT NOT NULL,
            message_metadata JSONB DEFAULT '{}'::jsonb,
            tokens_used INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        CREATE INDEX IF NOT EXISTS idx_messages_created_at ON messages(created_at);
        """,
        
        # Clinics table
        """
        CREATE TABLE IF NOT EXISTS clinics (
            id SERIAL PRIMARY KEY,
            name VARCHAR(255) NOT NULL,
            name_ar VARCHAR(255),
            name_ko VARCHAR(255),
            description TEXT,
            description_ar TEXT,
            description_ko TEXT,
            address TEXT NOT NULL,
            district VARCHAR(100),
            city VARCHAR(100) DEFAULT 'Seoul',
            phone VARCHAR(50),
            email VARCHAR(255),
            website VARCHAR(255),
            specialties JSONB DEFAULT '[]'::jsonb,
            certifications JSONB DEFAULT '[]'::jsonb,
            languages_supported JSONB DEFAULT '[]'::jsonb,
            halal_friendly BOOLEAN DEFAULT FALSE,
            arabic_support BOOLEAN DEFAULT FALSE,
            female_staff_available BOOLEAN DEFAULT FALSE,
            rating FLOAT DEFAULT 0.0,
            review_count INTEGER DEFAULT 0,
            price_range VARCHAR(50),
            operating_hours JSONB DEFAULT '{}'::jsonb,
            images JSONB DEFAULT '[]'::jsonb,
            latitude FLOAT,
            longitude FLOAT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            is_active BOOLEAN DEFAULT TRUE
        );
        """,
        
        # Procedures table
        """
        CREATE TABLE IF NOT EXISTS procedures (
            id SERIAL PRIMARY KEY,
            name VARCHAR(255) NOT NULL UNIQUE,
            name_ar VARCHAR(255),
            name_ko VARCHAR(255),
            category VARCHAR(100) NOT NULL,
            description TEXT,
            description_ar TEXT,
            description_ko TEXT,
            duration_min INTEGER,
            duration_max INTEGER,
            recovery_days_min INTEGER,
            recovery_days_max INTEGER,
            anesthesia_type VARCHAR(100),
            price_range_min INTEGER,
            price_range_max INTEGER,
            risks JSONB DEFAULT '[]'::jsonb,
            benefits JSONB DEFAULT '[]'::jsonb,
            preparation_steps JSONB DEFAULT '[]'::jsonb,
            aftercare_steps JSONB DEFAULT '[]'::jsonb,
            images JSONB DEFAULT '[]'::jsonb,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            is_active BOOLEAN DEFAULT TRUE
        );
        """,
        
        # Clinic procedures association table
        """
        CREATE TABLE IF NOT EXISTS clinic_procedures (
            id SERIAL PRIMARY KEY,
            clinic_id INTEGER NOT NULL REFERENCES clinics(id) ON DELETE CASCADE,
            procedure_id INTEGER NOT NULL REFERENCES procedures(id) ON DELETE CASCADE,
            price_min INTEGER,
            price_max INTEGER,
            special_notes TEXT,
            is_available BOOLEAN DEFAULT TRUE
        );
        CREATE INDEX IF NOT EXISTS idx_clinic_procedures ON clinic_procedures(clinic_id, procedure_id);
        """,
        
        # Reviews table
        """
        CREATE TABLE IF NOT EXISTS reviews (
            id SERIAL PRIMARY KEY,
            user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
            clinic_id INTEGER REFERENCES clinics(id) ON DELETE CASCADE,
            procedure_id INTEGER REFERENCES procedures(id) ON DELETE CASCADE,
            rating FLOAT NOT NULL,
            title VARCHAR(255),
            content TEXT,
            pros JSONB DEFAULT '[]'::jsonb,
            cons JSONB DEFAULT '[]'::jsonb,
            youtube_video_id VARCHAR(50),
            youtube_channel VARCHAR(255),
            source VARCHAR(50) DEFAULT 'direct',
            language VARCHAR(10) DEFAULT 'en',
            sentiment_score FLOAT,
            helpful_count INTEGER DEFAULT 0,
            verified BOOLEAN DEFAULT FALSE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            is_active BOOLEAN DEFAULT TRUE
        );
        CREATE INDEX IF NOT EXISTS idx_reviews_clinic_rating ON reviews(clinic_id, rating);
        CREATE INDEX IF NOT EXISTS idx_reviews_procedure_rating ON reviews(procedure_id, rating);
        """,
        
        # Halal places table
        """
        CREATE TABLE IF NOT EXISTS halal_places (
            id SERIAL PRIMARY KEY,
            name VARCHAR(255) NOT NULL,
            name_ar VARCHAR(255),
            type VARCHAR(50) NOT NULL,
            cuisine VARCHAR(100),
            certification VARCHAR(100),
            address TEXT NOT NULL,
            district VARCHAR(100),
            phone VARCHAR(50),
            operating_hours JSONB DEFAULT '{}'::jsonb,
            delivery_available BOOLEAN DEFAULT FALSE,
            latitude FLOAT,
            longitude FLOAT,
            distance_from_gangnam FLOAT,
            rating FLOAT DEFAULT 0.0,
            price_range VARCHAR(50),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            is_active BOOLEAN DEFAULT TRUE
        );
        """,
        
        # Translation cache table
        """
        CREATE TABLE IF NOT EXISTS translation_cache (
            id SERIAL PRIMARY KEY,
            source_text TEXT NOT NULL,
            source_language VARCHAR(10) NOT NULL,
            target_language VARCHAR(10) NOT NULL,
            translated_text TEXT NOT NULL,
            translation_service VARCHAR(50) DEFAULT 'google',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        CREATE INDEX IF NOT EXISTS idx_translation_lookup 
            ON translation_cache(source_language, target_language, source_text);
        """
    ]
    
    async with get_db_connection() as conn:
        for statement in create_statements:
            try:
                await conn.execute(statement)
            except Exception as e:
                logger.error(f"Error creating table: {str(e)}")
                raise
    
    logger.info("Database tables created successfully")


async def health_check() -> bool:
    """
    Check database health.
    
    Returns:
        bool: True if database is healthy
    """
    try:
        async with get_db_connection() as conn:
            result = await conn.fetchval("SELECT 1")
            return result == 1
    except Exception as e:
        logger.error(f"Database health check failed: {str(e)}")
        return False