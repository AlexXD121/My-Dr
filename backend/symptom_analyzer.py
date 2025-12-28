"""
Symptom Analysis Engine for MyDoc AI Medical Assistant

This module provides comprehensive symptom analysis capabilities including:
- Symptom severity scoring (1-10 scale)
- Medical condition suggestions with confidence scoring
- Urgency assessment and recommendation generation
- Medical knowledge base integration
"""

import re
import json
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)


class UrgencyLevel(Enum):
    """Urgency levels for medical situations"""
    ROUTINE = "routine"
    MODERATE = "moderate"
    URGENT = "urgent"
    EMERGENCY = "emergency"
    CRITICAL = "critical"


class SeverityLevel(Enum):
    """Severity levels for symptoms"""
    MILD = "mild"
    MODERATE = "moderate"
    SEVERE = "severe"
    CRITICAL = "critical"


@dataclass
class SymptomInput:
    """Input data structure for symptom analysis"""
    symptoms: List[str]
    duration: Optional[str] = None
    severity_self_rating: Optional[int] = None  # 1-10 user self-rating
    location: Optional[str] = None
    triggers: List[str] = field(default_factory=list)
    alleviating_factors: List[str] = field(default_factory=list)
    associated_symptoms: List[str] = field(default_factory=list)
    medical_history: List[str] = field(default_factory=list)
    current_medications: List[str] = field(default_factory=list)
    age: Optional[int] = None
    gender: Optional[str] = None


@dataclass
class ConditionSuggestion:
    """Medical condition suggestion with confidence"""
    condition_name: str
    confidence_score: float  # 0.0 to 1.0
    description: str
    common_symptoms: List[str]
    severity_indicators: List[str]
    recommended_actions: List[str]


@dataclass
class SymptomAnalysis:
    """Complete symptom analysis result"""
    urgency_score: int  # 1-10 scale
    urgency_level: UrgencyLevel
    severity_level: SeverityLevel
    primary_symptoms: List[str]
    red_flags: List[str]
    possible_conditions: List[ConditionSuggestion]
    recommendations: List[str]
    follow_up_questions: List[str]
    emergency_indicators: List[str]
    confidence_score: float
    analysis_timestamp: datetime
    requires_immediate_attention: bool


