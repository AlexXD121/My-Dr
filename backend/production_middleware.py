"""
Production-ready middleware for My Dr AI Medical Assistant
Includes security, monitoring, and performance optimizations
"""

import time
import logging
from typing import Callable
from fastapi import Request, Response, HTTPException
from fastapi.middleware.base import BaseHTTPMiddleware
from starlette.middleware.base import RequestResponseEndpoint
import asyncio
from datetime import datetime, timedelta
import json

logger = logging.getLogger(__name__)

class ProductionSecurityMiddleware(BaseHTTPMiddleware):
    """Enhanced security middleware for production"""
    
    def __init__(self, app, max_request_size: int = 16 * 1024 * 1024):  # 16MB
        super().__init__(app)
        self.max_request_size = max_request_size
        self.rate_limit_store = {}
        
    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        # Check request size
        if hasattr(request, 'headers') and 'content-length' in request.headers:
            content_length = int(request.headers['content-length'])
            if content_length > self.max_request_size:
                raise HTTPException(status_code=413, detail="Request too large")
        
        # Rate limiting (basic implementation)
        client_ip = request.client.host if request.client else "unknown"
        current_time = datetime.now()
        
        if client_ip in self.rate_limit_store:
            last_request_time, request_count = self.rate_limit_store[client_ip]
            if current_time - last_request_time < timedelta(minutes=1):
                if request_count > 60:  # 60 requests per minute
                    raise HTTPException(status_code=429, detail="Rate limit exceeded")
                self.rate_limit_store[client_ip] = (last_request_time, request_count + 1)
            else:
                self.rate_limit_store[client_ip] = (current_time, 1)
        else:
            self.rate_limit_store[client_ip] = (current_time, 1)
        
        # Clean old entries (basic cleanup)
        if len(self.rate_limit_store) > 10000:
            cutoff_time = current_time - timedelta(hours=1)
            self.rate_limit_store = {
                ip: (time, count) for ip, (time, count) in self.rate_limit_store.items()
                if time > cutoff_time
            }
        
        # Process request
        start_time = time.time()
        response = await call_next(request)
        process_time = time.time() - start_time
        
        # Add security headers
        response.headers["X-Process-Time"] = str(process_time)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        
        return response


class PerformanceMonitoringMiddleware(BaseHTTPMiddleware):
    """Monitor API performance and log slow requests"""
    
    def __init__(self, app, slow_request_threshold: float = 2.0):
        super().__init__(app)
        self.slow_request_threshold = slow_request_threshold
        
    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        start_time = time.time()
        
        # Process request
        response = await call_next(request)
        
        # Calculate processing time
        process_time = time.time() - start_time
        
        # Log slow requests
        if process_time > self.slow_request_threshold:
            logger.warning(
                f"Slow request detected: {request.method} {request.url.path} "
                f"took {process_time:.2f}s (threshold: {self.slow_request_threshold}s)"
            )
        
        # Add performance headers
        response.headers["X-Response-Time"] = f"{process_time:.3f}s"
        
        return response


class HealthCheckMiddleware(BaseHTTPMiddleware):
    """Add health check capabilities"""
    
    def __init__(self, app):
        super().__init__(app)
        self.start_time = datetime.now()
        
    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        # Handle health check requests
        if request.url.path == "/health":
            uptime = datetime.now() - self.start_time
            health_data = {
                "status": "healthy",
                "uptime_seconds": int(uptime.total_seconds()),
                "timestamp": datetime.now().isoformat(),
                "version": "1.0.0"
            }
            return Response(
                content=json.dumps(health_data),
                media_type="application/json",
                status_code=200
            )
        
        return await call_next(request)


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """Enhanced request logging for production"""
    
    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        start_time = time.time()
        
        # Log request
        logger.info(
            f"Request: {request.method} {request.url.path} "
            f"from {request.client.host if request.client else 'unknown'}"
        )
        
        # Process request
        response = await call_next(request)
        
        # Log response
        process_time = time.time() - start_time
        logger.info(
            f"Response: {response.status_code} "
            f"in {process_time:.3f}s"
        )
        
        return response


class ErrorHandlingMiddleware(BaseHTTPMiddleware):
    """Global error handling for production"""
    
    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        try:
            return await call_next(request)
        except Exception as e:
            logger.error(f"Unhandled error in {request.url.path}: {str(e)}", exc_info=True)
            
            # Return generic error response (don't expose internal details)
            error_response = {
                "error": "Internal server error",
                "message": "An unexpected error occurred. Please try again later.",
                "timestamp": datetime.now().isoformat(),
                "path": request.url.path
            }
            
            return Response(
                content=json.dumps(error_response),
                media_type="application/json",
                status_code=500
            )


def add_production_middleware(app):
    """Add all production middleware to the FastAPI app"""
    
    # Add middleware in reverse order (last added = first executed)
    app.add_middleware(ErrorHandlingMiddleware)
    app.add_middleware(RequestLoggingMiddleware)
    app.add_middleware(HealthCheckMiddleware)
    app.add_middleware(PerformanceMonitoringMiddleware, slow_request_threshold=2.0)
    app.add_middleware(ProductionSecurityMiddleware, max_request_size=16 * 1024 * 1024)
    
    logger.info("Production middleware added successfully")