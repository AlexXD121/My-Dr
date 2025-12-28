"""
Health Analytics API endpoints for My Dr AI Medical Assistant
Provides comprehensive health data analysis, insights, and reporting endpoints
"""
import logging
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Optional, Any
from fastapi import APIRouter, Depends, HTTPException, Query, BackgroundTasks
from sqlalchemy.orm import Session
from sqlalchemy import and_
from pydantic import BaseModel, Field
import json

from database import get_db
from models import User, HealthAnalytics
from health_analytics_engine import health_analytics_engine
from auth_middleware import get_current_user

logger = logging.getLogger(__name__)

# Create router
router = APIRouter(prefix="/health-analytics", tags=["health-analytics"])


# Pydantic models for request/response
class HealthAnalyticsRequest(BaseModel):
    period_type: str = Field(default="monthly", description="Analysis period: daily, weekly, monthly, quarterly, yearly")
    analysis_scope: str = Field(default="comprehensive", description="Analysis scope: comprehensive, symptoms_only, consultations_only")
    include_historical: bool = Field(default=True, description="Include historical comparison data")
    generate_insights: bool = Field(default=True, description="Generate AI-powered insights")


class HealthInsightsRequest(BaseModel):
    focus_areas: Optional[List[str]] = Field(default=None, description="Specific areas to focus insights on")
    priority_level: str = Field(default="all", description="Priority level filter: all, high, medium, low")
    include_recommendations: bool = Field(default=True, description="Include actionable recommendations")


class HealthTrendsRequest(BaseModel):
    period_type: str = Field(default="monthly", description="Trend analysis period")
    trend_categories: Optional[List[str]] = Field(default=None, description="Categories to analyze: symptoms, consultations, medications, risk")
    comparison_periods: int = Field(default=6, description="Number of periods to compare")


class HealthReportRequest(BaseModel):
    report_type: str = Field(default="comprehensive", description="Report type: comprehensive, summary, trends, risk_assessment")
    format: str = Field(default="json", description="Report format: json, pdf")
    include_charts: bool = Field(default=True, description="Include data visualizations")
    date_range: Optional[Dict[str, str]] = Field(default=None, description="Custom date range for report")


class HealthAnalyticsResponse(BaseModel):
    user_id: str
    period_type: str
    period_start: datetime
    period_end: datetime
    analysis_scope: str
    consultation_count: int
    total_messages: int
    avg_consultation_length: float
    avg_response_time: float
    symptom_frequency: Dict[str, int]
    symptom_severity_trends: Dict[str, Any]
    new_symptoms_detected: List[str]
    health_trends: Dict[str, Any]
    risk_assessment: Dict[str, Any]
    overall_health_score: float
    health_insights: List[Dict[str, Any]]
    personalized_recommendations: List[Dict[str, Any]]
    generated_at: datetime
    computation_time_ms: int


class HealthInsightsResponse(BaseModel):
    user_id: str
    insights: List[Dict[str, Any]]
    recommendations: List[Dict[str, Any]]
    priority_summary: Dict[str, int]
    generated_at: datetime


class HealthTrendsResponse(BaseModel):
    user_id: str
    period_type: str
    comparison_periods: int
    consultation_trends: Dict[str, Any]
    symptom_trends: Dict[str, Any]
    health_score_trends: Dict[str, Any]
    risk_trends: Dict[str, Any]
    seasonal_patterns: Dict[str, Any]
    generated_at: datetime


class HealthReportResponse(BaseModel):
    user_id: str
    report_type: str
    format: str
    report_data: Dict[str, Any]
    file_path: Optional[str] = None
    generated_at: datetime


