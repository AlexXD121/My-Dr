"""
Medical History Management API endpoints for MyDoc AI Doctor Assistant
Implements comprehensive CRUD operations for medical records with validation and categorization
"""
import logging
from datetime import datetime, timezone, timedelta
from typing import List, Optional, Dict, Any, Union
from fastapi import APIRouter, Depends, HTTPException, Query, status, UploadFile, File
from sqlalchemy.orm import Session
from sqlalchemy import desc, func, and_, or_
from pydantic import BaseModel, Field, validator
import uuid
import json
import os

from database import get_db
from models import User, MedicalRecord

logger = logging.getLogger(__name__)

# Create router
router = APIRouter(prefix="/medical-history", tags=["medical-history"])


# Pydantic models for API requests/responses
class MedicalRecordCreate(BaseModel):
    """Model for creating a new medical record"""
    record_type: str = Field(..., description="Type of medical record")
    title: str = Field(..., min_length=1, max_length=255, description="Title/summary of the record")
    description: Optional[str] = Field(None, description="Detailed description")
    date_recorded: datetime = Field(..., description="Date of the medical event")
    healthcare_provider: Optional[str] = Field(None, max_length=255, description="Doctor/clinic name")
    provider_specialty: Optional[str] = Field(None, max_length=255, description="Medical specialty")
    facility_name: Optional[str] = Field(None, max_length=255, description="Hospital/clinic name")
    facility_address: Optional[str] = Field(None, description="Facility address")
    condition: Optional[str] = Field(None, max_length=255, description="Primary condition/diagnosis")
    icd_code: Optional[str] = Field(None, max_length=20, description="ICD-10 diagnosis code")
    severity: Optional[str] = Field(None, description="Severity level")
    status: str = Field(default="active", description="Record status")
    medications: List[Dict[str, Any]] = Field(default=[], description="List of prescribed medications")
    dosages: Dict[str, Any] = Field(default={}, description="Medication dosages and instructions")
    treatments: List[str] = Field(default=[], description="List of treatments/procedures")
    test_results: Dict[str, Any] = Field(default={}, description="Lab results and test outcomes")
    allergies: List[str] = Field(default=[], description="Known allergies related to this record")
    symptoms: List[str] = Field(default=[], description="Associated symptoms")
    vital_signs: Dict[str, Any] = Field(default={}, description="Recorded vital signs")
    follow_up_date: Optional[datetime] = Field(None, description="Next appointment/follow-up")
    follow_up_instructions: Optional[str] = Field(None, description="Care instructions")
    referrals: List[str] = Field(default=[], description="Specialist referrals")
    notes: Optional[str] = Field(None, description="Additional notes")
    tags: List[str] = Field(default=[], description="User-defined tags for organization")
    priority: str = Field(default="normal", description="Priority level")
    is_private: bool = Field(default=True, description="Privacy flag")

    @validator('record_type')
    def validate_record_type(cls, v):
        valid_types = ['visit', 'diagnosis', 'medication', 'test', 'procedure', 'vaccination', 'allergy']
        if v not in valid_types:
            raise ValueError(f'Record type must be one of: {", ".join(valid_types)}')
        return v

    @validator('severity')
    def validate_severity(cls, v):
        if v is not None:
            valid_severities = ['mild', 'moderate', 'severe', 'critical']
            if v not in valid_severities:
                raise ValueError(f'Severity must be one of: {", ".join(valid_severities)}')
        return v

    @validator('status')
    def validate_status(cls, v):
        valid_statuses = ['active', 'resolved', 'chronic', 'monitoring', 'inactive']
        if v not in valid_statuses:
            raise ValueError(f'Status must be one of: {", ".join(valid_statuses)}')
        return v

    @validator('priority')
    def validate_priority(cls, v):
        valid_priorities = ['low', 'normal', 'high', 'urgent']
        if v not in valid_priorities:
            raise ValueError(f'Priority must be one of: {", ".join(valid_priorities)}')
        return v


class MedicalRecordUpdate(BaseModel):
    """Model for updating an existing medical record"""
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    date_recorded: Optional[datetime] = None
    healthcare_provider: Optional[str] = Field(None, max_length=255)
    provider_specialty: Optional[str] = Field(None, max_length=255)
    facility_name: Optional[str] = Field(None, max_length=255)
    facility_address: Optional[str] = None
    condition: Optional[str] = Field(None, max_length=255)
    icd_code: Optional[str] = Field(None, max_length=20)
    severity: Optional[str] = None
    status: Optional[str] = None
    medications: Optional[List[Dict[str, Any]]] = None
    dosages: Optional[Dict[str, Any]] = None
    treatments: Optional[List[str]] = None
    test_results: Optional[Dict[str, Any]] = None
    allergies: Optional[List[str]] = None
    symptoms: Optional[List[str]] = None
    vital_signs: Optional[Dict[str, Any]] = None
    follow_up_date: Optional[datetime] = None
    follow_up_instructions: Optional[str] = None
    referrals: Optional[List[str]] = None
    notes: Optional[str] = None
    tags: Optional[List[str]] = None
    priority: Optional[str] = None
    is_private: Optional[bool] = None

    @validator('severity')
    def validate_severity(cls, v):
        if v is not None:
            valid_severities = ['mild', 'moderate', 'severe', 'critical']
            if v not in valid_severities:
                raise ValueError(f'Severity must be one of: {", ".join(valid_severities)}')
        return v

    @validator('status')
    def validate_status(cls, v):
        if v is not None:
            valid_statuses = ['active', 'resolved', 'chronic', 'monitoring', 'inactive']
            if v not in valid_statuses:
                raise ValueError(f'Status must be one of: {", ".join(valid_statuses)}')
        return v

    @validator('priority')
    def validate_priority(cls, v):
        if v is not None:
            valid_priorities = ['low', 'normal', 'high', 'urgent']
            if v not in valid_priorities:
                raise ValueError(f'Priority must be one of: {", ".join(valid_priorities)}')
        return v


