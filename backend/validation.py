import re
import bleach
import html
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, validator, Field
import logging

logger = logging.getLogger(__name__)

# Allowed HTML tags and attributes for sanitization
ALLOWED_TAGS = ['p', 'br', 'strong', 'em', 'u', 'ol', 'ul', 'li', 'blockquote']
ALLOWED_ATTRIBUTES = {
    'a': ['href', 'title'],
    'blockquote': ['cite']
}

# SQL injection patterns to detect
SQL_INJECTION_PATTERNS = [
    r'(\b(union|select|insert|update|delete|drop|create|alter|exec|execute)\b)',
    r'(\b(or|and)\s+\d+\s*=\s*\d+)',
    r'(\b(or|and)\s+[\'"]?\w+[\'"]?\s*=\s*[\'"]?\w+[\'"]?)',
    r'(--|#|/\*|\*/)',
    r'(\bxp_cmdshell\b)',
    r'(\bsp_executesql\b)',
    r'(\bsysobjects\b)',
    r'(\bsyscolumns\b)'
]

# XSS patterns to detect
XSS_PATTERNS = [
    r'<script[^>]*>.*?</script>',
    r'javascript:',
    r'on\w+\s*=',
    r'<iframe[^>]*>.*?</iframe>',
    r'<object[^>]*>.*?</object>',
    r'<embed[^>]*>.*?</embed>',
    r'<link[^>]*>',
    r'<meta[^>]*>',
    r'<style[^>]*>.*?</style>'
]


def sanitize_text(text: str) -> str:
    """Comprehensive text sanitization"""
    if not text:
        return ""
    
    # Remove null bytes and control characters
    text = re.sub(r'[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]', '', text)
    
    # Remove potential SQL injection patterns
    for pattern in SQL_INJECTION_PATTERNS:
        if re.search(pattern, text, re.IGNORECASE):
            logger.warning(f"Potential SQL injection attempt detected: {pattern}")
            # Replace with safe placeholder
            text = re.sub(pattern, '[FILTERED]', text, flags=re.IGNORECASE)
    
    # Remove potential XSS patterns
    for pattern in XSS_PATTERNS:
        if re.search(pattern, text, re.IGNORECASE):
            logger.warning(f"Potential XSS attempt detected: {pattern}")
            text = re.sub(pattern, '[FILTERED]', text, flags=re.IGNORECASE)
    
    # Strip whitespace and normalize
    text = text.strip()
    
    # Remove excessive whitespace
    text = re.sub(r'\s+', ' ', text)
    
    return text


def validate_no_sql_injection(text: str) -> bool:
    """Check for SQL injection patterns"""
    if not text:
        return True
    
    text_lower = text.lower()
    for pattern in SQL_INJECTION_PATTERNS:
        if re.search(pattern, text_lower, re.IGNORECASE):
            return False
    return True


def validate_no_xss(text: str) -> bool:
    """Check for XSS patterns"""
    if not text:
        return True
    
    for pattern in XSS_PATTERNS:
        if re.search(pattern, text, re.IGNORECASE):
            return False
    return True


# Request/Response Models for Medical Chat
class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=2000, description="Chat message content")
    context: Optional[Dict[str, Any]] = Field(None, description="Optional conversation context")
    
    @validator('message')
    def validate_message(cls, v):
        if not v or not v.strip():
            raise ValueError('Message cannot be empty')
        
        # Check for malicious patterns before sanitization
        if not validate_no_sql_injection(v):
            raise ValueError('Message contains potentially harmful content')
        
        if not validate_no_xss(v):
            raise ValueError('Message contains potentially harmful content')
        
        # Sanitize the message
        sanitized = sanitize_text(v)
        
        if len(sanitized) > 2000:
            raise ValueError('Message too long (max 2000 characters)')
        
        # Check for minimum meaningful content after sanitization
        if len(sanitized.strip()) < 1:
            raise ValueError('Message contains no valid content')
        
        return sanitized
    
    @validator('context')
    def validate_context(cls, v):
        if v is not None:
            # Limit context size
            if len(str(v)) > 5000:
                raise ValueError('Context too large (max 5000 characters)')
            
            # Sanitize context values if they're strings
            if isinstance(v, dict):
                sanitized_context = {}
                for key, value in v.items():
                    if isinstance(key, str):
                        key = sanitize_text(key)[:100]  # Limit key length
                    if isinstance(value, str):
                        value = sanitize_text(value)[:1000]  # Limit value length
                    sanitized_context[key] = value
                return sanitized_context
        
        return v


class ChatResponse(BaseModel):
    reply: str = Field(..., description="AI response message")
    mood_analysis: Optional[Dict[str, Any]] = Field(None, description="Mood analysis results")
    suggestions: Optional[List[str]] = Field(None, description="AI suggestions")
    timestamp: str = Field(..., description="Response timestamp")
    
    @validator('reply')
    def validate_reply(cls, v):
        return sanitize_text(v)
    
    @validator('suggestions')
    def validate_suggestions(cls, v):
        if v:
            sanitized_suggestions = []
            for suggestion in v[:5]:  # Limit suggestions
                if isinstance(suggestion, str):
                    sanitized = sanitize_text(suggestion)
                    if len(sanitized) <= 200:
                        sanitized_suggestions.append(sanitized)
            return sanitized_suggestions
        return v


