"""
Medical Information API endpoints for MyDoc AI Doctor Assistant
"""
import logging
from datetime import datetime, timezone, timedelta
from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from sqlalchemy import desc, func, and_
from pydantic import BaseModel, Field

from database import get_db
from models import User, Conversation, Message

logger = logging.getLogger(__name__)

# Create router
router = APIRouter(prefix="/medical", tags=["medical"])


# Pydantic models for API requests/responses
class SymptomAnalysisRequest(BaseModel):
    """Request model for symptom analysis"""
    symptoms: List[str] = Field(..., description="List of symptoms")
    duration: Optional[str] = Field(None, description="Duration of symptoms")
    severity: Optional[int] = Field(None, ge=1, le=10, description="Severity scale 1-10")
    additional_info: Optional[str] = Field(None, description="Additional information")


class SymptomAnalysisResponse(BaseModel):
    """Response model for symptom analysis"""
    possible_conditions: List[str]
    recommendations: List[str]
    urgency_level: str
    disclaimer: str


class MedicalHistoryEntry(BaseModel):
    """Model for medical history entry"""
    condition: str = Field(..., description="Medical condition or diagnosis")
    date_diagnosed: Optional[datetime] = Field(None, description="Date of diagnosis")
    medications: List[str] = Field(default=[], description="Related medications")
    notes: Optional[str] = Field(None, description="Additional notes")


class MedicalHistoryResponse(BaseModel):
    """Response model for medical history"""
    id: str
    condition: str
    date_diagnosed: Optional[datetime]
    medications: List[str]
    notes: Optional[str]
    created_at: datetime
    
    class Config:
        from_attributes = True


class DrugInteractionRequest(BaseModel):
    """Request model for drug interaction check"""
    medications: List[str] = Field(..., min_items=2, description="List of medications to check")


class DrugInteractionResponse(BaseModel):
    """Response model for drug interaction check"""
    interactions_found: bool
    interactions: List[Dict[str, Any]]
    warnings: List[str]
    recommendations: List[str]


