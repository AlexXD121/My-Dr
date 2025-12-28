"""
Enhanced Conversation API endpoints for MyDoc AI Medical Assistant

This module provides context-aware conversation endpoints with memory management
and intelligent conversation handling.
"""

import logging
from datetime import datetime, timezone
from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import desc, and_
from pydantic import BaseModel, Field
import uuid

from database import get_db
from models import User, Conversation, Message
from conversation_context import create_context_manager, get_enhanced_ai_prompt
from mydoc import ask_mydoc
from enhanced_medical_ai import enhanced_medical_ai, MedicalConsultationRequest

logger = logging.getLogger(__name__)

# Create router
router = APIRouter(prefix="/conversations", tags=["conversations"])


# Pydantic models for API requests/responses
class ConversationCreateRequest(BaseModel):
    """Request model for creating a new conversation"""
    initial_message: Optional[str] = Field(None, description="Optional initial message")
    session_id: Optional[str] = Field(None, description="Optional session ID")


class MessageSendRequest(BaseModel):
    """Request model for sending a message"""
    content: str = Field(..., min_length=1, max_length=5000, description="Message content")
    session_id: Optional[str] = Field(None, description="Session ID")


class MessageResponse(BaseModel):
    """Response model for a message"""
    id: str
    content: str
    sender: str
    timestamp: datetime
    medical_analysis: Optional[Dict[str, Any]]
    
    class Config:
        from_attributes = True


class ConversationResponse(BaseModel):
    """Response model for a conversation"""
    id: str
    started_at: datetime
    last_message_at: datetime
    status: str
    context_summary: Optional[str]
    message_count: int
    crisis_level: str


class ConversationDetailResponse(BaseModel):
    """Detailed response model for a conversation with messages"""
    id: str
    started_at: datetime
    last_message_at: datetime
    status: str
    context_summary: Optional[str]
    crisis_level: str
    messages: List[MessageResponse]
    context_metadata: Dict[str, Any]


class ChatResponse(BaseModel):
    """Response model for chat interactions"""
    message_id: str
    ai_response: str
    user_message_id: str
    conversation_id: str
    medical_analysis: Optional[Dict[str, Any]]
    context_metadata: Dict[str, Any]
    timestamp: datetime
    crisis_detection: Optional[Dict[str, Any]] = None  # Crisis detection results


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
@router.post("/", response_model=ConversationResponse)
async def create_conversation(
    request: ConversationCreateRequest,
    db: Session = Depends(get_db)
):
    """Create a new conversation"""
    try:
        # Get or create user
        user = get_or_create_user(db)
        
        # Create new conversation
        conversation = Conversation(
            user_id=user.id,
            started_at=datetime.now(timezone.utc),
            last_message_at=datetime.now(timezone.utc),
            status="active",
            crisis_level="low"
        )
        
        db.add(conversation)
        db.commit()
        db.refresh(conversation)
        
        # If initial message provided, process it
        message_count = 0
        if request.initial_message:
            # Create user message
            user_message = Message(
                conversation_id=conversation.id,
                content=request.initial_message,
                sender="user",
                timestamp=datetime.now(timezone.utc)
            )
            db.add(user_message)
            db.commit()
            
            # Get AI response with enhanced medical AI
            context_manager = create_context_manager(user, conversation, db)
            context = context_manager.build_context()
            
            # Use enhanced medical AI service
            consultation_request = MedicalConsultationRequest(
                message=request.initial_message,
                user_id=user.firebase_uid,
                context=context,
                conversation_id=conversation.id
            )
            
            consultation_response = await enhanced_medical_ai.medical_consultation(consultation_request)
            ai_response = consultation_response.response
            context_metadata = consultation_response.consultation_metadata
            
            # Create AI message
            ai_message = Message(
                conversation_id=conversation.id,
                content=ai_response,
                sender="ai",
                timestamp=datetime.now(timezone.utc)
            )
            db.add(ai_message)
            db.commit()
            
            message_count = 2
            
            # Update conversation
            conversation.last_message_at = datetime.now(timezone.utc)
            db.commit()
        
        logger.info(f"Created conversation {conversation.id} for user {user.email}")
        
        return ConversationResponse(
            id=conversation.id,
            started_at=conversation.started_at,
            last_message_at=conversation.last_message_at,
            status=conversation.status,
            context_summary=conversation.context_summary,
            message_count=message_count,
            crisis_level=conversation.crisis_level
        )
        
    except Exception as e:
        logger.error(f"Failed to create conversation for user {current_user.uid}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create conversation. Please try again."
        )