class MedicalRecordResponse(BaseModel):
    """Response model for medical record"""
    id: str
    record_type: str
    title: str
    description: Optional[str]
    date_recorded: datetime
    healthcare_provider: Optional[str]
    provider_specialty: Optional[str]
    facility_name: Optional[str]
    facility_address: Optional[str]
    condition: Optional[str]
    icd_code: Optional[str]
    severity: Optional[str]
    status: str
    medications: List[Dict[str, Any]]
    dosages: Dict[str, Any]
    treatments: List[str]
    test_results: Dict[str, Any]
    allergies: List[str]
    symptoms: List[str]
    vital_signs: Dict[str, Any]
    attachments: List[Dict[str, Any]]
    follow_up_date: Optional[datetime]
    follow_up_instructions: Optional[str]
    referrals: List[str]
    notes: Optional[str]
    tags: List[str]
    priority: str
    is_private: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class MedicalRecordSummary(BaseModel):
    """Summary model for medical record lists"""
    id: str
    record_type: str
    title: str
    date_recorded: datetime
    condition: Optional[str]
    healthcare_provider: Optional[str]
    status: str
    priority: str
    tags: List[str]
    created_at: datetime

    class Config:
        from_attributes = True


class MedicalHistoryStats(BaseModel):
    """Statistics model for medical history"""
    total_records: int
    records_by_type: Dict[str, int]
    records_by_status: Dict[str, int]
    recent_records_count: int
    follow_ups_due: int
    most_common_conditions: List[Dict[str, Any]]
    most_frequent_providers: List[Dict[str, Any]]


