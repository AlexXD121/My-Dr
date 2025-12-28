"""
Medication Management API - Endpoints for medication list management and drug interaction checking
"""
import logging
from datetime import datetime, timezone, timedelta
from typing import List, Dict, Any, Optional
from fastapi import APIRouter, HTTPException, Depends, status, Query
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field, validator
from database import get_db
from models import User
from drug_interaction_models import (
    Medication, UserMedication, MedicationDoseLog, 
    DrugInteractionReport, MedicationReminder
)
from drug_interaction_checker import DrugInteractionChecker
from medication_database_seeder import MedicationDatabaseSeeder

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/medications", tags=["medications"])


# Pydantic models for request/response
class MedicationSearchRequest(BaseModel):
    query: str = Field(..., min_length=2, max_length=100, description="Medication name to search")
    limit: int = Field(10, ge=1, le=50, description="Maximum number of results")


class MedicationValidationRequest(BaseModel):
    medication_name: str = Field(..., min_length=2, max_length=100, description="Medication name to validate")


class AddMedicationRequest(BaseModel):
    medication_name: str = Field(..., min_length=2, max_length=100, description="Medication name")
    dosage: str = Field(..., min_length=1, max_length=50, description="Dosage (e.g., '500mg')")
    frequency: str = Field(..., min_length=1, max_length=100, description="Frequency (e.g., 'twice daily')")
    instructions: Optional[str] = Field(None, max_length=500, description="Special instructions")
    prescribed_by: Optional[str] = Field(None, max_length=100, description="Prescribing doctor")
    start_date: Optional[datetime] = Field(None, description="Start date")
    end_date: Optional[datetime] = Field(None, description="End date (for temporary medications)")
    schedule_times: Optional[List[str]] = Field(None, description="Schedule times (e.g., ['08:00', '20:00'])")
    reminder_enabled: bool = Field(True, description="Enable medication reminders")
    
    @validator('end_date')
    def validate_end_date(cls, v, values):
        if v and 'start_date' in values and values['start_date']:
            if v <= values['start_date']:
                raise ValueError('End date must be after start date')
        return v


class UpdateMedicationRequest(BaseModel):
    dosage: Optional[str] = Field(None, max_length=50, description="Dosage")
    frequency: Optional[str] = Field(None, max_length=100, description="Frequency")
    instructions: Optional[str] = Field(None, max_length=500, description="Instructions")
    status: Optional[str] = Field(None, description="Status (active, paused, discontinued)")
    reason_for_discontinuation: Optional[str] = Field(None, max_length=200, description="Reason for stopping")
    schedule_times: Optional[List[str]] = Field(None, description="Schedule times")
    reminder_enabled: Optional[bool] = Field(None, description="Enable reminders")
    patient_notes: Optional[str] = Field(None, max_length=500, description="Patient notes")


class InteractionCheckRequest(BaseModel):
    medications: List[str] = Field(..., min_items=2, max_items=20, description="List of medication names")


class LogDoseRequest(BaseModel):
    user_medication_id: str = Field(..., description="User medication ID")
    status: str = Field(..., description="Status: taken, missed, skipped, late")
    actual_time: Optional[datetime] = Field(None, description="When dose was actually taken")
    dosage_taken: Optional[str] = Field(None, description="Actual dosage if different")
    notes: Optional[str] = Field(None, max_length=500, description="Notes about the dose")
    side_effects_reported: Optional[List[str]] = Field(None, description="Any side effects")
    severity_rating: Optional[int] = Field(None, ge=1, le=10, description="Severity rating 1-10")


class MedicationReminderRequest(BaseModel):
    user_medication_id: str = Field(..., description="User medication ID")
    reminder_time: datetime = Field(..., description="When to send reminder")
    reminder_type: str = Field("dose", description="Type: dose, refill, appointment")
    title: str = Field(..., max_length=100, description="Reminder title")
    message: Optional[str] = Field(None, max_length=500, description="Reminder message")
    delivery_methods: List[str] = Field(["in_app"], description="Delivery methods")
    priority: str = Field("normal", description="Priority: low, normal, high, urgent")