@router.get("/", response_model=List[ConversationResponse])
async def get_conversations(
    limit: int = 20,
    offset: int = 0,
    status_filter: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Get user's conversations"""
    try:
        # Get or create user
        user = get_or_create_user(db)
        
        # Build query
        query = db.query(Conversation).filter(Conversation.user_id == user.id)
        
        if status_filter:
            query = query.filter(Conversation.status == status_filter)
        
        # Get conversations with message counts
        conversations = query.order_by(desc(Conversation.last_message_at)).offset(offset).limit(limit).all()
        
        result = []
        for conv in conversations:
            message_count = db.query(Message).filter(Message.conversation_id == conv.id).count()
            
            result.append(ConversationResponse(
                id=conv.id,
                started_at=conv.started_at,
                last_message_at=conv.last_message_at,
                status=conv.status,
                context_summary=conv.context_summary,
                message_count=message_count,
                crisis_level=conv.crisis_level
            ))
        
        return result
        
    except Exception as e:
        logger.error(f"Failed to get conversations for user {current_user.uid}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve conversations. Please try again."
        )


@router.get("/{conversation_id}", response_model=ConversationDetailResponse)
async def get_conversation(
    conversation_id: str,
    db: Session = Depends(get_db)
):
    """Get a specific conversation with messages"""
    try:
        # Get or create user
        user = get_or_create_user(db)
        
        # Get conversation
        conversation = db.query(Conversation).filter(
            and_(
                Conversation.id == conversation_id,
                Conversation.user_id == user.id
            )
        ).first()
        
        if not conversation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Conversation not found"
            )
        
        # Get messages
        messages = db.query(Message).filter(
            Message.conversation_id == conversation_id
        ).order_by(Message.timestamp).all()
        
        # Get conversation context for metadata
        conversation = db.query(Conversation).filter(Conversation.id == conversation_id).first()
        context_manager = create_context_manager(user, conversation, db)
        context = context_manager.build_context()
        
        context_metadata = {
            "medical_history": context.get('medical_history', ''),
            "conversation_history": context.get('conversation_history', ''),
            "timestamp": context.get('timestamp', '')
        }
        
        message_responses = [
            MessageResponse(
                id=msg.id,
                content=msg.content,
                sender=msg.sender,
                timestamp=msg.timestamp,
                medical_analysis=msg.medical_analysis
            )
            for msg in messages
        ]
        
        return ConversationDetailResponse(
            id=conversation.id,
            started_at=conversation.started_at,
            last_message_at=conversation.last_message_at,
            status=conversation.status,
            context_summary=conversation.context_summary,
            crisis_level=conversation.crisis_level,
            messages=message_responses,
            context_metadata=context_metadata
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get conversation {conversation_id} for user {current_user.uid}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve conversation. Please try again."
        )


@router.post("/{conversation_id}/messages", response_model=ChatResponse)
async def send_message(
    conversation_id: str,
    request: MessageSendRequest,
    db: Session = Depends(get_db)
):
    """Send a message in a conversation and get AI response"""
    try:
        # Get or create user
        user = get_or_create_user(db)
        
        # Verify conversation exists and belongs to user
        conversation = db.query(Conversation).filter(
            and_(
                Conversation.id == conversation_id,
                Conversation.user_id == user.id
            )
        ).first()
        
        if not conversation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Conversation not found"
            )
        
        # Create user message
        user_message = Message(
            conversation_id=conversation_id,
            content=request.content,
            sender="user",
            timestamp=datetime.now(timezone.utc)
        )
        db.add(user_message)
        db.commit()
        db.refresh(user_message)
        
        # Analyze medical content from user message
        medical_analysis = None
        crisis_detection_result = None
        try:
            # For medical system, we could do medical symptom analysis if needed
            # For now, we'll keep it simple
            medical_analysis = None
            
            # Extract crisis detection results (if we had analysis)
            # if analysis_result and analysis_result.crisis_detection:
            #     crisis_detection_result = analysis_result.crisis_detection
            
            # Update message with medical analysis
            user_message.medical_analysis = medical_analysis
            # user_message.urgency_score = analysis_result.urgency_score  # If we had analysis
            db.commit()
            
        except Exception as e:
            logger.warning(f"Mood analysis failed for message: {e}")
        
        # Get AI response with enhanced medical AI
        conversation = db.query(Conversation).filter(Conversation.id == conversation_id).first()
        context_manager = create_context_manager(user, conversation, db)
        context = context_manager.build_context()
        
        # Use enhanced medical AI service
        consultation_request = MedicalConsultationRequest(
            message=request.content,
            user_id=user.firebase_uid,
            context=context,
            conversation_id=conversation_id
        )
        
        consultation_response = await enhanced_medical_ai.medical_consultation(consultation_request)
        ai_response = consultation_response.response
        context_metadata = consultation_response.consultation_metadata
        
        # Update conversation crisis level based on emergency assessment
        if consultation_response.is_emergency:
            conversation.crisis_level = consultation_response.emergency_assessment.emergency_level.value
        
        # Store additional metadata in AI message
        ai_message_metadata = {
            "emergency_detected": consultation_response.is_emergency,
            "urgency_score": consultation_response.emergency_assessment.urgency_score,
            "validation_result": consultation_response.validation.validation_result.value,
            "quality_score": consultation_response.validation.quality_score,
            "ai_provider": consultation_response.ai_metadata["provider"]
        }
        
        # Create AI message with enhanced metadata
        ai_message = Message(
            conversation_id=conversation_id,
            content=ai_response,
            sender="ai",
            timestamp=datetime.now(timezone.utc),
            medical_analysis=ai_message_metadata
        )
        db.add(ai_message)
        db.commit()
        db.refresh(ai_message)
        
        # Update conversation context (simplified for medical system)
        # In medical system, context is managed differently
        
        # Update conversation last message time
        conversation.last_message_at = datetime.now(timezone.utc)
        
        # Update crisis level and flags based on detection results
        if crisis_detection_result:
            crisis_level = crisis_detection_result.get('overall_level', 'low')
            conversation.crisis_level = crisis_level
            
            # Update crisis flags if high-risk indicators found
            if crisis_level in ['high', 'critical']:
                current_flags = conversation.crisis_flags or []
                new_flag = {
                    'timestamp': datetime.now(timezone.utc).isoformat(),
                    'level': crisis_level,
                    'indicators': crisis_detection_result.get('top_indicators', []),
                    'severity_score': crisis_detection_result.get('severity_score', 0)
                }
                current_flags.append(new_flag)
                # Keep only last 10 crisis flags
                conversation.crisis_flags = current_flags[-10:]
        
        # Also check context changes for additional crisis indicators
        if context_metadata.get("context_changes", {}).get("crisis_indicators"):
            if conversation.crisis_level == "low":
                conversation.crisis_level = "medium"
        
        db.commit()
        
        logger.info(f"Message exchange completed for conversation {conversation_id}")
        
        return ChatResponse(
            message_id=ai_message.id,
            ai_response=ai_response,
            user_message_id=user_message.id,
            conversation_id=conversation_id,
            medical_analysis=medical_analysis,
            context_metadata=context_metadata,
            timestamp=ai_message.timestamp,
            crisis_detection=crisis_detection_result
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to send message in conversation {conversation_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to send message. Please try again."
        )


@router.put("/{conversation_id}/status")
async def update_conversation_status(
    conversation_id: str,
    status: str,
    db: Session = Depends(get_db)
):
    """Update conversation status (active, archived, flagged)"""
    try:
        # Get or create user
        user = get_or_create_user(db)
        
        # Verify conversation exists and belongs to user
        conversation = db.query(Conversation).filter(
            and_(
                Conversation.id == conversation_id,
                Conversation.user_id == user.id
            )
        ).first()
        
        if not conversation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Conversation not found"
            )
        
        # Validate status
        valid_statuses = ["active", "archived", "flagged"]
        if status not in valid_statuses:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid status. Must be one of: {', '.join(valid_statuses)}"
            )
        
        # Update status
        conversation.status = status
        db.commit()
        
        logger.info(f"Updated conversation {conversation_id} status to {status}")
        
        return {"message": f"Conversation status updated to {status}"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to update conversation status: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update conversation status. Please try again."
        )


@router.delete("/{conversation_id}")
async def delete_conversation(
    conversation_id: str,
    db: Session = Depends(get_db)
):
    """Delete a conversation and all its messages"""
    try:
        # Get or create user
        user = get_or_create_user(db)
        
        # Verify conversation exists and belongs to user
        conversation = db.query(Conversation).filter(
            and_(
                Conversation.id == conversation_id,
                Conversation.user_id == user.id
            )
        ).first()
        
        if not conversation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Conversation not found"
            )
        
        # Delete conversation (messages will be deleted due to cascade)
        db.delete(conversation)
        db.commit()
        
        logger.info(f"Deleted conversation {conversation_id} for user {user.email}")
        
        return {"message": "Conversation deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to delete conversation {conversation_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete conversation. Please try again."
        )


@router.post("/{conversation_id}/summarize")
async def regenerate_summary(
    conversation_id: str,
    db: Session = Depends(get_db)
):
    """Regenerate conversation summary"""
    try:
        # Get or create user
        user = get_or_create_user(db)
        
        # Verify conversation exists and belongs to user
        conversation = db.query(Conversation).filter(
            and_(
                Conversation.id == conversation_id,
                Conversation.user_id == user.id
            )
        ).first()
        
        if not conversation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Conversation not found"
            )
        
        # Force regenerate summary
        messages = db.query(Message).filter(
            Message.conversation_id == conversation_id
        ).order_by(Message.timestamp).all()
        
        # Generate simple summary for medical conversations
        if messages:
            new_summary = f"Medical consultation with {len(messages)} messages. Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M')}"
        else:
            new_summary = "Empty conversation"
        
        conversation.context_summary = new_summary
        db.commit()
        
        logger.info(f"Regenerated summary for conversation {conversation_id}")
        
        return {
            "message": "Summary regenerated successfully",
            "summary": new_summary
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to regenerate summary for conversation {conversation_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to regenerate summary. Please try again."
        )