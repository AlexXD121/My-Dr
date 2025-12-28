from datetime import datetime
from typing import Optional, List
from fastapi import FastAPI, HTTPException, Request, status, Depends, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import asyncio
import json
import uuid

# Import our modules
from config import settings
from database import get_db
from validation import ChatRequest, ChatResponse
from middleware import security_middleware
from groq import Groq  # Import Groq

from auth_middleware import auth_middleware, get_current_user, require_auth, require_verified_email, check_rate_limit
from mydoc import ask_mydoc
from medical_api import router as medical_router
from export_api import router as export_router
from conversation_api import router as conversation_router
from monitoring_api import router as monitoring_router
from sqlalchemy.orm import Session
from models import User

# Import monitoring system
from monitoring_middleware import (
    monitoring_middleware, 
    initialize_monitoring_system, 
    shutdown_monitoring_system
)
from logging_system import get_medical_logger


# Lifespan context manager for startup/shutdown events
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    print("🚀 MyDoc backend starting up...")
    
    # Initialize monitoring system FIRST
    try:
        print("📊 Initializing comprehensive monitoring system...")
        monitoring_success = await initialize_monitoring_system()
        if monitoring_success:
            print("✅ Monitoring system initialized!")
        else:
            print("⚠️  Monitoring system initialization had issues, continuing...")
    except Exception as e:
        print(f"⚠️  Monitoring system error: {e}, continuing...")
    
    # Initialize database
    try:
        from database import init_database
        from migrations import run_database_setup
        
        print("📊 Initializing database...")
        if not init_database():
            print("❌ Database initialization failed")
            raise RuntimeError("Database initialization failed")
        
        print("📊 Running database setup...")
        if not run_database_setup():
            print("❌ Database setup failed")
            raise RuntimeError("Database setup failed")
        
        print("✅ Database ready!")
        
    except Exception as e:
        print(f"❌ Database error: {e}")
        raise RuntimeError(f"Database startup failed: {e}")
    
    # Run startup validation
    try:
        from startup import startup_application
        if not startup_application():
            print("❌ Startup validation failed")
            raise RuntimeError("Application startup failed")
    except ImportError:
        print("⚠️  Startup validation not available, continuing...")
    except Exception as e:
        print(f"❌ Startup error: {e}")
        raise
    
    print(f"Environment: {settings.environment.value}")
    print(f"Debug mode: {settings.debug}")
    allowed_origins = [origin.strip() for origin in settings.allowed_origins.split(',') if origin.strip()]
    print(f"Allowed origins: {len(allowed_origins)} configured")
    print("✅ MyDoc AI Doctor Assistant ready to serve requests (Demo Mode)")
    
    yield
    
    # Shutdown
    print("👋 MyDoc backend shutting down...")
    
    # Shutdown monitoring system
    try:
        await shutdown_monitoring_system()
        print("✅ Monitoring system shutdown completed")
    except Exception as e:
        print(f"⚠️  Monitoring system shutdown error: {e}")


# Initialize FastAPI app
app = FastAPI(
    title=settings.app_name,
    description=settings.app_description + " (Demo Mode - No Authentication)",
    version=settings.app_version,
    lifespan=lifespan,
    debug=settings.debug
)

# Add trusted host middleware (security)
app.add_middleware(
    TrustedHostMiddleware, 
    allowed_hosts=["localhost", "127.0.0.1", "*.vercel.app", "*.railway.app", "*.render.com"]
)

# CORS middleware with restricted origins
allowed_origins = [origin.strip() for origin in settings.allowed_origins.split(',') if origin.strip()]
if "http://localhost:5173" not in allowed_origins:
    allowed_origins.append("http://localhost:5173")
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# Add comprehensive security middleware (temporarily disabled for debugging)
# app.middleware("http")(security_middleware)
app.middleware("http")(auth_middleware)

# Add monitoring middleware (temporarily disabled for debugging)
# app.middleware("http")(monitoring_middleware)

# Include API routers
app.include_router(medical_router)
app.include_router(export_router)
app.include_router(conversation_router)
app.include_router(monitoring_router)

# Include symptom checker API
from symptom_api import router as symptom_router
app.include_router(symptom_router)

# Include health monitoring API
from health_api import router as health_router
app.include_router(health_router)

# Include medical history API
from medical_history_api import router as medical_history_router
app.include_router(medical_history_router)

# Include medication management API
from medication_api import router as medication_router
app.include_router(medication_router)

# Include health analytics API
from health_analytics_api import router as health_analytics_router
app.include_router(health_analytics_router)

# Include user profile API
from user_api import router as user_router
app.include_router(user_router)

# Import drug interaction models to ensure they're registered with SQLAlchemy
import drug_interaction_models

# WebSocket manager will be imported when needed

# Background task for WebSocket cleanup
async def start_websocket_cleanup():
    """Start WebSocket cleanup background task"""
    try:
        from websocket_manager import cleanup_task
        asyncio.create_task(cleanup_task())
    except Exception as e:
        print(f"⚠️ Failed to start WebSocket cleanup task: {e}")

# Start background tasks
@app.on_event("startup")
async def startup_background_tasks():
    """Start background tasks on application startup"""
    await start_websocket_cleanup()

# Additional APIs can be added here in the future


# Health check endpoint
@app.get("/")
async def root():
    return {
        "message": f"{settings.app_name} is running in demo mode! 🩺",
        "version": settings.app_version,
        "environment": settings.environment.value,
        "timestamp": datetime.utcnow().isoformat(),
        "description": "AI-powered medical assistant for health consultations (Demo Mode)",
        "mode": "demo"
    }


# Health check endpoint
@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "environment": settings.environment.value,
        "version": settings.app_version,
        "mode": "demo"
    }

# Simple test chat endpoint
@app.post("/test-chat")
async def test_chat(chat_request: ChatRequest):
    """Simple test chat endpoint without complex middleware"""
    try:
        return ChatResponse(
            reply=f"Test response to: {chat_request.message}",
            timestamp=datetime.utcnow().isoformat(),
            mood_analysis={}
        )
    except Exception as e:
        print(f"Test chat error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Working chat endpoint with Groq API
@app.post("/simple-chat")
async def simple_chat(chat_request: ChatRequest):
    """Simple chat endpoint that works with Groq API"""
    try:
        # Build medical system prompt
        system_prompt = """You are MyDoc AI, a helpful medical assistant. You provide accurate, helpful medical information while being empathetic and professional. 

IMPORTANT GUIDELINES:
- Always remind users that you're an AI assistant and not a replacement for professional medical advice
- For serious symptoms or emergencies, advise users to seek immediate medical attention
- Be supportive and understanding while providing helpful information
- Keep responses concise but informative
- Use a caring, professional tone

Remember: Always recommend consulting healthcare professionals for proper diagnosis and treatment."""

        client = Groq(api_key=settings.groq_api_key)

        print(f"🤖 Calling Groq API with model {settings.groq_model}")
        
        completion = client.chat.completions.create(
            model=settings.groq_model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": chat_request.message}
            ],
            temperature=0.3,
            max_tokens=400,
            stream=False
        )
        
        reply = completion.choices[0].message.content.strip()
        print(f"✅ Groq response received: {len(reply)} characters")
        
        return ChatResponse(
            reply=reply,
            timestamp=datetime.utcnow().isoformat(),
            mood_analysis={}
        )
            
    except Exception as ai_error:
        print(f"⚠️ Simple chat AI service error: {ai_error}")
        return ChatResponse(
            reply=f"I understand you're asking about: '{chat_request.message}'. I'm currently experiencing some technical difficulties with my AI processing system. Please try again in a moment, or if this is urgent, please consult with a healthcare professional directly. 🩺",
            timestamp=datetime.utcnow().isoformat(),
            mood_analysis={}
        )


# Test Groq connectivity
@app.get("/test-groq")
async def test_groq():
    """Test Groq connectivity"""
    try:
        client = Groq(api_key=settings.groq_api_key)
        
        # Simple test call
        completion = client.chat.completions.create(
            model=settings.groq_model,
            messages=[{"role": "user", "content": "Hello"}],
            max_tokens=10
        )
        
        return {
            "status": "connected",
            "model": settings.groq_model,
            "response": completion.choices[0].message.content
        }
            
    except Exception as e:
        return {
            "status": "error",
            "error": str(e)
        }



# Chat endpoint - supports both authenticated and demo users
@app.post("/chat", response_model=ChatResponse)
async def chat(
    request: Request,
    chat_request: ChatRequest,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user),
    conversation_id: str = None  # Optional conversation ID for threading
):
    """Send a message to MyDoc AI medical assistant (supports auth and demo mode)"""
    print(f"🩺 Medical consultation request: {chat_request.message[:50]}...")
    
    try:
        # Get or create user (authenticated or demo)
        from models import User, Conversation, Message
        
        if current_user:
            # Use authenticated user
            user = current_user
            print(f"🔐 Authenticated user: {user.email}")
        else:
            # Use demo user
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
            print("🎭 Demo mode user")
        
        # Update user's last login and message count
        user.update_last_login()
        user.increment_message_count()
        
        # Get or create conversation
        conversation = None
        if conversation_id:
            # Try to find existing conversation
            conversation = db.query(Conversation).filter(
                Conversation.id == conversation_id,
                Conversation.user_id == user.id,
                Conversation.status == "active"
            ).first()
        
        if not conversation:
            # Create new conversation or get active one
            conversation = db.query(Conversation).filter(
                Conversation.user_id == user.id,
                Conversation.status == "active"
            ).first()
            
            if not conversation:
                conversation = Conversation(
                    user_id=user.id,
                    consultation_type="general",
                    status="active",
                    started_at=datetime.utcnow(),
                    last_message_at=datetime.utcnow()
                )
                db.add(conversation)
                db.commit()
                db.refresh(conversation)
        
        # Calculate sequence number for message ordering
        message_count = db.query(Message).filter(Message.conversation_id == conversation.id).count()
        sequence_number = message_count + 1
        
        # Save user message with enhanced metadata
        user_message = Message(
            conversation_id=conversation.id,
            content=chat_request.message,
            sender="user",
            timestamp=datetime.utcnow(),
            sequence_number=sequence_number,
            message_metadata={
                "client_info": {
                    "user_agent": request.headers.get("user-agent", ""),
                    "ip_address": request.client.host if request.client else "",
                    "timestamp": datetime.utcnow().isoformat()
                },
                "session_info": {
                    "conversation_id": conversation.id,
                    "message_sequence": sequence_number
                }
            }
        )
        db.add(user_message)
        db.flush()  # Get the message ID without committing
        
        # Get AI medical response using Groq API
        try:
            # Build medical system prompt
            system_prompt = """You are MyDoc AI, a helpful medical assistant. You provide accurate, helpful medical information while being empathetic and professional. 

IMPORTANT GUIDELINES:
- Always remind users that you're an AI assistant and not a replacement for professional medical advice
- For serious symptoms or emergencies, advise users to seek immediate medical attention
- Be supportive and understanding while providing helpful information
- Keep responses concise but informative
- Use a caring, professional tone

Remember: Always recommend consulting healthcare professionals for proper diagnosis and treatment."""

            client = Groq(api_key=settings.groq_api_key)
            
            print(f"🤖 Calling Groq API using model {settings.groq_model}")
            completion = client.chat.completions.create(
                model=settings.groq_model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": chat_request.message}
                ],
                temperature=0.3,
                max_tokens=400,
                stream=False
            )
            
            reply = completion.choices[0].message.content.strip()
            print(f"✅ Groq response received: {len(reply)} characters")
                
        except Exception as ai_error:
            print(f"⚠️ AI service error: {ai_error}")
            reply = f"I understand you're asking about: '{chat_request.message}'. I'm currently experiencing some technical difficulties with my AI processing system. Please try again in a moment, or if this is urgent, please consult with a healthcare professional directly. 🩺"
        
        # Save AI response with basic metadata
        ai_message = Message(
            conversation_id=conversation.id,
            content=reply,
            sender="ai",
            timestamp=datetime.utcnow(),
            sequence_number=sequence_number + 1,
            ai_model=settings.groq_model,
            ai_provider="groq",
            confidence_score=0.8,
            response_time_ms=0,
            emergency_flag=False,
            medical_analysis={
                "emergency_detected": False,
                "urgency_score": 1,
                "validation_result": "valid",
                "quality_score": 0.8,
                "ai_provider": "groq",
                "emergency_level": "none",
                "medical_disclaimers": ["This is an AI assistant. Always consult healthcare professionals for medical advice."]
            }
        )
        db.add(ai_message)
        
        # Update conversation metadata
        conversation.last_message_at = datetime.utcnow()
        conversation.total_messages = (conversation.total_messages or 0) + 2
        conversation.user_messages = (conversation.user_messages or 0) + 1
        conversation.ai_messages = (conversation.ai_messages or 0) + 1
        
        # Update conversation urgency (basic implementation)
        conversation.urgency_score = 1
        conversation.urgency_level = "normal"
        
        # Update user consultation count
        user.increment_consultation_count()
        
        db.commit()
        
        # Broadcast new messages via WebSocket
        try:
            from websocket_manager import connection_manager
            await connection_manager.broadcast_new_message(user_message, conversation.id)
            await connection_manager.broadcast_new_message(ai_message, conversation.id)
            await connection_manager.broadcast_conversation_update(conversation)
        except Exception as ws_error:
            print(f"⚠️ WebSocket broadcast failed: {ws_error}")
            # Don't fail the request if WebSocket fails
        
        print(f"🤖 Medical AI response generated and saved with metadata")
        
        return ChatResponse(
            reply=reply,
            timestamp=datetime.utcnow().isoformat(),
            mood_analysis={
                "conversation_id": conversation.id,
                "message_id": ai_message.id,
                "emergency_detected": False,
                "urgency_score": 1
            }
        )
    
    except Exception as e:
        print(f"❌ Medical consultation error: {e}")
        import traceback
        print(f"❌ Full traceback: {traceback.format_exc()}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Sorry, I'm having trouble with the medical consultation right now. Error: {str(e)}"
        )


# Conversation management endpoints
@app.post("/conversations/new")
async def create_new_conversation(
    request: Request,
    db: Session = Depends(get_db)
):
    """Create a new conversation session"""
    try:
        from models import User, Conversation
        
        # Get or create demo user
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
        
        # Create new conversation
        conversation = Conversation(
            user_id=user.id,
            consultation_type="general",
            status="active",
            started_at=datetime.utcnow(),
            last_message_at=datetime.utcnow()
        )
        db.add(conversation)
        db.commit()
        db.refresh(conversation)
        
        return {
            "conversation_id": conversation.id,
            "status": "created",
            "started_at": conversation.started_at.isoformat(),
            "consultation_type": conversation.consultation_type
        }
        
    except Exception as e:
        print(f"❌ Failed to create conversation: {e}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create new conversation"
        )


@app.get("/conversations")
async def get_conversations(
    db: Session = Depends(get_db),
    limit: int = 20,
    offset: int = 0,
    status_filter: str = None,
    consultation_type: str = None,
    date_from: str = None,
    date_to: str = None,
    search_query: str = None
):
    """Get user's conversation history with filtering and search"""
    try:
        from models import User, Conversation, Message
        from sqlalchemy import and_, or_, desc
        from datetime import datetime
        
        # Get or create demo user
        user = db.query(User).filter(User.firebase_uid == "demo-user").first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Build query with filters
        query = db.query(Conversation).filter(Conversation.user_id == user.id)
        
        # Status filter
        if status_filter:
            valid_statuses = ['active', 'completed', 'archived']
            if status_filter in valid_statuses:
                query = query.filter(Conversation.status == status_filter)
        
        # Consultation type filter
        if consultation_type:
            valid_types = ['general', 'symptom_check', 'follow_up', 'emergency', 'medication_inquiry']
            if consultation_type in valid_types:
                query = query.filter(Conversation.consultation_type == consultation_type)
        
        # Date range filter
        if date_from:
            try:
                from_date = datetime.fromisoformat(date_from.replace('Z', '+00:00'))
                query = query.filter(Conversation.started_at >= from_date)
            except ValueError:
                pass
        
        if date_to:
            try:
                to_date = datetime.fromisoformat(date_to.replace('Z', '+00:00'))
                query = query.filter(Conversation.started_at <= to_date)
            except ValueError:
                pass
        
        # Search query - search in conversation context and recent messages
        if search_query and len(search_query.strip()) > 0:
            search_term = f"%{search_query.strip()}%"
            # Search in conversation context summary and primary concern
            query = query.filter(
                or_(
                    Conversation.context_summary.ilike(search_term),
                    Conversation.primary_concern.ilike(search_term)
                )
            )
        
        # Get total count for pagination
        total_count = query.count()
        
        # Get conversations with pagination
        conversations = query.order_by(desc(Conversation.last_message_at)).offset(offset).limit(limit).all()
        
        # Format response
        result = []
        for conv in conversations:
            # Get last message preview
            last_message = db.query(Message).filter(
                Message.conversation_id == conv.id
            ).order_by(desc(Message.timestamp)).first()
            
            last_message_preview = ""
            if last_message:
                last_message_preview = last_message.content[:100] + "..." if len(last_message.content) > 100 else last_message.content
            
            result.append({
                "id": conv.id,
                "started_at": conv.started_at.isoformat(),
                "last_message_at": conv.last_message_at.isoformat(),
                "status": conv.status,
                "consultation_type": conv.consultation_type,
                "primary_concern": conv.primary_concern,
                "context_summary": conv.context_summary,
                "total_messages": conv.total_messages or 0,
                "urgency_level": conv.urgency_level,
                "emergency_detected": conv.emergency_detected or False,
                "crisis_level": conv.crisis_level,
                "last_message_preview": last_message_preview,
                "duration_minutes": conv.duration_minutes
            })
        
        return {
            "conversations": result,
            "total_count": total_count,
            "limit": limit,
            "offset": offset,
            "has_more": (offset + limit) < total_count
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Failed to get conversations: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve conversations"
        )


@app.get("/conversations/{conversation_id}")
async def get_conversation_detail(
    conversation_id: str,
    db: Session = Depends(get_db)
):
    """Get detailed conversation information"""
    try:
        from models import User, Conversation, Message
        
        # Get or create demo user
        user = db.query(User).filter(User.firebase_uid == "demo-user").first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Get conversation
        conversation = db.query(Conversation).filter(
            Conversation.id == conversation_id,
            Conversation.user_id == user.id
        ).first()
        
        if not conversation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Conversation not found"
            )
        
        # Update last accessed timestamp
        conversation.last_accessed_at = datetime.utcnow()
        db.commit()
        
        return {
            "id": conversation.id,
            "started_at": conversation.started_at.isoformat(),
            "last_message_at": conversation.last_message_at.isoformat(),
            "ended_at": conversation.ended_at.isoformat() if conversation.ended_at else None,
            "status": conversation.status,
            "consultation_type": conversation.consultation_type,
            "primary_concern": conversation.primary_concern,
            "context_summary": conversation.context_summary,
            "total_messages": conversation.total_messages or 0,
            "user_messages": conversation.user_messages or 0,
            "ai_messages": conversation.ai_messages or 0,
            "urgency_level": conversation.urgency_level,
            "urgency_score": conversation.urgency_score,
            "emergency_detected": conversation.emergency_detected or False,
            "crisis_level": conversation.crisis_level,
            "duration_minutes": conversation.duration_minutes,
            "medical_context": conversation.medical_context,
            "ai_models_used": conversation.ai_models_used,
            "service_quality_score": conversation.service_quality_score,
            "user_satisfaction_rating": conversation.user_satisfaction_rating,
            "tags": conversation.tags or [],
            "follow_up_needed": conversation.follow_up_needed or False,
            "follow_up_date": conversation.follow_up_date.isoformat() if conversation.follow_up_date else None
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Failed to get conversation detail: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve conversation details"
        )


@app.get("/conversations/{conversation_id}/messages")
async def get_conversation_messages(
    conversation_id: str,
    db: Session = Depends(get_db),
    limit: int = 50,
    offset: int = 0
):
    """Get messages from a specific conversation"""
    try:
        from models import User, Conversation, Message
        
        # Get or create demo user
        user = db.query(User).filter(User.firebase_uid == "demo-user").first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Verify conversation belongs to user
        conversation = db.query(Conversation).filter(
            Conversation.id == conversation_id,
            Conversation.user_id == user.id
        ).first()
        
        if not conversation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Conversation not found"
            )
        
        # Get messages with pagination
        messages = db.query(Message).filter(
            Message.conversation_id == conversation_id
        ).order_by(Message.sequence_number).offset(offset).limit(limit).all()
        
        return {
            "conversation_id": conversation_id,
            "messages": [
                {
                    "id": msg.id,
                    "content": msg.content,
                    "sender": msg.sender,
                    "timestamp": msg.timestamp.isoformat(),
                    "sequence_number": msg.sequence_number,
                    "medical_analysis": msg.medical_analysis,
                    "ai_model": msg.ai_model,
                    "confidence_score": msg.confidence_score,
                    "emergency_flag": msg.emergency_flag,
                    "urgency_score": msg.urgency_score,
                    "user_reaction": msg.user_reaction,
                    "user_rating": msg.user_rating
                }
                for msg in messages
            ],
            "total_messages": conversation.total_messages or 0,
            "conversation_status": conversation.status
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Failed to get conversation messages: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve conversation messages"
        )


@app.put("/conversations/{conversation_id}/archive")
async def archive_conversation(
    conversation_id: str,
    db: Session = Depends(get_db)
):
    """Archive a conversation"""
    try:
        from models import User, Conversation
        
        # Get or create demo user
        user = db.query(User).filter(User.firebase_uid == "demo-user").first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Get conversation
        conversation = db.query(Conversation).filter(
            Conversation.id == conversation_id,
            Conversation.user_id == user.id
        ).first()
        
        if not conversation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Conversation not found"
            )
        
        # Archive conversation
        conversation.archive_conversation()
        db.commit()
        
        return {
            "message": "Conversation archived successfully",
            "conversation_id": conversation_id,
            "status": conversation.status,
            "archived_at": conversation.archived_at.isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Failed to archive conversation: {e}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to archive conversation"
        )


@app.delete("/conversations/{conversation_id}")
async def delete_conversation(
    conversation_id: str,
    db: Session = Depends(get_db)
):
    """Delete a conversation and all its messages"""
    try:
        from models import User, Conversation
        
        # Get or create demo user
        user = db.query(User).filter(User.firebase_uid == "demo-user").first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Get conversation
        conversation = db.query(Conversation).filter(
            Conversation.id == conversation_id,
            Conversation.user_id == user.id
        ).first()
        
        if not conversation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Conversation not found"
            )
        
        # Delete conversation (messages will be deleted due to cascade)
        db.delete(conversation)
        db.commit()
        
        return {
            "message": "Conversation deleted successfully",
            "conversation_id": conversation_id
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Failed to delete conversation: {e}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete conversation"
        )


@app.get("/conversations/{conversation_id}/export")
async def export_conversation(
    conversation_id: str,
    format: str = "json",
    db: Session = Depends(get_db)
):
    """Export conversation data in specified format"""
    try:
        from models import User, Conversation, Message
        import json
        
        # Validate format
        valid_formats = ['json', 'txt', 'csv']
        if format not in valid_formats:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid format. Must be one of: {', '.join(valid_formats)}"
            )
        
        # Get or create demo user
        user = db.query(User).filter(User.firebase_uid == "demo-user").first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Get conversation
        conversation = db.query(Conversation).filter(
            Conversation.id == conversation_id,
            Conversation.user_id == user.id
        ).first()
        
        if not conversation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Conversation not found"
            )
        
        # Get all messages
        messages = db.query(Message).filter(
            Message.conversation_id == conversation_id
        ).order_by(Message.sequence_number).all()
        
        # Prepare export data
        export_data = {
            "conversation_id": conversation.id,
            "started_at": conversation.started_at.isoformat(),
            "last_message_at": conversation.last_message_at.isoformat(),
            "consultation_type": conversation.consultation_type,
            "status": conversation.status,
            "total_messages": len(messages),
            "messages": [
                {
                    "id": msg.id,
                    "content": msg.content,
                    "sender": msg.sender,
                    "timestamp": msg.timestamp.isoformat(),
                    "sequence_number": msg.sequence_number,
                    "ai_model": msg.ai_model,
                    "emergency_flag": msg.emergency_flag or False
                }
                for msg in messages
            ],
            "exported_at": datetime.utcnow().isoformat(),
            "export_format": format
        }
        
        if format == "json":
            return export_data
        elif format == "txt":
            # Create text format
            text_content = f"Medical Consultation Export\n"
            text_content += f"Conversation ID: {conversation.id}\n"
            text_content += f"Started: {conversation.started_at.isoformat()}\n"
            text_content += f"Type: {conversation.consultation_type}\n"
            text_content += f"Total Messages: {len(messages)}\n\n"
            
            for msg in messages:
                text_content += f"[{msg.timestamp.isoformat()}] {msg.sender.upper()}: {msg.content}\n"
                if msg.emergency_flag:
                    text_content += "  ⚠️ EMERGENCY FLAG DETECTED\n"
                text_content += "\n"
            
            return {"content": text_content, "format": "text"}
        elif format == "csv":
            # Create CSV format data
            csv_data = []
            for msg in messages:
                csv_data.append({
                    "timestamp": msg.timestamp.isoformat(),
                    "sender": msg.sender,
                    "content": msg.content.replace('\n', ' ').replace('\r', ' '),
                    "emergency_flag": msg.emergency_flag or False,
                    "ai_model": msg.ai_model or ""
                })
            
            return {"data": csv_data, "format": "csv"}
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Failed to export conversation: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to export conversation"
        )


@app.get("/conversations/search")
async def search_conversations_and_messages(
    query: str,
    db: Session = Depends(get_db),
    limit: int = 20,
    offset: int = 0,
    search_type: str = "all"  # "all", "conversations", "messages"
):
    """Search across conversations and messages"""
    try:
        from models import User, Conversation, Message
        from sqlalchemy import and_, or_, desc
        
        if not query or len(query.strip()) < 2:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Search query must be at least 2 characters long"
            )
        
        # Get or create demo user
        user = db.query(User).filter(User.firebase_uid == "demo-user").first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        search_term = f"%{query.strip()}%"
        results = {"conversations": [], "messages": [], "total_results": 0}
        
        # Search conversations
        if search_type in ["all", "conversations"]:
            conversation_query = db.query(Conversation).filter(
                and_(
                    Conversation.user_id == user.id,
                    or_(
                        Conversation.context_summary.ilike(search_term),
                        Conversation.primary_concern.ilike(search_term)
                    )
                )
            ).order_by(desc(Conversation.last_message_at))
            
            conversations = conversation_query.offset(offset).limit(limit).all()
            
            for conv in conversations:
                results["conversations"].append({
                    "id": conv.id,
                    "started_at": conv.started_at.isoformat(),
                    "consultation_type": conv.consultation_type,
                    "context_summary": conv.context_summary,
                    "primary_concern": conv.primary_concern,
                    "total_messages": conv.total_messages or 0,
                    "match_type": "conversation"
                })
        
        # Search messages
        if search_type in ["all", "messages"]:
            message_query = db.query(Message).join(Conversation).filter(
                and_(
                    Conversation.user_id == user.id,
                    Message.content.ilike(search_term)
                )
            ).order_by(desc(Message.timestamp))
            
            messages = message_query.offset(offset).limit(limit).all()
            
            for msg in messages:
                # Get conversation info
                conversation = db.query(Conversation).filter(Conversation.id == msg.conversation_id).first()
                
                # Highlight search term in content (simple highlighting)
                highlighted_content = msg.content
                if query.strip().lower() in msg.content.lower():
                    highlighted_content = msg.content.replace(
                        query.strip(), 
                        f"**{query.strip()}**"
                    )
                
                results["messages"].append({
                    "id": msg.id,
                    "content": highlighted_content,
                    "original_content": msg.content,
                    "sender": msg.sender,
                    "timestamp": msg.timestamp.isoformat(),
                    "conversation_id": msg.conversation_id,
                    "conversation_type": conversation.consultation_type if conversation else "unknown",
                    "emergency_flag": msg.emergency_flag or False,
                    "match_type": "message"
                })
        
        # Calculate total results
        results["total_results"] = len(results["conversations"]) + len(results["messages"])
        
        return {
            "query": query,
            "search_type": search_type,
            "results": results,
            "limit": limit,
            "offset": offset
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Failed to search conversations: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to search conversations and messages"
        )


@app.put("/conversations/{conversation_id}/tags")
async def update_conversation_tags(
    conversation_id: str,
    tags: List[str],
    db: Session = Depends(get_db)
):
    """Update conversation tags for organization"""
    try:
        from models import User, Conversation
        
        # Validate tags
        if len(tags) > 10:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Maximum 10 tags allowed"
            )
        
        # Sanitize tags
        sanitized_tags = []
        for tag in tags:
            if isinstance(tag, str) and len(tag.strip()) > 0:
                clean_tag = tag.strip()[:50]  # Limit tag length
                if clean_tag not in sanitized_tags:
                    sanitized_tags.append(clean_tag)
        
        # Get or create demo user
        user = db.query(User).filter(User.firebase_uid == "demo-user").first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Get conversation
        conversation = db.query(Conversation).filter(
            Conversation.id == conversation_id,
            Conversation.user_id == user.id
        ).first()
        
        if not conversation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Conversation not found"
            )
        
        # Update tags
        conversation.tags = sanitized_tags
        db.commit()
        
        return {
            "message": "Tags updated successfully",
            "conversation_id": conversation_id,
            "tags": sanitized_tags
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Failed to update conversation tags: {e}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update conversation tags"
        )


# WebSocket endpoint for real-time chat
@app.websocket("/ws/{user_id}")
async def websocket_endpoint(websocket: WebSocket, user_id: str):
    """WebSocket endpoint for real-time chat features"""
    from websocket_manager import connection_manager, handle_websocket_message
    
    connection_id = str(uuid.uuid4())
    
    try:
        await connection_manager.connect(websocket, user_id, connection_id)
        
        while True:
            try:
                # Receive message from client
                data = await websocket.receive_text()
                message_data = json.loads(data)
                
                # Handle the message
                await handle_websocket_message(websocket, user_id, connection_id, message_data)
                
            except WebSocketDisconnect:
                break
            except json.JSONDecodeError:
                await connection_manager.send_personal_message({
                    "type": "error",
                    "message": "Invalid JSON format"
                }, websocket)
            except Exception as e:
                print(f"WebSocket error: {e}")
                await connection_manager.send_personal_message({
                    "type": "error",
                    "message": "Internal server error"
                }, websocket)
    
    except Exception as e:
        print(f"WebSocket connection error: {e}")
    
    finally:
        connection_manager.disconnect(user_id, connection_id)