# Helper function to get demo user
def get_demo_user(db: Session) -> User:
    """Get or create demo user for medication management"""
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


@router.get("/search")
async def search_medications(
    query: str = Query(..., min_length=2, max_length=100, description="Medication name to search"),
    limit: int = Query(10, ge=1, le=50, description="Maximum number of results"),
    db: Session = Depends(get_db)
):
    """Search for medications in the database"""
    try:
        # Search medications by name or brand names
        medications = db.query(Medication).filter(
            Medication.name.ilike(f"%{query}%")
        ).filter(Medication.is_active == True).limit(limit).all()
        
        # Also search by brand names
        brand_name_results = db.query(Medication).filter(
            Medication.brand_names.op('?')(query)  # JSON contains operator
        ).filter(Medication.is_active == True).limit(limit).all()
        
        # Combine and deduplicate results
        all_results = {med.id: med for med in medications + brand_name_results}
        medications = list(all_results.values())[:limit]
        
        results = []
        for med in medications:
            results.append({
                "id": med.id,
                "name": med.name,
                "brand_names": med.brand_names or [],
                "drug_class": med.drug_class,
                "strength": med.strength,
                "dosage_form": med.dosage_form,
                "indication": med.indication
            })
        
        return {
            "medications": results,
            "total_found": len(results),
            "query": query
        }
        
    except Exception as e:
        logger.error(f"Error searching medications: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to search medications"
        )


@router.post("/validate")
async def validate_medication(
    request: MedicationValidationRequest,
    db: Session = Depends(get_db)
):
    """Validate and get information about a medication"""
    try:
        checker = DrugInteractionChecker(db)
        validation_result = checker.validate_medication_name(request.medication_name)
        
        return validation_result
        
    except Exception as e:
        logger.error(f"Error validating medication: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to validate medication"
        )


@router.get("/user-medications")
async def get_user_medications(
    status_filter: Optional[str] = Query(None, description="Filter by status: active, paused, discontinued"),
    include_inactive: bool = Query(False, description="Include inactive medications"),
    db: Session = Depends(get_db)
):
    """Get user's medication list"""
    try:
        user = get_demo_user(db)
        
        # Build query
        query = db.query(UserMedication).filter(UserMedication.user_id == user.id)
        
        if status_filter:
            query = query.filter(UserMedication.status == status_filter)
        elif not include_inactive:
            query = query.filter(UserMedication.status == "active")
        
        user_medications = query.all()
        
        results = []
        for um in user_medications:
            medication_info = None
            if um.medication:
                medication_info = {
                    "id": um.medication.id,
                    "name": um.medication.name,
                    "brand_names": um.medication.brand_names or [],
                    "drug_class": um.medication.drug_class,
                    "strength": um.medication.strength,
                    "dosage_form": um.medication.dosage_form
                }
            
            results.append({
                "id": um.id,
                "medication": medication_info,
                "dosage": um.dosage,
                "frequency": um.frequency,
                "instructions": um.instructions,
                "prescribed_by": um.prescribed_by,
                "start_date": um.start_date.isoformat() if um.start_date else None,
                "end_date": um.end_date.isoformat() if um.end_date else None,
                "status": um.status,
                "schedule_times": um.schedule_times or [],
                "reminder_enabled": um.reminder_enabled,
                "adherence_percentage": um.adherence_percentage,
                "total_doses_prescribed": um.total_doses_prescribed,
                "doses_taken": um.doses_taken,
                "doses_missed": um.doses_missed,
                "patient_notes": um.patient_notes,
                "created_at": um.created_at.isoformat(),
                "is_active": um.is_active()
            })
        
        return {
            "medications": results,
            "total_count": len(results),
            "active_count": len([m for m in results if m["is_active"]]),
            "status_filter": status_filter
        }
        
    except Exception as e:
        logger.error(f"Error getting user medications: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve user medications"
        )


