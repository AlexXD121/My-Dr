"""
Symptom Checker API Endpoints for MyDoc AI Medical Assistant

This module provides REST API endpoints for symptom analysis including:
- Symptom analysis and processing
- Symptom history tracking and pattern recognition
- Health insights generation based on symptoms
- Symptom data export functionality
"""

from fastapi import APIRouter, HTTPException, Depends, Query, status
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from pydantic import BaseModel, Field, validator
import json
import logging

from database import get_db
from models import User, SymptomRecord, HealthAnalytics
from symptom_analyzer import (
    SymptomAnalyzer, 
    SymptomInput, 
    SymptomAnalysis,
    create_symptom_input_from_text,
    normalize_symptom_text
)

logger = logging.getLogger(__name__)

# Initialize router
router = APIRouter(prefix="/symptoms", tags=["symptom-checker"])

# Initialize symptom analyzer
symptom_analyzer = SymptomAnalyzer()


# Pydantic models for API requests/responses
class SymptomAnalysisRequest(BaseModel):
    """Request model for symptom analysis"""
    symptoms: List[str] = Field(..., min_items=1, max_items=10, description="List of symptoms")
    duration: Optional[str] = Field(None, description="Duration of symptoms (e.g., '2 days', '1 week')")
    severity_rating: Optional[int] = Field(None, ge=1, le=10, description="Self-rated severity (1-10)")
    location: Optional[str] = Field(None, description="Location of symptoms")
    triggers: List[str] = Field(default_factory=list, description="Known triggers")
    alleviating_factors: List[str] = Field(default_factory=list, description="Things that help")
    associated_symptoms: List[str] = Field(default_factory=list, description="Additional symptoms")
    medical_history: List[str] = Field(default_factory=list, description="Relevant medical history")
    current_medications: List[str] = Field(default_factory=list, description="Current medications")
    
    @validator('symptoms')
    def validate_symptoms(cls, v):
        """Validate symptoms list"""
        if not v:
            raise ValueError("At least one symptom is required")
        
        # Normalize and validate each symptom
        normalized_symptoms = []
        for symptom in v:
            if not symptom or len(symptom.strip()) < 2:
                continue
            normalized = normalize_symptom_text(symptom)
            if normalized:
                normalized_symptoms.append(normalized)
        
        if not normalized_symptoms:
            raise ValueError("No valid symptoms provided")
        
        return normalized_symptoms[:10]  # Limit to 10 symptoms


class ConditionSuggestionResponse(BaseModel):
    """Response model for condition suggestions"""
    condition_name: str
    confidence_score: float
    description: str
    common_symptoms: List[str]
    severity_indicators: List[str]
    recommended_actions: List[str]


class SymptomAnalysisResponse(BaseModel):
    """Response model for symptom analysis"""
    analysis_id: str
    urgency_score: int
    urgency_level: str
    severity_level: str
    primary_symptoms: List[str]
    red_flags: List[str]
    possible_conditions: List[ConditionSuggestionResponse]
    recommendations: List[str]
    follow_up_questions: List[str]
    emergency_indicators: List[str]
    confidence_score: float
    requires_immediate_attention: bool
    analysis_timestamp: str
    disclaimer: str


class SymptomHistoryResponse(BaseModel):
    """Response model for symptom history"""
    record_id: str
    symptoms: List[str]
    analysis_summary: Dict[str, Any]
    recorded_at: str
    urgency_level: str
    follow_up_needed: bool


class SymptomInsightsResponse(BaseModel):
    """Response model for symptom-based health insights"""
    total_symptom_records: int
    most_common_symptoms: List[Dict[str, Any]]
    urgency_trends: Dict[str, int]
    pattern_insights: List[str]
    recommendations: List[str]
    risk_factors: List[str]


# Helper functions
def get_demo_user(db: Session) -> User:
    """Get or create demo user for symptom tracking"""
    user = db.query(User).filter(User.firebase_uid == "demo-user").first()
    if not user:
        user = User(
            firebase_uid="demo-user",
            email="demo@mydoc.ai",
            display_name="Demo User"
        )
        db.add(user)
        db.commit()
        db.refresh(user)
    return user