# Message reaction endpoints
@app.post("/messages/{message_id}/reaction")
async def add_message_reaction(
    message_id: str,
    reaction: str,
    db: Session = Depends(get_db)
):
    """Add reaction to a message"""
    try:
        from models import User, Message, Conversation
        
        # Validate reaction
        valid_reactions = ['helpful', 'not_helpful', 'accurate', 'inaccurate', 'like', 'dislike']
        if reaction not in valid_reactions:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid reaction. Must be one of: {', '.join(valid_reactions)}"
            )
        
        # Get or create demo user
        user = db.query(User).filter(User.firebase_uid == "demo-user").first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Get message
        message = db.query(Message).join(Conversation).filter(
            Message.id == message_id,
            Conversation.user_id == user.id
        ).first()
        
        if not message:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Message not found"
            )
        
        # Update message reaction
        message.user_reaction = reaction
        db.commit()
        
        # Broadcast reaction update via WebSocket
        try:
            from websocket_manager import connection_manager
            await connection_manager.broadcast_to_conversation({
                "type": "message_reaction",
                "message_id": message_id,
                "reaction": reaction,
                "user_id": user.firebase_uid,
                "timestamp": datetime.utcnow().isoformat()
            }, message.conversation_id)
        except Exception as ws_error:
            print(f"⚠️ WebSocket broadcast failed: {ws_error}")
        
        return {
            "message": "Reaction added successfully",
            "message_id": message_id,
            "reaction": reaction
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Failed to add message reaction: {e}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to add message reaction"
        )


@app.post("/messages/{message_id}/rating")
async def rate_message(
    message_id: str,
    rating: int,
    feedback: str = None,
    db: Session = Depends(get_db)
):
    """Rate an AI message (1-5 stars)"""
    try:
        from models import User, Message, Conversation
        
        # Validate rating
        if not 1 <= rating <= 5:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Rating must be between 1 and 5"
            )
        
        # Get or create demo user
        user = db.query(User).filter(User.firebase_uid == "demo-user").first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Get message
        message = db.query(Message).join(Conversation).filter(
            Message.id == message_id,
            Conversation.user_id == user.id,
            Message.sender == "ai"  # Only AI messages can be rated
        ).first()
        
        if not message:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="AI message not found"
            )
        
        # Update message rating
        message.user_rating = rating
        if feedback:
            message.feedback_text = feedback[:500]  # Limit feedback length
        
        db.commit()
        
        # Broadcast rating update via WebSocket
        try:
            from websocket_manager import connection_manager
            await connection_manager.broadcast_to_conversation({
                "type": "message_rating",
                "message_id": message_id,
                "rating": rating,
                "feedback": feedback,
                "user_id": user.firebase_uid,
                "timestamp": datetime.utcnow().isoformat()
            }, message.conversation_id)
        except Exception as ws_error:
            print(f"⚠️ WebSocket broadcast failed: {ws_error}")
        
        return {
            "message": "Rating added successfully",
            "message_id": message_id,
            "rating": rating,
            "feedback": feedback
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Failed to rate message: {e}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to rate message"
        )


# WebSocket status endpoints
@app.get("/ws/status")
async def get_websocket_status():
    """Get WebSocket connection status"""
    try:
        from websocket_manager import connection_manager
        return {
            "active_users": connection_manager.get_active_users(),
            "total_connections": sum(len(connections) for connections in connection_manager.active_connections.values()),
            "active_conversations": list(connection_manager.conversation_subscriptions.keys()),
            "typing_indicators": {
                conv_id: list(users.keys()) 
                for conv_id, users in connection_manager.typing_indicators.items()
            }
        }
    except Exception as e:
        return {
            "error": "WebSocket manager not available",
            "active_users": [],
            "total_connections": 0,
            "active_conversations": [],
            "typing_indicators": {}
        }


# User profile endpoint - demo mode
@app.get("/user/profile")
async def get_user_profile(request: Request):
    """Get demo user profile"""
    return {
        "uid": "demo-user",
        "email": "demo@example.com",
        "display_name": "Demo User",
        "email_verified": True,
        "created_at": datetime.utcnow().isoformat(),
        "last_login": datetime.utcnow().isoformat(),
        "mode": "demo"
    }


# Error handlers
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": True,
            "status_code": exc.status_code,
            "detail": exc.detail,
            "timestamp": datetime.utcnow().isoformat()
        }
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    print(f"❌ Unhandled error: {exc}")
    return JSONResponse(
        status_code=500,
        content={
            "error": True,
            "status_code": 500,
            "detail": "Internal server error" if not settings.debug else str(exc),
            "timestamp": datetime.utcnow().isoformat()
        }
    )