@router.post("/user-medications")
async def add_user_medication(
    request: AddMedicationRequest,
    db: Session = Depends(get_db)
):
    """Add medication to user's list"""
    try:
        user = get_demo_user(db)
        
        # Find or create medication
        medication = db.query(Medication).filter(
            Medication.name.ilike(f"%{request.medication_name}%")
        ).first()
        
        if not medication:
            # Create basic medication entry
            medication = Medication(
                name=request.medication_name.lower().strip(),
                drug_class="unknown",
                active_ingredients=[request.medication_name.lower().strip()]
            )
            db.add(medication)
            db.flush()
        
        # Check if user already has this medication active
        existing = db.query(UserMedication).filter(
            UserMedication.user_id == user.id,
            UserMedication.medication_id == medication.id,
            UserMedication.status == "active"
        ).first()
        
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User already has this medication in their active list"
            )
        
        # Create user medication
        user_medication = UserMedication(
            user_id=user.id,
            medication_id=medication.id,
            dosage=request.dosage,
            frequency=request.frequency,
            instructions=request.instructions,
            prescribed_by=request.prescribed_by,
            start_date=request.start_date or datetime.now(timezone.utc),
            end_date=request.end_date,
            schedule_times=request.schedule_times or [],
            reminder_enabled=request.reminder_enabled
        )
        
        db.add(user_medication)
        db.commit()
        db.refresh(user_medication)
        
        # Check for drug interactions with existing medications
        try:
            checker = DrugInteractionChecker(db)
            interactions = checker.get_user_medication_interactions(user.id)
            
            interaction_warnings = []
            for interaction in interactions:
                if (interaction["medication_a"].lower() == request.medication_name.lower() or 
                    interaction["medication_b"].lower() == request.medication_name.lower()):
                    interaction_warnings.append(interaction)
        
        except Exception as e:
            logger.warning(f"Failed to check interactions for new medication: {e}")
            interaction_warnings = []
        
        return {
            "message": "Medication added successfully",
            "user_medication_id": user_medication.id,
            "medication": {
                "id": medication.id,
                "name": medication.name,
                "brand_names": medication.brand_names or []
            },
            "interaction_warnings": interaction_warnings,
            "created_at": user_medication.created_at.isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error adding user medication: {e}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to add medication"
        )


@router.put("/user-medications/{user_medication_id}")
async def update_user_medication(
    user_medication_id: str,
    request: UpdateMedicationRequest,
    db: Session = Depends(get_db)
):
    """Update user's medication"""
    try:
        user = get_demo_user(db)
        
        user_medication = db.query(UserMedication).filter(
            UserMedication.id == user_medication_id,
            UserMedication.user_id == user.id
        ).first()
        
        if not user_medication:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User medication not found"
            )
        
        # Update fields if provided
        if request.dosage is not None:
            user_medication.dosage = request.dosage
        if request.frequency is not None:
            user_medication.frequency = request.frequency
        if request.instructions is not None:
            user_medication.instructions = request.instructions
        if request.status is not None:
            valid_statuses = ["active", "paused", "discontinued", "completed"]
            if request.status not in valid_statuses:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Invalid status. Must be one of: {', '.join(valid_statuses)}"
                )
            user_medication.status = request.status
        if request.reason_for_discontinuation is not None:
            user_medication.reason_for_discontinuation = request.reason_for_discontinuation
        if request.schedule_times is not None:
            user_medication.schedule_times = request.schedule_times
        if request.reminder_enabled is not None:
            user_medication.reminder_enabled = request.reminder_enabled
        if request.patient_notes is not None:
            user_medication.patient_notes = request.patient_notes
        
        user_medication.updated_at = datetime.now(timezone.utc)
        
        db.commit()
        
        return {
            "message": "Medication updated successfully",
            "user_medication_id": user_medication_id,
            "updated_at": user_medication.updated_at.isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating user medication: {e}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update medication"
        )