class SymptomAnalyzer:
    """Advanced symptom analysis engine with medical knowledge base"""
    
    def __init__(self):
        """Initialize the symptom analyzer with medical knowledge base"""
        self.emergency_keywords = self._load_emergency_keywords()
        self.symptom_patterns = self._load_symptom_patterns()
        self.condition_database = self._load_condition_database()
        self.red_flag_indicators = self._load_red_flag_indicators()
        
    def _load_emergency_keywords(self) -> Dict[str, int]:
        """Load emergency keywords with urgency scores"""
        return {
            # Critical emergency indicators (9-10)
            "chest pain": 10,
            "difficulty breathing": 10,
            "shortness of breath": 9,
            "severe chest pain": 10,
            "heart attack": 10,
            "stroke": 10,
            "severe bleeding": 10,
            "unconscious": 10,
            "not breathing": 10,
            "severe head injury": 10,
            "severe burns": 10,
            "poisoning": 10,
            "overdose": 10,
            "severe allergic reaction": 10,
            "anaphylaxis": 10,
            "severe abdominal pain": 9,
            "sudden severe headache": 9,
            "loss of consciousness": 10,
            "seizure": 9,
            "severe vomiting blood": 10,
            "coughing up blood": 9,
            
            # High urgency indicators (7-8)
            "severe pain": 8,
            "high fever": 7,
            "persistent vomiting": 7,
            "severe diarrhea": 7,
            "dehydration": 7,
            "confusion": 8,
            "disorientation": 8,
            "severe dizziness": 7,
            "fainting": 8,
            "rapid heartbeat": 7,
            "irregular heartbeat": 8,
            "severe headache": 7,
            "blurred vision": 7,
            "sudden vision loss": 9,
            "severe nausea": 6,
            "persistent fever": 7,
            
            # Moderate urgency indicators (5-6)
            "moderate pain": 5,
            "fever": 5,
            "headache": 4,
            "nausea": 4,
            "vomiting": 5,
            "diarrhea": 4,
            "dizziness": 5,
            "fatigue": 3,
            "weakness": 4,
            "joint pain": 4,
            "muscle pain": 3,
            "back pain": 4,
            "stomach pain": 5,
            "sore throat": 3,
            "cough": 3,
            "runny nose": 2,
            "congestion": 2,
        }
    
    def _load_symptom_patterns(self) -> Dict[str, Dict]:
        """Load symptom patterns for analysis"""
        return {
            "cardiovascular": {
                "keywords": ["chest pain", "heart", "palpitations", "shortness of breath", "dizziness", "fainting"],
                "urgency_modifier": 2.0,
                "red_flags": ["severe chest pain", "crushing chest pain", "radiating pain", "sweating with chest pain"]
            },
            "respiratory": {
                "keywords": ["breathing", "cough", "wheeze", "shortness of breath", "chest tightness"],
                "urgency_modifier": 1.5,
                "red_flags": ["severe difficulty breathing", "blue lips", "gasping for air"]
            },
            "neurological": {
                "keywords": ["headache", "dizziness", "confusion", "seizure", "weakness", "numbness"],
                "urgency_modifier": 1.8,
                "red_flags": ["sudden severe headache", "loss of consciousness", "paralysis", "speech problems"]
            },
            "gastrointestinal": {
                "keywords": ["nausea", "vomiting", "diarrhea", "abdominal pain", "stomach"],
                "urgency_modifier": 1.2,
                "red_flags": ["severe abdominal pain", "vomiting blood", "black stools", "severe dehydration"]
            },
            "infectious": {
                "keywords": ["fever", "chills", "sweats", "fatigue", "weakness"],
                "urgency_modifier": 1.3,
                "red_flags": ["high fever", "persistent fever", "severe fatigue", "confusion with fever"]
            }
        }
    
    def _load_condition_database(self) -> Dict[str, Dict]:
        """Load medical condition database"""
        return {
            "myocardial_infarction": {
                "name": "Heart Attack (Myocardial Infarction)",
                "symptoms": ["chest pain", "shortness of breath", "sweating", "nausea", "arm pain"],
                "urgency": 10,
                "description": "A serious condition where blood flow to the heart is blocked",
                "red_flags": ["severe crushing chest pain", "pain radiating to arm/jaw", "cold sweats"],
                "actions": ["Call emergency services immediately", "Take aspirin if not allergic", "Rest and stay calm"]
            },
            "stroke": {
                "name": "Stroke",
                "symptoms": ["sudden weakness", "speech problems", "facial drooping", "confusion", "severe headache"],
                "urgency": 10,
                "description": "A medical emergency where blood flow to the brain is interrupted",
                "red_flags": ["sudden onset", "facial asymmetry", "slurred speech", "arm weakness"],
                "actions": ["Call emergency services immediately", "Note time of symptom onset", "Do not give food or water"]
            },
            "pneumonia": {
                "name": "Pneumonia",
                "symptoms": ["cough", "fever", "shortness of breath", "chest pain", "fatigue"],
                "urgency": 6,
                "description": "Infection that inflames air sacs in one or both lungs",
                "red_flags": ["high fever", "severe breathing difficulty", "chest pain with breathing"],
                "actions": ["See healthcare provider", "Rest and hydration", "Monitor symptoms"]
            },
            "gastroenteritis": {
                "name": "Gastroenteritis",
                "symptoms": ["nausea", "vomiting", "diarrhea", "abdominal pain", "fever"],
                "urgency": 4,
                "description": "Inflammation of the stomach and intestines",
                "red_flags": ["severe dehydration", "blood in vomit/stool", "high fever"],
                "actions": ["Stay hydrated", "Rest", "Bland diet", "Monitor for dehydration"]
            },
            "migraine": {
                "name": "Migraine Headache",
                "symptoms": ["severe headache", "nausea", "sensitivity to light", "visual disturbances"],
                "urgency": 5,
                "description": "A type of headache with severe throbbing pain",
                "red_flags": ["sudden onset", "worst headache ever", "fever with headache"],
                "actions": ["Rest in dark room", "Apply cold compress", "Take prescribed medication"]
            },
            "anxiety_attack": {
                "name": "Anxiety/Panic Attack",
                "symptoms": ["rapid heartbeat", "sweating", "trembling", "shortness of breath", "chest tightness"],
                "urgency": 5,
                "description": "Sudden episode of intense fear or anxiety",
                "red_flags": ["persistent chest pain", "severe breathing difficulty", "loss of consciousness"],
                "actions": ["Practice deep breathing", "Find calm environment", "Use coping techniques"]
            }
        }
    
    def _load_red_flag_indicators(self) -> List[str]:
        """Load red flag indicators that require immediate attention"""
        return [
            "sudden onset of severe symptoms",
            "loss of consciousness",
            "severe difficulty breathing",
            "chest pain with sweating",
            "severe bleeding",
            "signs of stroke (FAST)",
            "high fever with confusion",
            "severe abdominal pain",
            "vomiting blood",
            "severe allergic reaction",
            "poisoning or overdose",
            "severe burns",
            "severe head injury",
            "seizure activity",
            "sudden vision loss",
            "severe dehydration"
        ]
    
    def analyze_symptoms(self, symptom_input: SymptomInput) -> SymptomAnalysis:
        """
        Perform comprehensive symptom analysis
        
        Args:
            symptom_input: SymptomInput object containing symptom information
            
        Returns:
            SymptomAnalysis object with complete analysis results
        """
        try:
            # Calculate urgency score
            urgency_score = self._calculate_urgency_score(symptom_input)
            
            # Determine urgency level
            urgency_level = self._determine_urgency_level(urgency_score)
            
            # Determine severity level
            severity_level = self._determine_severity_level(symptom_input, urgency_score)
            
            # Identify red flags
            red_flags = self._identify_red_flags(symptom_input)
            
            # Generate condition suggestions
            possible_conditions = self._suggest_conditions(symptom_input, urgency_score)
            
            # Generate recommendations
            recommendations = self._generate_recommendations(symptom_input, urgency_score, urgency_level)
            
            # Generate follow-up questions
            follow_up_questions = self._generate_follow_up_questions(symptom_input)
            
            # Identify emergency indicators
            emergency_indicators = self._identify_emergency_indicators(symptom_input)
            
            # Calculate overall confidence
            confidence_score = self._calculate_confidence_score(symptom_input, possible_conditions)
            
            # Determine if immediate attention is required
            requires_immediate_attention = urgency_score >= 8 or len(red_flags) > 0
            
            return SymptomAnalysis(
                urgency_score=urgency_score,
                urgency_level=urgency_level,
                severity_level=severity_level,
                primary_symptoms=symptom_input.symptoms[:3],  # Top 3 symptoms
                red_flags=red_flags,
                possible_conditions=possible_conditions,
                recommendations=recommendations,
                follow_up_questions=follow_up_questions,
                emergency_indicators=emergency_indicators,
                confidence_score=confidence_score,
                analysis_timestamp=datetime.utcnow(),
                requires_immediate_attention=requires_immediate_attention
            )
            
        except Exception as e:
            logger.error(f"Error in symptom analysis: {e}")
            # Return safe default analysis
            return self._create_safe_default_analysis(symptom_input)
    
    def _calculate_urgency_score(self, symptom_input: SymptomInput) -> int:
        """Calculate urgency score from 1-10 based on symptoms"""
        base_score = 1
        max_keyword_score = 0
        
        # Check each symptom against emergency keywords
        for symptom in symptom_input.symptoms:
            symptom_lower = symptom.lower().strip()
            
            # Direct keyword match
            for keyword, score in self.emergency_keywords.items():
                if keyword in symptom_lower:
                    max_keyword_score = max(max_keyword_score, score)
            
            # Pattern matching for symptom categories
            for category, pattern_data in self.symptom_patterns.items():
                for keyword in pattern_data["keywords"]:
                    if keyword in symptom_lower:
                        category_score = int(5 * pattern_data["urgency_modifier"])
                        max_keyword_score = max(max_keyword_score, category_score)
        
        base_score = max(base_score, max_keyword_score)
        
        # Adjust based on user self-rating
        if symptom_input.severity_self_rating:
            if symptom_input.severity_self_rating >= 8:
                base_score = max(base_score, 7)
            elif symptom_input.severity_self_rating >= 6:
                base_score = max(base_score, 5)
        
        # Adjust based on duration
        if symptom_input.duration:
            duration_lower = symptom_input.duration.lower()
            if any(word in duration_lower for word in ["sudden", "acute", "immediate"]):
                base_score += 2
            elif any(word in duration_lower for word in ["chronic", "ongoing", "months"]):
                base_score = max(1, base_score - 1)
        
        # Adjust based on associated symptoms
        if len(symptom_input.associated_symptoms) >= 3:
            base_score += 1
        
        # Cap at 10
        return min(10, base_score)
    
    def _determine_urgency_level(self, urgency_score: int) -> UrgencyLevel:
        """Determine urgency level based on score"""
        if urgency_score >= 9:
            return UrgencyLevel.CRITICAL
        elif urgency_score >= 7:
            return UrgencyLevel.EMERGENCY
        elif urgency_score >= 5:
            return UrgencyLevel.URGENT
        elif urgency_score >= 3:
            return UrgencyLevel.MODERATE
        else:
            return UrgencyLevel.ROUTINE
    
    def _determine_severity_level(self, symptom_input: SymptomInput, urgency_score: int) -> SeverityLevel:
        """Determine severity level based on symptoms and urgency"""
        if urgency_score >= 9:
            return SeverityLevel.CRITICAL
        elif urgency_score >= 7:
            return SeverityLevel.SEVERE
        elif urgency_score >= 4 or (symptom_input.severity_self_rating and symptom_input.severity_self_rating >= 6):
            return SeverityLevel.MODERATE
        else:
            return SeverityLevel.MILD
    
    def _identify_red_flags(self, symptom_input: SymptomInput) -> List[str]:
        """Identify red flag indicators in symptoms"""
        red_flags = []
        
        for symptom in symptom_input.symptoms + symptom_input.associated_symptoms:
            symptom_lower = symptom.lower().strip()
            
            # Check against red flag patterns
            for category, pattern_data in self.symptom_patterns.items():
                for red_flag in pattern_data.get("red_flags", []):
                    if red_flag.lower() in symptom_lower:
                        red_flags.append(red_flag)
            
            # Check against general red flag indicators
            for indicator in self.red_flag_indicators:
                if any(word in symptom_lower for word in indicator.lower().split()):
                    red_flags.append(indicator)
        
        return list(set(red_flags))  # Remove duplicates
    
    def _suggest_conditions(self, symptom_input: SymptomInput, urgency_score: int) -> List[ConditionSuggestion]:
        """Suggest possible medical conditions based on symptoms"""
        suggestions = []
        
        for condition_id, condition_data in self.condition_database.items():
            # Calculate match score
            symptom_matches = 0
            total_condition_symptoms = len(condition_data["symptoms"])
            
            for symptom in symptom_input.symptoms:
                symptom_lower = symptom.lower().strip()
                for condition_symptom in condition_data["symptoms"]:
                    if condition_symptom.lower() in symptom_lower or symptom_lower in condition_symptom.lower():
                        symptom_matches += 1
                        break
            
            if symptom_matches > 0:
                # Calculate confidence score
                confidence = symptom_matches / max(len(symptom_input.symptoms), total_condition_symptoms)
                
                # Adjust confidence based on urgency match
                urgency_diff = abs(condition_data["urgency"] - urgency_score)
                if urgency_diff <= 2:
                    confidence += 0.2
                elif urgency_diff <= 4:
                    confidence += 0.1
                
                # Cap confidence at 0.95 (never 100% certain)
                confidence = min(0.95, confidence)
                
                if confidence >= 0.2:  # Only include if reasonable match
                    suggestion = ConditionSuggestion(
                        condition_name=condition_data["name"],
                        confidence_score=confidence,
                        description=condition_data["description"],
                        common_symptoms=condition_data["symptoms"],
                        severity_indicators=condition_data.get("red_flags", []),
                        recommended_actions=condition_data.get("actions", [])
                    )
                    suggestions.append(suggestion)
        
        # Sort by confidence score
        suggestions.sort(key=lambda x: x.confidence_score, reverse=True)
        
        # Return top 5 suggestions
        return suggestions[:5]
    
    def _generate_recommendations(self, symptom_input: SymptomInput, urgency_score: int, urgency_level: UrgencyLevel) -> List[str]:
        """Generate specific recommendations based on analysis"""
        recommendations = []
        
        # Emergency recommendations
        if urgency_level in [UrgencyLevel.CRITICAL, UrgencyLevel.EMERGENCY]:
            recommendations.extend([
                "🚨 Seek immediate emergency medical attention",
                "Call emergency services (911) or go to the nearest emergency room",
                "Do not drive yourself - have someone else drive or call an ambulance",
                "If symptoms worsen, call emergency services immediately"
            ])
        elif urgency_level == UrgencyLevel.URGENT:
            recommendations.extend([
                "⚠️ Seek medical attention within the next few hours",
                "Contact your healthcare provider or visit urgent care",
                "Monitor symptoms closely and seek emergency care if they worsen",
                "Do not delay medical evaluation"
            ])
        elif urgency_level == UrgencyLevel.MODERATE:
            recommendations.extend([
                "📞 Schedule an appointment with your healthcare provider within 1-2 days",
                "Monitor your symptoms and keep a symptom diary",
                "Rest and stay hydrated",
                "Seek immediate care if symptoms worsen significantly"
            ])
        else:  # ROUTINE
            recommendations.extend([
                "💡 Consider scheduling a routine appointment with your healthcare provider",
                "Monitor symptoms and note any changes",
                "Practice self-care measures appropriate for your symptoms",
                "Seek medical attention if symptoms persist or worsen"
            ])
        
        # Symptom-specific recommendations
        symptom_text = " ".join(symptom_input.symptoms).lower()
        
        if "fever" in symptom_text:
            recommendations.append("🌡️ Monitor temperature regularly and stay hydrated")
        
        if "pain" in symptom_text:
            recommendations.append("💊 Consider appropriate over-the-counter pain relief if not contraindicated")
        
        if "cough" in symptom_text or "cold" in symptom_text:
            recommendations.append("🍯 Rest, stay hydrated, and consider throat lozenges or warm liquids")
        
        if "nausea" in symptom_text or "vomiting" in symptom_text:
            recommendations.append("🥤 Stay hydrated with small, frequent sips of clear fluids")
        
        # General health recommendations
        recommendations.extend([
            "📝 Keep a record of your symptoms, including when they started and any triggers",
            "💊 Review your current medications with a healthcare provider",
            "🏥 Always seek immediate medical attention if you feel your condition is worsening"
        ])
        
        return recommendations
    
    def _generate_follow_up_questions(self, symptom_input: SymptomInput) -> List[str]:
        """Generate follow-up questions for more detailed analysis"""
        questions = []
        
        # Duration-based questions
        if not symptom_input.duration:
            questions.append("How long have you been experiencing these symptoms?")
        
        # Severity questions
        if not symptom_input.severity_self_rating:
            questions.append("On a scale of 1-10, how would you rate the severity of your symptoms?")
        
        # Location questions
        if not symptom_input.location and any(word in " ".join(symptom_input.symptoms).lower() for word in ["pain", "ache", "hurt"]):
            questions.append("Can you describe the exact location of your pain or discomfort?")
        
        # Trigger questions
        if not symptom_input.triggers:
            questions.append("Have you noticed anything that triggers or worsens your symptoms?")
        
        # Medical history questions
        if not symptom_input.medical_history:
            questions.append("Do you have any relevant medical history or chronic conditions?")
        
        # Medication questions
        if not symptom_input.current_medications:
            questions.append("Are you currently taking any medications or supplements?")
        
        # Symptom-specific questions
        symptom_text = " ".join(symptom_input.symptoms).lower()
        
        if "chest pain" in symptom_text:
            questions.extend([
                "Does the chest pain radiate to your arm, jaw, or back?",
                "Is the pain sharp, crushing, or burning?",
                "Does the pain worsen with movement or breathing?"
            ])
        
        if "headache" in symptom_text:
            questions.extend([
                "Is this the worst headache you've ever experienced?",
                "Do you have any visual changes or sensitivity to light?",
                "Is the headache accompanied by neck stiffness?"
            ])
        
        if "shortness of breath" in symptom_text or "breathing" in symptom_text:
            questions.extend([
                "Does the breathing difficulty occur at rest or only with activity?",
                "Do you have any chest tightness or wheezing?",
                "Are your lips or fingernails blue or gray?"
            ])
        
        return questions[:5]  # Limit to 5 questions
    
    def _identify_emergency_indicators(self, symptom_input: SymptomInput) -> List[str]:
        """Identify specific emergency indicators"""
        indicators = []
        
        all_symptoms = symptom_input.symptoms + symptom_input.associated_symptoms
        symptom_text = " ".join(all_symptoms).lower()
        
        # Cardiovascular emergencies
        if any(phrase in symptom_text for phrase in ["chest pain", "heart attack", "crushing pain"]):
            indicators.append("Potential cardiovascular emergency")
        
        # Respiratory emergencies
        if any(phrase in symptom_text for phrase in ["difficulty breathing", "can't breathe", "gasping"]):
            indicators.append("Potential respiratory emergency")
        
        # Neurological emergencies
        if any(phrase in symptom_text for phrase in ["stroke", "paralysis", "speech problems", "confusion"]):
            indicators.append("Potential neurological emergency")
        
        # Severe bleeding
        if any(phrase in symptom_text for phrase in ["severe bleeding", "blood loss", "hemorrhage"]):
            indicators.append("Potential severe bleeding")
        
        # Allergic reactions
        if any(phrase in symptom_text for phrase in ["allergic reaction", "anaphylaxis", "swelling"]):
            indicators.append("Potential severe allergic reaction")
        
        # Poisoning/overdose
        if any(phrase in symptom_text for phrase in ["poisoning", "overdose", "toxic"]):
            indicators.append("Potential poisoning or overdose")
        
        return indicators
    
    def _calculate_confidence_score(self, symptom_input: SymptomInput, possible_conditions: List[ConditionSuggestion]) -> float:
        """Calculate overall confidence in the analysis"""
        base_confidence = 0.5
        
        # Increase confidence based on symptom detail
        if len(symptom_input.symptoms) >= 3:
            base_confidence += 0.1
        
        if symptom_input.duration:
            base_confidence += 0.1
        
        if symptom_input.severity_self_rating:
            base_confidence += 0.1
        
        if symptom_input.medical_history:
            base_confidence += 0.1
        
        # Increase confidence if we have good condition matches
        if possible_conditions and possible_conditions[0].confidence_score > 0.6:
            base_confidence += 0.1
        
        # Decrease confidence for vague symptoms
        vague_symptoms = ["feeling unwell", "not feeling good", "something wrong"]
        if any(vague in " ".join(symptom_input.symptoms).lower() for vague in vague_symptoms):
            base_confidence -= 0.2
        
        return min(0.95, max(0.2, base_confidence))
    
    def _create_safe_default_analysis(self, symptom_input: SymptomInput) -> SymptomAnalysis:
        """Create a safe default analysis when errors occur"""
        return SymptomAnalysis(
            urgency_score=5,
            urgency_level=UrgencyLevel.MODERATE,
            severity_level=SeverityLevel.MODERATE,
            primary_symptoms=symptom_input.symptoms[:3] if symptom_input.symptoms else ["General symptoms"],
            red_flags=[],
            possible_conditions=[],
            recommendations=[
                "⚠️ Please consult with a healthcare provider for proper evaluation",
                "Monitor your symptoms and seek immediate care if they worsen",
                "Keep a record of your symptoms and their progression"
            ],
            follow_up_questions=[
                "Can you provide more details about your symptoms?",
                "How long have you been experiencing these symptoms?",
                "Have you noticed any patterns or triggers?"
            ],
            emergency_indicators=[],
            confidence_score=0.3,
            analysis_timestamp=datetime.utcnow(),
            requires_immediate_attention=False
        )


