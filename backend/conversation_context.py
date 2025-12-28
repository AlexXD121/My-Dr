"""
Conversation Context Management for MyDoc AI Medical Assistant
"""
from typing import Dict, List, Any, Optional
from datetime import datetime
from sqlalchemy.orm import Session
from models import User, Conversation, Message, MedicalRecord


class ContextManager:
    """Manages conversation context for medical consultations"""
    
    def __init__(self, user: User, conversation: Conversation, db: Session):
        self.user = user
        self.conversation = conversation
        self.db = db
        self.context = {}
    
    def get_medical_history_context(self) -> str:
        """Get relevant medical history for context"""
        recent_records = self.db.query(MedicalRecord)\
            .filter(MedicalRecord.user_id == self.user.id)\
            .order_by(MedicalRecord.created_at.desc())\
            .limit(5).all()
        
        if not recent_records:
            return "No previous medical records available."
        
        context_parts = ["Recent medical history:"]
        for record in recent_records:
            context_parts.append(f"- {record.created_at.strftime('%Y-%m-%d')}: {record.record_type}")
            if record.symptoms:
                context_parts.append(f"  Symptoms: {', '.join(record.symptoms)}")
            if record.diagnosis:
                context_parts.append(f"  Diagnosis: {record.diagnosis}")
        
        return "\n".join(context_parts)
    
    def get_conversation_history(self, limit: int = 10) -> str:
        """Get recent conversation history"""
        recent_messages = self.db.query(Message)\
            .filter(Message.conversation_id == self.conversation.id)\
            .order_by(Message.timestamp.desc())\
            .limit(limit).all()
        
        if not recent_messages:
            return ""
        
        history_parts = []
        for msg in reversed(recent_messages):
            history_parts.append(f"{msg.sender}: {msg.content}")
        
        return "\n".join(history_parts)
    
    def build_context(self) -> Dict[str, Any]:
        """Build comprehensive context for AI"""
        return {
            'user_id': self.user.id,
            'conversation_id': self.conversation.id,
            'medical_history': self.get_medical_history_context(),
            'conversation_history': self.get_conversation_history(),
            'timestamp': datetime.now().isoformat()
        }


def create_context_manager(user: User, conversation: Conversation, db: Session) -> ContextManager:
    """Create a context manager instance"""
    return ContextManager(user, conversation, db)


def get_enhanced_ai_prompt(context: Dict[str, Any], user_message: str) -> str:
    """Generate enhanced AI prompt with context"""
    base_prompt = """You are MyDoc AI, a professional medical assistant. You provide helpful medical information and guidance while emphasizing that you are not a replacement for professional medical care.

IMPORTANT DISCLAIMERS:
- Always remind users to consult healthcare professionals for serious concerns
- If symptoms suggest emergency conditions, advise immediate medical attention
- Provide general medical information, not specific diagnoses
- Be empathetic and professional

"""
    
    if context.get('medical_history'):
        base_prompt += f"\nMEDICAL HISTORY CONTEXT:\n{context['medical_history']}\n"
    
    if context.get('conversation_history'):
        base_prompt += f"\nCONVERSATION HISTORY:\n{context['conversation_history']}\n"
    
    base_prompt += f"\nUSER MESSAGE: {user_message}\n\nPlease provide a helpful, professional medical response:"
    
    return base_prompt