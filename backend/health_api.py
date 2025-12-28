"""
Health Monitoring API for MyDoc AI Medical Assistant

This module provides health monitoring endpoints for the enhanced AI services,
including AI provider status, emergency detection statistics, and overall system health.
"""

import logging
from datetime import datetime, timezone
from typing import Dict, Any
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel

from enhanced_medical_ai import enhanced_medical_ai
from ai_service_manager import ai_service_manager
from emergency_detector import emergency_detector

logger = logging.getLogger(__name__)

# Create router
router = APIRouter(prefix="/health", tags=["health"])


class HealthResponse(BaseModel):
    """Health check response model"""
    status: str
    timestamp: str
    details: Dict[str, Any]


class ServiceStatusResponse(BaseModel):
    """Service status response model"""
    overall_status: str
    timestamp: str
    ai_service: Dict[str, Any]
    emergency_detector: Dict[str, Any]
    provider_health: Dict[str, str]
    components: Dict[str, str]


@router.get("/", response_model=HealthResponse)
async def health_check():
    """Basic health check endpoint"""
    try:
        # Get basic service status
        ai_status = ai_service_manager.get_service_status()
        
        overall_status = "healthy" if ai_status["available_count"] > 0 else "degraded"
        
        return HealthResponse(
            status=overall_status,
            timestamp=datetime.now(timezone.utc).isoformat(),
            details={
                "available_providers": ai_status["available_count"],
                "total_providers": ai_status["total_count"],
                "last_health_check": ai_status["last_health_check"]
            }
        )
        
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Health check failed"
        )


@router.get("/detailed", response_model=ServiceStatusResponse)
async def detailed_health_check():
    """Detailed health check with full service status"""
    try:
        service_health = await enhanced_medical_ai.get_service_health()
        
        return ServiceStatusResponse(
            overall_status=service_health["overall_status"],
            timestamp=service_health["timestamp"],
            ai_service=service_health["ai_service"],
            emergency_detector=service_health["emergency_detector"],
            provider_health=service_health["provider_health"],
            components=service_health["components"]
        )
        
    except Exception as e:
        logger.error(f"Detailed health check failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Detailed health check failed"
        )


@router.get("/ai-providers")
async def get_ai_provider_status():
    """Get detailed AI provider status"""
    try:
        # Perform health checks on all providers
        health_results = await ai_service_manager.health_check_all_providers()
        
        provider_details = {}
        for provider_type, health in health_results.items():
            provider_details[provider_type.value] = {
                "status": health.status.value,
                "success_rate": health.success_rate,
                "response_time": health.response_time,
                "consecutive_failures": health.consecutive_failures,
                "error_count": health.error_count,
                "last_check": health.last_check.isoformat(),
                "last_error": health.last_error
            }
        
        return {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "providers": provider_details
        }
        
    except Exception as e:
        logger.error(f"AI provider status check failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="AI provider status check failed"
        )


@router.get("/emergency-stats")
async def get_emergency_statistics():
    """Get emergency detection system statistics"""
    try:
        stats = emergency_detector.get_emergency_statistics()
        
        return {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "statistics": stats
        }
        
    except Exception as e:
        logger.error(f"Emergency statistics check failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Emergency statistics check failed"
        )


@router.post("/test-emergency")
async def test_emergency_detection(test_message: str):
    """Test emergency detection system with a message"""
    try:
        assessment = emergency_detector.detect_emergency(test_message)
        
        return {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "test_message": test_message,
            "assessment": {
                "is_emergency": assessment.is_emergency,
                "urgency_score": assessment.urgency_score,
                "emergency_level": assessment.emergency_level.value,
                "detected_keywords": assessment.detected_keywords,
                "categories": [cat.value for cat in assessment.categories],
                "confidence": assessment.confidence,
                "recommendations": assessment.recommendations[:3]  # Limit for API response
            }
        }
        
    except Exception as e:
        logger.error(f"Emergency detection test failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Emergency detection test failed"
        )


@router.get("/system-metrics")
async def get_system_metrics():
    """Get comprehensive system metrics"""
    try:
        ai_status = ai_service_manager.get_service_status()
        emergency_stats = emergency_detector.get_emergency_statistics()
        
        # Calculate system metrics
        total_providers = ai_status["total_count"]
        available_providers = ai_status["available_count"]
        availability_percentage = (available_providers / total_providers * 100) if total_providers > 0 else 0
        
        return {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "system_availability": {
                "percentage": availability_percentage,
                "available_providers": available_providers,
                "total_providers": total_providers
            },
            "emergency_detection": {
                "total_keywords": emergency_stats["total_keywords"],
                "categories_count": len(emergency_stats["categories"]),
                "emergency_levels": emergency_stats["emergency_levels"]
            },
            "last_health_check": ai_status["last_health_check"],
            "uptime_status": "operational" if availability_percentage > 0 else "degraded"
        }
        
    except Exception as e:
        logger.error(f"System metrics check failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="System metrics check failed"
        )