@router.get("/", response_model=HealthAnalyticsResponse)
async def get_comprehensive_health_analytics(
    request: HealthAnalyticsRequest = Depends(),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get comprehensive health analytics for the current user
    
    This endpoint provides a complete health analysis including:
    - Consultation patterns and metrics
    - Symptom frequency and severity trends
    - Health risk assessment
    - Personalized insights and recommendations
    - Overall health score
    """
    try:
        logger.info(f"Generating comprehensive health analytics for user {current_user.id}")
        
        # Generate analytics using the engine
        analytics_data = await health_analytics_engine.generate_comprehensive_analytics(
            user_id=current_user.id,
            period_type=request.period_type,
            analysis_scope=request.analysis_scope
        )
        
        # Save analytics to database for historical tracking
        await _save_analytics_to_database(db, current_user.id, analytics_data)
        
        # Convert to response model
        response = HealthAnalyticsResponse(
            user_id=analytics_data["user_id"],
            period_type=analytics_data["period_type"],
            period_start=analytics_data["period_start"],
            period_end=analytics_data["period_end"],
            analysis_scope=analytics_data["analysis_scope"],
            consultation_count=analytics_data.get("consultation_count", 0),
            total_messages=analytics_data.get("total_messages", 0),
            avg_consultation_length=analytics_data.get("avg_consultation_length", 0.0),
            avg_response_time=analytics_data.get("avg_response_time", 0.0),
            symptom_frequency=analytics_data.get("symptom_frequency", {}),
            symptom_severity_trends=analytics_data.get("symptom_severity_trends", {}),
            new_symptoms_detected=analytics_data.get("new_symptoms_detected", []),
            health_trends=analytics_data.get("health_trends", {}),
            risk_assessment=analytics_data.get("risk_assessment", {}),
            overall_health_score=analytics_data.get("overall_health_score", 0.0),
            health_insights=analytics_data.get("health_insights", []),
            personalized_recommendations=analytics_data.get("personalized_recommendations", []),
            generated_at=analytics_data["generated_at"],
            computation_time_ms=analytics_data.get("computation_time_ms", 0)
        )
        
        logger.info(f"Successfully generated health analytics for user {current_user.id}")
        return response
        
    except Exception as e:
        logger.error(f"Failed to generate health analytics for user {current_user.id}: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate health analytics: {str(e)}"
        )


@router.get("/insights", response_model=HealthInsightsResponse)
async def get_personalized_health_insights(
    request: HealthInsightsRequest = Depends(),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get personalized health insights and recommendations
    
    This endpoint provides AI-generated insights based on user's health data:
    - Pattern-based insights
    - Risk-based recommendations
    - Preventive care suggestions
    - Lifestyle recommendations
    """
    try:
        logger.info(f"Generating health insights for user {current_user.id}")
        
        # Get recent analytics data
        recent_analytics = db.query(HealthAnalytics).filter(
            HealthAnalytics.user_id == current_user.id
        ).order_by(HealthAnalytics.generated_at.desc()).first()
        
        if not recent_analytics:
            # Generate fresh analytics if none exist
            analytics_data = await health_analytics_engine.generate_comprehensive_analytics(
                user_id=current_user.id,
                period_type="monthly",
                analysis_scope="comprehensive"
            )
            insights = analytics_data.get("health_insights", [])
            recommendations = analytics_data.get("personalized_recommendations", [])
        else:
            # Use existing analytics data
            insights = recent_analytics.health_insights or []
            recommendations = recent_analytics.personalized_recommendations or []
        
        # Filter by priority if specified
        if request.priority_level != "all":
            insights = [i for i in insights if i.get("priority") == request.priority_level]
            recommendations = [r for r in recommendations if r.get("priority") == request.priority_level]
        
        # Filter by focus areas if specified
        if request.focus_areas:
            insights = [i for i in insights if i.get("type") in request.focus_areas]
            recommendations = [r for r in recommendations if r.get("category") in request.focus_areas]
        
        # Calculate priority summary
        priority_summary = {"high": 0, "medium": 0, "low": 0}
        for insight in insights:
            priority = insight.get("priority", "low")
            priority_summary[priority] = priority_summary.get(priority, 0) + 1
        
        response = HealthInsightsResponse(
            user_id=current_user.id,
            insights=insights,
            recommendations=recommendations if request.include_recommendations else [],
            priority_summary=priority_summary,
            generated_at=datetime.now(timezone.utc)
        )
        
        logger.info(f"Successfully generated {len(insights)} insights for user {current_user.id}")
        return response
        
    except Exception as e:
        logger.error(f"Failed to generate health insights for user {current_user.id}: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate health insights: {str(e)}"
        )


@router.get("/trends", response_model=HealthTrendsResponse)
async def get_health_trends_analysis(
    request: HealthTrendsRequest = Depends(),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get time-based health pattern analysis and trends
    
    This endpoint provides trend analysis across multiple time periods:
    - Consultation frequency trends
    - Symptom severity trends
    - Health score progression
    - Risk level changes
    - Seasonal patterns
    """
    try:
        logger.info(f"Generating health trends analysis for user {current_user.id}")
        
        # Get historical analytics data
        historical_analytics = db.query(HealthAnalytics).filter(
            HealthAnalytics.user_id == current_user.id
        ).order_by(HealthAnalytics.period_end.desc()).limit(request.comparison_periods).all()
        
        if not historical_analytics:
            raise HTTPException(
                status_code=404,
                detail="Insufficient historical data for trend analysis"
            )
        
        # Analyze consultation trends
        consultation_trends = _analyze_consultation_trends(historical_analytics)
        
        # Analyze symptom trends
        symptom_trends = _analyze_symptom_trends(historical_analytics)
        
        # Analyze health score trends
        health_score_trends = _analyze_health_score_trends(historical_analytics)
        
        # Analyze risk trends
        risk_trends = _analyze_risk_trends(historical_analytics)
        
        # Analyze seasonal patterns
        seasonal_patterns = _analyze_seasonal_patterns(historical_analytics)
        
        response = HealthTrendsResponse(
            user_id=current_user.id,
            period_type=request.period_type,
            comparison_periods=len(historical_analytics),
            consultation_trends=consultation_trends,
            symptom_trends=symptom_trends,
            health_score_trends=health_score_trends,
            risk_trends=risk_trends,
            seasonal_patterns=seasonal_patterns,
            generated_at=datetime.now(timezone.utc)
        )
        
        logger.info(f"Successfully generated trends analysis for user {current_user.id}")
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to generate health trends for user {current_user.id}: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate health trends: {str(e)}"
        )


@router.post("/report", response_model=HealthReportResponse)
async def generate_health_report(
    request: HealthReportRequest,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Generate comprehensive health report with exportable summaries
    
    This endpoint generates detailed health reports in various formats:
    - Comprehensive health summary
    - Trend analysis report
    - Risk assessment report
    - Exportable PDF format
    """
    try:
        logger.info(f"Generating health report for user {current_user.id}")
        
        # Get analytics data based on report type
        if request.report_type == "comprehensive":
            report_data = await _generate_comprehensive_report(db, current_user.id, request)
        elif request.report_type == "summary":
            report_data = await _generate_summary_report(db, current_user.id, request)
        elif request.report_type == "trends":
            report_data = await _generate_trends_report(db, current_user.id, request)
        elif request.report_type == "risk_assessment":
            report_data = await _generate_risk_assessment_report(db, current_user.id, request)
        else:
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported report type: {request.report_type}"
            )
        
        # Handle PDF generation in background if requested
        file_path = None
        if request.format == "pdf":
            file_path = f"reports/health_report_{current_user.id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
            background_tasks.add_task(_generate_pdf_report, report_data, file_path)
        
        response = HealthReportResponse(
            user_id=current_user.id,
            report_type=request.report_type,
            format=request.format,
            report_data=report_data,
            file_path=file_path,
            generated_at=datetime.now(timezone.utc)
        )
        
        logger.info(f"Successfully generated {request.report_type} report for user {current_user.id}")
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to generate health report for user {current_user.id}: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate health report: {str(e)}"
        )


