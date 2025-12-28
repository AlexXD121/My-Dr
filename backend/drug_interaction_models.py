"""
Drug interaction models for medication management system
"""
from datetime import datetime, timezone
from typing import List, Optional, Dict, Any
from sqlalchemy import (
    Column, Integer, String, Float, DateTime, Text, JSON, 
    ForeignKey, Boolean, Index, UniqueConstraint
)
from sqlalchemy.orm import relationship
from models import Base
import uuid


class Medication(Base):
    """Medication model for storing drug information"""
    __tablename__ = "medications"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    
    # Basic medication information
    name = Column(String, nullable=False, index=True)  # Generic name
    brand_names = Column(JSON, default=list)  # List of brand names
    drug_class = Column(String, nullable=True, index=True)  # Therapeutic class
    active_ingredients = Column(JSON, default=list)  # List of active ingredients
    
    # Drug identification
    ndc_number = Column(String, nullable=True, unique=True)  # National Drug Code
    rxcui = Column(String, nullable=True, unique=True)  # RxNorm Concept Unique Identifier
    atc_code = Column(String, nullable=True)  # Anatomical Therapeutic Chemical code
    
    # Medication details
    strength = Column(String, nullable=True)  # e.g., "500mg", "10mg/ml"
    dosage_form = Column(String, nullable=True)  # tablet, capsule, liquid, etc.
    route_of_administration = Column(String, nullable=True)  # oral, IV, topical, etc.
    
    # Clinical information
    indication = Column(Text, nullable=True)  # What it's used for
    contraindications = Column(JSON, default=list)  # When not to use
    side_effects = Column(JSON, default=list)  # Common side effects
    warnings = Column(JSON, default=list)  # Important warnings
    
    # Interaction data
    interaction_severity_high = Column(JSON, default=list)  # High severity interactions
    interaction_severity_moderate = Column(JSON, default=list)  # Moderate severity
    interaction_severity_low = Column(JSON, default=list)  # Low severity
    
    # Metadata
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    is_active = Column(Boolean, default=True)
    
    # Relationships
    user_medications = relationship("UserMedication", back_populates="medication")
    interaction_reports = relationship("DrugInteractionReport", 
                                     foreign_keys="DrugInteractionReport.medication_a_id",
                                     back_populates="medication_a")
    
    # Indexes
    __table_args__ = (
        Index('idx_medication_name_class', 'name', 'drug_class'),
        Index('idx_medication_active_ingredients', 'active_ingredients'),
        Index('idx_medication_brand_names', 'brand_names'),
    )
    
    def get_all_names(self) -> List[str]:
        """Get all names (generic + brand names) for this medication"""
        names = [self.name]
        if self.brand_names:
            names.extend(self.brand_names)
        return names
    
    def has_high_severity_interaction_with(self, other_medication_name: str) -> bool:
        """Check if this medication has high severity interaction with another"""
        if not self.interaction_severity_high:
            return False
        return other_medication_name.lower() in [name.lower() for name in self.interaction_severity_high]
    
    def __repr__(self):
        return f"<Medication(id={self.id}, name={self.name}, class={self.drug_class})>"


