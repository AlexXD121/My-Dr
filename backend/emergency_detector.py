"""
Emergency Detection System for MyDoc AI Medical Assistant

This module provides comprehensive emergency detection capabilities including
medical keyword pattern matching, urgency scoring, and automatic emergency
response generation with logging and alerting.
"""

import logging
import re
from datetime import datetime, timezone
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass, field
from enum import Enum
import json

logger = logging.getLogger(__name__)


class EmergencyLevel(Enum):
    """Emergency severity levels"""
    LOW = "low"
    MODERATE = "moderate"
    HIGH = "high"
    CRITICAL = "critical"


class SymptomCategory(Enum):
    """Medical symptom categories"""
    CARDIAC = "cardiac"
    RESPIRATORY = "respiratory"
    NEUROLOGICAL = "neurological"
    TRAUMA = "trauma"
    ALLERGIC = "allergic"
    PSYCHIATRIC = "psychiatric"
    GASTROINTESTINAL = "gastrointestinal"
    POISONING = "poisoning"
    GENERAL = "general"


@dataclass
class EmergencyKeyword:
    """Emergency keyword with associated metadata"""
    keyword: str
    category: SymptomCategory
    urgency_score: int  # 1-10 scale
    emergency_level: EmergencyLevel
    context_required: bool = False
    aliases: List[str] = field(default_factory=list)


@dataclass
class EmergencyAssessment:
    """Emergency assessment result"""
    is_emergency: bool
    urgency_score: int  # 1-10 scale
    emergency_level: EmergencyLevel
    detected_keywords: List[str]
    categories: List[SymptomCategory]
    confidence: float
    recommendations: List[str]
    emergency_response: str
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    metadata: Dict[str, Any] = field(default_factory=dict)


class EmergencyDetector:
    """
    Comprehensive emergency detection system with medical keyword pattern matching,
    urgency scoring algorithm, and automatic emergency response generation.
    """
    
    def __init__(self):
        self.emergency_keywords = self._initialize_emergency_keywords()
        self.urgency_modifiers = self._initialize_urgency_modifiers()
        self.context_patterns = self._initialize_context_patterns()
        
    def _initialize_emergency_keywords(self) -> List[EmergencyKeyword]:
        """Initialize comprehensive emergency keyword database"""
        keywords = [
            # Critical Cardiac Emergencies
            EmergencyKeyword("heart attack", SymptomCategory.CARDIAC, 10, EmergencyLevel.CRITICAL),
            EmergencyKeyword("chest pain", SymptomCategory.CARDIAC, 8, EmergencyLevel.HIGH, 
                           aliases=["chest pressure", "chest tightness", "chest burning"]),
            EmergencyKeyword("cardiac arrest", SymptomCategory.CARDIAC, 10, EmergencyLevel.CRITICAL),
            EmergencyKeyword("severe chest pain", SymptomCategory.CARDIAC, 9, EmergencyLevel.CRITICAL),
            EmergencyKeyword("crushing chest pain", SymptomCategory.CARDIAC, 10, EmergencyLevel.CRITICAL),
            
            # Critical Respiratory Emergencies
            EmergencyKeyword("can't breathe", SymptomCategory.RESPIRATORY, 10, EmergencyLevel.CRITICAL,
                           aliases=["cannot breathe", "unable to breathe"]),
            EmergencyKeyword("difficulty breathing", SymptomCategory.RESPIRATORY, 8, EmergencyLevel.HIGH,
                           aliases=["shortness of breath", "trouble breathing", "hard to breathe"]),
            EmergencyKeyword("choking", SymptomCategory.RESPIRATORY, 10, EmergencyLevel.CRITICAL),
            EmergencyKeyword("severe asthma attack", SymptomCategory.RESPIRATORY, 9, EmergencyLevel.CRITICAL),
            EmergencyKeyword("blue lips", SymptomCategory.RESPIRATORY, 9, EmergencyLevel.CRITICAL,
                           aliases=["blue skin", "cyanosis"]),
            
            # Critical Neurological Emergencies
            EmergencyKeyword("stroke", SymptomCategory.NEUROLOGICAL, 10, EmergencyLevel.CRITICAL),
            EmergencyKeyword("seizure", SymptomCategory.NEUROLOGICAL, 9, EmergencyLevel.CRITICAL,
                           aliases=["convulsion", "fit"]),
            EmergencyKeyword("unconscious", SymptomCategory.NEUROLOGICAL, 10, EmergencyLevel.CRITICAL,
                           aliases=["passed out", "unresponsive", "not responding"]),
            EmergencyKeyword("severe head injury", SymptomCategory.NEUROLOGICAL, 9, EmergencyLevel.CRITICAL),
            EmergencyKeyword("sudden severe headache", SymptomCategory.NEUROLOGICAL, 8, EmergencyLevel.HIGH),
            EmergencyKeyword("confusion", SymptomCategory.NEUROLOGICAL, 6, EmergencyLevel.MODERATE, context_required=True),
            
            # Trauma Emergencies
            EmergencyKeyword("severe bleeding", SymptomCategory.TRAUMA, 9, EmergencyLevel.CRITICAL,
                           aliases=["heavy bleeding", "blood loss", "hemorrhage"]),
            EmergencyKeyword("broken bone", SymptomCategory.TRAUMA, 6, EmergencyLevel.MODERATE,
                           aliases=["fractured bone", "bone fracture"]),
            EmergencyKeyword("severe burn", SymptomCategory.TRAUMA, 8, EmergencyLevel.HIGH),
            EmergencyKeyword("deep cut", SymptomCategory.TRAUMA, 7, EmergencyLevel.HIGH,
                           aliases=["deep wound", "severe laceration"]),
            
            # Allergic Reactions
            EmergencyKeyword("anaphylaxis", SymptomCategory.ALLERGIC, 10, EmergencyLevel.CRITICAL),
            EmergencyKeyword("severe allergic reaction", SymptomCategory.ALLERGIC, 9, EmergencyLevel.CRITICAL),
            EmergencyKeyword("swollen throat", SymptomCategory.ALLERGIC, 8, EmergencyLevel.HIGH,
                           aliases=["throat swelling", "throat closing"]),
            
            # Poisoning/Overdose
            EmergencyKeyword("overdose", SymptomCategory.POISONING, 10, EmergencyLevel.CRITICAL),
            EmergencyKeyword("poisoning", SymptomCategory.POISONING, 9, EmergencyLevel.CRITICAL,
                           aliases=["poison", "toxic"]),
            EmergencyKeyword("drug overdose", SymptomCategory.POISONING, 10, EmergencyLevel.CRITICAL),
            
            # Psychiatric Emergencies
            EmergencyKeyword("suicide", SymptomCategory.PSYCHIATRIC, 10, EmergencyLevel.CRITICAL,
                           aliases=["kill myself", "end my life", "suicidal"]),
            EmergencyKeyword("self harm", SymptomCategory.PSYCHIATRIC, 8, EmergencyLevel.HIGH,
                           aliases=["hurt myself", "self-harm", "cutting myself"]),
            
            # General Emergency Indicators
            EmergencyKeyword("emergency", SymptomCategory.GENERAL, 8, EmergencyLevel.HIGH),
            EmergencyKeyword("911", SymptomCategory.GENERAL, 9, EmergencyLevel.CRITICAL,
                           aliases=["999", "112", "ambulance"]),
            EmergencyKeyword("dying", SymptomCategory.GENERAL, 10, EmergencyLevel.CRITICAL,
                           aliases=["going to die", "feel like dying"]),
            EmergencyKeyword("severe pain", SymptomCategory.GENERAL, 7, EmergencyLevel.HIGH,
                           aliases=["excruciating pain", "unbearable pain"]),
            
            # Gastrointestinal Emergencies
            EmergencyKeyword("severe abdominal pain", SymptomCategory.GASTROINTESTINAL, 7, EmergencyLevel.HIGH),
            EmergencyKeyword("vomiting blood", SymptomCategory.GASTROINTESTINAL, 9, EmergencyLevel.CRITICAL,
                           aliases=["throwing up blood", "blood in vomit"]),
            EmergencyKeyword("severe dehydration", SymptomCategory.GASTROINTESTINAL, 6, EmergencyLevel.MODERATE),
        ]
        
        return keywords
    
    def _initialize_urgency_modifiers(self) -> Dict[str, int]:
        """Initialize urgency modifier words that increase/decrease urgency scores"""
        return {
            # Intensity modifiers (increase urgency)
            "severe": +2,
            "extreme": +3,
            "excruciating": +3,
            "unbearable": +3,
            "crushing": +2,
            "sudden": +2,
            "acute": +2,
            "intense": +1,
            "sharp": +1,
            "stabbing": +1,
            
            # Temporal modifiers
            "sudden onset": +2,
            "getting worse": +1,
            "worsening": +1,
            "rapidly": +2,
            
            # Frequency modifiers
            "constant": +1,
            "continuous": +1,
            "persistent": +1,
            
            # Diminishing modifiers (decrease urgency)
            "mild": -2,
            "slight": -2,
            "minor": -1,
            "occasional": -1,
            "intermittent": -1,
        }
    
    def _initialize_context_patterns(self) -> Dict[str, List[str]]:
        """Initialize context patterns that help determine emergency severity"""
        return {
            "time_indicators": [
                r"(\d+)\s*(minutes?|hours?|days?)\s*ago",
                r"since\s*(yesterday|this morning|last night)",
                r"for\s*(\d+)\s*(minutes?|hours?|days?)",
                r"started\s*(suddenly|gradually|slowly)"
            ],
            "severity_indicators": [
                r"(worst|most severe|never felt|unbearable|excruciating)",
                r"(scale of \d+|out of 10|10/10|9/10|8/10)",
                r"(can't|cannot|unable to)\s*(walk|move|stand|function)"
            ],
            "associated_symptoms": [
                r"(with|along with|accompanied by|also have)",
                r"(nausea|vomiting|dizziness|sweating|fever)"
            ]
        }
    
    def detect_emergency(self, message: str, context: Dict[str, Any] = None) -> EmergencyAssessment:
        """
        Comprehensive emergency detection with urgency scoring
        
        Args:
            message: User's message to analyze
            context: Additional context (medical history, previous messages, etc.)
            
        Returns:
            EmergencyAssessment with detailed analysis
        """
        message_lower = message.lower()
        detected_keywords = []
        categories = set()
        urgency_scores = []
        emergency_levels = []
        
        # Check for emergency keywords and aliases
        for keyword_obj in self.emergency_keywords:
            # Check main keyword
            if keyword_obj.keyword in message_lower:
                detected_keywords.append(keyword_obj.keyword)
                categories.add(keyword_obj.category)
                urgency_scores.append(keyword_obj.urgency_score)
                emergency_levels.append(keyword_obj.emergency_level)
            
            # Check aliases
            for alias in keyword_obj.aliases:
                if alias in message_lower:
                    detected_keywords.append(alias)
                    categories.add(keyword_obj.category)
                    urgency_scores.append(keyword_obj.urgency_score)
                    emergency_levels.append(keyword_obj.emergency_level)
        
        # Calculate base urgency score
        base_urgency = max(urgency_scores) if urgency_scores else 0
        
        # Apply urgency modifiers
        modified_urgency = self._apply_urgency_modifiers(message_lower, base_urgency)
        
        # Apply context analysis
        context_urgency = self._analyze_context(message_lower, context)
        
        # Final urgency score (1-10 scale)
        final_urgency = min(10, max(1, modified_urgency + context_urgency))
        
        # Determine emergency level
        emergency_level = self._determine_emergency_level(final_urgency, emergency_levels)
        
        # Determine if this is an emergency
        is_emergency = final_urgency >= 6 or emergency_level in [EmergencyLevel.HIGH, EmergencyLevel.CRITICAL]
        
        # Calculate confidence based on keyword matches and context
        confidence = self._calculate_confidence(detected_keywords, message_lower, context)
        
        # Generate recommendations and emergency response
        recommendations = self._generate_recommendations(emergency_level, list(categories), final_urgency)
        emergency_response = self._generate_emergency_response(emergency_level, list(categories), detected_keywords)
        
        # Log emergency detection
        if is_emergency:
            self._log_emergency_detection(message, final_urgency, emergency_level, detected_keywords)
        
        return EmergencyAssessment(
            is_emergency=is_emergency,
            urgency_score=final_urgency,
            emergency_level=emergency_level,
            detected_keywords=detected_keywords,
            categories=list(categories),
            confidence=confidence,
            recommendations=recommendations,
            emergency_response=emergency_response,
            metadata={
                "base_urgency": base_urgency,
                "modified_urgency": modified_urgency,
                "context_urgency": context_urgency,
                "keyword_count": len(detected_keywords),
                "message_length": len(message)
            }
        )
    
    def _apply_urgency_modifiers(self, message_lower: str, base_urgency: int) -> int:
        """Apply urgency modifiers based on intensity and temporal words"""
        modifier_score = 0
        
        for modifier, score_change in self.urgency_modifiers.items():
            if modifier in message_lower:
                modifier_score += score_change
        
        return base_urgency + modifier_score
    
    def _analyze_context(self, message_lower: str, context: Dict[str, Any] = None) -> int:
        """Analyze message context for additional urgency indicators"""
        context_score = 0
        
        # Check for time-based urgency
        for pattern in self.context_patterns["time_indicators"]:
            matches = re.findall(pattern, message_lower)
            if matches:
                # Recent onset increases urgency
                if any(word in message_lower for word in ["minutes", "suddenly", "just started"]):
                    context_score += 1
        
        # Check for severity indicators
        for pattern in self.context_patterns["severity_indicators"]:
            if re.search(pattern, message_lower):
                context_score += 2
        
        # Check for functional impairment
        if any(phrase in message_lower for phrase in ["can't walk", "can't move", "can't function", "collapsed"]):
            context_score += 2
        
        # Check medical history context if available
        if context and context.get("medical_history"):
            history = context["medical_history"].lower()
            # High-risk conditions increase urgency
            if any(condition in history for condition in ["heart disease", "diabetes", "hypertension", "asthma"]):
                context_score += 1
        
        return context_score
    
    def _determine_emergency_level(self, urgency_score: int, detected_levels: List[EmergencyLevel]) -> EmergencyLevel:
        """Determine overall emergency level"""
        if EmergencyLevel.CRITICAL in detected_levels or urgency_score >= 9:
            return EmergencyLevel.CRITICAL
        elif EmergencyLevel.HIGH in detected_levels or urgency_score >= 7:
            return EmergencyLevel.HIGH
        elif EmergencyLevel.MODERATE in detected_levels or urgency_score >= 5:
            return EmergencyLevel.MODERATE
        else:
            return EmergencyLevel.LOW
    
    def _calculate_confidence(self, detected_keywords: List[str], message: str, context: Dict[str, Any] = None) -> float:
        """Calculate confidence score for emergency detection"""
        base_confidence = 0.5
        
        # More keywords increase confidence
        keyword_confidence = min(0.3, len(detected_keywords) * 0.1)
        
        # Specific medical terms increase confidence
        medical_terms = ["pain", "symptoms", "doctor", "hospital", "medical", "health"]
        medical_confidence = sum(0.05 for term in medical_terms if term in message) 
        
        # Context availability increases confidence
        context_confidence = 0.1 if context and context.get("medical_history") else 0
        
        return min(1.0, base_confidence + keyword_confidence + medical_confidence + context_confidence)
    
    def _generate_recommendations(self, level: EmergencyLevel, categories: List[SymptomCategory], urgency: int) -> List[str]:
        """Generate specific recommendations based on emergency assessment"""
        recommendations = []
        
        if level == EmergencyLevel.CRITICAL:
            recommendations.extend([
                "Call emergency services immediately (911/999/112)",
                "Do not drive yourself - call an ambulance",
                "If possible, have someone stay with you until help arrives"
            ])
        elif level == EmergencyLevel.HIGH:
            recommendations.extend([
                "Seek immediate medical attention at the nearest emergency room",
                "Contact your healthcare provider immediately",
                "Consider calling emergency services if symptoms worsen"
            ])
        elif level == EmergencyLevel.MODERATE:
            recommendations.extend([
                "Contact your healthcare provider as soon as possible",
                "Visit an urgent care center if your doctor is unavailable",
                "Monitor symptoms closely and seek emergency care if they worsen"
            ])
        else:
            recommendations.extend([
                "Schedule an appointment with your healthcare provider",
                "Monitor symptoms and seek medical attention if they persist or worsen",
                "Consider telehealth consultation for initial assessment"
            ])
        
        # Category-specific recommendations
        if SymptomCategory.CARDIAC in categories:
            recommendations.append("If you have aspirin available and no allergies, consider taking one (consult emergency services)")
        
        if SymptomCategory.RESPIRATORY in categories:
            recommendations.append("Try to stay calm and sit upright to help breathing")
        
        if SymptomCategory.PSYCHIATRIC in categories:
            recommendations.extend([
                "Contact a mental health crisis hotline immediately",
                "Reach out to a trusted friend, family member, or mental health professional",
                "National Suicide Prevention Lifeline: 988 (US)"
            ])
        
        return recommendations
    
    def _generate_emergency_response(self, level: EmergencyLevel, categories: List[SymptomCategory], keywords: List[str]) -> str:
        """Generate appropriate emergency response message"""
        if level == EmergencyLevel.CRITICAL:
            response = "🚨 MEDICAL EMERGENCY DETECTED 🚨\n\n"
            response += "This appears to be a serious medical emergency. Please:\n\n"
            response += "• Call emergency services IMMEDIATELY (911 in US, 999 in UK, 112 in EU)\n"
            response += "• Do NOT drive yourself - call an ambulance\n"
            response += "• If possible, have someone stay with you until help arrives\n"
            response += "• Follow any instructions given by emergency operators\n\n"
            
        elif level == EmergencyLevel.HIGH:
            response = "⚠️ URGENT MEDICAL ATTENTION NEEDED ⚠️\n\n"
            response += "Your symptoms suggest you need immediate medical care. Please:\n\n"
            response += "• Go to the nearest emergency room immediately\n"
            response += "• Contact your healthcare provider right away\n"
            response += "• Call emergency services if symptoms worsen\n"
            response += "• Do not delay seeking medical attention\n\n"
            
        elif level == EmergencyLevel.MODERATE:
            response = "⚡ MEDICAL ATTENTION RECOMMENDED ⚡\n\n"
            response += "Your symptoms warrant prompt medical evaluation. Please:\n\n"
            response += "• Contact your healthcare provider as soon as possible\n"
            response += "• Visit an urgent care center if your doctor is unavailable\n"
            response += "• Monitor symptoms closely\n"
            response += "• Seek emergency care if symptoms worsen\n\n"
            
        else:
            response = "💡 MEDICAL CONSULTATION SUGGESTED 💡\n\n"
            response += "While not immediately urgent, your symptoms should be evaluated. Please:\n\n"
            response += "• Schedule an appointment with your healthcare provider\n"
            response += "• Monitor symptoms and seek care if they persist or worsen\n"
            response += "• Consider a telehealth consultation for initial assessment\n\n"
        
        # Add category-specific guidance
        if SymptomCategory.PSYCHIATRIC in categories:
            response += "\n🆘 MENTAL HEALTH RESOURCES:\n"
            response += "• National Suicide Prevention Lifeline: 988 (US)\n"
            response += "• Crisis Text Line: Text HOME to 741741\n"
            response += "• International Association for Suicide Prevention: https://www.iasp.info/resources/Crisis_Centres/\n\n"
        
        response += "⚠️ I'm an AI assistant and cannot provide emergency medical care. "
        response += "This assessment is based on keywords and should not replace professional medical judgment. "
        response += "When in doubt, always seek immediate medical attention."
        
        return response
    
    def _log_emergency_detection(self, message: str, urgency: int, level: EmergencyLevel, keywords: List[str]):
        """Log emergency detection for monitoring and alerting"""
        log_data = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "urgency_score": urgency,
            "emergency_level": level.value,
            "detected_keywords": keywords,
            "message_preview": message[:100] + "..." if len(message) > 100 else message
        }
        
        # Log at appropriate level
        if level == EmergencyLevel.CRITICAL:
            logger.critical(f"CRITICAL EMERGENCY DETECTED: {json.dumps(log_data)}")
        elif level == EmergencyLevel.HIGH:
            logger.error(f"HIGH URGENCY EMERGENCY DETECTED: {json.dumps(log_data)}")
        else:
            logger.warning(f"MODERATE EMERGENCY DETECTED: {json.dumps(log_data)}")
    
    def get_emergency_statistics(self) -> Dict[str, Any]:
        """Get emergency detection statistics (would be implemented with persistent storage)"""
        return {
            "total_keywords": len(self.emergency_keywords),
            "categories": [cat.value for cat in SymptomCategory],
            "emergency_levels": [level.value for level in EmergencyLevel],
            "modifier_count": len(self.urgency_modifiers)
        }


# Global instance
emergency_detector = EmergencyDetector()