# Helper functions
def get_or_create_user(db: Session, user_id: str = "default_user") -> User:
    """Get or create user in database"""
    user = db.query(User).filter(User.firebase_uid == user_id).first()
    
    if not user:
        user = User(
            firebase_uid=user_id,
            email=f"{user_id}@example.com",
            display_name="Default User",
            last_login=datetime.now(timezone.utc)
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        logger.info(f"Created new user: {user.email}")
    else:
        # Update last login
        user.last_login = datetime.now(timezone.utc)
        db.commit()
    
    return user


# API Endpoints
@router.post("/analyze-symptoms", response_model=SymptomAnalysisResponse)
async def analyze_symptoms(
    request: SymptomAnalysisRequest,
    db: Session = Depends(get_db)
):
    """Analyze symptoms and provide preliminary assessment"""
    try:
        # Get or create user
        user = get_or_create_user(db)
        
        # Basic symptom analysis logic
        symptoms_lower = [s.lower() for s in request.symptoms]
        
        # Determine urgency level
        emergency_symptoms = [
            "chest pain", "difficulty breathing", "severe bleeding", 
            "unconscious", "severe head injury", "stroke symptoms"
        ]
        
        high_urgency_symptoms = [
            "high fever", "severe pain", "persistent vomiting", 
            "severe headache", "vision problems"
        ]
        
        if any(symptom in " ".join(symptoms_lower) for symptom in emergency_symptoms):
            urgency_level = "EMERGENCY"
            recommendations = [
                "Seek immediate emergency medical attention",
                "Call emergency services (911)",
                "Go to the nearest emergency room"
            ]
            possible_conditions = ["Medical Emergency - Requires Immediate Attention"]
        elif any(symptom in " ".join(symptoms_lower) for symptom in high_urgency_symptoms):
            urgency_level = "HIGH"
            recommendations = [
                "Contact your healthcare provider today",
                "Consider visiting urgent care",
                "Monitor symptoms closely"
            ]
            possible_conditions = ["Requires Medical Evaluation"]
        else:
            urgency_level = "MODERATE"
            recommendations = [
                "Schedule an appointment with your healthcare provider",
                "Monitor symptoms and note any changes",
                "Consider rest and basic self-care measures"
            ]
            possible_conditions = ["General Medical Consultation Recommended"]
        
        logger.info(f"Symptom analysis completed for user {user.email}: urgency={urgency_level}")
        
        return SymptomAnalysisResponse(
            possible_conditions=possible_conditions,
            recommendations=recommendations,
            urgency_level=urgency_level,
            disclaimer="This analysis is for informational purposes only and should not replace professional medical diagnosis. Always consult with a healthcare provider for proper medical evaluation."
        )
        
    except Exception as e:
        logger.error(f"Symptom analysis failed for user {current_user.uid}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Symptom analysis failed. Please try again or consult with a healthcare provider."
        )


@router.post("/check-drug-interactions", response_model=DrugInteractionResponse)
async def check_drug_interactions(
    request: DrugInteractionRequest,
    db: Session = Depends(get_db)
):
    """Check for potential drug interactions"""
    try:
        # Get or create user
        user = get_or_create_user(db)
        
        # Basic drug interaction checking (in a real app, you'd use a medical database)
        medications = [med.lower().strip() for med in request.medications]
        
        # Common drug interaction patterns (simplified for demo)
        known_interactions = {
            ("warfarin", "aspirin"): "Increased bleeding risk",
            ("warfarin", "ibuprofen"): "Increased bleeding risk",
            ("metformin", "alcohol"): "Risk of lactic acidosis",
            ("simvastatin", "grapefruit"): "Increased statin levels",
        }
        
        interactions = []
        warnings = []
        
        # Check for known interactions
        for i, med1 in enumerate(medications):
            for med2 in medications[i+1:]:
                interaction_key = tuple(sorted([med1, med2]))
                if interaction_key in known_interactions:
                    interactions.append({
                        "drug1": med1,
                        "drug2": med2,
                        "interaction": known_interactions[interaction_key],
                        "severity": "moderate"
                    })
        
        # General warnings
        if len(medications) > 5:
            warnings.append("Taking multiple medications increases the risk of interactions")
        
        interactions_found = len(interactions) > 0
        
        recommendations = [
            "Always inform your healthcare provider about all medications you're taking",
            "Include over-the-counter drugs and supplements in your medication list",
            "Use the same pharmacy for all prescriptions when possible",
            "Keep an updated list of all your medications"
        ]
        
        if interactions_found:
            recommendations.insert(0, "Consult with your healthcare provider about potential interactions")
        
        logger.info(f"Drug interaction check completed for user {user.email}: {len(interactions)} interactions found")
        
        return DrugInteractionResponse(
            interactions_found=interactions_found,
            interactions=interactions,
            warnings=warnings,
            recommendations=recommendations
        )
        
    except Exception as e:
        logger.error(f"Drug interaction check failed for user {current_user.uid}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Drug interaction check failed. Please consult with your pharmacist or healthcare provider."
        )


@router.get("/consultation-history")
async def get_consultation_history(
    limit: int = Query(50, ge=1, le=200, description="Number of consultations to return"),
    offset: int = Query(0, ge=0, description="Number of consultations to skip"),
    db: Session = Depends(get_db)
):
    """Get user's medical consultation history"""
    try:
        # Get or create user
        user = get_or_create_user(db)
        
        # Get conversations (medical consultations)
        conversations = db.query(Conversation).filter(
            Conversation.user_id == user.id
        ).order_by(desc(Conversation.last_message_at)).offset(offset).limit(limit).all()
        
        consultation_history = []
        for conversation in conversations:
            # Get messages for this conversation
            messages = db.query(Message).filter(
                Message.conversation_id == conversation.id
            ).order_by(Message.timestamp).all()
            
            if messages:
                consultation_history.append({
                    "consultation_id": conversation.id,
                    "date": conversation.started_at.isoformat(),
                    "last_updated": conversation.last_message_at.isoformat(),
                    "message_count": len(messages),
                    "first_message": messages[0].content[:100] + "..." if len(messages[0].content) > 100 else messages[0].content,
                    "status": conversation.status
                })
        
        return {
            "consultations": consultation_history,
            "total": len(consultation_history),
            "limit": limit,
            "offset": offset
        }
        
    except Exception as e:
        logger.error(f"Failed to get consultation history for user {current_user.uid}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve consultation history. Please try again."
        )


@router.get("/health-tips")
async def get_health_tips(
    category: Optional[str] = Query(None, description="Health tip category")
):
    """Get general health tips and wellness advice"""
    try:
        # Health tips organized by category
        health_tips = {
            "general": [
                "Stay hydrated by drinking at least 8 glasses of water daily",
                "Aim for 7-9 hours of quality sleep each night",
                "Eat a balanced diet rich in fruits and vegetables",
                "Exercise regularly - at least 150 minutes of moderate activity per week",
                "Practice stress management techniques like meditation or deep breathing"
            ],
            "nutrition": [
                "Include a variety of colorful fruits and vegetables in your diet",
                "Choose whole grains over refined grains",
                "Limit processed foods and added sugars",
                "Include lean proteins in your meals",
                "Practice portion control"
            ],
            "exercise": [
                "Start with small, achievable fitness goals",
                "Include both cardio and strength training exercises",
                "Take regular breaks from sitting throughout the day",
                "Find physical activities you enjoy",
                "Warm up before exercising and cool down afterward"
            ],
            "mental_health": [
                "Practice mindfulness and meditation",
                "Maintain social connections with friends and family",
                "Set realistic goals and expectations",
                "Take breaks when feeling overwhelmed",
                "Seek professional help when needed"
            ]
        }
        
        if category and category in health_tips:
            tips = health_tips[category]
        else:
            # Return random tips from all categories
            import random
            all_tips = []
            for category_tips in health_tips.values():
                all_tips.extend(category_tips)
            tips = random.sample(all_tips, min(5, len(all_tips)))
        
        return {
            "category": category or "general",
            "tips": tips,
            "disclaimer": "These are general health tips and should not replace professional medical advice."
        }
        
    except Exception as e:
        logger.error(f"Failed to get health tips: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve health tips. Please try again."
        )