# Helper functions
def get_or_create_user(db: Session, user_id: str = "demo-user") -> User:
    """Get or create user in database"""
    user = db.query(User).filter(User.firebase_uid == user_id).first()
    
    if not user:
        user = User(
            firebase_uid=user_id,
            email=f"{user_id}@mydoc.ai",
            display_name="Demo User",
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


def validate_and_sanitize_record_data(record_data: Dict[str, Any]) -> Dict[str, Any]:
    """Validate and sanitize medical record data"""
    # Remove any potentially harmful content
    if 'description' in record_data and record_data['description']:
        # Basic sanitization - in production, use a proper sanitization library
        record_data['description'] = record_data['description'].strip()
    
    if 'notes' in record_data and record_data['notes']:
        record_data['notes'] = record_data['notes'].strip()
    
    # Ensure medications list is properly formatted
    if 'medications' in record_data and record_data['medications']:
        sanitized_medications = []
        for med in record_data['medications']:
            if isinstance(med, dict):
                sanitized_medications.append(med)
            elif isinstance(med, str):
                sanitized_medications.append({"name": med})
        record_data['medications'] = sanitized_medications
    
    return record_data


def categorize_medical_record(record: MedicalRecord) -> List[str]:
    """Automatically categorize medical record based on content"""
    categories = []
    
    # Categorize by record type
    categories.append(f"type_{record.record_type}")
    
    # Categorize by condition if available
    if record.condition:
        condition_lower = record.condition.lower()
        if any(term in condition_lower for term in ['diabetes', 'blood sugar']):
            categories.append('endocrine')
        elif any(term in condition_lower for term in ['heart', 'cardiac', 'blood pressure']):
            categories.append('cardiovascular')
        elif any(term in condition_lower for term in ['lung', 'respiratory', 'asthma']):
            categories.append('respiratory')
        elif any(term in condition_lower for term in ['mental', 'depression', 'anxiety']):
            categories.append('mental_health')
        elif any(term in condition_lower for term in ['bone', 'joint', 'arthritis']):
            categories.append('musculoskeletal')
    
    # Categorize by severity
    if record.severity:
        categories.append(f"severity_{record.severity}")
    
    # Categorize by status
    categories.append(f"status_{record.status}")
    
    return categories


# API Endpoints
@router.post("/records", response_model=MedicalRecordResponse)
async def create_medical_record(
    record_data: MedicalRecordCreate,
    db: Session = Depends(get_db)
):
    """Create a new medical record"""
    try:
        # Get or create user
        user = get_or_create_user(db)
        
        # Validate and sanitize data
        sanitized_data = validate_and_sanitize_record_data(record_data.dict())
        
        # Create new medical record
        medical_record = MedicalRecord(
            id=str(uuid.uuid4()),
            user_id=user.id,
            **sanitized_data,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
            created_by=user.id,
            last_modified_by=user.id
        )
        
        # Auto-categorize the record
        categories = categorize_medical_record(medical_record)
        if hasattr(medical_record, 'categories'):
            medical_record.categories = categories
        
        db.add(medical_record)
        db.commit()
        db.refresh(medical_record)
        
        logger.info(f"Created medical record {medical_record.id} for user {user.email}")
        
        return medical_record
        
    except Exception as e:
        logger.error(f"Failed to create medical record: {e}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create medical record. Please try again."
        )


@router.get("/records", response_model=List[MedicalRecordSummary])
async def get_medical_records(
    db: Session = Depends(get_db),
    limit: int = Query(50, ge=1, le=200, description="Number of records to return"),
    offset: int = Query(0, ge=0, description="Number of records to skip"),
    record_type: Optional[str] = Query(None, description="Filter by record type"),
    status: Optional[str] = Query(None, description="Filter by status"),
    condition: Optional[str] = Query(None, description="Filter by condition"),
    provider: Optional[str] = Query(None, description="Filter by healthcare provider"),
    date_from: Optional[str] = Query(None, description="Filter records from date (ISO format)"),
    date_to: Optional[str] = Query(None, description="Filter records to date (ISO format)"),
    search: Optional[str] = Query(None, description="Search in title, description, and condition"),
    tags: Optional[str] = Query(None, description="Filter by tags (comma-separated)"),
    sort_by: str = Query("date_recorded", description="Sort field"),
    sort_order: str = Query("desc", description="Sort order (asc/desc)")
):
    """Get user's medical records with filtering and search"""
    try:
        # Get or create user
        user = get_or_create_user(db)
        
        # Build query
        query = db.query(MedicalRecord).filter(MedicalRecord.user_id == user.id)
        
        # Apply filters
        if record_type:
            query = query.filter(MedicalRecord.record_type == record_type)
        
        if status:
            query = query.filter(MedicalRecord.status == status)
        
        if condition:
            query = query.filter(MedicalRecord.condition.ilike(f"%{condition}%"))
        
        if provider:
            query = query.filter(MedicalRecord.healthcare_provider.ilike(f"%{provider}%"))
        
        # Date range filters
        if date_from:
            try:
                from_date = datetime.fromisoformat(date_from.replace('Z', '+00:00'))
                query = query.filter(MedicalRecord.date_recorded >= from_date)
            except ValueError:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid date_from format. Use ISO format."
                )
        
        if date_to:
            try:
                to_date = datetime.fromisoformat(date_to.replace('Z', '+00:00'))
                query = query.filter(MedicalRecord.date_recorded <= to_date)
            except ValueError:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid date_to format. Use ISO format."
                )
        
        # Search filter
        if search:
            search_term = f"%{search}%"
            query = query.filter(
                or_(
                    MedicalRecord.title.ilike(search_term),
                    MedicalRecord.description.ilike(search_term),
                    MedicalRecord.condition.ilike(search_term),
                    MedicalRecord.notes.ilike(search_term)
                )
            )
        
        # Tags filter
        if tags:
            tag_list = [tag.strip() for tag in tags.split(',')]
            # This would need to be adjusted based on how tags are stored in the database
            # For now, assuming tags are stored as JSON array
            for tag in tag_list:
                query = query.filter(MedicalRecord.tags.contains([tag]))
        
        # Sorting
        if sort_by == "date_recorded":
            sort_field = MedicalRecord.date_recorded
        elif sort_by == "created_at":
            sort_field = MedicalRecord.created_at
        elif sort_by == "title":
            sort_field = MedicalRecord.title
        elif sort_by == "priority":
            sort_field = MedicalRecord.priority
        else:
            sort_field = MedicalRecord.date_recorded
        
        if sort_order.lower() == "desc":
            query = query.order_by(desc(sort_field))
        else:
            query = query.order_by(sort_field)
        
        # Get total count for pagination
        total_count = query.count()
        
        # Apply pagination
        records = query.offset(offset).limit(limit).all()
        
        logger.info(f"Retrieved {len(records)} medical records for user {user.email}")
        
        return records
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get medical records: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve medical records. Please try again."
        )


@router.get("/records/{record_id}", response_model=MedicalRecordResponse)
async def get_medical_record(
    record_id: str,
    db: Session = Depends(get_db)
):
    """Get a specific medical record by ID"""
    try:
        # Get or create user
        user = get_or_create_user(db)
        
        # Get the medical record
        record = db.query(MedicalRecord).filter(
            MedicalRecord.id == record_id,
            MedicalRecord.user_id == user.id
        ).first()
        
        if not record:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Medical record not found"
            )
        
        logger.info(f"Retrieved medical record {record_id} for user {user.email}")
        
        return record
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get medical record {record_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve medical record. Please try again."
        )


@router.put("/records/{record_id}", response_model=MedicalRecordResponse)
async def update_medical_record(
    record_id: str,
    record_data: MedicalRecordUpdate,
    db: Session = Depends(get_db)
):
    """Update an existing medical record"""
    try:
        # Get or create user
        user = get_or_create_user(db)
        
        # Get the medical record
        record = db.query(MedicalRecord).filter(
            MedicalRecord.id == record_id,
            MedicalRecord.user_id == user.id
        ).first()
        
        if not record:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Medical record not found"
            )
        
        # Update only provided fields
        update_data = record_data.dict(exclude_unset=True)
        if update_data:
            # Validate and sanitize data
            sanitized_data = validate_and_sanitize_record_data(update_data)
            
            for field, value in sanitized_data.items():
                setattr(record, field, value)
            
            record.updated_at = datetime.now(timezone.utc)
            record.last_modified_by = user.id
            
            # Re-categorize if condition or type changed
            if 'condition' in update_data or 'record_type' in update_data:
                categories = categorize_medical_record(record)
                if hasattr(record, 'categories'):
                    record.categories = categories
            
            db.commit()
            db.refresh(record)
        
        logger.info(f"Updated medical record {record_id} for user {user.email}")
        
        return record
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to update medical record {record_id}: {e}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update medical record. Please try again."
        )


