"""Health check endpoints for monitoring."""

from fastapi import APIRouter, Request
from typing import Dict, Any
from datetime import datetime
import psutil
import asyncpg

from src.utils.config import settings
from src.database.connection import get_db_pool

router = APIRouter()


@router.get("/")
async def health_check() -> Dict[str, str]:
    """
    Basic health check endpoint.
    
    Returns:
        Simple health status
    """
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat()
    }


@router.get("/detailed")
async def detailed_health_check(request: Request) -> Dict[str, Any]:
    """
    Detailed health check with system information.
    
    Args:
        request: FastAPI request object
        
    Returns:
        Detailed system and application health information
    """
    health_data = {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "application": {
            "name": "Ahrie AI",
            "version": "1.0.0",
            "uptime_seconds": get_uptime()
        },
        "system": {
            "cpu_percent": psutil.cpu_percent(interval=1),
            "memory": {
                "percent": psutil.virtual_memory().percent,
                "available_mb": psutil.virtual_memory().available / (1024 * 1024),
                "total_mb": psutil.virtual_memory().total / (1024 * 1024)
            },
            "disk": {
                "percent": psutil.disk_usage('/').percent,
                "free_gb": psutil.disk_usage('/').free / (1024 * 1024 * 1024)
            }
        },
        "services": {
            "database": await check_database_health(),
            "agents": check_agents_health(request.app.state.agents),
            "telegram_bot": await check_telegram_health()
        }
    }
    
    # Determine overall health status
    if any(service["status"] != "healthy" for service in health_data["services"].values()):
        health_data["status"] = "degraded"
    
    return health_data


async def check_database_health() -> Dict[str, Any]:
    """
    Check database connection health.
    
    Returns:
        Database health status
    """
    try:
        pool = await get_db_pool()
        
        async with pool.acquire() as connection:
            # Simple query to test connection
            result = await connection.fetchval("SELECT 1")
            
            # Get connection pool stats
            stats = {
                "status": "healthy" if result == 1 else "unhealthy",
                "pool_size": pool.get_size(),
                "pool_free": pool.get_idle_size(),
                "response_time_ms": 0  # Would measure actual response time
            }
            
            return stats
            
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e),
            "pool_size": 0,
            "pool_free": 0
        }


def check_agents_health(agents: Dict[str, Any]) -> Dict[str, Any]:
    """
    Check health status of all agents.
    
    Args:
        agents: Dictionary of initialized agents
        
    Returns:
        Agents health status
    """
    try:
        agent_status = {}
        
        for name, agent in agents.items():
            # Check if agent is initialized and responsive
            agent_status[name] = {
                "initialized": agent is not None,
                "type": type(agent).__name__ if agent else "None"
            }
        
        all_healthy = all(status["initialized"] for status in agent_status.values())
        
        return {
            "status": "healthy" if all_healthy else "unhealthy",
            "agents": agent_status,
            "total_agents": len(agents),
            "healthy_agents": sum(1 for s in agent_status.values() if s["initialized"])
        }
        
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e),
            "agents": {},
            "total_agents": 0,
            "healthy_agents": 0
        }


async def check_telegram_health() -> Dict[str, Any]:
    """
    Check Telegram bot connection health.
    
    Returns:
        Telegram bot health status
    """
    try:
        from telegram import Bot
        
        bot = Bot(token=settings.TELEGRAM_BOT_TOKEN)
        
        # Get bot info to test connection
        bot_info = await bot.get_me()
        
        # Get webhook info
        webhook_info = await bot.get_webhook_info()
        
        return {
            "status": "healthy",
            "bot_username": bot_info.username,
            "bot_id": bot_info.id,
            "webhook_set": bool(webhook_info.url),
            "pending_updates": webhook_info.pending_update_count
        }
        
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e),
            "bot_username": None,
            "bot_id": None,
            "webhook_set": False
        }


def get_uptime() -> float:
    """
    Get application uptime in seconds.
    
    Returns:
        Uptime in seconds
    """
    # This would track actual application start time
    # For now, return system uptime
    return psutil.boot_time()


@router.get("/readiness")
async def readiness_check(request: Request) -> Dict[str, Any]:
    """
    Kubernetes readiness probe endpoint.
    
    Args:
        request: FastAPI request object
        
    Returns:
        Readiness status
    """
    try:
        # Check critical services
        db_health = await check_database_health()
        agents_health = check_agents_health(request.app.state.agents)
        
        is_ready = (
            db_health["status"] == "healthy" and
            agents_health["status"] == "healthy"
        )
        
        return {
            "ready": is_ready,
            "timestamp": datetime.now().isoformat(),
            "checks": {
                "database": db_health["status"],
                "agents": agents_health["status"]
            }
        }
        
    except Exception as e:
        return {
            "ready": False,
            "timestamp": datetime.now().isoformat(),
            "error": str(e)
        }


@router.get("/liveness")
async def liveness_check() -> Dict[str, str]:
    """
    Kubernetes liveness probe endpoint.
    
    Returns:
        Liveness status
    """
    return {
        "alive": True,
        "timestamp": datetime.now().isoformat()
    }