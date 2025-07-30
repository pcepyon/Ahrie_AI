"""Custom middleware for the FastAPI application."""

from fastapi import Request, Response
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from typing import Callable
import time
import logging
import uuid
from datetime import datetime

logger = logging.getLogger(__name__)


class LoggingMiddleware(BaseHTTPMiddleware):
    """
    Middleware for logging HTTP requests and responses.
    """
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """
        Log incoming requests and outgoing responses.
        
        Args:
            request: FastAPI request object
            call_next: Next middleware or route handler
            
        Returns:
            HTTP response
        """
        # Generate request ID for tracing
        request_id = str(uuid.uuid4())
        request.state.request_id = request_id
        
        # Log request
        start_time = time.time()
        logger.info(
            f"Incoming request: {request.method} {request.url.path} "
            f"[ID: {request_id}] [Client: {request.client.host}]"
        )
        
        # Process request
        response = await call_next(request)
        
        # Calculate processing time
        process_time = time.time() - start_time
        
        # Add custom headers
        response.headers["X-Request-ID"] = request_id
        response.headers["X-Process-Time"] = str(process_time)
        
        # Log response
        logger.info(
            f"Outgoing response: {response.status_code} "
            f"[ID: {request_id}] [Time: {process_time:.3f}s]"
        )
        
        return response


class ErrorHandlerMiddleware(BaseHTTPMiddleware):
    """
    Middleware for handling uncaught exceptions.
    """
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """
        Catch and handle uncaught exceptions.
        
        Args:
            request: FastAPI request object
            call_next: Next middleware or route handler
            
        Returns:
            HTTP response
        """
        try:
            response = await call_next(request)
            return response
            
        except Exception as e:
            # Log the error
            request_id = getattr(request.state, "request_id", "unknown")
            logger.error(
                f"Unhandled exception in request {request_id}: {str(e)}",
                exc_info=True
            )
            
            # Return error response
            return JSONResponse(
                status_code=500,
                content={
                    "error": "Internal server error",
                    "message": "An unexpected error occurred",
                    "request_id": request_id,
                    "timestamp": datetime.now().isoformat()
                }
            )


class RateLimitMiddleware(BaseHTTPMiddleware):
    """
    Simple rate limiting middleware.
    """
    
    def __init__(self, app, max_requests: int = 60, window_seconds: int = 60):
        super().__init__(app)
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.request_counts = {}  # Simple in-memory storage
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """
        Implement rate limiting per IP address.
        
        Args:
            request: FastAPI request object
            call_next: Next middleware or route handler
            
        Returns:
            HTTP response
        """
        # Skip rate limiting for health checks
        if request.url.path.startswith("/api/v1/health"):
            return await call_next(request)
        
        # Get client IP
        client_ip = request.client.host
        current_time = time.time()
        
        # Clean old entries
        self._clean_old_entries(current_time)
        
        # Check rate limit
        if client_ip in self.request_counts:
            requests_in_window = [
                timestamp for timestamp in self.request_counts[client_ip]
                if current_time - timestamp < self.window_seconds
            ]
            
            if len(requests_in_window) >= self.max_requests:
                logger.warning(f"Rate limit exceeded for IP: {client_ip}")
                return JSONResponse(
                    status_code=429,
                    content={
                        "error": "Rate limit exceeded",
                        "message": f"Maximum {self.max_requests} requests per {self.window_seconds} seconds",
                        "retry_after": self.window_seconds
                    },
                    headers={
                        "Retry-After": str(self.window_seconds),
                        "X-RateLimit-Limit": str(self.max_requests),
                        "X-RateLimit-Remaining": "0",
                        "X-RateLimit-Reset": str(int(current_time + self.window_seconds))
                    }
                )
            
            self.request_counts[client_ip] = requests_in_window + [current_time]
        else:
            self.request_counts[client_ip] = [current_time]
        
        # Process request
        response = await call_next(request)
        
        # Add rate limit headers
        remaining = self.max_requests - len(self.request_counts[client_ip])
        response.headers["X-RateLimit-Limit"] = str(self.max_requests)
        response.headers["X-RateLimit-Remaining"] = str(max(0, remaining))
        response.headers["X-RateLimit-Reset"] = str(int(current_time + self.window_seconds))
        
        return response
    
    def _clean_old_entries(self, current_time: float) -> None:
        """
        Clean old entries from request counts.
        
        Args:
            current_time: Current timestamp
        """
        for ip in list(self.request_counts.keys()):
            self.request_counts[ip] = [
                timestamp for timestamp in self.request_counts[ip]
                if current_time - timestamp < self.window_seconds
            ]
            
            if not self.request_counts[ip]:
                del self.request_counts[ip]


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """
    Middleware to add security headers to responses.
    """
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """
        Add security headers to the response.
        
        Args:
            request: FastAPI request object
            call_next: Next middleware or route handler
            
        Returns:
            HTTP response with security headers
        """
        response = await call_next(request)
        
        # Add security headers
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        
        # Content Security Policy (adjust as needed)
        response.headers["Content-Security-Policy"] = (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline' 'unsafe-eval'; "
            "style-src 'self' 'unsafe-inline'; "
            "img-src 'self' data: https:; "
            "font-src 'self' data:; "
            "connect-src 'self' https://api.telegram.org"
        )
        
        return response