def convert_analysis_to_response(analysis: SymptomAnalysis, analysis_id: str) -> SymptomAnalysisResponse:
    """Convert SymptomAnalysis to API response format"""
    return SymptomAnalysisResponse(
        analysis_id=analysis_id,
        urgency_score=analysis.urgency_score,
        urgency_level=analysis.urgency_level.value,
        severity_level=analysis.severity_level.value,
        primary_symptoms=analysis.primary_symptoms,
        red_flags=analysis.red_flags,
        possible_conditions=[
            ConditionSuggestionResponse(
                condition_name=condition.condition_name,
                confidence_score=condition.confidence_score,
                description=condition.description,
                common_symptoms=condition.common_symptoms,
                severity_indicators=condition.severity_indicators,
                recommended_actions=condition.recommended_actions
            )
            for condition in analysis.possible_conditions
        ],
        recommendations=analysis.recommendations,
        follow_up_questions=analysis.follow_up_questions,
        emergency_indicators=analysis.emergency_indicators,
        confidence_score=analysis.confidence_score,
        requires_immediate_attention=analysis.requires_immediate_attention,
        analysis_timestamp=analysis.analysis_timestamp.isoformat(),
        disclaimer="This analysis is for informational purposes only and does not replace professional medical advice. Always consult with a healthcare provider for proper diagnosis and treatment."
    )


# API Endpoints
@router.post("/analyze", response_model=SymptomAnalysisResponse)
async def analyze_symptoms(
    request: SymptomAnalysisRequest,
    db: Session = Depends(get_db),
    save_to_history: bool = Query(True, description="Whether to save analysis to user's history")
):
    """
    Analyze symptoms and provide medical insights
    
    This endpoint performs comprehensive symptom analysis including:
    - Urgency scoring and severity assessment
    - Medical condition suggestions with confidence scores
    - Personalized recommendations and follow-up questions
    - Emergency indicator detection
    """
    try:
        # Get demo user
        user = get_demo_user(db)
        
        # Create symptom input
        symptom_input = SymptomInput(
            symptoms=request.symptoms,
            duration=request.duration,
            severity_self_rating=request.severity_rating,
            location=request.location,
            triggers=request.triggers,
            alleviating_factors=request.alleviating_factors,
            associated_symptoms=request.associated_symptoms,
            medical_history=request.medical_history,
            current_medications=request.current_medications,
            age=user.get_age(),
            gender=user.gender
        )
        
        # Perform symptom analysis
        analysis = symptom_analyzer.analyze_symptoms(symptom_input)
        
        # Generate unique analysis ID
        import uuid
        analysis_id = str(uuid.uuid4())
        
        # Save to symptom history if requested
        if save_to_history:
            try:
                symptom_record = SymptomRecord(
                    user_id=user.id,
                    symptoms=request.symptoms,
                    duration=request.duration,
                    severity_rating=request.severity_rating,
                    location=request.location,
                    triggers=request.triggers,
                    alleviating_factors=request.alleviating_factors,
                    associated_symptoms=request.associated_symptoms,
                    analysis_results={
                        "analysis_id": analysis_id,
                        "urgency_score": analysis.urgency_score,
                        "urgency_level": analysis.urgency_level.value,
                        "severity_level": analysis.severity_level.value,
                        "confidence_score": analysis.confidence_score,
                        "requires_immediate_attention": analysis.requires_immediate_attention,
                        "red_flags": analysis.red_flags,
                        "emergency_indicators": analysis.emergency_indicators,
                        "possible_conditions": [
                            {
                                "name": condition.condition_name,
                                "confidence": condition.confidence_score
                            }
                            for condition in analysis.possible_conditions
                        ]
                    },
                    urgency_level=analysis.urgency_level.value,
                    requires_follow_up=analysis.requires_immediate_attention or analysis.urgency_score >= 6,
                    recorded_at=datetime.utcnow()
                )
                db.add(symptom_record)
                db.commit()
                
                logger.info(f"Symptom analysis saved for user {user.id}: urgency={analysis.urgency_score}")
                
            except Exception as save_error:
                logger.error(f"Failed to save symptom record: {save_error}")
                db.rollback()
                # Continue with analysis even if saving fails
        
        # Convert to response format
        response = convert_analysis_to_response(analysis, analysis_id)
        
        logger.info(f"Symptom analysis completed: urgency={analysis.urgency_score}, conditions={len(analysis.possible_conditions)}")
        
        return response
        
    except ValueError as ve:
        logger.warning(f"Invalid symptom analysis request: {ve}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid request: {str(ve)}"
        )
    except Exception as e:
        logger.error(f"Symptom analysis error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to analyze symptoms. Please try again."
        )