@router.get("/historical")
async def get_historical_analytics(
    period_type: str = Query(default="monthly", description="Period type for historical data"),
    limit: int = Query(default=12, description="Number of historical periods to retrieve"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get historical health analytics data for trend visualization
    """
    try:
        historical_data = db.query(HealthAnalytics).filter(
            and_(
                HealthAnalytics.user_id == current_user.id,
                HealthAnalytics.period_type == period_type
            )
        ).order_by(HealthAnalytics.period_end.desc()).limit(limit).all()
        
        # Convert to JSON-serializable format
        result = []
        for analytics in historical_data:
            result.append({
                "period_start": analytics.period_start.isoformat(),
                "period_end": analytics.period_end.isoformat(),
                "consultation_count": analytics.consultation_count,
                "overall_health_score": analytics.overall_health_score,
                "risk_assessment": analytics.risk_assessment,
                "symptom_frequency": analytics.symptom_frequency,
                "generated_at": analytics.generated_at.isoformat()
            })
        
        return {
            "user_id": current_user.id,
            "period_type": period_type,
            "historical_data": result,
            "total_periods": len(result)
        }
        
    except Exception as e:
        logger.error(f"Failed to get historical analytics for user {current_user.id}: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve historical analytics: {str(e)}"
        )


@router.delete("/")
async def delete_analytics_data(
    period_type: Optional[str] = Query(default=None, description="Specific period type to delete"),
    older_than_days: Optional[int] = Query(default=None, description="Delete data older than specified days"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Delete analytics data for the current user
    """
    try:
        query = db.query(HealthAnalytics).filter(HealthAnalytics.user_id == current_user.id)
        
        if period_type:
            query = query.filter(HealthAnalytics.period_type == period_type)
        
        if older_than_days:
            cutoff_date = datetime.now(timezone.utc) - timedelta(days=older_than_days)
            query = query.filter(HealthAnalytics.generated_at < cutoff_date)
        
        deleted_count = query.count()
        query.delete()
        db.commit()
        
        logger.info(f"Deleted {deleted_count} analytics records for user {current_user.id}")
        
        return {
            "message": f"Successfully deleted {deleted_count} analytics records",
            "deleted_count": deleted_count
        }
        
    except Exception as e:
        logger.error(f"Failed to delete analytics data for user {current_user.id}: {e}")
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Failed to delete analytics data: {str(e)}"
        )


# Helper functions
async def _save_analytics_to_database(db: Session, user_id: str, analytics_data: Dict[str, Any]):
    """Save analytics data to database for historical tracking"""
    try:
        health_analytics = HealthAnalytics(
            user_id=user_id,
            period_type=analytics_data["period_type"],
            period_start=analytics_data["period_start"],
            period_end=analytics_data["period_end"],
            analysis_scope=analytics_data["analysis_scope"],
            consultation_count=analytics_data.get("consultation_count", 0),
            total_messages=analytics_data.get("total_messages", 0),
            avg_consultation_length=analytics_data.get("avg_consultation_length", 0.0),
            avg_response_time=analytics_data.get("avg_response_time", 0.0),
            symptom_frequency=analytics_data.get("symptom_frequency", {}),
            symptom_severity_trends=analytics_data.get("symptom_severity_trends", {}),
            new_symptoms_detected=analytics_data.get("new_symptoms_detected", []),
            health_trends=analytics_data.get("health_trends", {}),
            risk_assessment=analytics_data.get("risk_assessment", {}),
            overall_health_score=analytics_data.get("overall_health_score", 0.0),
            health_insights=analytics_data.get("health_insights", []),
            personalized_recommendations=analytics_data.get("personalized_recommendations", []),
            generated_at=analytics_data["generated_at"],
            computation_time_ms=analytics_data.get("computation_time_ms", 0),
            version=analytics_data["version"],
            is_complete=True
        )
        
        db.add(health_analytics)
        db.commit()
        
        logger.info(f"Saved analytics data to database for user {user_id}")
        
    except Exception as e:
        logger.error(f"Failed to save analytics to database: {e}")
        db.rollback()
        raise


def _analyze_consultation_trends(historical_analytics: List[HealthAnalytics]) -> Dict[str, Any]:
    """Analyze consultation trends from historical data"""
    if not historical_analytics:
        return {}
    
    consultation_counts = [analytics.consultation_count for analytics in historical_analytics]
    consultation_counts.reverse()  # Chronological order
    
    # Calculate trend
    if len(consultation_counts) >= 2:
        recent_avg = sum(consultation_counts[-3:]) / min(3, len(consultation_counts))
        older_avg = sum(consultation_counts[:3]) / min(3, len(consultation_counts))
        
        trend = "stable"
        if recent_avg > older_avg * 1.2:
            trend = "increasing"
        elif recent_avg < older_avg * 0.8:
            trend = "decreasing"
        
        return {
            "trend": trend,
            "recent_average": round(recent_avg, 1),
            "historical_average": round(older_avg, 1),
            "data_points": consultation_counts,
            "total_periods": len(consultation_counts)
        }
    
    return {"trend": "insufficient_data", "data_points": consultation_counts}


def _analyze_symptom_trends(historical_analytics: List[HealthAnalytics]) -> Dict[str, Any]:
    """Analyze symptom trends from historical data"""
    if not historical_analytics:
        return {}
    
    # Aggregate symptom frequency data
    all_symptoms = {}
    for analytics in historical_analytics:
        if analytics.symptom_frequency:
            for symptom, count in analytics.symptom_frequency.items():
                if symptom not in all_symptoms:
                    all_symptoms[symptom] = []
                all_symptoms[symptom].append(count)
    
    # Analyze trends for top symptoms
    symptom_trends = {}
    for symptom, counts in all_symptoms.items():
        if len(counts) >= 2:
            counts.reverse()  # Chronological order
            recent_avg = sum(counts[-3:]) / min(3, len(counts))
            older_avg = sum(counts[:3]) / min(3, len(counts))
            
            trend = "stable"
            if recent_avg > older_avg * 1.5:
                trend = "increasing"
            elif recent_avg < older_avg * 0.5:
                trend = "decreasing"
            
            symptom_trends[symptom] = {
                "trend": trend,
                "recent_average": round(recent_avg, 1),
                "historical_average": round(older_avg, 1),
                "data_points": counts
            }
    
    return symptom_trends


def _analyze_health_score_trends(historical_analytics: List[HealthAnalytics]) -> Dict[str, Any]:
    """Analyze health score trends from historical data"""
    if not historical_analytics:
        return {}
    
    health_scores = [analytics.overall_health_score for analytics in historical_analytics if analytics.overall_health_score]
    health_scores.reverse()  # Chronological order
    
    if len(health_scores) >= 2:
        current_score = health_scores[-1]
        previous_score = health_scores[-2] if len(health_scores) >= 2 else health_scores[0]
        
        trend = "stable"
        score_change = current_score - previous_score
        
        if score_change > 5:
            trend = "improving"
        elif score_change < -5:
            trend = "declining"
        
        return {
            "trend": trend,
            "current_score": current_score,
            "previous_score": previous_score,
            "score_change": round(score_change, 1),
            "data_points": health_scores,
            "average_score": round(sum(health_scores) / len(health_scores), 1)
        }
    
    return {"trend": "insufficient_data", "data_points": health_scores}


def _analyze_risk_trends(historical_analytics: List[HealthAnalytics]) -> Dict[str, Any]:
    """Analyze risk level trends from historical data"""
    if not historical_analytics:
        return {}
    
    risk_levels = []
    risk_scores = []
    
    for analytics in historical_analytics:
        if analytics.risk_assessment:
            risk_levels.append(analytics.risk_assessment.get("risk_level", "low"))
            risk_scores.append(analytics.risk_assessment.get("risk_score", 0.0))
    
    risk_levels.reverse()  # Chronological order
    risk_scores.reverse()
    
    if len(risk_levels) >= 2:
        current_level = risk_levels[-1]
        previous_level = risk_levels[-2]
        
        level_hierarchy = {"low": 1, "moderate": 2, "high": 3, "critical": 4}
        current_rank = level_hierarchy.get(current_level, 1)
        previous_rank = level_hierarchy.get(previous_level, 1)
        
        trend = "stable"
        if current_rank > previous_rank:
            trend = "increasing"
        elif current_rank < previous_rank:
            trend = "decreasing"
        
        return {
            "trend": trend,
            "current_level": current_level,
            "previous_level": previous_level,
            "risk_levels": risk_levels,
            "risk_scores": risk_scores
        }
    
    return {"trend": "insufficient_data", "risk_levels": risk_levels}


def _analyze_seasonal_patterns(historical_analytics: List[HealthAnalytics]) -> Dict[str, Any]:
    """Analyze seasonal patterns from historical data"""
    if not historical_analytics:
        return {}
    
    seasonal_data = {"spring": [], "summer": [], "fall": [], "winter": []}
    
    for analytics in historical_analytics:
        month = analytics.period_start.month
        season = "winter"
        
        if month in [3, 4, 5]:
            season = "spring"
        elif month in [6, 7, 8]:
            season = "summer"
        elif month in [9, 10, 11]:
            season = "fall"
        
        seasonal_data[season].append({
            "consultation_count": analytics.consultation_count,
            "health_score": analytics.overall_health_score,
            "period": analytics.period_start.isoformat()
        })
    
    # Calculate seasonal averages
    seasonal_averages = {}
    for season, data in seasonal_data.items():
        if data:
            avg_consultations = sum(d["consultation_count"] for d in data) / len(data)
            avg_health_score = sum(d["health_score"] for d in data if d["health_score"]) / len([d for d in data if d["health_score"]])
            
            seasonal_averages[season] = {
                "avg_consultations": round(avg_consultations, 1),
                "avg_health_score": round(avg_health_score, 1),
                "data_points": len(data)
            }
    
    return seasonal_averages


async def _generate_comprehensive_report(db: Session, user_id: str, request: HealthReportRequest) -> Dict[str, Any]:
    """Generate comprehensive health report"""
    # Get latest analytics
    analytics_data = await health_analytics_engine.generate_comprehensive_analytics(
        user_id=user_id,
        period_type="monthly",
        analysis_scope="comprehensive"
    )
    
    return {
        "report_type": "comprehensive",
        "user_id": user_id,
        "summary": {
            "overall_health_score": analytics_data.get("overall_health_score", 0),
            "risk_level": analytics_data.get("risk_assessment", {}).get("risk_level", "low"),
            "total_consultations": analytics_data.get("consultation_count", 0),
            "active_symptoms": len(analytics_data.get("symptom_frequency", {}))
        },
        "detailed_analytics": analytics_data,
        "generated_at": datetime.now(timezone.utc).isoformat()
    }


async def _generate_summary_report(db: Session, user_id: str, request: HealthReportRequest) -> Dict[str, Any]:
    """Generate summary health report"""
    # Get basic analytics
    analytics_data = await health_analytics_engine.generate_comprehensive_analytics(
        user_id=user_id,
        period_type="monthly",
        analysis_scope="comprehensive"
    )
    
    return {
        "report_type": "summary",
        "user_id": user_id,
        "health_score": analytics_data.get("overall_health_score", 0),
        "risk_assessment": analytics_data.get("risk_assessment", {}),
        "key_insights": analytics_data.get("health_insights", [])[:5],
        "top_recommendations": analytics_data.get("personalized_recommendations", [])[:3],
        "generated_at": datetime.now(timezone.utc).isoformat()
    }


async def _generate_trends_report(db: Session, user_id: str, request: HealthReportRequest) -> Dict[str, Any]:
    """Generate trends analysis report"""
    # Get historical data
    historical_analytics = db.query(HealthAnalytics).filter(
        HealthAnalytics.user_id == user_id
    ).order_by(HealthAnalytics.period_end.desc()).limit(12).all()
    
    consultation_trends = _analyze_consultation_trends(historical_analytics)
    health_score_trends = _analyze_health_score_trends(historical_analytics)
    
    return {
        "report_type": "trends",
        "user_id": user_id,
        "consultation_trends": consultation_trends,
        "health_score_trends": health_score_trends,
        "trend_summary": {
            "overall_trend": "improving" if health_score_trends.get("trend") == "improving" else "stable",
            "data_periods": len(historical_analytics)
        },
        "generated_at": datetime.now(timezone.utc).isoformat()
    }


async def _generate_risk_assessment_report(db: Session, user_id: str, request: HealthReportRequest) -> Dict[str, Any]:
    """Generate risk assessment report"""
    analytics_data = await health_analytics_engine.generate_comprehensive_analytics(
        user_id=user_id,
        period_type="monthly",
        analysis_scope="comprehensive"
    )
    
    risk_assessment = analytics_data.get("risk_assessment", {})
    
    return {
        "report_type": "risk_assessment",
        "user_id": user_id,
        "current_risk": risk_assessment,
        "risk_mitigation": [
            rec for rec in analytics_data.get("personalized_recommendations", [])
            if rec.get("category") == "risk_management"
        ],
        "generated_at": datetime.now(timezone.utc).isoformat()
    }


async def _generate_pdf_report(report_data: Dict[str, Any], file_path: str):
    """Generate PDF report (placeholder for actual PDF generation)"""
    # This would integrate with a PDF generation library like ReportLab
    # For now, we'll just log the action
    logger.info(f"PDF report generation requested for file: {file_path}")
    # TODO: Implement actual PDF generation
    pass