@router.delete("/records/{record_id}")
async def delete_medical_record(
    record_id: str,
    db: Session = Depends(get_db)
):
    """Delete a medical record"""
    try:
        # Get or create user
        user = get_or_create_user(db)
        
        # Get the medical record
        record = db.query(MedicalRecord).filter(
            MedicalRecord.id == record_id,
            MedicalRecord.user_id == user.id
        ).first()
        
        if not record:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Medical record not found"
            )
        
        # Delete the record
        db.delete(record)
        db.commit()
        
        logger.info(f"Deleted medical record {record_id} for user {user.email}")
        
        return {"message": "Medical record deleted successfully", "record_id": record_id}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to delete medical record {record_id}: {e}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete medical record. Please try again."
        )


@router.get("/stats", response_model=MedicalHistoryStats)
async def get_medical_history_stats(
    db: Session = Depends(get_db)
):
    """Get statistics about user's medical history"""
    try:
        # Get or create user
        user = get_or_create_user(db)
        
        # Get all records for the user
        records = db.query(MedicalRecord).filter(MedicalRecord.user_id == user.id).all()
        
        total_records = len(records)
        
        # Count by type
        records_by_type = {}
        for record in records:
            record_type = record.record_type
            records_by_type[record_type] = records_by_type.get(record_type, 0) + 1
        
        # Count by status
        records_by_status = {}
        for record in records:
            status = record.status
            records_by_status[status] = records_by_status.get(status, 0) + 1
        
        # Count recent records (last 30 days)
        thirty_days_ago = datetime.now(timezone.utc) - timedelta(days=30)
        recent_records_count = len([r for r in records if r.created_at >= thirty_days_ago])
        
        # Count follow-ups due
        now = datetime.now(timezone.utc)
        follow_ups_due = len([r for r in records if r.follow_up_date and r.follow_up_date <= now])
        
        # Most common conditions
        condition_counts = {}
        for record in records:
            if record.condition:
                condition = record.condition
                condition_counts[condition] = condition_counts.get(condition, 0) + 1
        
        most_common_conditions = [
            {"condition": condition, "count": count}
            for condition, count in sorted(condition_counts.items(), key=lambda x: x[1], reverse=True)[:5]
        ]
        
        # Most frequent providers
        provider_counts = {}
        for record in records:
            if record.healthcare_provider:
                provider = record.healthcare_provider
                provider_counts[provider] = provider_counts.get(provider, 0) + 1
        
        most_frequent_providers = [
            {"provider": provider, "count": count}
            for provider, count in sorted(provider_counts.items(), key=lambda x: x[1], reverse=True)[:5]
        ]
        
        stats = MedicalHistoryStats(
            total_records=total_records,
            records_by_type=records_by_type,
            records_by_status=records_by_status,
            recent_records_count=recent_records_count,
            follow_ups_due=follow_ups_due,
            most_common_conditions=most_common_conditions,
            most_frequent_providers=most_frequent_providers
        )
        
        logger.info(f"Generated medical history stats for user {user.email}")
        
        return stats
        
    except Exception as e:
        logger.error(f"Failed to get medical history stats: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve medical history statistics. Please try again."
        )