@router.get("/history", response_model=List[SymptomHistoryResponse])
async def get_symptom_history(
    db: Session = Depends(get_db),
    limit: int = Query(20, ge=1, le=100, description="Number of records to return"),
    offset: int = Query(0, ge=0, description="Number of records to skip"),
    urgency_filter: Optional[str] = Query(None, description="Filter by urgency level"),
    date_from: Optional[str] = Query(None, description="Filter from date (ISO format)"),
    date_to: Optional[str] = Query(None, description="Filter to date (ISO format)")
):
    """
    Get user's symptom analysis history with filtering options
    
    Returns a paginated list of previous symptom analyses with filtering capabilities.
    """
    try:
        # Get demo user
        user = get_demo_user(db)
        
        # Build query
        query = db.query(SymptomRecord).filter(SymptomRecord.user_id == user.id)
        
        # Apply filters
        if urgency_filter:
            valid_urgency_levels = ["routine", "moderate", "urgent", "emergency", "critical"]
            if urgency_filter.lower() in valid_urgency_levels:
                query = query.filter(SymptomRecord.urgency_level == urgency_filter.lower())
        
        if date_from:
            try:
                from_date = datetime.fromisoformat(date_from.replace('Z', '+00:00'))
                query = query.filter(SymptomRecord.recorded_at >= from_date)
            except ValueError:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid date_from format. Use ISO format (YYYY-MM-DDTHH:MM:SS)"
                )
        
        if date_to:
            try:
                to_date = datetime.fromisoformat(date_to.replace('Z', '+00:00'))
                query = query.filter(SymptomRecord.recorded_at <= to_date)
            except ValueError:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid date_to format. Use ISO format (YYYY-MM-DDTHH:MM:SS)"
                )
        
        # Get records with pagination
        records = query.order_by(SymptomRecord.recorded_at.desc()).offset(offset).limit(limit).all()
        
        # Convert to response format
        history = []
        for record in records:
            history.append(SymptomHistoryResponse(
                record_id=record.id,
                symptoms=record.symptoms or [],
                analysis_summary={
                    "urgency_score": record.analysis_results.get("urgency_score", 0) if record.analysis_results else 0,
                    "severity_level": record.analysis_results.get("severity_level", "unknown") if record.analysis_results else "unknown",
                    "confidence_score": record.analysis_results.get("confidence_score", 0.0) if record.analysis_results else 0.0,
                    "condition_count": len(record.analysis_results.get("possible_conditions", [])) if record.analysis_results else 0
                },
                recorded_at=record.recorded_at.isoformat(),
                urgency_level=record.urgency_level or "routine",
                follow_up_needed=record.requires_follow_up or False
            ))
        
        logger.info(f"Retrieved {len(history)} symptom records for user {user.id}")
        
        return history
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get symptom history: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve symptom history"
        )