@router.delete("/user-medications/{user_medication_id}")
async def delete_user_medication(
    user_medication_id: str,
    db: Session = Depends(get_db)
):
    """Delete user's medication"""
    try:
        user = get_demo_user(db)
        
        user_medication = db.query(UserMedication).filter(
            UserMedication.id == user_medication_id,
            UserMedication.user_id == user.id
        ).first()
        
        if not user_medication:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User medication not found"
            )
        
        db.delete(user_medication)
        db.commit()
        
        return {
            "message": "Medication deleted successfully",
            "user_medication_id": user_medication_id
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting user medication: {e}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete medication"
        )


@router.post("/check-interactions")
async def check_drug_interactions(
    request: InteractionCheckRequest,
    db: Session = Depends(get_db)
):
    """Check for drug interactions between medications"""
    try:
        user = get_demo_user(db)
        
        checker = DrugInteractionChecker(db)
        interactions = checker.check_medication_list(request.medications, user.id)
        
        results = []
        for interaction in interactions:
            results.append({
                "medication_a": interaction.medication_a,
                "medication_b": interaction.medication_b,
                "severity": interaction.severity.value,
                "severity_score": interaction.severity_score,
                "severity_color": checker._get_severity_color(interaction.severity),
                "interaction_type": interaction.interaction_type.value,
                "mechanism": interaction.mechanism,
                "clinical_effects": interaction.clinical_effects,
                "management_recommendations": interaction.management_recommendations,
                "contraindicated": interaction.contraindicated,
                "monitoring_required": interaction.monitoring_required,
                "evidence_level": interaction.evidence_level,
                "risk_factors": interaction.risk_factors
            })
        
        # Get summary statistics
        high_severity_count = len([r for r in results if r["severity"] == "high"])
        moderate_severity_count = len([r for r in results if r["severity"] == "moderate"])
        contraindicated_count = len([r for r in results if r["contraindicated"]])
        
        return {
            "interactions": results,
            "summary": {
                "total_interactions": len(results),
                "high_severity": high_severity_count,
                "moderate_severity": moderate_severity_count,
                "low_severity": len(results) - high_severity_count - moderate_severity_count,
                "contraindicated": contraindicated_count,
                "requires_monitoring": len([r for r in results if r["monitoring_required"]])
            },
            "medications_checked": request.medications,
            "checked_at": datetime.now(timezone.utc).isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error checking drug interactions: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to check drug interactions"
        )


@router.get("/user-interactions")
async def get_user_drug_interactions(
    severity_filter: Optional[str] = Query(None, description="Filter by severity: low, moderate, high"),
    include_acknowledged: bool = Query(False, description="Include acknowledged interactions"),
    db: Session = Depends(get_db)
):
    """Get all drug interactions for user's current medications"""
    try:
        user = get_demo_user(db)
        
        checker = DrugInteractionChecker(db)
        interactions = checker.get_user_medication_interactions(user.id)
        
        # Apply filters
        if severity_filter:
            interactions = [i for i in interactions if i["severity"] == severity_filter]
        
        if not include_acknowledged:
            # Get acknowledged interaction IDs
            acknowledged_reports = db.query(DrugInteractionReport).filter(
                DrugInteractionReport.user_id == user.id,
                DrugInteractionReport.acknowledged_by_user == True
            ).all()
            
            acknowledged_pairs = set()
            for report in acknowledged_reports:
                pair = (report.medication_a.name, report.medication_b.name)
                acknowledged_pairs.add(pair)
                acknowledged_pairs.add((pair[1], pair[0]))  # Both directions
            
            interactions = [
                i for i in interactions 
                if (i["medication_a"], i["medication_b"]) not in acknowledged_pairs
            ]
        
        return {
            "interactions": interactions,
            "total_count": len(interactions),
            "severity_filter": severity_filter,
            "include_acknowledged": include_acknowledged,
            "checked_at": datetime.now(timezone.utc).isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error getting user drug interactions: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve drug interactions"
        )


