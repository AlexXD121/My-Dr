"""
Database models for MyDoc AI Medical Assistant
"""
from datetime import datetime, timezone
from typing import List, Optional, Dict, Any
from sqlalchemy import (
    Column, Integer, String, Float, DateTime, Text, JSON, 
    ForeignKey, Boolean, Index, UniqueConstraint
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, Session
from sqlalchemy.dialects.postgresql import UUID
import uuid

Base = declarative_base()


class User(Base):
    """User model for storing user information"""
    __tablename__ = "users"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    firebase_uid = Column(String, unique=True, nullable=False, index=True)
    email = Column(String, unique=True, nullable=False, index=True)
    display_name = Column(String, nullable=True)
    
    # Personal information (some fields may be encrypted)
    first_name = Column(String, nullable=True)
    last_name = Column(String, nullable=True)
    date_of_birth = Column(String, nullable=True)  # Encrypted sensitive data
    gender = Column(String, nullable=True)  # male, female, other, prefer_not_to_say
    phone_number = Column(String, nullable=True)  # Encrypted sensitive data
    phone_encrypted = Column(Boolean, default=False)
    date_of_birth_encrypted = Column(Boolean, default=False)
    
    # Address information
    address_line1 = Column(String, nullable=True)
    address_line2 = Column(String, nullable=True)
    city = Column(String, nullable=True)
    state = Column(String, nullable=True)
    postal_code = Column(String, nullable=True)
    country = Column(String, nullable=True)
    
    # Emergency contact (encrypted sensitive data)
    emergency_contact = Column(JSON, nullable=True)  # Encrypted emergency contact info
    emergency_contact_encrypted = Column(Boolean, default=False)
    
    # Account status and metadata
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    last_login = Column(DateTime, nullable=True)
    is_active = Column(Boolean, default=True)
    email_verified = Column(Boolean, default=False)
    photo_url = Column(String, nullable=True)
    account_type = Column(String, default="standard")  # standard, premium, healthcare_provider
    
    # Data retention and privacy
    data_retention_policy = Column(String, default="2years")  # 1year, 2years, 5years, indefinite
    consent_given_at = Column(DateTime, nullable=True)
    consent_version = Column(String, nullable=True)
    deactivated_at = Column(DateTime, nullable=True)
    
    # User preferences and settings
    preferences = Column(JSON, default=lambda: {
        'language': 'en',
        'timezone': 'UTC',
        'notification_preferences': {
            'email_notifications': True,
            'sms_notifications': False,
            'push_notifications': True,
            'medication_reminders': True,
            'appointment_reminders': True
        },
        'ui_preferences': {
            'theme': 'light',
            'font_size': 'medium',
            'high_contrast': False
        },
        'medical_preferences': {
            'units': 'metric',  # metric or imperial
            'default_consultation_type': 'general',
            'voice_enabled': True,
            'auto_save_conversations': True
        }
    })
    
    # Privacy and security settings
    privacy_settings = Column(JSON, default=lambda: {
        'share_data_for_research': False,
        'allow_analytics': True,
        'data_retention_period': '2years',
        'allow_third_party_integrations': False,
        'marketing_communications': False,
        'data_sharing': {
            'share_anonymized_data': False,
            'share_with_researchers': False,
            'share_with_healthcare_providers': False
        },
        'visibility': {
            'profile_visibility': 'private',
            'medical_history_visibility': 'private'
        },
        'security': {
            'two_factor_enabled': False,
            'session_timeout': 3600,  # seconds
            'require_password_change': False,
            'encryption_enabled': True
        },
        'data_retention': {
            'auto_delete_conversations': False,
            'conversation_retention_days': 365,
            'medical_record_retention_years': 7
        }
    })
    
    # Medical profile information (encrypted sensitive data)
    medical_info = Column(JSON, nullable=True)  # Encrypted medical information
    medical_info_encrypted = Column(Boolean, default=False)
    
    # Subscription and billing
    subscription_status = Column(String, default="free")  # free, trial, active, expired, cancelled
    subscription_start_date = Column(DateTime, nullable=True)
    subscription_end_date = Column(DateTime, nullable=True)
    billing_info = Column(JSON, default=dict)
    
    # Usage statistics
    total_consultations = Column(Integer, default=0)
    total_messages = Column(Integer, default=0)
    last_consultation_date = Column(DateTime, nullable=True)
    
    # Relationships
    medical_records = relationship("MedicalRecord", back_populates="user", cascade="all, delete-orphan")
    conversations = relationship("Conversation", back_populates="user", cascade="all, delete-orphan")
    consultations = relationship("Consultation", back_populates="user", cascade="all, delete-orphan")
    health_analytics = relationship("HealthAnalytics", back_populates="user", cascade="all, delete-orphan")
    symptom_records = relationship("SymptomRecord", back_populates="user", cascade="all, delete-orphan")
    user_medications = relationship("UserMedication", cascade="all, delete-orphan")
    drug_interaction_reports = relationship("DrugInteractionReport", cascade="all, delete-orphan")
    
    # Indexes for performance
    __table_args__ = (
        Index('idx_user_email', 'email'),
        Index('idx_user_firebase_uid', 'firebase_uid'),
        Index('idx_user_active', 'is_active'),
        Index('idx_user_subscription', 'subscription_status'),
        Index('idx_user_last_login', 'last_login'),
    )
    
    def validate_email(self) -> bool:
        """Validate email format"""
        import re
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(email_pattern, self.email) is not None
    
    def validate_gender(self) -> bool:
        """Validate gender value"""
        if self.gender is None:
            return True
        valid_genders = ['male', 'female', 'other', 'prefer_not_to_say']
        return self.gender in valid_genders
    
    def validate_account_type(self) -> bool:
        """Validate account type"""
        valid_types = ['standard', 'premium', 'healthcare_provider', 'admin']
        account_type = self.account_type or 'standard'  # Use default if None
        return account_type in valid_types
    
    def validate_subscription_status(self) -> bool:
        """Validate subscription status"""
        valid_statuses = ['free', 'trial', 'active', 'expired', 'cancelled', 'suspended']
        return self.subscription_status in valid_statuses
    
    def get_full_name(self) -> str:
        """Get user's full name"""
        if self.first_name and self.last_name:
            return f"{self.first_name} {self.last_name}"
        elif self.display_name:
            return self.display_name
        else:
            return self.email.split('@')[0]
    
    def get_age(self) -> Optional[int]:
        """Calculate user's age from date of birth"""
        if not self.date_of_birth:
            return None
        
        today = datetime.now(timezone.utc).date()
        birth_date = self.date_of_birth.date() if isinstance(self.date_of_birth, datetime) else self.date_of_birth
        
        age = today.year - birth_date.year
        if today.month < birth_date.month or (today.month == birth_date.month and today.day < birth_date.day):
            age -= 1
        
        return age
    
    def is_subscription_active(self) -> bool:
        """Check if user has active subscription"""
        if self.subscription_status not in ['active', 'trial']:
            return False
        
        if self.subscription_end_date:
            return datetime.now(timezone.utc) <= self.subscription_end_date
        
        return True
    
    def update_last_login(self):
        """Update last login timestamp"""
        self.last_login = datetime.now(timezone.utc)
    
    def increment_consultation_count(self):
        """Increment total consultation count"""
        self.total_consultations += 1
        self.last_consultation_date = datetime.now(timezone.utc)
    
    def increment_message_count(self):
        """Increment total message count"""
        self.total_messages += 1
    
    def get_preference(self, key: str, default=None):
        """Get user preference by key"""
        if not self.preferences:
            return default
        
        keys = key.split('.')
        value = self.preferences
        
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        
        return value
    
    def set_preference(self, key: str, value):
        """Set user preference by key"""
        if not self.preferences:
            self.preferences = {}
        
        keys = key.split('.')
        current = self.preferences
        
        for k in keys[:-1]:
            if k not in current:
                current[k] = {}
            current = current[k]
        
        current[keys[-1]] = value
    
    def get_privacy_setting(self, key: str, default=None):
        """Get privacy setting by key"""
        if not self.privacy_settings:
            return default
        
        keys = key.split('.')
        value = self.privacy_settings
        
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        
        return value
    
    def encrypt_sensitive_data(self):
        """Encrypt sensitive user data"""
        from encryption_service import encryption_service
        
        # Encrypt phone number if not already encrypted
        if self.phone_number and not self.phone_encrypted:
            self.phone_number = encryption_service.encrypt_data(self.phone_number)
            self.phone_encrypted = True
        
        # Encrypt date of birth if not already encrypted
        if self.date_of_birth and not self.date_of_birth_encrypted:
            if isinstance(self.date_of_birth, datetime):
                date_str = self.date_of_birth.isoformat()
            else:
                date_str = str(self.date_of_birth)
            self.date_of_birth = encryption_service.encrypt_data(date_str)
            self.date_of_birth_encrypted = True
        
        # Encrypt emergency contact if not already encrypted
        if self.emergency_contact and not self.emergency_contact_encrypted:
            self.emergency_contact = encryption_service.encrypt_data(self.emergency_contact)
            self.emergency_contact_encrypted = True
        
        # Encrypt medical info if not already encrypted
        if self.medical_info and not self.medical_info_encrypted:
            self.medical_info = encryption_service.encrypt_data(self.medical_info)
            self.medical_info_encrypted = True
    
    def decrypt_sensitive_data(self):
        """Decrypt sensitive user data for display"""
        from encryption_service import encryption_service
        
        decrypted_data = {}
        
        # Decrypt phone number
        if self.phone_number and self.phone_encrypted:
            try:
                decrypted_data['phone'] = encryption_service.decrypt_data(self.phone_number)
            except Exception:
                decrypted_data['phone'] = None
        else:
            decrypted_data['phone'] = self.phone_number
        
        # Decrypt date of birth
        if self.date_of_birth and self.date_of_birth_encrypted:
            try:
                date_str = encryption_service.decrypt_data(self.date_of_birth)
                decrypted_data['date_of_birth'] = date_str
            except Exception:
                decrypted_data['date_of_birth'] = None
        else:
            decrypted_data['date_of_birth'] = self.date_of_birth
        
        # Decrypt emergency contact
        if self.emergency_contact and self.emergency_contact_encrypted:
            try:
                decrypted_data['emergency_contact'] = encryption_service.decrypt_data(self.emergency_contact)
            except Exception:
                decrypted_data['emergency_contact'] = None
        else:
            decrypted_data['emergency_contact'] = self.emergency_contact
        
        # Decrypt medical info
        if self.medical_info and self.medical_info_encrypted:
            try:
                decrypted_data['medical_info'] = encryption_service.decrypt_data(self.medical_info)
            except Exception:
                decrypted_data['medical_info'] = None
        else:
            decrypted_data['medical_info'] = self.medical_info
        
        return decrypted_data
    
    def should_encrypt_data(self) -> bool:
        """Check if user has enabled data encryption"""
        return self.get_privacy_setting('security.encryption_enabled', True)
    
    def can_share_for_research(self) -> bool:
        """Check if user allows data sharing for research"""
        return self.get_privacy_setting('share_data_for_research', False)
    
    def can_use_for_analytics(self) -> bool:
        """Check if user allows data for analytics"""
        return self.get_privacy_setting('allow_analytics', True)
    
    def get_data_retention_period(self) -> str:
        """Get user's data retention preference"""
        return self.get_privacy_setting('data_retention_period', '2years')
    
    def anonymize_for_research(self) -> Dict[str, Any]:
        """Return anonymized user data for research purposes"""
        from encryption_service import privacy_control_service
        
        if not self.can_share_for_research():
            return None
        
        user_data = {
            'user_id_hash': hash(self.firebase_uid) % 100000,
            'age': self.get_age(),
            'gender': self.gender,
            'account_type': self.account_type,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'total_consultations': self.total_consultations,
            'total_messages': self.total_messages,
            'subscription_status': self.subscription_status
        }
        
        return privacy_control_service.anonymize_user_data(user_data)
    
    def __repr__(self):
        return f"<User(id={self.id}, email={self.email}, name={self.get_full_name()})>"


class MedicalRecord(Base):
    """Medical record model for storing user's medical information"""
    __tablename__ = "medical_records"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id"), nullable=False, index=True)
    
    # Record type and basic information
    record_type = Column(String, nullable=False)  # 'visit', 'diagnosis', 'medication', 'test', 'procedure'
    title = Column(String, nullable=False)  # Title/summary of the record
    description = Column(Text, nullable=True)  # Detailed description
    date_recorded = Column(DateTime, nullable=False)  # Date of the medical event
    
    # Healthcare provider information
    healthcare_provider = Column(String, nullable=True)  # Doctor/clinic name
    provider_specialty = Column(String, nullable=True)  # Medical specialty
    facility_name = Column(String, nullable=True)  # Hospital/clinic name
    facility_address = Column(String, nullable=True)  # Facility address
    
    # Medical details
    condition = Column(String, nullable=True)  # Primary condition/diagnosis
    icd_code = Column(String, nullable=True)  # ICD-10 diagnosis code
    severity = Column(String, nullable=True)  # mild, moderate, severe, critical
    status = Column(String, default="active")  # active, resolved, chronic, monitoring
    
    # Treatment and medication information
    medications = Column(JSON, default=list)  # List of prescribed medications
    dosages = Column(JSON, default=dict)  # Medication dosages and instructions
    treatments = Column(JSON, default=list)  # List of treatments/procedures
    test_results = Column(JSON, default=dict)  # Lab results and test outcomes
    
    # Additional medical data
    allergies = Column(JSON, default=list)  # Known allergies related to this record
    symptoms = Column(JSON, default=list)  # Associated symptoms
    vital_signs = Column(JSON, default=dict)  # Recorded vital signs
    
    # File attachments and references
    attachments = Column(JSON, default=list)  # File attachments (images, PDFs, etc.)
    external_references = Column(JSON, default=list)  # External system references
    
    # Follow-up and care coordination
    follow_up_date = Column(DateTime, nullable=True)  # Next appointment/follow-up
    follow_up_instructions = Column(Text, nullable=True)  # Care instructions
    referrals = Column(JSON, default=list)  # Specialist referrals
    
    # Privacy and sharing
    is_private = Column(Boolean, default=True)  # Privacy flag
    shared_with = Column(JSON, default=list)  # List of authorized viewers
    
    # Additional notes and metadata
    notes = Column(Text, nullable=True)  # Additional notes
    tags = Column(JSON, default=list)  # User-defined tags for organization
    priority = Column(String, default="normal")  # low, normal, high, urgent
    
    # Audit trail
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    created_by = Column(String, nullable=True)  # Who created the record
    last_modified_by = Column(String, nullable=True)  # Who last modified
    
    # Relationships
    user = relationship("User", back_populates="medical_records")
    
    # Indexes for performance and data integrity
    __table_args__ = (
        Index('idx_medical_user_date', 'user_id', 'date_recorded'),
        Index('idx_medical_type_date', 'record_type', 'date_recorded'),
        Index('idx_medical_condition', 'condition'),
        Index('idx_medical_provider', 'healthcare_provider'),
        Index('idx_medical_status', 'status'),
        Index('idx_medical_priority', 'priority'),
    )
    
    def validate_record_type(self):
        """Validate record type"""
        valid_types = ['visit', 'diagnosis', 'medication', 'test', 'procedure', 'vaccination', 'allergy']
        return self.record_type in valid_types
    
    def validate_severity(self):
        """Validate severity level"""
        if self.severity is None:
            return True
        valid_severities = ['mild', 'moderate', 'severe', 'critical']
        return self.severity in valid_severities
    
    def validate_status(self):
        """Validate record status"""
        valid_statuses = ['active', 'resolved', 'chronic', 'monitoring', 'inactive']
        status = self.status or 'active'  # Use default if None
        return status in valid_statuses
    
    def validate_priority(self):
        """Validate priority level"""
        valid_priorities = ['low', 'normal', 'high', 'urgent']
        priority = self.priority or 'normal'  # Use default if None
        return priority in valid_priorities
    
    def is_recent(self, days: int = 30) -> bool:
        """Check if record is recent (within specified days)"""
        if not self.date_recorded:
            return False
        delta = datetime.now(timezone.utc) - self.date_recorded
        return delta.days <= days
    
    def has_follow_up_due(self) -> bool:
        """Check if follow-up is due"""
        if not self.follow_up_date:
            return False
        return datetime.now(timezone.utc) >= self.follow_up_date
    
    def get_medications_list(self) -> List[str]:
        """Get list of medication names"""
        if not self.medications:
            return []
        return [med.get('name', '') for med in self.medications if isinstance(med, dict)]
    
    def add_attachment(self, file_path: str, file_type: str, description: str = None):
        """Add file attachment to record"""
        if not self.attachments:
            self.attachments = []
        
        attachment = {
            'file_path': file_path,
            'file_type': file_type,
            'description': description,
            'uploaded_at': datetime.now(timezone.utc).isoformat()
        }
        self.attachments.append(attachment)
    
    def __repr__(self):
        return f"<MedicalRecord(id={self.id}, type={self.record_type}, title={self.title})>"


class Conversation(Base):
    """Conversation model for storing medical consultation sessions"""
    __tablename__ = "conversations"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id"), nullable=False, index=True)
    
    # Basic conversation information
    title = Column(String, nullable=True)  # User-defined or AI-generated title
    description = Column(Text, nullable=True)  # Brief description of the conversation
    
    # Conversation metadata and timing
    started_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    last_message_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    ended_at = Column(DateTime, nullable=True)  # When conversation was closed
    duration_minutes = Column(Integer, nullable=True)  # Total conversation duration
    
    # Status and lifecycle management
    status = Column(String, default="active")  # active, paused, completed, archived, deleted
    is_archived = Column(Boolean, default=False)  # Soft delete flag
    archived_at = Column(DateTime, nullable=True)  # When conversation was archived
    
    # Medical consultation context
    consultation_type = Column(String, default="general")  # general, symptom_check, follow_up, emergency, medication_inquiry
    primary_concern = Column(Text, nullable=True)  # Main health concern discussed
    context_summary = Column(Text, nullable=True)  # AI-generated conversation summary
    medical_context = Column(JSON, default=lambda: {
        'symptoms_discussed': [],
        'conditions_mentioned': [],
        'medications_discussed': [],
        'recommendations_given': [],
        'follow_up_needed': False,
        'referrals_suggested': []
    })
    
    # Urgency and priority assessment
    urgency_level = Column(String, default="routine")  # routine, urgent, emergency, critical
    urgency_score = Column(Float, nullable=True)  # Numerical urgency score (0-10)
    priority_flags = Column(JSON, default=list)  # List of priority indicators
    emergency_detected = Column(Boolean, default=False)  # Emergency situation flag
    
    # Crisis and safety assessment
    crisis_level = Column(String, default="low")  # low, medium, high, critical
    crisis_flags = Column(JSON, default=list)  # Crisis detection flags
    safety_assessment = Column(JSON, default=lambda: {
        'risk_level': 'low',
        'risk_factors': [],
        'protective_factors': [],
        'intervention_needed': False
    })
    
    # AI and service metadata
    ai_models_used = Column(JSON, default=list)  # List of AI models used in conversation
    service_quality_score = Column(Float, nullable=True)  # Quality assessment score
    user_satisfaction_rating = Column(Integer, nullable=True)  # User rating (1-5)
    
    # Message statistics
    total_messages = Column(Integer, default=0)  # Total number of messages
    user_messages = Column(Integer, default=0)  # Number of user messages
    ai_messages = Column(Integer, default=0)  # Number of AI messages
    
    # Follow-up and care coordination
    follow_up_needed = Column(Boolean, default=False)  # Whether follow-up is needed
    follow_up_date = Column(DateTime, nullable=True)  # Scheduled follow-up date
    follow_up_type = Column(String, nullable=True)  # Type of follow-up needed
    care_plan_created = Column(Boolean, default=False)  # Whether care plan was created
    
    # Privacy and sharing
    is_private = Column(Boolean, default=True)  # Privacy flag
    shared_with_providers = Column(JSON, default=list)  # Healthcare providers with access
    consent_for_research = Column(Boolean, default=False)  # Research consent
    
    # Tags and categorization
    tags = Column(JSON, default=list)  # User-defined tags
    categories = Column(JSON, default=list)  # System-generated categories
    
    # Audit and compliance
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    last_accessed_at = Column(DateTime, nullable=True)  # Last time conversation was viewed
    
    # Relationships
    user = relationship("User", back_populates="conversations")
    messages = relationship("Message", back_populates="conversation", cascade="all, delete-orphan", order_by="Message.timestamp")
    
    # Indexes for performance
    __table_args__ = (
        Index('idx_conversation_user_status', 'user_id', 'status'),
        Index('idx_conversation_type_urgency', 'consultation_type', 'urgency_level'),
        Index('idx_conversation_started_at', 'started_at'),
        Index('idx_conversation_last_message', 'last_message_at'),
        Index('idx_conversation_archived', 'is_archived'),
        Index('idx_conversation_emergency', 'emergency_detected'),
    )
    
    def validate_status(self) -> bool:
        """Validate conversation status"""
        valid_statuses = ['active', 'paused', 'completed', 'archived', 'deleted']
        status = self.status or 'active'  # Use default if None
        return status in valid_statuses
    
    def validate_consultation_type(self) -> bool:
        """Validate consultation type"""
        valid_types = ['general', 'symptom_check', 'follow_up', 'emergency', 'medication_inquiry', 'mental_health', 'chronic_care']
        return self.consultation_type in valid_types
    
    def validate_urgency_level(self) -> bool:
        """Validate urgency level"""
        valid_levels = ['routine', 'urgent', 'emergency', 'critical']
        urgency_level = self.urgency_level or 'routine'  # Use default if None
        return urgency_level in valid_levels
    
    def validate_crisis_level(self) -> bool:
        """Validate crisis level"""
        valid_levels = ['low', 'medium', 'high', 'critical']
        return self.crisis_level in valid_levels
    
    def is_active(self) -> bool:
        """Check if conversation is currently active"""
        status = self.status or 'active'  # Use default if None
        is_archived = self.is_archived or False  # Use default if None
        return status == 'active' and not is_archived
    
    def is_emergency(self) -> bool:
        """Check if conversation involves emergency situation"""
        return self.emergency_detected or self.urgency_level in ['emergency', 'critical']
    
    def needs_follow_up(self) -> bool:
        """Check if conversation needs follow-up"""
        return self.follow_up_needed and self.follow_up_date and datetime.now(timezone.utc) >= self.follow_up_date
    
    def calculate_duration(self):
        """Calculate and update conversation duration"""
        if self.started_at and self.ended_at:
            delta = self.ended_at - self.started_at
            self.duration_minutes = int(delta.total_seconds() / 60)
        elif self.started_at:
            delta = datetime.now(timezone.utc) - self.started_at
            self.duration_minutes = int(delta.total_seconds() / 60)
    
    def update_message_counts(self):
        """Update message count statistics"""
        if self.messages:
            self.total_messages = len(self.messages)
            self.user_messages = len([m for m in self.messages if m.sender == 'user'])
            self.ai_messages = len([m for m in self.messages if m.sender == 'ai'])
    
    def archive_conversation(self):
        """Archive the conversation (soft delete)"""
        self.is_archived = True
        self.archived_at = datetime.now(timezone.utc)
        self.status = 'archived'
    
    def close_conversation(self):
        """Close the conversation"""
        self.status = 'completed'
        self.ended_at = datetime.now(timezone.utc)
        self.calculate_duration()
    
    def add_tag(self, tag: str):
        """Add a tag to the conversation"""
        if not self.tags:
            self.tags = []
        if tag not in self.tags:
            self.tags.append(tag)
    
    def remove_tag(self, tag: str):
        """Remove a tag from the conversation"""
        if self.tags and tag in self.tags:
            self.tags.remove(tag)
    
    def update_urgency(self, urgency_level: str, urgency_score: float = None):
        """Update urgency level and score"""
        if self.validate_urgency_level():
            self.urgency_level = urgency_level
            if urgency_score is not None:
                self.urgency_score = urgency_score
            
            # Set emergency flag for high urgency
            if urgency_level in ['emergency', 'critical']:
                self.emergency_detected = True
    
    def get_last_message(self):
        """Get the last message in the conversation"""
        if self.messages:
            return max(self.messages, key=lambda m: m.timestamp)
        return None
    
    def get_message_count(self) -> int:
        """Get total message count"""
        return len(self.messages) if self.messages else 0
    
    def __repr__(self):
        return f"<Conversation(id={self.id}, type={self.consultation_type}, status={self.status})>"


class Message(Base):
    """Message model for individual consultation messages"""
    __tablename__ = "messages"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    conversation_id = Column(String, ForeignKey("conversations.id"), nullable=False, index=True)
    
    # Message content and type
    content = Column(Text, nullable=False)  # Message text content
    original_content = Column(Text, nullable=True)  # Original content before processing
    sender = Column(String, nullable=False)  # 'user' or 'ai'
    message_type = Column(String, default="text")  # text, voice, image, file, system
    
    # Timing and ordering
    timestamp = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    sequence_number = Column(Integer, nullable=True)  # Message order in conversation
    
    # AI-specific metadata (for AI messages)
    ai_model = Column(String, nullable=True)  # AI model used to generate response
    ai_provider = Column(String, nullable=True)  # AI service provider (Jan, Perplexity, etc.)
    confidence_score = Column(Float, nullable=True)  # AI confidence in response (0-1)
    response_time_ms = Column(Integer, nullable=True)  # Time taken to generate response
    token_count = Column(Integer, nullable=True)  # Number of tokens in response
    
    # Medical analysis and assessment
    medical_analysis = Column(JSON, default=lambda: {
        'symptoms_detected': [],
        'conditions_mentioned': [],
        'medications_mentioned': [],
        'medical_terms': [],
        'urgency_indicators': [],
        'red_flags': []
    })
    
    # Symptom and keyword detection
    symptom_keywords = Column(JSON, default=list)  # Detected medical keywords
    medical_entities = Column(JSON, default=list)  # Named medical entities
    urgency_score = Column(Float, nullable=True)  # Urgency assessment score (0-10)
    
    # Emergency and crisis detection
    emergency_flag = Column(Boolean, default=False)  # Emergency situation detected
    crisis_indicators = Column(JSON, default=list)  # Crisis-related indicators
    safety_concerns = Column(JSON, default=list)  # Safety-related concerns
    
    # Content analysis and quality
    sentiment_score = Column(Float, nullable=True)  # Sentiment analysis score (-1 to 1)
    readability_score = Column(Float, nullable=True)  # Content readability score
    medical_accuracy_score = Column(Float, nullable=True)  # Medical accuracy assessment
    
    # User interaction and feedback
    user_reaction = Column(String, nullable=True)  # User reaction (helpful, not_helpful, etc.)
    user_rating = Column(Integer, nullable=True)  # User rating for AI response (1-5)
    feedback_text = Column(Text, nullable=True)  # User feedback text
    
    # Message status and processing
    is_processed = Column(Boolean, default=False)  # Whether message has been processed
    processing_status = Column(String, default="pending")  # pending, processing, completed, failed
    error_message = Column(Text, nullable=True)  # Error message if processing failed
    
    # Voice and multimedia
    voice_data = Column(JSON, default=dict)  # Voice message metadata
    attachments = Column(JSON, default=list)  # File attachments
    media_metadata = Column(JSON, default=dict)  # Multimedia content metadata
    
    # Privacy and moderation
    is_flagged = Column(Boolean, default=False)  # Content moderation flag
    moderation_reason = Column(String, nullable=True)  # Reason for flagging
    is_private = Column(Boolean, default=True)  # Privacy flag
    
    # Edit and version history
    is_edited = Column(Boolean, default=False)  # Whether message was edited
    edit_count = Column(Integer, default=0)  # Number of edits
    last_edited_at = Column(DateTime, nullable=True)  # Last edit timestamp
    edit_history = Column(JSON, default=list)  # Edit history
    
    # Message metadata and context
    message_metadata = Column(JSON, default=lambda: {
        'client_info': {},
        'session_info': {},
        'context_data': {},
        'processing_info': {}
    })
    
    # Follow-up and recommendations
    generates_follow_up = Column(Boolean, default=False)  # Whether message generates follow-up
    recommendations = Column(JSON, default=list)  # Specific recommendations from this message
    action_items = Column(JSON, default=list)  # Action items for user
    
    # Audit trail
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    
    # Relationships
    conversation = relationship("Conversation", back_populates="messages")
    
    # Indexes for performance
    __table_args__ = (
        Index('idx_message_conversation_timestamp', 'conversation_id', 'timestamp'),
        Index('idx_message_sender_timestamp', 'sender', 'timestamp'),
        Index('idx_message_emergency', 'emergency_flag'),
        Index('idx_message_urgency', 'urgency_score'),
        Index('idx_message_sequence', 'conversation_id', 'sequence_number'),
        Index('idx_message_processed', 'is_processed'),
    )
    
    def validate_sender(self) -> bool:
        """Validate message sender"""
        valid_senders = ['user', 'ai', 'system']
        return self.sender in valid_senders
    
    def validate_message_type(self) -> bool:
        """Validate message type"""
        valid_types = ['text', 'voice', 'image', 'file', 'system', 'notification']
        message_type = self.message_type or 'text'  # Use default if None
        return message_type in valid_types
    
    def validate_processing_status(self) -> bool:
        """Validate processing status"""
        valid_statuses = ['pending', 'processing', 'completed', 'failed', 'skipped']
        return self.processing_status in valid_statuses
    
    def is_from_user(self) -> bool:
        """Check if message is from user"""
        return self.sender == 'user'
    
    def is_from_ai(self) -> bool:
        """Check if message is from AI"""
        return self.sender == 'ai'
    
    def is_emergency_message(self) -> bool:
        """Check if message contains emergency indicators"""
        return self.emergency_flag or (self.urgency_score and self.urgency_score >= 8.0)
    
    def has_medical_content(self) -> bool:
        """Check if message contains medical content"""
        return bool(self.symptom_keywords or self.medical_entities or 
                   (self.medical_analysis and self.medical_analysis.get('symptoms_detected')))
    
    def get_word_count(self) -> int:
        """Get word count of message content"""
        if not self.content:
            return 0
        return len(self.content.split())
    
    def get_character_count(self) -> int:
        """Get character count of message content"""
        return len(self.content) if self.content else 0
    
    def add_symptom_keyword(self, keyword: str):
        """Add a symptom keyword"""
        if not self.symptom_keywords:
            self.symptom_keywords = []
        if keyword not in self.symptom_keywords:
            self.symptom_keywords.append(keyword)
    
    def add_medical_entity(self, entity: dict):
        """Add a medical entity"""
        if not self.medical_entities:
            self.medical_entities = []
        self.medical_entities.append(entity)
    
    def set_emergency_flag(self, reason: str = None):
        """Set emergency flag with optional reason"""
        self.emergency_flag = True
        if reason and not self.crisis_indicators:
            self.crisis_indicators = []
        if reason and reason not in self.crisis_indicators:
            self.crisis_indicators.append(reason)
    
    def add_recommendation(self, recommendation: str, priority: str = "normal"):
        """Add a recommendation"""
        if not self.recommendations:
            self.recommendations = []
        
        rec_obj = {
            'text': recommendation,
            'priority': priority,
            'timestamp': datetime.now(timezone.utc).isoformat()
        }
        self.recommendations.append(rec_obj)
    
    def mark_as_processed(self, status: str = "completed"):
        """Mark message as processed"""
        self.is_processed = True
        self.processing_status = status
        self.updated_at = datetime.now(timezone.utc)
    
    def add_user_feedback(self, rating: int = None, reaction: str = None, feedback_text: str = None):
        """Add user feedback to the message"""
        if rating is not None:
            self.user_rating = rating
        if reaction is not None:
            self.user_reaction = reaction
        if feedback_text is not None:
            self.feedback_text = feedback_text
    
    def edit_content(self, new_content: str, edit_reason: str = None):
        """Edit message content with history tracking"""
        if not self.edit_history:
            self.edit_history = []
        
        # Save current content to history
        edit_entry = {
            'previous_content': self.content,
            'edited_at': datetime.now(timezone.utc).isoformat(),
            'edit_reason': edit_reason
        }
        self.edit_history.append(edit_entry)
        
        # Update content
        self.content = new_content
        self.is_edited = True
        self.edit_count += 1
        self.last_edited_at = datetime.now(timezone.utc)
    
    def __repr__(self):
        return f"<Message(id={self.id}, sender={self.sender}, type={self.message_type}, timestamp={self.timestamp})>"


class Consultation(Base):
    """Consultation model for detailed medical consultations"""
    __tablename__ = "consultations"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id"), nullable=False, index=True)
    
    # Consultation details
    title = Column(String, nullable=True)
    chief_complaint = Column(Text, nullable=False)  # Main reason for consultation
    symptoms = Column(JSON, default=list)  # List of symptoms
    duration = Column(String, nullable=True)  # Duration of symptoms
    severity = Column(Integer, nullable=True)  # Severity scale 1-10
    
    # Assessment and recommendations
    ai_assessment = Column(Text, nullable=True)  # AI-generated assessment
    recommendations = Column(JSON, default=list)  # List of recommendations
    urgency_level = Column(String, default="routine")  # routine, urgent, emergency
    
    # Timestamps
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    
    # Status and follow-up
    status = Column(String, default="open")  # open, closed, follow_up_needed
    follow_up_date = Column(DateTime, nullable=True)
    
    # Privacy and sharing
    is_private = Column(Boolean, default=True)
    tags = Column(JSON, default=list)  # User-defined tags
    
    # Relationships
    user = relationship("User", back_populates="consultations")
    
    def __repr__(self):
        return f"<Consultation(id={self.id}, user_id={self.user_id}, title={self.title})>"


class HealthAnalytics(Base):
    """Analytics data model for aggregated health and consultation analytics"""
    __tablename__ = "health_analytics"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id"), nullable=False, index=True)
    
    # Time period and scope
    period_type = Column(String, nullable=False)  # 'daily', 'weekly', 'monthly', 'quarterly', 'yearly'
    period_start = Column(DateTime, nullable=False)
    period_end = Column(DateTime, nullable=False)
    analysis_scope = Column(String, default="comprehensive")  # comprehensive, symptoms_only, consultations_only
    
    # Basic health metrics
    consultation_count = Column(Integer, default=0)
    total_messages = Column(Integer, default=0)
    avg_consultation_length = Column(Float, nullable=True)  # Average messages per consultation
    avg_response_time = Column(Float, nullable=True)  # Average AI response time
    
    # Symptom and condition analytics
    symptom_frequency = Column(JSON, default=lambda: {})  # Frequency of reported symptoms
    symptom_severity_trends = Column(JSON, default=lambda: {})  # Severity trends over time
    condition_tracking = Column(JSON, default=lambda: {})  # Tracking of medical conditions
    new_symptoms_detected = Column(JSON, default=list)  # New symptoms in this period
    
    # Consultation patterns
    consultation_patterns = Column(JSON, default=lambda: {
        'peak_hours': [],
        'consultation_types': {},
        'urgency_distribution': {},
        'duration_patterns': {}
    })
    
    # Health trends and patterns
    health_trends = Column(JSON, default=lambda: {
        'improving_areas': [],
        'concerning_trends': [],
        'stable_conditions': [],
        'seasonal_patterns': {}
    })
    
    # Risk assessment and scoring
    overall_health_score = Column(Float, nullable=True)  # Overall health score (0-100)
    risk_assessment = Column(JSON, default=lambda: {
        'risk_level': 'low',  # low, moderate, high, critical
        'risk_factors': [],
        'protective_factors': [],
        'risk_score': 0.0
    })
    
    # Medication and treatment analytics
    medication_adherence = Column(JSON, default=lambda: {})  # Medication adherence patterns
    treatment_effectiveness = Column(JSON, default=lambda: {})  # Treatment outcome tracking
    drug_interaction_alerts = Column(Integer, default=0)  # Number of interaction alerts
    
    # Engagement and usage metrics
    engagement_metrics = Column(JSON, default=lambda: {
        'session_frequency': 0,
        'avg_session_duration': 0,
        'feature_usage': {},
        'user_satisfaction': 0.0
    })
    
    # AI performance metrics
    ai_performance = Column(JSON, default=lambda: {
        'accuracy_score': 0.0,
        'response_quality': 0.0,
        'emergency_detection_rate': 0.0,
        'user_feedback_score': 0.0
    })
    
    # Health insights and recommendations
    health_insights = Column(JSON, default=list)  # AI-generated health insights
    personalized_recommendations = Column(JSON, default=list)  # Personalized health recommendations
    preventive_care_suggestions = Column(JSON, default=list)  # Preventive care suggestions
    lifestyle_recommendations = Column(JSON, default=list)  # Lifestyle improvement suggestions
    
    # Alert and notification data
    alerts_generated = Column(Integer, default=0)  # Number of health alerts generated
    emergency_flags = Column(Integer, default=0)  # Number of emergency situations detected
    follow_up_reminders = Column(Integer, default=0)  # Follow-up reminders sent
    
    # Comparative analytics
    peer_comparison = Column(JSON, default=lambda: {})  # Anonymous peer comparison data
    historical_comparison = Column(JSON, default=lambda: {})  # Comparison with user's history
    benchmark_metrics = Column(JSON, default=lambda: {})  # Benchmark against health standards
    
    # Data quality and completeness
    data_completeness_score = Column(Float, nullable=True)  # Data completeness percentage
    data_quality_flags = Column(JSON, default=list)  # Data quality issues
    missing_data_areas = Column(JSON, default=list)  # Areas with insufficient data
    
    # Metadata and versioning
    generated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    last_updated = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    version = Column(String, default="2.0")  # Analytics algorithm version
    computation_time_ms = Column(Integer, nullable=True)  # Time taken to compute analytics
    
    # Status and flags
    is_complete = Column(Boolean, default=False)  # Whether analytics computation is complete
    has_anomalies = Column(Boolean, default=False)  # Whether anomalies were detected
    requires_attention = Column(Boolean, default=False)  # Whether results require medical attention
    
    # Relationships
    user = relationship("User", back_populates="health_analytics")
    
    # Indexes for performance
    __table_args__ = (
        Index('idx_health_analytics_user_period', 'user_id', 'period_type', 'period_start'),
        Index('idx_health_analytics_generated', 'generated_at'),
        Index('idx_health_analytics_complete', 'is_complete'),
        Index('idx_health_analytics_attention', 'requires_attention'),
        UniqueConstraint('user_id', 'period_type', 'period_start', name='uq_user_health_period'),
    )
    
    def validate_period_type(self) -> bool:
        """Validate period type"""
        valid_types = ['daily', 'weekly', 'monthly', 'quarterly', 'yearly', 'custom']
        return self.period_type in valid_types
    
    def validate_analysis_scope(self) -> bool:
        """Validate analysis scope"""
        valid_scopes = ['comprehensive', 'symptoms_only', 'consultations_only', 'medications_only', 'trends_only']
        return self.analysis_scope in valid_scopes
    
    def get_period_duration_days(self) -> int:
        """Get period duration in days"""
        if self.period_start and self.period_end:
            delta = self.period_end - self.period_start
            return delta.days
        return 0
    
    def calculate_health_score(self) -> float:
        """Calculate overall health score based on various metrics"""
        # This would implement a complex algorithm to calculate health score
        # For now, return a placeholder
        base_score = 75.0
        
        # Adjust based on consultation frequency
        if self.consultation_count > 10:
            base_score -= 5.0
        elif self.consultation_count == 0:
            base_score += 5.0
        
        # Adjust based on emergency flags
        if self.emergency_flags > 0:
            base_score -= self.emergency_flags * 10.0
        
        # Ensure score is within bounds
        return max(0.0, min(100.0, base_score))
    
    def get_top_symptoms(self, limit: int = 5) -> List[dict]:
        """Get top reported symptoms"""
        if not self.symptom_frequency:
            return []
        
        sorted_symptoms = sorted(
            self.symptom_frequency.items(),
            key=lambda x: x[1],
            reverse=True
        )
        
        return [{'symptom': k, 'frequency': v} for k, v in sorted_symptoms[:limit]]
    
    def has_concerning_trends(self) -> bool:
        """Check if there are concerning health trends"""
        if self.requires_attention:
            return True
        
        if self.health_trends and self.health_trends.get('concerning_trends'):
            return len(self.health_trends['concerning_trends']) > 0
        
        return self.emergency_flags > 0 or (self.overall_health_score and self.overall_health_score < 50)
    
    def get_risk_level(self) -> str:
        """Get current risk level"""
        if self.risk_assessment:
            return self.risk_assessment.get('risk_level', 'unknown')
        return 'unknown'
    
    def add_health_insight(self, insight: str, category: str = "general", confidence: float = 1.0):
        """Add a health insight"""
        if not self.health_insights:
            self.health_insights = []
        
        insight_obj = {
            'text': insight,
            'category': category,
            'confidence': confidence,
            'generated_at': datetime.now(timezone.utc).isoformat()
        }
        self.health_insights.append(insight_obj)
    
    def add_recommendation(self, recommendation: str, priority: str = "normal", category: str = "general"):
        """Add a personalized recommendation"""
        if not self.personalized_recommendations:
            self.personalized_recommendations = []
        
        rec_obj = {
            'text': recommendation,
            'priority': priority,
            'category': category,
            'generated_at': datetime.now(timezone.utc).isoformat()
        }
        self.personalized_recommendations.append(rec_obj)
    
    def mark_complete(self):
        """Mark analytics computation as complete"""
        self.is_complete = True
        self.last_updated = datetime.now(timezone.utc)
        self.overall_health_score = self.calculate_health_score()
    
    def __repr__(self):
        return f"<HealthAnalytics(id={self.id}, user_id={self.user_id}, period={self.period_type}, score={self.overall_health_score})>"


class SymptomPattern(Base):
    """Model for storing detected symptom patterns and health trends"""
    __tablename__ = "symptom_patterns"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id"), nullable=False, index=True)
    
    # Pattern identification
    pattern_type = Column(String, nullable=False)  # 'recurring', 'seasonal', 'trigger-based', 'progressive', 'cyclical'
    symptom_name = Column(String, nullable=False)
    symptom_category = Column(String, nullable=True)  # Category of symptom (pain, respiratory, etc.)
    description = Column(Text, nullable=True)
    
    # Pattern characteristics
    confidence_score = Column(Float, nullable=False)  # 0-1 confidence in pattern
    statistical_significance = Column(Float, nullable=True)  # Statistical significance of pattern
    frequency = Column(String, nullable=True)  # Pattern frequency (daily, weekly, monthly, etc.)
    frequency_numeric = Column(Float, nullable=True)  # Numeric frequency (times per period)
    
    # Severity and progression
    severity_trend = Column(String, nullable=True)  # increasing, decreasing, stable, fluctuating
    average_severity = Column(Float, nullable=True)  # Average severity score (1-10)
    peak_severity = Column(Float, nullable=True)  # Peak severity observed
    severity_variance = Column(Float, nullable=True)  # Variance in severity scores
    
    # Temporal patterns
    detected_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    first_occurrence = Column(DateTime, nullable=True)
    last_occurrence = Column(DateTime, nullable=True)
    next_predicted_occurrence = Column(DateTime, nullable=True)
    
    # Duration patterns
    typical_duration_hours = Column(Float, nullable=True)  # Typical episode duration
    duration_trend = Column(String, nullable=True)  # increasing, decreasing, stable
    
    # Timing patterns
    time_of_day_pattern = Column(JSON, default=lambda: {})  # Hour-based occurrence pattern
    day_of_week_pattern = Column(JSON, default=lambda: {})  # Day-based occurrence pattern
    seasonal_pattern = Column(JSON, default=lambda: {})  # Seasonal occurrence pattern
    
    # Pattern details and metadata
    pattern_data = Column(JSON, default=lambda: {
        'occurrence_count': 0,
        'total_episodes': 0,
        'pattern_strength': 0.0,
        'predictability_score': 0.0
    })
    
    # Triggers and correlations
    triggers = Column(JSON, default=list)  # Potential triggers (weather, stress, food, etc.)
    trigger_confidence = Column(JSON, default=lambda: {})  # Confidence scores for each trigger
    correlations = Column(JSON, default=list)  # Correlated symptoms or factors
    correlation_strength = Column(JSON, default=lambda: {})  # Strength of correlations
    
    # Environmental and lifestyle factors
    weather_correlation = Column(JSON, default=lambda: {})  # Weather-related correlations
    activity_correlation = Column(JSON, default=lambda: {})  # Activity-related correlations
    medication_correlation = Column(JSON, default=lambda: {})  # Medication-related correlations
    
    # Medical significance
    medical_significance = Column(String, default="unknown")  # low, moderate, high, critical
    requires_attention = Column(Boolean, default=False)  # Medically significant
    recommended_action = Column(String, nullable=True)  # Recommended medical action
    
    # Pattern status and lifecycle
    is_active = Column(Boolean, default=True)
    is_validated = Column(Boolean, default=False)  # Whether pattern has been medically validated
    validation_date = Column(DateTime, nullable=True)
    pattern_status = Column(String, default="detected")  # detected, confirmed, resolved, monitoring
    
    # Analytics and insights
    health_impact_score = Column(Float, nullable=True)  # Impact on overall health (0-10)
    quality_of_life_impact = Column(Float, nullable=True)  # Impact on quality of life (0-10)
    intervention_effectiveness = Column(JSON, default=lambda: {})  # Effectiveness of interventions
    
    # Prediction and forecasting
    prediction_model = Column(JSON, default=lambda: {})  # Prediction model parameters
    forecast_accuracy = Column(Float, nullable=True)  # Accuracy of predictions
    risk_prediction = Column(JSON, default=lambda: {})  # Risk predictions
    
    # Audit and versioning
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    algorithm_version = Column(String, default="1.0")  # Pattern detection algorithm version
    
    # Indexes for efficient querying
    __table_args__ = (
        Index('idx_symptom_pattern_user_symptom', 'user_id', 'symptom_name'),
        Index('idx_symptom_pattern_type', 'pattern_type'),
        Index('idx_symptom_pattern_active', 'is_active'),
        Index('idx_symptom_pattern_attention', 'requires_attention'),
        Index('idx_symptom_pattern_confidence', 'confidence_score'),
        Index('idx_symptom_pattern_detected', 'detected_at'),
    )
    
    def validate_pattern_type(self) -> bool:
        """Validate pattern type"""
        valid_types = ['recurring', 'seasonal', 'trigger-based', 'progressive', 'cyclical', 'episodic']
        return self.pattern_type in valid_types
    
    def validate_severity_trend(self) -> bool:
        """Validate severity trend"""
        if self.severity_trend is None:
            return True
        valid_trends = ['increasing', 'decreasing', 'stable', 'fluctuating', 'unknown']
        return self.severity_trend in valid_trends
    
    def validate_medical_significance(self) -> bool:
        """Validate medical significance level"""
        valid_levels = ['low', 'moderate', 'high', 'critical', 'unknown']
        return self.medical_significance in valid_levels
    
    def is_concerning_pattern(self) -> bool:
        """Check if pattern is medically concerning"""
        return (self.requires_attention or 
                self.medical_significance in ['high', 'critical'] or
                self.severity_trend == 'increasing' or
                (self.confidence_score and self.confidence_score > 0.8 and 
                 self.health_impact_score and self.health_impact_score > 7.0))
    
    def get_pattern_strength(self) -> float:
        """Get pattern strength score"""
        if self.pattern_data and 'pattern_strength' in self.pattern_data:
            return self.pattern_data['pattern_strength']
        return 0.0
    
    def get_occurrence_count(self) -> int:
        """Get total occurrence count"""
        if self.pattern_data and 'occurrence_count' in self.pattern_data:
            return self.pattern_data['occurrence_count']
        return 0
    
    def update_occurrence_count(self, count: int):
        """Update occurrence count"""
        if not self.pattern_data:
            self.pattern_data = {}
        self.pattern_data['occurrence_count'] = count
        self.last_occurrence = datetime.now(timezone.utc)
    
    def add_trigger(self, trigger: str, confidence: float = 0.5):
        """Add a potential trigger"""
        if not self.triggers:
            self.triggers = []
        if not self.trigger_confidence:
            self.trigger_confidence = {}
        
        if trigger not in self.triggers:
            self.triggers.append(trigger)
        self.trigger_confidence[trigger] = confidence
    
    def add_correlation(self, factor: str, strength: float = 0.5):
        """Add a correlation factor"""
        if not self.correlations:
            self.correlations = []
        if not self.correlation_strength:
            self.correlation_strength = {}
        
        if factor not in self.correlations:
            self.correlations.append(factor)
        self.correlation_strength[factor] = strength
    
    def predict_next_occurrence(self) -> Optional[datetime]:
        """Predict next occurrence based on pattern"""
        if not self.frequency_numeric or not self.last_occurrence:
            return None
        
        # Simple prediction based on frequency
        if self.frequency == 'daily':
            days_to_add = 1 / self.frequency_numeric
        elif self.frequency == 'weekly':
            days_to_add = 7 / self.frequency_numeric
        elif self.frequency == 'monthly':
            days_to_add = 30 / self.frequency_numeric
        else:
            return None
        
        from datetime import timedelta
        return self.last_occurrence + timedelta(days=days_to_add)
    
    def calculate_health_impact(self) -> float:
        """Calculate health impact score"""
        impact = 0.0
        
        # Base impact from severity
        if self.average_severity:
            impact += self.average_severity * 0.3
        
        # Frequency impact
        if self.frequency_numeric:
            if self.frequency == 'daily':
                impact += self.frequency_numeric * 2.0
            elif self.frequency == 'weekly':
                impact += self.frequency_numeric * 0.5
        
        # Trend impact
        if self.severity_trend == 'increasing':
            impact += 2.0
        elif self.severity_trend == 'decreasing':
            impact -= 1.0
        
        return min(10.0, max(0.0, impact))
    
    def __repr__(self):
        return f"<SymptomPattern(id={self.id}, type={self.pattern_type}, symptom={self.symptom_name}, confidence={self.confidence_score})>"


class HealthMetric(Base):
    """Model for storing individual health metrics and measurements"""
    __tablename__ = "health_metrics"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id"), nullable=False, index=True)
    
    # Metric identification
    metric_type = Column(String, nullable=False)  # 'vital_sign', 'lab_result', 'symptom_score', 'wellness_indicator'
    metric_name = Column(String, nullable=False)  # 'blood_pressure', 'heart_rate', 'pain_level', etc.
    metric_category = Column(String, nullable=True)  # 'cardiovascular', 'respiratory', 'metabolic', etc.
    
    # Measurement data
    value = Column(Float, nullable=False)  # Numeric value of the metric
    unit = Column(String, nullable=True)  # Unit of measurement
    reference_range_min = Column(Float, nullable=True)  # Normal range minimum
    reference_range_max = Column(Float, nullable=True)  # Normal range maximum
    
    # Status and interpretation
    status = Column(String, nullable=True)  # 'normal', 'low', 'high', 'critical'
    interpretation = Column(Text, nullable=True)  # Clinical interpretation
    
    # Temporal information
    measured_at = Column(DateTime, nullable=False)
    recorded_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    
    # Source and context
    source = Column(String, nullable=True)  # 'user_input', 'device', 'lab_report', 'clinical_visit'
    device_info = Column(JSON, default=dict)  # Device information if applicable
    measurement_context = Column(JSON, default=dict)  # Context of measurement
    
    # Quality and reliability
    reliability_score = Column(Float, nullable=True)  # Reliability of measurement (0-1)
    quality_flags = Column(JSON, default=list)  # Quality issues or flags
    
    # Relationships and references
    related_conversation_id = Column(String, nullable=True)  # Related conversation
    related_medical_record_id = Column(String, nullable=True)  # Related medical record
    
    # Metadata
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    
    # Indexes
    __table_args__ = (
        Index('idx_health_metric_user_type', 'user_id', 'metric_type'),
        Index('idx_health_metric_name_measured', 'metric_name', 'measured_at'),
        Index('idx_health_metric_status', 'status'),
        Index('idx_health_metric_recorded', 'recorded_at'),
    )
    
    def is_normal(self) -> bool:
        """Check if metric value is within normal range"""
        if self.reference_range_min is not None and self.value < self.reference_range_min:
            return False
        if self.reference_range_max is not None and self.value > self.reference_range_max:
            return False
        return True
    
    def get_deviation_percentage(self) -> Optional[float]:
        """Get percentage deviation from normal range"""
        if self.reference_range_min is None or self.reference_range_max is None:
            return None
        
        range_center = (self.reference_range_min + self.reference_range_max) / 2
        range_width = self.reference_range_max - self.reference_range_min
        
        if range_width == 0:
            return 0.0
        
        deviation = abs(self.value - range_center)
        return (deviation / (range_width / 2)) * 100
    
    def __repr__(self):
        return f"<HealthMetric(id={self.id}, name={self.metric_name}, value={self.value}, unit={self.unit})>"


class TrendAnalysis(Base):
    """Model for storing trend analysis results"""
    __tablename__ = "trend_analyses"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id"), nullable=False, index=True)
    
    # Analysis scope
    analysis_type = Column(String, nullable=False)  # 'symptom_trend', 'metric_trend', 'consultation_trend'
    target_name = Column(String, nullable=False)  # Name of what's being analyzed
    time_period_days = Column(Integer, nullable=False)  # Analysis time period
    
    # Trend characteristics
    trend_direction = Column(String, nullable=True)  # 'increasing', 'decreasing', 'stable', 'cyclical'
    trend_strength = Column(Float, nullable=True)  # Strength of trend (0-1)
    statistical_significance = Column(Float, nullable=True)  # P-value or similar
    
    # Trend data
    data_points = Column(JSON, default=list)  # Time series data points
    trend_line_params = Column(JSON, default=dict)  # Trend line parameters
    seasonal_components = Column(JSON, default=dict)  # Seasonal decomposition
    
    # Analysis results
    insights = Column(JSON, default=list)  # Generated insights
    recommendations = Column(JSON, default=list)  # Recommendations based on trend
    risk_assessment = Column(JSON, default=dict)  # Risk assessment
    
    # Metadata
    analyzed_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    algorithm_version = Column(String, default="1.0")
    
    # Indexes
    __table_args__ = (
        Index('idx_trend_analysis_user_type', 'user_id', 'analysis_type'),
        Index('idx_trend_analysis_target', 'target_name'),
        Index('idx_trend_analysis_analyzed', 'analyzed_at'),
    )
    
    def __repr__(self):
        return f"<TrendAnalysis(id={self.id}, type={self.analysis_type}, target={self.target_name}, direction={self.trend_direction})>"


class SymptomRecord(Base):
    """Model for storing symptom analysis records"""
    __tablename__ = "symptom_records"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id"), nullable=False, index=True)
    
    # Symptom information
    symptoms = Column(JSON, default=list)  # List of reported symptoms
    duration = Column(String, nullable=True)  # Duration of symptoms
    severity_rating = Column(Integer, nullable=True)  # User self-rating (1-10)
    location = Column(String, nullable=True)  # Location of symptoms
    
    # Additional symptom details
    triggers = Column(JSON, default=list)  # Known triggers
    alleviating_factors = Column(JSON, default=list)  # Things that help
    associated_symptoms = Column(JSON, default=list)  # Additional symptoms
    
    # Analysis results
    analysis_results = Column(JSON, default=dict)  # Complete analysis results
    urgency_level = Column(String, nullable=True)  # Calculated urgency level
    requires_follow_up = Column(Boolean, default=False)  # Whether follow-up is needed
    
    # Timestamps
    recorded_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    
    # Relationships
    user = relationship("User", back_populates="symptom_records")
    
    # Indexes
    __table_args__ = (
        Index('idx_symptom_record_user_recorded', 'user_id', 'recorded_at'),
        Index('idx_symptom_record_urgency', 'urgency_level'),
        Index('idx_symptom_record_follow_up', 'requires_follow_up'),
    )
    
    def __repr__(self):
        return f"<SymptomRecord(id={self.id}, symptoms={len(self.symptoms or [])}, urgency={self.urgency_level})>"


# Note: Drug interaction models are imported separately to avoid circular imports