@router.get("/insights", response_model=SymptomInsightsResponse)
async def get_symptom_insights(
    db: Session = Depends(get_db),
    days_back: int = Query(30, ge=7, le=365, description="Number of days to analyze")
):
    """
    Generate health insights based on symptom patterns and history
    
    Analyzes user's symptom history to identify patterns, trends, and provide
    personalized health recommendations.
    """
    try:
        # Get demo user
        user = get_demo_user(db)
        
        # Get symptom records from specified time period
        cutoff_date = datetime.utcnow() - timedelta(days=days_back)
        records = db.query(SymptomRecord).filter(
            SymptomRecord.user_id == user.id,
            SymptomRecord.recorded_at >= cutoff_date
        ).all()
        
        if not records:
            return SymptomInsightsResponse(
                total_symptom_records=0,
                most_common_symptoms=[],
                urgency_trends={},
                pattern_insights=["No symptom data available for the selected time period."],
                recommendations=["Start tracking your symptoms to receive personalized insights."],
                risk_factors=[]
            )
        
        # Analyze symptom patterns
        symptom_frequency = {}
        urgency_counts = {"routine": 0, "moderate": 0, "urgent": 0, "emergency": 0, "critical": 0}
        
        for record in records:
            # Count symptom frequency
            for symptom in record.symptoms or []:
                symptom_lower = symptom.lower().strip()
                symptom_frequency[symptom_lower] = symptom_frequency.get(symptom_lower, 0) + 1
            
            # Count urgency levels
            urgency = record.urgency_level or "routine"
            if urgency in urgency_counts:
                urgency_counts[urgency] += 1
        
        # Get most common symptoms
        most_common = sorted(symptom_frequency.items(), key=lambda x: x[1], reverse=True)[:10]
        most_common_symptoms = [
            {"symptom": symptom, "frequency": count, "percentage": round((count / len(records)) * 100, 1)}
            for symptom, count in most_common
        ]
        
        # Generate pattern insights
        pattern_insights = []
        recommendations = []
        risk_factors = []
        
        # Analyze frequency patterns
        if len(records) >= 3:
            recent_records = sorted(records, key=lambda x: x.recorded_at, reverse=True)[:7]
            if len(recent_records) >= 3:
                pattern_insights.append(f"You've recorded {len(recent_records)} symptom episodes in the past week.")
        
        # Analyze urgency trends
        high_urgency_count = urgency_counts["urgent"] + urgency_counts["emergency"] + urgency_counts["critical"]
        if high_urgency_count > 0:
            percentage = round((high_urgency_count / len(records)) * 100, 1)
            pattern_insights.append(f"{percentage}% of your symptoms were classified as urgent or higher.")
            if percentage > 30:
                risk_factors.append("Frequent high-urgency symptoms")
                recommendations.append("Consider scheduling a comprehensive health evaluation with your healthcare provider")
        
        # Analyze most common symptoms
        if most_common_symptoms:
            top_symptom = most_common_symptoms[0]
            if top_symptom["frequency"] >= 3:
                pattern_insights.append(f"'{top_symptom['symptom']}' is your most frequently reported symptom ({top_symptom['frequency']} times).")
                
                # Symptom-specific recommendations
                symptom_name = top_symptom["symptom"]
                if "headache" in symptom_name:
                    recommendations.extend([
                        "Keep a headache diary to identify triggers",
                        "Ensure adequate hydration and regular sleep schedule"
                    ])
                elif "pain" in symptom_name:
                    recommendations.append("Consider discussing pain management strategies with your healthcare provider")
                elif "fatigue" in symptom_name or "tired" in symptom_name:
                    recommendations.extend([
                        "Evaluate your sleep quality and duration",
                        "Consider discussing fatigue with your healthcare provider"
                    ])
        
        # Check for concerning patterns
        if len(records) >= 5:
            recent_week = [r for r in records if r.recorded_at >= datetime.utcnow() - timedelta(days=7)]
            if len(recent_week) >= 3:
                risk_factors.append("Increased symptom frequency in recent week")
                recommendations.append("Monitor symptoms closely and consider medical evaluation if pattern continues")
        
        # General recommendations
        recommendations.extend([
            "Continue tracking symptoms to identify patterns and triggers",
            "Maintain a healthy lifestyle with regular exercise and balanced nutrition",
            "Seek medical attention for any concerning or persistent symptoms"
        ])
        
        # Default insights if none generated
        if not pattern_insights:
            pattern_insights = [
                f"Analyzed {len(records)} symptom records over {days_back} days.",
                "Continue tracking to identify meaningful patterns."
            ]
        
        logger.info(f"Generated symptom insights for user {user.id}: {len(records)} records analyzed")
        
        return SymptomInsightsResponse(
            total_symptom_records=len(records),
            most_common_symptoms=most_common_symptoms,
            urgency_trends=urgency_counts,
            pattern_insights=pattern_insights,
            recommendations=list(set(recommendations)),  # Remove duplicates
            risk_factors=risk_factors
        )
        
    except Exception as e:
        logger.error(f"Failed to generate symptom insights: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate symptom insights"
        )


