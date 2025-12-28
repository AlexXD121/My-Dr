"""
Data Export API endpoints for MyDoc AI Medical Assistant
"""
import logging
import io
import csv
from datetime import datetime, timezone, timedelta
from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from sqlalchemy import desc, and_
from pydantic import BaseModel
import json

from database import get_db
from models import User, MedicalRecord, Conversation, Message, Consultation

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

logger = logging.getLogger(__name__)

# Create router
router = APIRouter(prefix="/export", tags=["export"])


# Pydantic models for API requests/responses
class ExportRequest(BaseModel):
    """Request model for data export"""
    format: str = "json"  # json, csv, pdf
    data_types: List[str] = ["medical_records", "conversations", "consultations"]
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    include_analysis: bool = True


class ExportSummary(BaseModel):
    """Response model for export summary"""
    total_medical_records: int
    total_conversations: int
    total_messages: int
    total_consultations: int
    date_range: Dict[str, str]
    export_timestamp: str


# Helper functions
def get_user_data(db: Session, user: User, start_date: Optional[datetime] = None, end_date: Optional[datetime] = None) -> Dict[str, Any]:
    """Get all user data for export"""
    
    # Get medical records
    medical_query = db.query(MedicalRecord).filter(MedicalRecord.user_id == user.id)
    if start_date:
        medical_query = medical_query.filter(MedicalRecord.created_at >= start_date)
    if end_date:
        medical_query = medical_query.filter(MedicalRecord.created_at <= end_date)
    medical_records = medical_query.order_by(desc(MedicalRecord.created_at)).all()
    
    # Get conversations and messages
    conv_query = db.query(Conversation).filter(Conversation.user_id == user.id)
    if start_date:
        conv_query = conv_query.filter(Conversation.started_at >= start_date)
    if end_date:
        conv_query = conv_query.filter(Conversation.started_at <= end_date)
    conversations = conv_query.order_by(desc(Conversation.started_at)).all()
    
    # Get messages for conversations
    all_messages = []
    for conv in conversations:
        messages = db.query(Message).filter(Message.conversation_id == conv.id).order_by(Message.timestamp).all()
        all_messages.extend(messages)
    
    # Get consultations
    consultation_query = db.query(Consultation).filter(Consultation.user_id == user.id)
    if start_date:
        consultation_query = consultation_query.filter(Consultation.created_at >= start_date)
    if end_date:
        consultation_query = consultation_query.filter(Consultation.created_at <= end_date)
    consultations = consultation_query.order_by(desc(Consultation.created_at)).all()
    
    return {
        'user_info': {
            'id': user.id,
            'email': user.email,
            'display_name': user.display_name,
            'created_at': user.created_at.isoformat() if user.created_at else None,
            'export_timestamp': datetime.now(timezone.utc).isoformat()
        },
        'medical_records': medical_records,
        'conversations': conversations,
        'messages': all_messages,
        'consultations': consultations
    }


def format_medical_record_for_export(record: MedicalRecord, include_analysis: bool = True) -> Dict[str, Any]:
    """Format medical record for export"""
    data = {
        'id': record.id,
        'created_at': record.created_at.isoformat(),
        'record_type': record.record_type,
        'title': record.title,
        'description': record.description,
        'symptoms': record.symptoms,
        'diagnosis': record.diagnosis,
        'treatment': record.treatment,
        'medications': record.medications,
        'notes': record.notes
    }
    
    if include_analysis:
        data.update({
            'severity_level': record.severity_level,
            'emergency_flags': record.emergency_flags,
            'follow_up_required': record.follow_up_required
        })
    
    return data


def format_conversation_for_export(conv: Conversation, messages: List[Message], include_analysis: bool = True) -> Dict[str, Any]:
    """Format conversation for export"""
    data = {
        'id': conv.id,
        'started_at': conv.started_at.isoformat(),
        'last_message_at': conv.last_message_at.isoformat() if conv.last_message_at else None,
        'status': conv.status,
        'message_count': len(messages),
        'messages': []
    }
    
    for msg in messages:
        msg_data = {
            'id': msg.id,
            'timestamp': msg.timestamp.isoformat(),
            'sender': msg.sender,
            'content': msg.content
        }
        
        if include_analysis and hasattr(msg, 'analysis'):
            msg_data['analysis'] = msg.analysis
        
        data['messages'].append(msg_data)
    
    if include_analysis:
        data.update({
            'context_summary': getattr(conv, 'context_summary', None),
            'medical_context': getattr(conv, 'medical_context', None)
        })
    
    return data


def format_consultation_for_export(consultation: Consultation, include_analysis: bool = True) -> Dict[str, Any]:
    """Format consultation for export"""
    data = {
        'id': consultation.id,
        'created_at': consultation.created_at.isoformat(),
        'symptoms': consultation.symptoms,
        'diagnosis': consultation.diagnosis,
        'recommendations': consultation.recommendations,
        'severity_assessment': consultation.severity_assessment,
        'follow_up_needed': consultation.follow_up_needed
    }
    
    if include_analysis:
        data.update({
            'emergency_level': getattr(consultation, 'emergency_level', None),
            'confidence_score': getattr(consultation, 'confidence_score', None)
        })
    
    return data


# API Endpoints
@router.get("/summary", response_model=ExportSummary)
async def get_export_summary(
    start_date: Optional[datetime] = Query(None, description="Start date for export"),
    end_date: Optional[datetime] = Query(None, description="End date for export"),
    db: Session = Depends(get_db)
):
    """Get summary of data available for export"""
    try:
        # Get or create user
        user = get_or_create_user(db)
        
        # Get data counts
        user_data = get_user_data(db, user, start_date, end_date)
        
        return ExportSummary(
            total_medical_records=len(user_data['medical_records']),
            total_conversations=len(user_data['conversations']),
            total_messages=len(user_data['messages']),
            total_consultations=len(user_data['consultations']),
            date_range={
                'start': start_date.isoformat() if start_date else 'all_time',
                'end': end_date.isoformat() if end_date else 'now'
            },
            export_timestamp=datetime.now(timezone.utc).isoformat()
        )
        
    except Exception as e:
        logger.error(f"Failed to get export summary: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate export summary. Please try again."
        )


@router.get("/json")
async def export_data_json(
    data_types: str = Query("medical_records,conversations,consultations", description="Comma-separated data types"),
    start_date: Optional[datetime] = Query(None, description="Start date for export"),
    end_date: Optional[datetime] = Query(None, description="End date for export"),
    include_analysis: bool = Query(True, description="Include analysis data"),
    db: Session = Depends(get_db)
):
    """Export user data as JSON"""
    try:
        # Get or create user
        user = get_or_create_user(db)
        
        # Parse data types
        requested_types = [t.strip() for t in data_types.split(',')]
        
        # Get user data
        user_data = get_user_data(db, user, start_date, end_date)
        
        # Format export data
        export_data = {
            'user_info': user_data['user_info'],
            'export_metadata': {
                'requested_types': requested_types,
                'include_analysis': include_analysis,
                'date_range': {
                    'start': start_date.isoformat() if start_date else None,
                    'end': end_date.isoformat() if end_date else None
                }
            }
        }
        
        # Add requested data types
        if 'medical_records' in requested_types:
            export_data['medical_records'] = [
                format_medical_record_for_export(record, include_analysis)
                for record in user_data['medical_records']
            ]
        
        if 'conversations' in requested_types:
            export_data['conversations'] = []
            for conv in user_data['conversations']:
                conv_messages = [msg for msg in user_data['messages'] if msg.conversation_id == conv.id]
                export_data['conversations'].append(
                    format_conversation_for_export(conv, conv_messages, include_analysis)
                )
        
        if 'consultations' in requested_types:
            export_data['consultations'] = [
                format_consultation_for_export(consultation, include_analysis)
                for consultation in user_data['consultations']
            ]
        
        # Create JSON response
        json_str = json.dumps(export_data, indent=2, default=str)
        
        # Generate filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"mydoc_data_export_{timestamp}.json"
        
        return Response(
            content=json_str,
            media_type="application/json",
            headers={
                "Content-Disposition": f"attachment; filename={filename}"
            }
        )
        
    except Exception as e:
        logger.error(f"Failed to export JSON data: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to export data. Please try again."
        )


