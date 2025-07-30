"""Logging configuration and utilities."""

import logging
import logging.handlers
import sys
from pathlib import Path
from typing import Optional
import json
from datetime import datetime

from .config import settings


class JSONFormatter(logging.Formatter):
    """Custom JSON formatter for structured logging."""
    
    def format(self, record: logging.LogRecord) -> str:
        """Format log record as JSON."""
        log_data = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno
        }
        
        # Add exception info if present
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)
        
        # Add extra fields
        for key, value in record.__dict__.items():
            if key not in ["name", "msg", "args", "created", "filename", "funcName",
                          "levelname", "levelno", "lineno", "module", "exc_info",
                          "exc_text", "stack_info", "pathname", "processName",
                          "process", "threadName", "thread", "getMessage"]:
                log_data[key] = value
        
        return json.dumps(log_data)


def setup_logger(
    name: Optional[str] = None,
    level: Optional[str] = None,
    log_file: Optional[Path] = None,
    use_json: bool = False
) -> logging.Logger:
    """
    Set up logger with console and file handlers.
    
    Args:
        name: Logger name (default: root logger)
        level: Log level (default: from settings)
        log_file: Log file path (default: from settings)
        use_json: Use JSON formatting
        
    Returns:
        Configured logger
    """
    logger = logging.getLogger(name)
    
    # Set level
    log_level = level or settings.LOG_LEVEL
    logger.setLevel(getattr(logging, log_level.upper()))
    
    # Remove existing handlers
    logger.handlers = []
    
    # Create formatters
    if use_json:
        formatter = JSONFormatter()
    else:
        formatter = logging.Formatter(settings.LOG_FORMAT)
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.DEBUG if settings.DEBUG else logging.INFO)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # File handler
    if log_file or not settings.is_development:
        file_path = log_file or settings.get_log_file_path(name or "app")
        
        # Rotating file handler (10MB per file, keep 5 backups)
        file_handler = logging.handlers.RotatingFileHandler(
            file_path,
            maxBytes=10 * 1024 * 1024,  # 10MB
            backupCount=5,
            encoding="utf-8"
        )
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    
    # Prevent propagation to avoid duplicate logs
    logger.propagate = False
    
    return logger


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger instance.
    
    Args:
        name: Logger name
        
    Returns:
        Logger instance
    """
    return logging.getLogger(name)


class LoggerAdapter(logging.LoggerAdapter):
    """
    Custom logger adapter for adding context to logs.
    """
    
    def __init__(self, logger: logging.Logger, extra: dict):
        """Initialize adapter with logger and extra context."""
        super().__init__(logger, extra)
    
    def process(self, msg: str, kwargs: dict) -> tuple:
        """Process log message and add extra context."""
        # Add extra context to all log messages
        if "extra" not in kwargs:
            kwargs["extra"] = {}
        
        kwargs["extra"].update(self.extra)
        
        return msg, kwargs


def get_logger_with_context(name: str, **context) -> LoggerAdapter:
    """
    Get a logger with additional context.
    
    Args:
        name: Logger name
        **context: Additional context to include in logs
        
    Returns:
        Logger adapter with context
    """
    logger = get_logger(name)
    return LoggerAdapter(logger, context)


# Configure root logger
root_logger = setup_logger()

# Configure specific loggers
setup_logger("ahrie_ai", level="DEBUG" if settings.DEBUG else "INFO")
setup_logger("agno", level="INFO")
setup_logger("telegram", level="INFO")
setup_logger("uvicorn", level="INFO")
setup_logger("fastapi", level="INFO")

# Reduce noise from third-party libraries
logging.getLogger("httpx").setLevel(logging.WARNING)
logging.getLogger("asyncio").setLevel(logging.WARNING)
logging.getLogger("googleapiclient").setLevel(logging.WARNING)