@router.get("/export")
async def export_symptom_data(
    db: Session = Depends(get_db),
    format: str = Query("json", regex="^(json|csv)$", description="Export format (json or csv)"),
    date_from: Optional[str] = Query(None, description="Export from date (ISO format)"),
    date_to: Optional[str] = Query(None, description="Export to date (ISO format)")
):
    """
    Export symptom data for healthcare providers or personal records
    
    Exports user's symptom history in JSON or CSV format for sharing with
    healthcare providers or personal record keeping.
    """
    try:
        from fastapi.responses import Response
        import csv
        from io import StringIO
        
        # Get demo user
        user = get_demo_user(db)
        
        # Build query with date filters
        query = db.query(SymptomRecord).filter(SymptomRecord.user_id == user.id)
        
        if date_from:
            try:
                from_date = datetime.fromisoformat(date_from.replace('Z', '+00:00'))
                query = query.filter(SymptomRecord.recorded_at >= from_date)
            except ValueError:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid date_from format"
                )
        
        if date_to:
            try:
                to_date = datetime.fromisoformat(date_to.replace('Z', '+00:00'))
                query = query.filter(SymptomRecord.recorded_at <= to_date)
            except ValueError:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid date_to format"
                )
        
        records = query.order_by(SymptomRecord.recorded_at.desc()).all()
        
        if not records:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No symptom records found for the specified criteria"
            )
        
        # Prepare export data
        export_data = []
        for record in records:
            export_record = {
                "record_id": record.id,
                "recorded_at": record.recorded_at.isoformat(),
                "symptoms": record.symptoms or [],
                "duration": record.duration,
                "severity_rating": record.severity_rating,
                "location": record.location,
                "triggers": record.triggers or [],
                "alleviating_factors": record.alleviating_factors or [],
                "associated_symptoms": record.associated_symptoms or [],
                "urgency_level": record.urgency_level,
                "requires_follow_up": record.requires_follow_up,
                "analysis_summary": {
                    "urgency_score": record.analysis_results.get("urgency_score", 0) if record.analysis_results else 0,
                    "confidence_score": record.analysis_results.get("confidence_score", 0.0) if record.analysis_results else 0.0,
                    "red_flags": record.analysis_results.get("red_flags", []) if record.analysis_results else [],
                    "emergency_indicators": record.analysis_results.get("emergency_indicators", []) if record.analysis_results else []
                }
            }
            export_data.append(export_record)
        
        # Generate export based on format
        if format == "json":
            export_content = json.dumps({
                "export_info": {
                    "user_id": user.id,
                    "export_date": datetime.utcnow().isoformat(),
                    "total_records": len(export_data),
                    "date_range": {
                        "from": date_from,
                        "to": date_to
                    }
                },
                "symptom_records": export_data
            }, indent=2)
            
            return Response(
                content=export_content,
                media_type="application/json",
                headers={"Content-Disposition": f"attachment; filename=symptom_history_{datetime.utcnow().strftime('%Y%m%d')}.json"}
            )
        
        elif format == "csv":
            output = StringIO()
            writer = csv.writer(output)
            
            # Write header
            writer.writerow([
                "Record ID", "Date", "Symptoms", "Duration", "Severity Rating",
                "Location", "Triggers", "Alleviating Factors", "Associated Symptoms",
                "Urgency Level", "Urgency Score", "Follow-up Required"
            ])
            
            # Write data rows
            for record in export_data:
                writer.writerow([
                    record["record_id"],
                    record["recorded_at"],
                    "; ".join(record["symptoms"]),
                    record["duration"] or "",
                    record["severity_rating"] or "",
                    record["location"] or "",
                    "; ".join(record["triggers"]),
                    "; ".join(record["alleviating_factors"]),
                    "; ".join(record["associated_symptoms"]),
                    record["urgency_level"],
                    record["analysis_summary"]["urgency_score"],
                    record["requires_follow_up"]
                ])
            
            csv_content = output.getvalue()
            output.close()
            
            return Response(
                content=csv_content,
                media_type="text/csv",
                headers={"Content-Disposition": f"attachment; filename=symptom_history_{datetime.utcnow().strftime('%Y%m%d')}.csv"}
            )
        
        logger.info(f"Exported {len(export_data)} symptom records for user {user.id} in {format} format")
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to export symptom data: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to export symptom data"
        )


@router.delete("/history/{record_id}")
async def delete_symptom_record(
    record_id: str,
    db: Session = Depends(get_db)
):
    """Delete a specific symptom record"""
    try:
        # Get demo user
        user = get_demo_user(db)
        
        # Find the record
        record = db.query(SymptomRecord).filter(
            SymptomRecord.id == record_id,
            SymptomRecord.user_id == user.id
        ).first()
        
        if not record:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Symptom record not found"
            )
        
        # Delete the record
        db.delete(record)
        db.commit()
        
        logger.info(f"Deleted symptom record {record_id} for user {user.id}")
        
        return {"message": "Symptom record deleted successfully", "record_id": record_id}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to delete symptom record: {e}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete symptom record"
        )


# Health check endpoint for symptom checker
@router.get("/health")
async def symptom_checker_health():
    """Health check endpoint for symptom checker service"""
    try:
        # Test symptom analyzer
        test_input = SymptomInput(symptoms=["test symptom"])
        test_analysis = symptom_analyzer.analyze_symptoms(test_input)
        
        return {
            "status": "healthy",
            "service": "symptom-checker",
            "analyzer_status": "operational",
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"Symptom checker health check failed: {e}")
        return {
            "status": "unhealthy",
            "service": "symptom-checker",
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }