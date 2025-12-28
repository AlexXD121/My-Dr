"""
User Profile Management API
Handles user profile CRUD operations with authentication
"""

from datetime import datetime
from typing import Optional, Dict, Any
from fastapi import APIRouter, HTTPException, Depends, status, Request
from pydantic import BaseModel, EmailStr, validator
from sqlalchemy.orm import Session

from database import get_db
from auth_middleware import require_auth, require_verified_email
from models import User
from encryption_service import (
    log_data_access, verify_data_ownership, audit_logger,
    privacy_control_service, data_retention_service
)

router = APIRouter(prefix="/user", tags=["user"])

# Pydantic models for request/response
class UserProfileUpdate(BaseModel):
    display_name: Optional[str] = None
    phone: Optional[str] = None
    date_of_birth: Optional[str] = None
    gender: Optional[str] = None
    emergency_contact: Optional[Dict[str, Any]] = None
    medical_info: Optional[Dict[str, Any]] = None
    preferences: Optional[Dict[str, Any]] = None
    privacy_settings: Optional[Dict[str, Any]] = None

    @validator('gender')
    def validate_gender(cls, v):
        if v and v not in ['male', 'female', 'other', 'prefer-not-to-say']:
            raise ValueError('Invalid gender value')
        return v

    @validator('date_of_birth')
    def validate_date_of_birth(cls, v):
        if v:
            try:
                datetime.fromisoformat(v.replace('Z', '+00:00'))
            except ValueError:
                raise ValueError('Invalid date format')
        return v

class UserProfileResponse(BaseModel):
    firebase_uid: str
    email: str
    display_name: Optional[str]
    phone: Optional[str]
    date_of_birth: Optional[str]
    gender: Optional[str]
    email_verified: bool
    photo_url: Optional[str]
    emergency_contact: Optional[Dict[str, Any]]
    medical_info: Optional[Dict[str, Any]]
    preferences: Optional[Dict[str, Any]]
    privacy_settings: Optional[Dict[str, Any]]
    created_at: datetime
    last_login: Optional[datetime]
    is_active: bool

class UserStatsResponse(BaseModel):
    total_consultations: int
    total_messages: int
    total_conversations: int
    last_consultation: Optional[datetime]
    account_age_days: int
    email_verified: bool
    profile_completion: float

@router.get("/profile", response_model=UserProfileResponse)
async def get_user_profile(
    request: Request,
    current_user: User = Depends(require_auth),
    db: Session = Depends(get_db)
):
    """Get current user's profile information"""
    try:
        # Log profile access
        audit_logger.log_profile_access(
            user_id=current_user.firebase_uid,
            operation="read",
            ip_address=request.client.host if request.client else None
        )
        
        # Decrypt sensitive data for display
        decrypted_data = current_user.decrypt_sensitive_data()
        
        return UserProfileResponse(
            firebase_uid=current_user.firebase_uid,
            email=current_user.email,
            display_name=current_user.display_name,
            phone=decrypted_data.get('phone'),
            date_of_birth=decrypted_data.get('date_of_birth'),
            gender=current_user.gender,
            email_verified=current_user.email_verified,
            photo_url=current_user.photo_url,
            emergency_contact=decrypted_data.get('emergency_contact'),
            medical_info=decrypted_data.get('medical_info'),
            preferences=current_user.preferences,
            privacy_settings=current_user.privacy_settings,
            created_at=current_user.created_at,
            last_login=current_user.last_login,
            is_active=current_user.is_active
        )
    except Exception as e:
        print(f"❌ Error getting user profile: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve user profile"
        )

@router.put("/profile", response_model=UserProfileResponse)
async def update_user_profile(
    request: Request,
    profile_update: UserProfileUpdate,
    current_user: User = Depends(require_auth),
    db: Session = Depends(get_db)
):
    """Update current user's profile information"""
    try:
        # Log profile update
        audit_logger.log_profile_access(
            user_id=current_user.firebase_uid,
            operation="update",
            fields_accessed=list(profile_update.dict(exclude_unset=True).keys()),
            ip_address=request.client.host if request.client else None
        )
        
        # Update user fields
        update_data = profile_update.dict(exclude_unset=True)
        
        for field, value in update_data.items():
            if hasattr(current_user, field):
                setattr(current_user, field, value)
        
        # Encrypt sensitive data if user has encryption enabled
        if current_user.should_encrypt_data():
            current_user.encrypt_sensitive_data()
        
        # Update timestamp
        current_user.updated_at = datetime.utcnow()
        
        db.commit()
        db.refresh(current_user)
        
        print(f"✅ Updated profile for user: {current_user.email}")
        
        # Return decrypted data for display
        decrypted_data = current_user.decrypt_sensitive_data()
        
        return UserProfileResponse(
            firebase_uid=current_user.firebase_uid,
            email=current_user.email,
            display_name=current_user.display_name,
            phone=decrypted_data.get('phone'),
            date_of_birth=decrypted_data.get('date_of_birth'),
            gender=current_user.gender,
            email_verified=current_user.email_verified,
            photo_url=current_user.photo_url,
            emergency_contact=decrypted_data.get('emergency_contact'),
            medical_info=decrypted_data.get('medical_info'),
            preferences=current_user.preferences,
            privacy_settings=current_user.privacy_settings,
            created_at=current_user.created_at,
            last_login=current_user.last_login,
            is_active=current_user.is_active
        )
        
    except Exception as e:
        print(f"❌ Error updating user profile: {e}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update user profile"
        )

@router.get("/stats", response_model=UserStatsResponse)
async def get_user_stats(
    current_user: User = Depends(require_auth),
    db: Session = Depends(get_db)
):
    """Get user statistics and account information"""
    try:
        from models import Conversation, Message
        from sqlalchemy import func
        
        # Get conversation stats
        total_conversations = db.query(Conversation).filter(
            Conversation.user_id == current_user.id
        ).count()
        
        # Get message stats
        total_messages = db.query(Message).join(Conversation).filter(
            Conversation.user_id == current_user.id,
            Message.sender == "user"
        ).count()
        
        # Get last consultation
        last_conversation = db.query(Conversation).filter(
            Conversation.user_id == current_user.id
        ).order_by(Conversation.last_message_at.desc()).first()
        
        last_consultation = last_conversation.last_message_at if last_conversation else None
        
        # Calculate account age
        account_age = (datetime.utcnow() - current_user.created_at).days
        
        # Calculate profile completion
        profile_fields = [
            current_user.display_name,
            current_user.phone,
            current_user.date_of_birth,
            current_user.gender,
            current_user.emergency_contact,
            current_user.medical_info
        ]
        completed_fields = sum(1 for field in profile_fields if field)
        profile_completion = (completed_fields / len(profile_fields)) * 100
        
        return UserStatsResponse(
            total_consultations=total_conversations,
            total_messages=total_messages,
            total_conversations=total_conversations,
            last_consultation=last_consultation,
            account_age_days=account_age,
            email_verified=current_user.email_verified,
            profile_completion=profile_completion
        )
        
    except Exception as e:
        print(f"❌ Error getting user stats: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve user statistics"
        )

@router.delete("/account")
async def delete_user_account(
    current_user: User = Depends(require_verified_email),
    db: Session = Depends(get_db)
):
    """Delete user account and all associated data"""
    try:
        from models import Conversation, Message
        
        # Delete all user's conversations and messages (cascade should handle this)
        conversations = db.query(Conversation).filter(
            Conversation.user_id == current_user.id
        ).all()
        
        for conversation in conversations:
            db.delete(conversation)
        
        # Delete user
        db.delete(current_user)
        db.commit()
        
        print(f"✅ Deleted account for user: {current_user.email}")
        
        return {
            "message": "Account deleted successfully",
            "deleted_at": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        print(f"❌ Error deleting user account: {e}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete user account"
        )

@router.post("/deactivate")
async def deactivate_user_account(
    current_user: User = Depends(require_auth),
    db: Session = Depends(get_db)
):
    """Deactivate user account (soft delete)"""
    try:
        current_user.is_active = False
        current_user.deactivated_at = datetime.utcnow()
        
        db.commit()
        
        print(f"✅ Deactivated account for user: {current_user.email}")
        
        return {
            "message": "Account deactivated successfully",
            "deactivated_at": current_user.deactivated_at.isoformat()
        }
        
    except Exception as e:
        print(f"❌ Error deactivating user account: {e}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to deactivate user account"
        )

@router.post("/reactivate")
async def reactivate_user_account(
    current_user: User = Depends(require_auth),
    db: Session = Depends(get_db)
):
    """Reactivate user account"""
    try:
        current_user.is_active = True
        current_user.deactivated_at = None
        current_user.last_login = datetime.utcnow()
        
        db.commit()
        
        print(f"✅ Reactivated account for user: {current_user.email}")
        
        return {
            "message": "Account reactivated successfully",
            "reactivated_at": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        print(f"❌ Error reactivating user account: {e}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to reactivate user account"
        )

@router.get("/data-export")
async def export_user_data(
    format: str = "json",
    current_user: User = Depends(require_verified_email),
    db: Session = Depends(get_db)
):
    """Export all user data in specified format"""
    try:
        from models import Conversation, Message
        
        # Validate format
        valid_formats = ['json', 'csv']
        if format not in valid_formats:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid format. Supported formats: {valid_formats}"
            )
        
        # Get all user data
        conversations = db.query(Conversation).filter(
            Conversation.user_id == current_user.id
        ).all()
        
        user_data = {
            "user_profile": {
                "firebase_uid": current_user.firebase_uid,
                "email": current_user.email,
                "display_name": current_user.display_name,
                "phone": current_user.phone,
                "date_of_birth": current_user.date_of_birth,
                "gender": current_user.gender,
                "emergency_contact": current_user.emergency_contact,
                "medical_info": current_user.medical_info,
                "preferences": current_user.preferences,
                "privacy_settings": current_user.privacy_settings,
                "created_at": current_user.created_at.isoformat(),
                "last_login": current_user.last_login.isoformat() if current_user.last_login else None
            },
            "conversations": [],
            "export_metadata": {
                "exported_at": datetime.utcnow().isoformat(),
                "format": format,
                "total_conversations": len(conversations)
            }
        }
        
        # Add conversation data
        for conversation in conversations:
            messages = db.query(Message).filter(
                Message.conversation_id == conversation.id
            ).order_by(Message.sequence_number).all()
            
            conversation_data = {
                "id": conversation.id,
                "started_at": conversation.started_at.isoformat(),
                "last_message_at": conversation.last_message_at.isoformat(),
                "status": conversation.status,
                "consultation_type": conversation.consultation_type,
                "primary_concern": conversation.primary_concern,
                "context_summary": conversation.context_summary,
                "messages": [
                    {
                        "id": msg.id,
                        "content": msg.content,
                        "sender": msg.sender,
                        "timestamp": msg.timestamp.isoformat(),
                        "sequence_number": msg.sequence_number
                    }
                    for msg in messages
                ]
            }
            user_data["conversations"].append(conversation_data)
        
        print(f"✅ Exported data for user: {current_user.email}")
        
        return user_data
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Error exporting user data: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to export user data"
        )