@router.get("/csv")
async def export_data_csv(
    data_type: str = Query("medical_records", description="Data type to export (medical_records, conversations, consultations)"),
    start_date: Optional[datetime] = Query(None, description="Start date for export"),
    end_date: Optional[datetime] = Query(None, description="End date for export"),
    db: Session = Depends(get_db)
):
    """Export user data as CSV"""
    try:
        # Get or create user
        user = get_or_create_user(db)
        
        # Get user data
        user_data = get_user_data(db, user, start_date, end_date)
        
        # Create CSV content based on data type
        output = io.StringIO()
        
        if data_type == "medical_records":
            writer = csv.writer(output)
            writer.writerow([
                'ID', 'Created At', 'Record Type', 'Title', 'Description', 
                'Symptoms', 'Diagnosis', 'Treatment', 'Medications', 'Notes'
            ])
            
            for record in user_data['medical_records']:
                writer.writerow([
                    record.id,
                    record.created_at.isoformat(),
                    record.record_type,
                    record.title or '',
                    record.description or '',
                    ', '.join(record.symptoms) if record.symptoms else '',
                    record.diagnosis or '',
                    record.treatment or '',
                    ', '.join(record.medications) if record.medications else '',
                    record.notes or ''
                ])
        
        elif data_type == "conversations":
            writer = csv.writer(output)
            writer.writerow([
                'Conversation ID', 'Started At', 'Message ID', 'Timestamp', 
                'Sender', 'Content'
            ])
            
            for conv in user_data['conversations']:
                conv_messages = [msg for msg in user_data['messages'] if msg.conversation_id == conv.id]
                for msg in conv_messages:
                    writer.writerow([
                        conv.id,
                        conv.started_at.isoformat(),
                        msg.id,
                        msg.timestamp.isoformat(),
                        msg.sender,
                        msg.content
                    ])
        
        elif data_type == "consultations":
            writer = csv.writer(output)
            writer.writerow([
                'ID', 'Created At', 'Symptoms', 'Diagnosis', 'Recommendations', 
                'Severity Assessment', 'Follow Up Needed'
            ])
            
            for consultation in user_data['consultations']:
                writer.writerow([
                    consultation.id,
                    consultation.created_at.isoformat(),
                    ', '.join(consultation.symptoms) if consultation.symptoms else '',
                    consultation.diagnosis or '',
                    consultation.recommendations or '',
                    consultation.severity_assessment or '',
                    consultation.follow_up_needed or False
                ])
        
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Unsupported data type: {data_type}"
            )
        
        # Generate filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"mydoc_{data_type}_{timestamp}.csv"
        
        # Create response
        csv_content = output.getvalue()
        output.close()
        
        return Response(
            content=csv_content,
            media_type="text/csv",
            headers={
                "Content-Disposition": f"attachment; filename={filename}"
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to export CSV data: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to export data. Please try again."
        )


@router.delete("/user-data")
async def delete_all_user_data(
    confirm: bool = Query(False, description="Confirmation flag"),
    db: Session = Depends(get_db)
):
    """Delete all user data (for GDPR compliance)"""
    if not confirm:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Data deletion requires confirmation. Set confirm=true to proceed."
        )
    
    try:
        # Get user
        user = db.query(User).filter(User.firebase_uid == "default_user").first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Delete all user data (cascading deletes will handle related records)
        db.delete(user)
        db.commit()
        
        logger.info(f"All data deleted for user {user.email}")
        
        return {
            "message": "All user data has been permanently deleted",
            "deleted_at": datetime.now(timezone.utc).isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to delete user data: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete user data. Please try again."
        )