@router.post("/records/{record_id}/attachments")
async def upload_attachment(
    record_id: str,
    file: UploadFile = File(...),
    description: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Upload an attachment to a medical record"""
    try:
        # Get or create user
        user = get_or_create_user(db)
        
        # Get the medical record
        record = db.query(MedicalRecord).filter(
            MedicalRecord.id == record_id,
            MedicalRecord.user_id == user.id
        ).first()
        
        if not record:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Medical record not found"
            )
        
        # Validate file type and size
        allowed_types = ['image/jpeg', 'image/png', 'image/gif', 'application/pdf', 'text/plain']
        max_size = 10 * 1024 * 1024  # 10MB
        
        if file.content_type not in allowed_types:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"File type {file.content_type} not allowed. Allowed types: {', '.join(allowed_types)}"
            )
        
        # Read file content to check size
        content = await file.read()
        if len(content) > max_size:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="File size exceeds 10MB limit"
            )
        
        # Create uploads directory if it doesn't exist
        upload_dir = "uploads/medical_records"
        os.makedirs(upload_dir, exist_ok=True)
        
        # Generate unique filename
        file_extension = os.path.splitext(file.filename)[1]
        unique_filename = f"{record_id}_{uuid.uuid4()}{file_extension}"
        file_path = os.path.join(upload_dir, unique_filename)
        
        # Save file
        with open(file_path, "wb") as f:
            f.write(content)
        
        # Add attachment to record
        record.add_attachment(file_path, file.content_type, description)
        record.updated_at = datetime.now(timezone.utc)
        record.last_modified_by = user.id
        
        db.commit()
        
        logger.info(f"Uploaded attachment {unique_filename} to medical record {record_id}")
        
        return {
            "message": "Attachment uploaded successfully",
            "filename": unique_filename,
            "file_path": file_path,
            "file_type": file.content_type,
            "description": description
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to upload attachment to record {record_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to upload attachment. Please try again."
        )


@router.get("/categories")
async def get_record_categories(
    db: Session = Depends(get_db)
):
    """Get available medical record categories and tags"""
    try:
        # Get or create user
        user = get_or_create_user(db)
        
        # Get all unique tags from user's records
        records = db.query(MedicalRecord).filter(MedicalRecord.user_id == user.id).all()
        
        all_tags = set()
        for record in records:
            if record.tags:
                all_tags.update(record.tags)
        
        # Predefined categories
        predefined_categories = {
            "record_types": ['visit', 'diagnosis', 'medication', 'test', 'procedure', 'vaccination', 'allergy'],
            "severities": ['mild', 'moderate', 'severe', 'critical'],
            "statuses": ['active', 'resolved', 'chronic', 'monitoring', 'inactive'],
            "priorities": ['low', 'normal', 'high', 'urgent'],
            "medical_specialties": [
                'cardiology', 'endocrinology', 'respiratory', 'mental_health', 
                'musculoskeletal', 'dermatology', 'neurology', 'gastroenterology'
            ]
        }
        
        return {
            "predefined_categories": predefined_categories,
            "user_tags": sorted(list(all_tags)),
            "total_user_tags": len(all_tags)
        }
        
    except Exception as e:
        logger.error(f"Failed to get record categories: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve record categories. Please try again."
        )


@router.get("/export")
async def export_medical_history(
    db: Session = Depends(get_db),
    format: str = Query("json", description="Export format: json, pdf, csv"),
    date_from: Optional[str] = Query(None, description="Start date for export (ISO format)"),
    date_to: Optional[str] = Query(None, description="End date for export (ISO format)"),
    record_types: Optional[str] = Query(None, description="Comma-separated record types to include"),
    include_private: bool = Query(True, description="Include private records"),
    summary_only: bool = Query(False, description="Export summary only")
):
    """Export medical history in various formats"""
    try:
        # Get or create user
        user = get_or_create_user(db)
        
        # Build query with filters
        query = db.query(MedicalRecord).filter(MedicalRecord.user_id == user.id)
        
        # Apply privacy filter
        if not include_private:
            query = query.filter(MedicalRecord.is_private == False)
        
        # Date range filters
        if date_from:
            try:
                from_date = datetime.fromisoformat(date_from.replace('Z', '+00:00'))
                query = query.filter(MedicalRecord.date_recorded >= from_date)
            except ValueError:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid date_from format. Use ISO format."
                )
        
        if date_to:
            try:
                to_date = datetime.fromisoformat(date_to.replace('Z', '+00:00'))
                query = query.filter(MedicalRecord.date_recorded <= to_date)
            except ValueError:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid date_to format. Use ISO format."
                )
        
        # Record type filter
        if record_types:
            type_list = [t.strip() for t in record_types.split(',')]
            query = query.filter(MedicalRecord.record_type.in_(type_list))
        
        # Get records
        records = query.order_by(desc(MedicalRecord.date_recorded)).all()
        
        # Generate export based on format
        if format.lower() == "json":
            return await export_as_json(user, records, summary_only)
        elif format.lower() == "pdf":
            return await export_as_pdf(user, records, summary_only)
        elif format.lower() == "csv":
            return await export_as_csv(user, records, summary_only)
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid format. Supported formats: json, pdf, csv"
            )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to export medical history: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to export medical history. Please try again."
        )


async def export_as_json(user: User, records: List[MedicalRecord], summary_only: bool = False):
    """Export medical records as JSON"""
    export_data = {
        "export_info": {
            "user_id": user.id,
            "user_name": user.get_full_name(),
            "export_date": datetime.now(timezone.utc).isoformat(),
            "total_records": len(records),
            "format": "json",
            "summary_only": summary_only
        },
        "user_profile": {
            "name": user.get_full_name(),
            "email": user.email,
            "date_of_birth": user.date_of_birth.isoformat() if user.date_of_birth else None,
            "gender": user.gender,
            "medical_profile": user.medical_profile
        },
        "medical_records": []
    }
    
    for record in records:
        if summary_only:
            record_data = {
                "id": record.id,
                "record_type": record.record_type,
                "title": record.title,
                "date_recorded": record.date_recorded.isoformat(),
                "condition": record.condition,
                "healthcare_provider": record.healthcare_provider,
                "status": record.status,
                "priority": record.priority
            }
        else:
            record_data = {
                "id": record.id,
                "record_type": record.record_type,
                "title": record.title,
                "description": record.description,
                "date_recorded": record.date_recorded.isoformat(),
                "healthcare_provider": record.healthcare_provider,
                "provider_specialty": record.provider_specialty,
                "facility_name": record.facility_name,
                "facility_address": record.facility_address,
                "condition": record.condition,
                "icd_code": record.icd_code,
                "severity": record.severity,
                "status": record.status,
                "medications": record.medications,
                "dosages": record.dosages,
                "treatments": record.treatments,
                "test_results": record.test_results,
                "allergies": record.allergies,
                "symptoms": record.symptoms,
                "vital_signs": record.vital_signs,
                "follow_up_date": record.follow_up_date.isoformat() if record.follow_up_date else None,
                "follow_up_instructions": record.follow_up_instructions,
                "referrals": record.referrals,
                "notes": record.notes,
                "tags": record.tags,
                "priority": record.priority,
                "created_at": record.created_at.isoformat(),
                "updated_at": record.updated_at.isoformat()
            }
        
        export_data["medical_records"].append(record_data)
    
    return export_data


async def export_as_csv(user: User, records: List[MedicalRecord], summary_only: bool = False):
    """Export medical records as CSV"""
    import csv
    import io
    from fastapi.responses import StreamingResponse
    
    output = io.StringIO()
    
    if summary_only:
        fieldnames = [
            'id', 'record_type', 'title', 'date_recorded', 'condition', 
            'healthcare_provider', 'status', 'priority', 'created_at'
        ]
    else:
        fieldnames = [
            'id', 'record_type', 'title', 'description', 'date_recorded',
            'healthcare_provider', 'provider_specialty', 'facility_name',
            'condition', 'icd_code', 'severity', 'status', 'medications',
            'treatments', 'allergies', 'symptoms', 'notes', 'tags',
            'priority', 'created_at', 'updated_at'
        ]
    
    writer = csv.DictWriter(output, fieldnames=fieldnames)
    writer.writeheader()
    
    for record in records:
        if summary_only:
            row = {
                'id': record.id,
                'record_type': record.record_type,
                'title': record.title,
                'date_recorded': record.date_recorded.isoformat(),
                'condition': record.condition or '',
                'healthcare_provider': record.healthcare_provider or '',
                'status': record.status,
                'priority': record.priority,
                'created_at': record.created_at.isoformat()
            }
        else:
            row = {
                'id': record.id,
                'record_type': record.record_type,
                'title': record.title,
                'description': record.description or '',
                'date_recorded': record.date_recorded.isoformat(),
                'healthcare_provider': record.healthcare_provider or '',
                'provider_specialty': record.provider_specialty or '',
                'facility_name': record.facility_name or '',
                'condition': record.condition or '',
                'icd_code': record.icd_code or '',
                'severity': record.severity or '',
                'status': record.status,
                'medications': json.dumps(record.medications) if record.medications else '',
                'treatments': json.dumps(record.treatments) if record.treatments else '',
                'allergies': json.dumps(record.allergies) if record.allergies else '',
                'symptoms': json.dumps(record.symptoms) if record.symptoms else '',
                'notes': record.notes or '',
                'tags': json.dumps(record.tags) if record.tags else '',
                'priority': record.priority,
                'created_at': record.created_at.isoformat(),
                'updated_at': record.updated_at.isoformat()
            }
        
        writer.writerow(row)
    
    output.seek(0)
    
    return StreamingResponse(
        io.BytesIO(output.getvalue().encode('utf-8')),
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename=medical_history_{user.id}_{datetime.now().strftime('%Y%m%d')}.csv"}
    )


async def export_as_pdf(user: User, records: List[MedicalRecord], summary_only: bool = False):
    """Export medical records as PDF"""
    try:
        from reportlab.lib.pagesizes import letter, A4
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib.units import inch
        from reportlab.lib import colors
        import io
        from fastapi.responses import StreamingResponse
        
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=72, leftMargin=72, topMargin=72, bottomMargin=18)
        
        # Container for the 'Flowable' objects
        elements = []
        
        # Define styles
        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            spaceAfter=30,
            alignment=1  # Center alignment
        )
        
        heading_style = ParagraphStyle(
            'CustomHeading',
            parent=styles['Heading2'],
            fontSize=16,
            spaceAfter=12,
            textColor=colors.darkblue
        )
        
        # Title
        elements.append(Paragraph("Medical History Report", title_style))
        elements.append(Spacer(1, 12))
        
        # User information
        elements.append(Paragraph("Patient Information", heading_style))
        user_info = [
            ["Name:", user.get_full_name()],
            ["Email:", user.email],
            ["Date of Birth:", user.date_of_birth.strftime('%B %d, %Y') if user.date_of_birth else 'Not specified'],
            ["Gender:", user.gender or 'Not specified'],
            ["Export Date:", datetime.now(timezone.utc).strftime('%B %d, %Y at %I:%M %p UTC')]
        ]
        
        user_table = Table(user_info, colWidths=[2*inch, 4*inch])
        user_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ]))
        
        elements.append(user_table)
        elements.append(Spacer(1, 20))
        
        # Medical records
        elements.append(Paragraph(f"Medical Records ({len(records)} records)", heading_style))
        
        if not records:
            elements.append(Paragraph("No medical records found.", styles['Normal']))
        else:
            for i, record in enumerate(records):
                # Record header
                record_title = f"{record.record_type.title()}: {record.title}"
                elements.append(Paragraph(record_title, styles['Heading3']))
                
                # Record details
                record_data = [
                    ["Date:", record.date_recorded.strftime('%B %d, %Y')],
                    ["Status:", record.status.title()],
                    ["Priority:", record.priority.title()]
                ]
                
                if record.healthcare_provider:
                    record_data.append(["Provider:", record.healthcare_provider])
                
                if record.condition:
                    record_data.append(["Condition:", record.condition])
                
                if not summary_only:
                    if record.description:
                        record_data.append(["Description:", record.description])
                    
                    if record.medications:
                        meds = ", ".join([med.get('name', '') for med in record.medications if med.get('name')])
                        if meds:
                            record_data.append(["Medications:", meds])
                    
                    if record.notes:
                        record_data.append(["Notes:", record.notes])
                
                record_table = Table(record_data, colWidths=[1.5*inch, 4.5*inch])
                record_table.setStyle(TableStyle([
                    ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                    ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, -1), 9),
                    ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
                    ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                ]))
                
                elements.append(record_table)
                
                if i < len(records) - 1:
                    elements.append(Spacer(1, 12))
        
        # Build PDF
        doc.build(elements)
        buffer.seek(0)
        
        return StreamingResponse(
            io.BytesIO(buffer.getvalue()),
            media_type="application/pdf",
            headers={"Content-Disposition": f"attachment; filename=medical_history_{user.id}_{datetime.now().strftime('%Y%m%d')}.pdf"}
        )
        
    except ImportError:
        # Fallback if reportlab is not available
        raise HTTPException(
            status_code=status.HTTP_501_NOT_IMPLEMENTED,
            detail="PDF export is not available. Please install reportlab package."
        )
    except Exception as e:
        logger.error(f"Failed to generate PDF export: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate PDF export. Please try again."
        )


@router.post("/share")
async def create_shareable_summary(
    db: Session = Depends(get_db),
    record_ids: List[str] = [],
    include_sensitive: bool = False,
    expiry_hours: int = 24,
    recipient_email: Optional[str] = None
):
    """Create a shareable medical summary for healthcare providers"""
    try:
        # Get or create user
        user = get_or_create_user(db)
        
        # Get specified records or all records if none specified
        if record_ids:
            records = db.query(MedicalRecord).filter(
                MedicalRecord.user_id == user.id,
                MedicalRecord.id.in_(record_ids)
            ).all()
        else:
            records = db.query(MedicalRecord).filter(
                MedicalRecord.user_id == user.id
            ).order_by(desc(MedicalRecord.date_recorded)).limit(20).all()
        
        # Filter out private records if not including sensitive data
        if not include_sensitive:
            records = [r for r in records if not r.is_private]
        
        # Generate shareable summary
        summary_id = str(uuid.uuid4())
        expiry_date = datetime.now(timezone.utc) + timedelta(hours=expiry_hours)
        
        summary_data = {
            "summary_id": summary_id,
            "patient_name": user.get_full_name(),
            "patient_email": user.email,
            "generated_date": datetime.now(timezone.utc).isoformat(),
            "expiry_date": expiry_date.isoformat(),
            "recipient_email": recipient_email,
            "include_sensitive": include_sensitive,
            "total_records": len(records),
            "medical_summary": {
                "current_conditions": [],
                "current_medications": [],
                "recent_visits": [],
                "allergies": [],
                "chronic_conditions": []
            },
            "records": []
        }
        
        # Process records for summary
        all_conditions = set()
        all_medications = []
        all_allergies = set()
        
        for record in records:
            # Add to summary data
            record_summary = {
                "id": record.id,
                "type": record.record_type,
                "title": record.title,
                "date": record.date_recorded.isoformat(),
                "provider": record.healthcare_provider,
                "condition": record.condition,
                "status": record.status
            }
            
            summary_data["records"].append(record_summary)
            
            # Collect conditions
            if record.condition and record.status in ['active', 'chronic']:
                all_conditions.add(record.condition)
                if record.status == 'chronic':
                    summary_data["medical_summary"]["chronic_conditions"].append(record.condition)
            
            # Collect medications
            if record.medications:
                for med in record.medications:
                    if isinstance(med, dict) and med.get('name'):
                        all_medications.append({
                            "name": med['name'],
                            "dosage": med.get('dosage', ''),
                            "frequency": med.get('frequency', ''),
                            "prescribed_date": record.date_recorded.isoformat()
                        })
            
            # Collect allergies
            if record.allergies:
                all_allergies.update(record.allergies)
            
            # Add recent visits
            if record.record_type == 'visit' and record.date_recorded >= datetime.now(timezone.utc) - timedelta(days=90):
                summary_data["medical_summary"]["recent_visits"].append({
                    "date": record.date_recorded.isoformat(),
                    "provider": record.healthcare_provider,
                    "purpose": record.title,
                    "condition": record.condition
                })
        
        # Finalize summary
        summary_data["medical_summary"]["current_conditions"] = list(all_conditions)
        summary_data["medical_summary"]["current_medications"] = all_medications[-10:]  # Last 10 medications
        summary_data["medical_summary"]["allergies"] = list(all_allergies)
        
        # In a real implementation, you would store this in a secure temporary storage
        # For now, we'll return it directly
        
        logger.info(f"Created shareable medical summary {summary_id} for user {user.email}")
        
        return {
            "summary_id": summary_id,
            "share_url": f"/medical-history/shared/{summary_id}",
            "expiry_date": expiry_date.isoformat(),
            "summary_data": summary_data
        }
        
    except Exception as e:
        logger.error(f"Failed to create shareable summary: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create shareable summary. Please try again."
        )


@router.get("/backup")
async def create_backup(
    db: Session = Depends(get_db),
    include_attachments: bool = False
):
    """Create a complete backup of user's medical data"""
    try:
        # Get or create user
        user = get_or_create_user(db)
        
        # Get all records
        records = db.query(MedicalRecord).filter(MedicalRecord.user_id == user.id).all()
        
        # Create comprehensive backup
        backup_data = {
            "backup_info": {
                "user_id": user.id,
                "backup_date": datetime.now(timezone.utc).isoformat(),
                "total_records": len(records),
                "include_attachments": include_attachments,
                "version": "1.0"
            },
            "user_data": {
                "id": user.id,
                "firebase_uid": user.firebase_uid,
                "email": user.email,
                "display_name": user.display_name,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "date_of_birth": user.date_of_birth.isoformat() if user.date_of_birth else None,
                "gender": user.gender,
                "phone_number": user.phone_number,
                "emergency_contact_name": user.emergency_contact_name,
                "emergency_contact_phone": user.emergency_contact_phone,
                "emergency_contact_relationship": user.emergency_contact_relationship,
                "medical_profile": user.medical_profile,
                "preferences": user.preferences,
                "privacy_settings": user.privacy_settings,
                "created_at": user.created_at.isoformat(),
                "updated_at": user.updated_at.isoformat()
            },
            "medical_records": []
        }
        
        # Add all medical records
        for record in records:
            record_data = {
                "id": record.id,
                "record_type": record.record_type,
                "title": record.title,
                "description": record.description,
                "date_recorded": record.date_recorded.isoformat(),
                "healthcare_provider": record.healthcare_provider,
                "provider_specialty": record.provider_specialty,
                "facility_name": record.facility_name,
                "facility_address": record.facility_address,
                "condition": record.condition,
                "icd_code": record.icd_code,
                "severity": record.severity,
                "status": record.status,
                "medications": record.medications,
                "dosages": record.dosages,
                "treatments": record.treatments,
                "test_results": record.test_results,
                "allergies": record.allergies,
                "symptoms": record.symptoms,
                "vital_signs": record.vital_signs,
                "attachments": record.attachments if include_attachments else [],
                "follow_up_date": record.follow_up_date.isoformat() if record.follow_up_date else None,
                "follow_up_instructions": record.follow_up_instructions,
                "referrals": record.referrals,
                "notes": record.notes,
                "tags": record.tags,
                "priority": record.priority,
                "is_private": record.is_private,
                "created_at": record.created_at.isoformat(),
                "updated_at": record.updated_at.isoformat()
            }
            
            backup_data["medical_records"].append(record_data)
        
        logger.info(f"Created backup for user {user.email} with {len(records)} records")
        
        return backup_data
        
    except Exception as e:
        logger.error(f"Failed to create backup: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create backup. Please try again."
        )


@router.post("/restore")
async def restore_from_backup(
    backup_data: Dict[str, Any],
    db: Session = Depends(get_db),
    overwrite_existing: bool = False
):
    """Restore medical data from backup"""
    try:
        # Get or create user
        user = get_or_create_user(db)
        
        # Validate backup data structure
        if "backup_info" not in backup_data or "medical_records" not in backup_data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid backup data format"
            )
        
        restored_count = 0
        skipped_count = 0
        
        # Restore medical records
        for record_data in backup_data["medical_records"]:
            try:
                # Check if record already exists
                existing_record = db.query(MedicalRecord).filter(
                    MedicalRecord.user_id == user.id,
                    MedicalRecord.id == record_data.get("id")
                ).first()
                
                if existing_record and not overwrite_existing:
                    skipped_count += 1
                    continue
                
                # Create or update record
                if existing_record and overwrite_existing:
                    # Update existing record
                    for key, value in record_data.items():
                        if key not in ['id', 'user_id', 'created_at']:
                            if key in ['date_recorded', 'follow_up_date'] and value:
                                value = datetime.fromisoformat(value.replace('Z', '+00:00'))
                            elif key == 'updated_at' and value:
                                value = datetime.fromisoformat(value.replace('Z', '+00:00'))
                            setattr(existing_record, key, value)
                    
                    existing_record.updated_at = datetime.now(timezone.utc)
                    restored_count += 1
                else:
                    # Create new record
                    record_data_copy = record_data.copy()
                    record_data_copy['user_id'] = user.id
                    
                    # Convert date strings back to datetime objects
                    if record_data_copy.get('date_recorded'):
                        record_data_copy['date_recorded'] = datetime.fromisoformat(
                            record_data_copy['date_recorded'].replace('Z', '+00:00')
                        )
                    
                    if record_data_copy.get('follow_up_date'):
                        record_data_copy['follow_up_date'] = datetime.fromisoformat(
                            record_data_copy['follow_up_date'].replace('Z', '+00:00')
                        )
                    
                    if record_data_copy.get('created_at'):
                        record_data_copy['created_at'] = datetime.fromisoformat(
                            record_data_copy['created_at'].replace('Z', '+00:00')
                        )
                    
                    if record_data_copy.get('updated_at'):
                        record_data_copy['updated_at'] = datetime.fromisoformat(
                            record_data_copy['updated_at'].replace('Z', '+00:00')
                        )
                    
                    new_record = MedicalRecord(**record_data_copy)
                    db.add(new_record)
                    restored_count += 1
                
            except Exception as record_error:
                logger.error(f"Failed to restore record {record_data.get('id', 'unknown')}: {record_error}")
                skipped_count += 1
                continue
        
        db.commit()
        
        logger.info(f"Restored {restored_count} records for user {user.email}, skipped {skipped_count}")
        
        return {
            "message": "Backup restored successfully",
            "restored_records": restored_count,
            "skipped_records": skipped_count,
            "total_records": len(backup_data["medical_records"])
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to restore from backup: {e}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to restore from backup. Please try again."
        )