# Utility functions for symptom analysis
def normalize_symptom_text(text: str) -> str:
    """Normalize symptom text for analysis"""
    if not text:
        return ""
    
    # Convert to lowercase
    text = text.lower().strip()
    
    # Remove extra whitespace
    text = re.sub(r'\s+', ' ', text)
    
    # Remove special characters but keep medical terms
    text = re.sub(r'[^\w\s\-/]', ' ', text)
    
    return text


def extract_symptoms_from_text(text: str) -> List[str]:
    """Extract individual symptoms from free text"""
    if not text:
        return []
    
    # Normalize text
    normalized = normalize_symptom_text(text)
    
    # Split on common delimiters
    symptoms = []
    for delimiter in [',', ';', ' and ', ' & ', '\n']:
        if delimiter in normalized:
            parts = normalized.split(delimiter)
            symptoms.extend([part.strip() for part in parts if part.strip()])
            break
    else:
        # No delimiters found, treat as single symptom
        symptoms = [normalized]
    
    # Filter out very short or empty symptoms
    symptoms = [s for s in symptoms if len(s.strip()) > 2]
    
    return symptoms[:10]  # Limit to 10 symptoms


def create_symptom_input_from_text(
    symptom_text: str,
    duration: str = None,
    severity: int = None,
    **kwargs
) -> SymptomInput:
    """Create SymptomInput from text description"""
    symptoms = extract_symptoms_from_text(symptom_text)
    
    return SymptomInput(
        symptoms=symptoms,
        duration=duration,
        severity_self_rating=severity,
        **kwargs
    )