@router.post("/dose-log")
async def log_medication_dose(
    request: LogDoseRequest,
    db: Session = Depends(get_db)
):
    """Log a medication dose (taken, missed, etc.)"""
    try:
        user = get_demo_user(db)
        
        # Verify user medication belongs to user
        user_medication = db.query(UserMedication).filter(
            UserMedication.id == request.user_medication_id,
            UserMedication.user_id == user.id
        ).first()
        
        if not user_medication:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User medication not found"
            )
        
        # Create dose log
        dose_log = MedicationDoseLog(
            user_medication_id=request.user_medication_id,
            scheduled_time=request.actual_time or datetime.now(timezone.utc),
            actual_time=request.actual_time,
            status=request.status,
            dosage_taken=request.dosage_taken,
            notes=request.notes,
            side_effects_reported=request.side_effects_reported or [],
            severity_rating=request.severity_rating
        )
        
        db.add(dose_log)
        
        # Update adherence statistics
        if request.status == "taken":
            user_medication.doses_taken += 1
        elif request.status == "missed":
            user_medication.doses_missed += 1
        
        user_medication.total_doses_prescribed += 1
        user_medication.calculate_adherence()
        
        db.commit()
        db.refresh(dose_log)
        
        return {
            "message": "Dose logged successfully",
            "dose_log_id": dose_log.id,
            "status": dose_log.status,
            "logged_at": dose_log.created_at.isoformat(),
            "adherence_percentage": user_medication.adherence_percentage
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error logging medication dose: {e}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to log medication dose"
        )


@router.get("/dose-history/{user_medication_id}")
async def get_dose_history(
    user_medication_id: str,
    days: int = Query(30, ge=1, le=365, description="Number of days to retrieve"),
    db: Session = Depends(get_db)
):
    """Get dose history for a specific medication"""
    try:
        user = get_demo_user(db)
        
        # Verify user medication belongs to user
        user_medication = db.query(UserMedication).filter(
            UserMedication.id == user_medication_id,
            UserMedication.user_id == user.id
        ).first()
        
        if not user_medication:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User medication not found"
            )
        
        # Get dose logs for the specified period
        start_date = datetime.now(timezone.utc) - timedelta(days=days)
        dose_logs = db.query(MedicationDoseLog).filter(
            MedicationDoseLog.user_medication_id == user_medication_id,
            MedicationDoseLog.scheduled_time >= start_date
        ).order_by(MedicationDoseLog.scheduled_time.desc()).all()
        
        results = []
        for log in dose_logs:
            results.append({
                "id": log.id,
                "scheduled_time": log.scheduled_time.isoformat(),
                "actual_time": log.actual_time.isoformat() if log.actual_time else None,
                "status": log.status,
                "dosage_taken": log.dosage_taken,
                "notes": log.notes,
                "side_effects_reported": log.side_effects_reported or [],
                "severity_rating": log.severity_rating,
                "is_late": log.is_late() if log.actual_time else False,
                "created_at": log.created_at.isoformat()
            })
        
        # Calculate statistics
        total_doses = len(results)
        taken_doses = len([r for r in results if r["status"] == "taken"])
        missed_doses = len([r for r in results if r["status"] == "missed"])
        late_doses = len([r for r in results if r["is_late"]])
        
        return {
            "dose_history": results,
            "medication": {
                "id": user_medication.id,
                "name": user_medication.medication.name if user_medication.medication else "Unknown",
                "dosage": user_medication.dosage,
                "frequency": user_medication.frequency
            },
            "statistics": {
                "total_doses": total_doses,
                "taken_doses": taken_doses,
                "missed_doses": missed_doses,
                "late_doses": late_doses,
                "adherence_percentage": user_medication.adherence_percentage,
                "period_days": days
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting dose history: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve dose history"
        )


@router.post("/reminders")
async def create_medication_reminder(
    request: MedicationReminderRequest,
    db: Session = Depends(get_db)
):
    """Create a medication reminder"""
    try:
        user = get_demo_user(db)
        
        # Verify user medication belongs to user
        user_medication = db.query(UserMedication).filter(
            UserMedication.id == request.user_medication_id,
            UserMedication.user_id == user.id
        ).first()
        
        if not user_medication:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User medication not found"
            )
        
        # Create reminder
        reminder = MedicationReminder(
            user_medication_id=request.user_medication_id,
            reminder_time=request.reminder_time,
            reminder_type=request.reminder_type,
            title=request.title,
            message=request.message,
            delivery_methods=request.delivery_methods,
            priority=request.priority
        )
        
        db.add(reminder)
        db.commit()
        db.refresh(reminder)
        
        return {
            "message": "Reminder created successfully",
            "reminder_id": reminder.id,
            "reminder_time": reminder.reminder_time.isoformat(),
            "title": reminder.title,
            "status": reminder.status
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating medication reminder: {e}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create medication reminder"
        )