class ConversationCreateRequest(BaseModel):
    """Request model for creating a new conversation"""
    consultation_type: Optional[str] = Field("general", description="Type of medical consultation")
    initial_message: Optional[str] = Field(None, max_length=2000, description="Optional initial message")
    
    @validator('consultation_type')
    def validate_consultation_type(cls, v):
        valid_types = ['general', 'symptom_check', 'follow_up', 'emergency', 'medication_inquiry']
        if v not in valid_types:
            raise ValueError(f'Invalid consultation type. Must be one of: {", ".join(valid_types)}')
        return v
    
    @validator('initial_message')
    def validate_initial_message(cls, v):
        if v:
            if not validate_no_sql_injection(v) or not validate_no_xss(v):
                raise ValueError('Initial message contains invalid characters')
            return sanitize_text(v)
        return v


class MessageSendRequest(BaseModel):
    """Request model for sending a message in a conversation"""
    content: str = Field(..., min_length=1, max_length=2000, description="Message content")
    conversation_id: str = Field(..., description="Conversation ID")
    message_type: Optional[str] = Field("text", description="Message type")
    
    @validator('content')
    def validate_content(cls, v):
        if not v or not v.strip():
            raise ValueError('Message content cannot be empty')
        
        if not validate_no_sql_injection(v) or not validate_no_xss(v):
            raise ValueError('Message contains invalid characters')
        
        sanitized = sanitize_text(v)
        if len(sanitized) > 2000:
            raise ValueError('Message too long (max 2000 characters)')
        
        return sanitized
    
    @validator('message_type')
    def validate_message_type(cls, v):
        valid_types = ['text', 'voice', 'image', 'file']
        if v not in valid_types:
            raise ValueError(f'Invalid message type. Must be one of: {", ".join(valid_types)}')
        return v
    
    @validator('conversation_id')
    def validate_conversation_id(cls, v):
        if not v or not v.strip():
            raise ValueError('Conversation ID cannot be empty')
        # Basic UUID format validation
        if not re.match(r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$', v, re.IGNORECASE):
            raise ValueError('Invalid conversation ID format')
        return v


class ConversationResponse(BaseModel):
    """Response model for conversation data"""
    id: str
    started_at: str
    last_message_at: str
    status: str
    consultation_type: str
    total_messages: int
    urgency_level: Optional[str] = None
    emergency_detected: bool = False


class MessageResponse(BaseModel):
    """Response model for message data"""
    id: str
    content: str
    sender: str
    timestamp: str
    sequence_number: Optional[int] = None
    ai_model: Optional[str] = None
    confidence_score: Optional[float] = None
    emergency_flag: bool = False
    medical_analysis: Optional[Dict[str, Any]] = None


class MedicalConsultationRequest(BaseModel):
    """Request model for medical consultations"""
    symptoms: List[str] = Field(..., min_items=1, max_items=10, description="List of symptoms")
    duration: Optional[str] = Field(None, max_length=100, description="Duration of symptoms")
    severity: Optional[int] = Field(None, ge=1, le=10, description="Severity scale 1-10")
    additional_info: Optional[str] = Field(None, max_length=1000, description="Additional information")
    
    @validator('symptoms')
    def validate_symptoms(cls, v):
        if v:
            sanitized_symptoms = []
            for symptom in v[:10]:
                if isinstance(symptom, str):
                    sanitized = sanitize_text(symptom)
                    if 1 <= len(sanitized) <= 100:
                        sanitized_symptoms.append(sanitized)
            return sanitized_symptoms
        return []
    
    @validator('additional_info')
    def validate_additional_info(cls, v):
        if v:
            if not validate_no_sql_injection(v) or not validate_no_xss(v):
                raise ValueError('Additional info contains invalid characters')
            
            sanitized = sanitize_text(v)
            if len(sanitized) > 1000:
                raise ValueError('Additional info too long (max 1000 characters)')
            return sanitized
        return v


class DataExportRequest(BaseModel):
    format: str = Field(..., pattern="^(json|csv|pdf)$", description="Export format")
    date_range: Optional[Dict[str, str]] = Field(None, description="Date range for export")
    include_conversations: bool = Field(default=True, description="Include conversation data")
    
    @validator('date_range')
    def validate_date_range(cls, v):
        if v:
            # Validate date format if provided
            for key, value in v.items():
                if key in ['start_date', 'end_date'] and isinstance(value, str):
                    # Basic date format validation
                    if not re.match(r'^\d{4}-\d{2}-\d{2}$', value):
                        raise ValueError(f'Invalid date format for {key}. Use YYYY-MM-DD')
        return v