class UserMedication(Base):
    """User's medication list with dosage and schedule information"""
    __tablename__ = "user_medications"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id"), nullable=False, index=True)
    medication_id = Column(String, ForeignKey("medications.id"), nullable=False, index=True)
    
    # Prescription details
    prescribed_by = Column(String, nullable=True)  # Doctor/provider name
    prescription_date = Column(DateTime, nullable=True)
    start_date = Column(DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))
    end_date = Column(DateTime, nullable=True)  # For temporary medications
    
    # Dosage information
    dosage = Column(String, nullable=False)  # e.g., "500mg"
    frequency = Column(String, nullable=False)  # e.g., "twice daily", "every 8 hours"
    instructions = Column(Text, nullable=True)  # Special instructions
    
    # Schedule and reminders
    schedule_times = Column(JSON, default=list)  # List of times to take medication
    reminder_enabled = Column(Boolean, default=True)
    last_reminder_sent = Column(DateTime, nullable=True)
    
    # Adherence tracking
    total_doses_prescribed = Column(Integer, default=0)
    doses_taken = Column(Integer, default=0)
    doses_missed = Column(Integer, default=0)
    adherence_percentage = Column(Float, default=0.0)
    
    # Status and notes
    status = Column(String, default="active")  # active, paused, discontinued, completed
    reason_for_discontinuation = Column(String, nullable=True)
    patient_notes = Column(Text, nullable=True)
    
    # Metadata
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    
    # Relationships
    user = relationship("User")
    medication = relationship("Medication", back_populates="user_medications")
    dose_logs = relationship("MedicationDoseLog", back_populates="user_medication", cascade="all, delete-orphan")
    
    # Indexes
    __table_args__ = (
        Index('idx_user_medication_status', 'user_id', 'status'),
        Index('idx_user_medication_dates', 'start_date', 'end_date'),
        UniqueConstraint('user_id', 'medication_id', 'start_date', name='uq_user_medication_start'),
    )
    
    def calculate_adherence(self):
        """Calculate and update adherence percentage"""
        if self.total_doses_prescribed > 0:
            self.adherence_percentage = (self.doses_taken / self.total_doses_prescribed) * 100
        else:
            self.adherence_percentage = 0.0
    
    def is_active(self) -> bool:
        """Check if medication is currently active"""
        if self.status != "active":
            return False
        
        now = datetime.now(timezone.utc)
        if self.end_date and now > self.end_date:
            return False
        
        return True
    
    def get_next_dose_time(self) -> Optional[datetime]:
        """Get the next scheduled dose time"""
        if not self.schedule_times or not self.is_active():
            return None
        
        # This is a simplified implementation
        # In a real system, you'd calculate based on current time and schedule
        now = datetime.now(timezone.utc)
        # Return next scheduled time (implementation would be more complex)
        return now  # Placeholder
    
    def __repr__(self):
        return f"<UserMedication(id={self.id}, user_id={self.user_id}, medication={self.medication.name if self.medication else 'Unknown'})>"


class MedicationDoseLog(Base):
    """Log of medication doses taken or missed"""
    __tablename__ = "medication_dose_logs"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_medication_id = Column(String, ForeignKey("user_medications.id"), nullable=False, index=True)
    
    # Dose information
    scheduled_time = Column(DateTime, nullable=False)
    actual_time = Column(DateTime, nullable=True)  # When actually taken
    status = Column(String, nullable=False)  # taken, missed, skipped, late
    
    # Dose details
    dosage_taken = Column(String, nullable=True)  # Actual dosage if different from prescribed
    notes = Column(Text, nullable=True)  # Patient notes about the dose
    
    # Side effects or reactions
    side_effects_reported = Column(JSON, default=list)
    severity_rating = Column(Integer, nullable=True)  # 1-10 scale
    
    # Metadata
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    
    # Relationships
    user_medication = relationship("UserMedication", back_populates="dose_logs")
    
    # Indexes
    __table_args__ = (
        Index('idx_dose_log_scheduled_time', 'scheduled_time'),
        Index('idx_dose_log_status', 'status'),
        Index('idx_dose_log_user_medication_time', 'user_medication_id', 'scheduled_time'),
    )
    
    def is_late(self, grace_period_minutes: int = 30) -> bool:
        """Check if dose was taken late"""
        if not self.actual_time or self.status != "taken":
            return False
        
        grace_period = timezone.timedelta(minutes=grace_period_minutes)
        return self.actual_time > (self.scheduled_time + grace_period)
    
    def __repr__(self):
        return f"<MedicationDoseLog(id={self.id}, status={self.status}, scheduled={self.scheduled_time})>"


class DrugInteractionReport(Base):
    """Drug interaction analysis results"""
    __tablename__ = "drug_interaction_reports"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id"), nullable=False, index=True)
    
    # Medications involved in interaction
    medication_a_id = Column(String, ForeignKey("medications.id"), nullable=False)
    medication_b_id = Column(String, ForeignKey("medications.id"), nullable=False)
    
    # Interaction details
    interaction_type = Column(String, nullable=False)  # pharmacokinetic, pharmacodynamic, etc.
    severity_level = Column(String, nullable=False)  # high, moderate, low
    severity_score = Column(Float, nullable=False)  # 0-10 numerical score
    
    # Clinical information
    mechanism = Column(Text, nullable=True)  # How the interaction occurs
    clinical_effects = Column(JSON, default=list)  # List of potential effects
    management_recommendations = Column(JSON, default=list)  # How to manage the interaction
    
    # Risk assessment
    risk_factors = Column(JSON, default=list)  # Patient-specific risk factors
    contraindicated = Column(Boolean, default=False)  # Should not be used together
    monitoring_required = Column(Boolean, default=False)  # Requires monitoring
    
    # Evidence and sources
    evidence_level = Column(String, nullable=True)  # high, moderate, low, theoretical
    sources = Column(JSON, default=list)  # Literature references
    
    # Report metadata
    generated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    algorithm_version = Column(String, nullable=True)  # Version of interaction algorithm used
    
    # User acknowledgment
    acknowledged_by_user = Column(Boolean, default=False)
    acknowledged_at = Column(DateTime, nullable=True)
    user_notes = Column(Text, nullable=True)
    
    # Relationships
    user = relationship("User")
    medication_a = relationship("Medication", foreign_keys=[medication_a_id], back_populates="interaction_reports")
    medication_b = relationship("Medication", foreign_keys=[medication_b_id])
    
    # Indexes
    __table_args__ = (
        Index('idx_interaction_user_severity', 'user_id', 'severity_level'),
        Index('idx_interaction_medications', 'medication_a_id', 'medication_b_id'),
        Index('idx_interaction_contraindicated', 'contraindicated'),
        UniqueConstraint('user_id', 'medication_a_id', 'medication_b_id', name='uq_user_drug_interaction'),
    )
    
    def get_severity_color(self) -> str:
        """Get color code for severity level"""
        severity_colors = {
            "high": "#dc3545",      # Red
            "moderate": "#fd7e14",  # Orange
            "low": "#ffc107"        # Yellow
        }
        return severity_colors.get(self.severity_level, "#6c757d")  # Gray for unknown
    
    def requires_immediate_attention(self) -> bool:
        """Check if interaction requires immediate medical attention"""
        return self.contraindicated or (self.severity_level == "high" and self.severity_score >= 8.0)
    
    def __repr__(self):
        return f"<DrugInteractionReport(id={self.id}, severity={self.severity_level}, score={self.severity_score})>"


class MedicationReminder(Base):
    """Medication reminder scheduling and tracking"""
    __tablename__ = "medication_reminders"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_medication_id = Column(String, ForeignKey("user_medications.id"), nullable=False, index=True)
    
    # Reminder scheduling
    reminder_time = Column(DateTime, nullable=False)
    reminder_type = Column(String, default="dose")  # dose, refill, appointment
    
    # Reminder content
    title = Column(String, nullable=False)
    message = Column(Text, nullable=True)
    
    # Delivery settings
    delivery_methods = Column(JSON, default=list)  # email, sms, push, in_app
    priority = Column(String, default="normal")  # low, normal, high, urgent
    
    # Status tracking
    status = Column(String, default="scheduled")  # scheduled, sent, acknowledged, dismissed, failed
    sent_at = Column(DateTime, nullable=True)
    acknowledged_at = Column(DateTime, nullable=True)
    
    # Retry logic
    retry_count = Column(Integer, default=0)
    max_retries = Column(Integer, default=3)
    next_retry_at = Column(DateTime, nullable=True)
    
    # Metadata
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    
    # Relationships
    user_medication = relationship("UserMedication")
    
    # Indexes
    __table_args__ = (
        Index('idx_reminder_time_status', 'reminder_time', 'status'),
        Index('idx_reminder_user_medication', 'user_medication_id'),
        Index('idx_reminder_retry', 'next_retry_at', 'retry_count'),
    )
    
    def is_due(self) -> bool:
        """Check if reminder is due to be sent"""
        if self.status != "scheduled":
            return False
        
        now = datetime.now(timezone.utc)
        return now >= self.reminder_time
    
    def can_retry(self) -> bool:
        """Check if reminder can be retried"""
        return self.retry_count < self.max_retries and self.status == "failed"
    
    def __repr__(self):
        return f"<MedicationReminder(id={self.id}, time={self.reminder_time}, status={self.status})>"