@router.get("/reminders")
async def get_medication_reminders(
    status_filter: Optional[str] = Query(None, description="Filter by status: scheduled, sent, acknowledged"),
    days_ahead: int = Query(7, ge=1, le=30, description="Days ahead to retrieve reminders"),
    db: Session = Depends(get_db)
):
    """Get medication reminders for user"""
    try:
        user = get_demo_user(db)
        
        # Get user's medication IDs
        user_medication_ids = [um.id for um in db.query(UserMedication).filter(
            UserMedication.user_id == user.id
        ).all()]
        
        if not user_medication_ids:
            return {"reminders": [], "total_count": 0}
        
        # Build query
        end_date = datetime.now(timezone.utc) + timedelta(days=days_ahead)
        query = db.query(MedicationReminder).filter(
            MedicationReminder.user_medication_id.in_(user_medication_ids),
            MedicationReminder.reminder_time <= end_date
        )
        
        if status_filter:
            query = query.filter(MedicationReminder.status == status_filter)
        
        reminders = query.order_by(MedicationReminder.reminder_time).all()
        
        results = []
        for reminder in reminders:
            user_medication = db.query(UserMedication).filter(
                UserMedication.id == reminder.user_medication_id
            ).first()
            
            medication_info = None
            if user_medication and user_medication.medication:
                medication_info = {
                    "name": user_medication.medication.name,
                    "dosage": user_medication.dosage,
                    "frequency": user_medication.frequency
                }
            
            results.append({
                "id": reminder.id,
                "reminder_time": reminder.reminder_time.isoformat(),
                "reminder_type": reminder.reminder_type,
                "title": reminder.title,
                "message": reminder.message,
                "status": reminder.status,
                "priority": reminder.priority,
                "delivery_methods": reminder.delivery_methods,
                "medication": medication_info,
                "is_due": reminder.is_due(),
                "sent_at": reminder.sent_at.isoformat() if reminder.sent_at else None,
                "acknowledged_at": reminder.acknowledged_at.isoformat() if reminder.acknowledged_at else None
            })
        
        return {
            "reminders": results,
            "total_count": len(results),
            "status_filter": status_filter,
            "days_ahead": days_ahead
        }
        
    except Exception as e:
        logger.error(f"Error getting medication reminders: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve medication reminders"
        )


@router.post("/seed-database")
async def seed_medication_database(
    db: Session = Depends(get_db)
):
    """Seed database with common medications (development/demo endpoint)"""
    try:
        seeder = MedicationDatabaseSeeder(db)
        
        # Check if database is already seeded
        current_count = seeder.get_medication_count()
        if current_count > 0:
            return {
                "message": f"Database already contains {current_count} medications",
                "seeded": False,
                "medication_count": current_count
            }
        
        # Seed the database
        success = seeder.seed_common_medications()
        
        if success:
            new_count = seeder.get_medication_count()
            return {
                "message": "Medication database seeded successfully",
                "seeded": True,
                "medication_count": new_count
            }
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to seed medication database"
            )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error seeding medication database: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to seed medication database"
        )