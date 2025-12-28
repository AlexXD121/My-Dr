"""
AI Response Validation and Safety System for MyDoc AI Medical Assistant

This module provides comprehensive validation of AI responses to ensure medical
accuracy, appropriate disclaimers, content filtering, and response quality scoring.
"""

import logging
import re
from datetime import datetime, timezone
from typing import Dict, List, Tuple, Optional, Any, Set
from dataclasses import dataclass, field
from enum import Enum
import json

logger = logging.getLogger(__name__)


class ValidationResult(Enum):
    """Validation result status"""
    PASSED = "passed"
    FAILED = "failed"
    WARNING = "warning"
    MODIFIED = "modified"


class SafetyLevel(Enum):
    """Safety level classification"""
    SAFE = "safe"
    CAUTION = "caution"
    UNSAFE = "unsafe"
    BLOCKED = "blocked"


class ResponseQuality(Enum):
    """Response quality classification"""
    EXCELLENT = "excellent"
    GOOD = "good"
    ACCEPTABLE = "acceptable"
    POOR = "poor"
    UNACCEPTABLE = "unacceptable"


@dataclass
class ValidationIssue:
    """Individual validation issue"""
    issue_type: str
    severity: str
    description: str
    suggestion: Optional[str] = None
    auto_fixable: bool = False


@dataclass
class ResponseValidation:
    """Complete response validation result"""
    original_response: str
    validated_response: str
    validation_result: ValidationResult
    safety_level: SafetyLevel
    quality_score: float  # 0.0 - 1.0
    quality_rating: ResponseQuality
    issues: List[ValidationIssue] = field(default_factory=list)
    modifications_made: List[str] = field(default_factory=list)
    disclaimer_added: bool = False
    content_filtered: bool = False
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    metadata: Dict[str, Any] = field(default_factory=dict)


class AIResponseValidator:
    """
    Comprehensive AI response validation system with medical safety checks,
    content filtering, quality scoring, and automatic disclaimer injection.
    """
    
    def __init__(self):
        self.medical_disclaimers = self._initialize_medical_disclaimers()
        self.prohibited_content = self._initialize_prohibited_content()
        self.required_disclaimers = self._initialize_required_disclaimers()
        self.quality_indicators = self._initialize_quality_indicators()
        self.medical_terms = self._initialize_medical_terms()
        
    def _initialize_medical_disclaimers(self) -> List[str]:
        """Initialize medical disclaimer templates"""
        return [
            "⚠️ Please remember: This information is for educational purposes only and should not replace professional medical advice. Always consult with a healthcare provider for proper diagnosis and treatment.",
            "⚠️ Important: This is general medical information and should not be used as a substitute for professional medical advice, diagnosis, or treatment. Please consult with a qualified healthcare provider.",
            "⚠️ Medical Disclaimer: The information provided is for educational purposes only. Always seek the advice of your physician or other qualified healthcare provider with any questions about your medical condition.",
            "⚠️ Please note: This information is not intended to replace professional medical advice. For accurate diagnosis and treatment, please consult with a healthcare professional.",
            "⚠️ Reminder: This is general health information only. For personalized medical advice, diagnosis, or treatment, please consult with your healthcare provider."
        ]
    
    def _initialize_prohibited_content(self) -> Dict[str, List[str]]:
        """Initialize prohibited content patterns"""
        return {
            "specific_diagnoses": [
                r"you have\s+(?:a\s+)?(?:definite|certain|clear)\s+(?:case\s+of\s+)?(\w+)",
                r"you\s+(?:definitely|certainly|clearly)\s+have\s+(\w+)",
                r"this\s+is\s+(?:definitely|certainly|clearly)\s+(\w+)",
                r"you\s+are\s+diagnosed\s+with\s+(\w+)"
            ],
            "medication_prescriptions": [
                r"take\s+(\d+(?:\.\d+)?)\s*(?:mg|g|ml|tablets?|pills?|capsules?)\s+of\s+(\w+)",
                r"I\s+(?:prescribe|recommend\s+taking)\s+(\w+)",
                r"you\s+should\s+take\s+(\w+)\s+(?:medication|drug|pill)",
                r"start\s+(?:taking\s+)?(\w+)\s+(?:immediately|right\s+away|now)"
            ],
            "dangerous_advice": [
                r"don't\s+(?:go\s+to\s+the\s+)?(?:doctor|hospital|emergency)",
                r"avoid\s+(?:seeing\s+a\s+)?(?:doctor|physician|healthcare\s+provider)",
                r"you\s+don't\s+need\s+(?:medical\s+)?(?:attention|care|help)",
                r"this\s+is\s+not\s+serious",
                r"ignore\s+(?:this\s+)?(?:symptom|pain|problem)"
            ],
            "emergency_dismissal": [
                r"this\s+is\s+not\s+an\s+emergency",
                r"no\s+need\s+to\s+worry",
                r"don't\s+call\s+(?:911|999|112|emergency)",
                r"you'll\s+be\s+fine"
            ],
            "inappropriate_reassurance": [
                r"everything\s+will\s+be\s+(?:fine|okay|alright)",
                r"don't\s+worry\s+about\s+it",
                r"it's\s+probably\s+nothing",
                r"you're\s+overreacting"
            ]
        }
    
    def _initialize_required_disclaimers(self) -> Dict[str, List[str]]:
        """Initialize patterns that require specific disclaimers"""
        return {
            "symptom_analysis": [
                r"(?:symptoms?|signs?)\s+(?:suggest|indicate|point\s+to|could\s+be)",
                r"(?:possible|potential|likely)\s+(?:cause|condition|diagnosis)",
                r"this\s+(?:could|might|may)\s+be\s+(?:a\s+sign\s+of|related\s+to)"
            ],
            "medication_discussion": [
                r"(?:medication|drug|medicine|treatment)\s+(?:for|to\s+treat|used\s+for)",
                r"(?:side\s+effects?|adverse\s+reactions?|interactions?)",
                r"(?:dosage|dose|amount)\s+(?:of|for)"
            ],
            "emergency_symptoms": [
                r"(?:emergency|urgent|serious|severe|critical)",
                r"(?:call|contact)\s+(?:911|999|112|emergency|doctor)",
                r"seek\s+(?:immediate|urgent)\s+(?:medical\s+)?(?:attention|care|help)"
            ]
        }
    
    def _initialize_quality_indicators(self) -> Dict[str, Dict[str, List[str]]]:
        """Initialize response quality indicators"""
        return {
            "positive_indicators": {
                "empathy": [
                    "I understand", "I can imagine", "that sounds", "I'm sorry to hear",
                    "it's understandable", "many people experience", "you're not alone"
                ],
                "professional_language": [
                    "healthcare provider", "medical professional", "physician", "doctor",
                    "medical attention", "proper evaluation", "clinical assessment"
                ],
                "evidence_based": [
                    "studies show", "research indicates", "medical literature", "evidence suggests",
                    "clinical trials", "peer-reviewed", "medical guidelines"
                ],
                "appropriate_caution": [
                    "consult with", "seek medical advice", "professional evaluation",
                    "healthcare provider", "medical attention", "proper diagnosis"
                ]
            },
            "negative_indicators": {
                "overconfidence": [
                    "definitely", "certainly", "absolutely", "without a doubt",
                    "I'm sure", "guaranteed", "100% certain"
                ],
                "dismissive": [
                    "just", "only", "simply", "don't worry", "it's nothing",
                    "no big deal", "not serious", "overreacting"
                ],
                "inappropriate_certainty": [
                    "you have", "this is", "you are", "definitely diagnosed",
                    "clear case of", "obvious that"
                ],
                "unprofessional": [
                    "I think you should", "in my opinion", "I believe",
                    "personally", "if I were you"
                ]
            }
        }
    
    def _initialize_medical_terms(self) -> Set[str]:
        """Initialize medical terminology for context detection"""
        return {
            "symptoms", "diagnosis", "treatment", "medication", "prescription", "therapy",
            "condition", "disease", "disorder", "syndrome", "infection", "inflammation",
            "pain", "fever", "nausea", "headache", "fatigue", "dizziness", "shortness",
            "breathing", "chest", "heart", "blood", "pressure", "diabetes", "cancer",
            "surgery", "hospital", "emergency", "urgent", "chronic", "acute", "severe"
        }
    
    def validate_response(
        self, 
        response: str, 
        original_message: str = "", 
        context: Dict[str, Any] = None
    ) -> ResponseValidation:
        """
        Comprehensive validation of AI response
        
        Args:
            response: AI-generated response to validate
            original_message: Original user message for context
            context: Additional context information
            
        Returns:
            ResponseValidation with complete analysis and modifications
        """
        validation = ResponseValidation(
            original_response=response,
            validated_response=response,
            validation_result=ValidationResult.PASSED,  # Will be updated later
            safety_level=SafetyLevel.SAFE,  # Will be updated later
            quality_score=0.5,  # Will be updated later
            quality_rating=ResponseQuality.ACCEPTABLE  # Will be updated later
        )
        
        # Step 1: Content Safety Filtering
        validation = self._filter_prohibited_content(validation)
        
        # Step 2: Medical Disclaimer Validation
        validation = self._validate_medical_disclaimers(validation, original_message)
        
        # Step 3: Response Quality Assessment
        validation = self._assess_response_quality(validation, original_message)
        
        # Step 4: Safety Level Assessment
        validation = self._assess_safety_level(validation)
        
        # Step 5: Final Validation Result
        validation.validation_result = self._determine_validation_result(validation)
        
        # Log validation results
        self._log_validation_results(validation, original_message)
        
        return validation
    
    def _filter_prohibited_content(self, validation: ResponseValidation) -> ResponseValidation:
        """Filter and modify prohibited content"""
        response = validation.validated_response
        modified = False
        
        for category, patterns in self.prohibited_content.items():
            for pattern in patterns:
                matches = re.finditer(pattern, response, re.IGNORECASE)
                for match in matches:
                    issue = ValidationIssue(
                        issue_type=f"prohibited_{category}",
                        severity="high",
                        description=f"Contains prohibited {category.replace('_', ' ')}: {match.group()}",
                        suggestion=self._get_content_replacement(category, match.group()),
                        auto_fixable=True
                    )
                    validation.issues.append(issue)
                    
                    # Apply automatic fix
                    replacement = self._get_content_replacement(category, match.group())
                    if replacement:
                        response = response.replace(match.group(), replacement)
                        modified = True
                        validation.modifications_made.append(f"Replaced prohibited {category}: {match.group()}")
        
        if modified:
            validation.validated_response = response
            validation.content_filtered = True
        
        return validation
    
    def _get_content_replacement(self, category: str, original_text: str) -> str:
        """Get appropriate replacement for prohibited content"""
        replacements = {
            "specific_diagnoses": "this could potentially be related to several conditions. A healthcare provider can provide proper evaluation and diagnosis",
            "medication_prescriptions": "discuss appropriate treatment options with your healthcare provider",
            "dangerous_advice": "it's important to consult with a healthcare provider for proper evaluation",
            "emergency_dismissal": "if you're concerned about your symptoms, it's always best to seek medical advice",
            "inappropriate_reassurance": "while symptoms can vary, it's important to have them properly evaluated by a healthcare professional"
        }
        return replacements.get(category, "please consult with a healthcare provider for proper guidance")
    
    def _validate_medical_disclaimers(self, validation: ResponseValidation, original_message: str) -> ResponseValidation:
        """Validate and add medical disclaimers as needed"""
        response = validation.validated_response.lower()
        
        # Check if response already has a disclaimer
        has_disclaimer = any(
            disclaimer_phrase in response 
            for disclaimer_phrase in [
                "medical advice", "healthcare provider", "consult", "disclaimer",
                "educational purposes", "professional medical", "qualified healthcare"
            ]
        )
        
        # Check if response needs a disclaimer
        needs_disclaimer = False
        disclaimer_type = "general"
        
        for category, patterns in self.required_disclaimers.items():
            for pattern in patterns:
                if re.search(pattern, response, re.IGNORECASE):
                    needs_disclaimer = True
                    disclaimer_type = category
                    break
            if needs_disclaimer:
                break
        
        # Check if response contains medical terms
        if not needs_disclaimer:
            medical_term_count = sum(1 for term in self.medical_terms if term in response)
            if medical_term_count >= 2:
                needs_disclaimer = True
        
        # Add disclaimer if needed and not present
        if needs_disclaimer and not has_disclaimer:
            disclaimer = self._select_appropriate_disclaimer(disclaimer_type)
            validation.validated_response += f"\n\n{disclaimer}"
            validation.disclaimer_added = True
            validation.modifications_made.append("Added medical disclaimer")
        elif needs_disclaimer and has_disclaimer:
            # Verify disclaimer quality
            if not self._validate_disclaimer_quality(validation.validated_response):
                issue = ValidationIssue(
                    issue_type="inadequate_disclaimer",
                    severity="medium",
                    description="Existing disclaimer may be inadequate",
                    suggestion="Consider strengthening the medical disclaimer"
                )
                validation.issues.append(issue)
        
        return validation
    
    def _select_appropriate_disclaimer(self, disclaimer_type: str) -> str:
        """Select appropriate disclaimer based on content type"""
        if disclaimer_type == "emergency_symptoms":
            return ("⚠️ IMPORTANT: If you're experiencing a medical emergency, "
                   "call emergency services immediately. This information is for "
                   "educational purposes only and should not delay emergency care.")
        elif disclaimer_type == "medication_discussion":
            return ("⚠️ Medication Information: This is general information only. "
                   "Never start, stop, or change medications without consulting "
                   "your healthcare provider or pharmacist.")
        else:
            # Use random disclaimer for variety
            import random
            return random.choice(self.medical_disclaimers)
    
    def _validate_disclaimer_quality(self, response: str) -> bool:
        """Validate the quality of existing disclaimers"""
        response_lower = response.lower()
        
        # Check for key disclaimer elements
        has_educational_purpose = any(phrase in response_lower for phrase in [
            "educational purposes", "information only", "general information"
        ])
        
        has_professional_advice = any(phrase in response_lower for phrase in [
            "professional medical advice", "healthcare provider", "qualified healthcare",
            "medical professional", "consult"
        ])
        
        has_no_substitute = any(phrase in response_lower for phrase in [
            "not replace", "should not substitute", "not intended to replace",
            "not a substitute"
        ])
        
        # Quality disclaimer should have at least 2 of these elements
        return sum([has_educational_purpose, has_professional_advice, has_no_substitute]) >= 2
    
    def _assess_response_quality(self, validation: ResponseValidation, original_message: str) -> ResponseValidation:
        """Assess overall response quality"""
        response = validation.validated_response.lower()
        
        # Calculate quality metrics
        empathy_score = self._calculate_empathy_score(response)
        professionalism_score = self._calculate_professionalism_score(response)
        accuracy_score = self._calculate_accuracy_score(response)
        completeness_score = self._calculate_completeness_score(response, original_message)
        
        # Weighted quality score
        quality_score = (
            empathy_score * 0.2 +
            professionalism_score * 0.3 +
            accuracy_score * 0.3 +
            completeness_score * 0.2
        )
        
        validation.quality_score = quality_score
        validation.quality_rating = self._determine_quality_rating(quality_score)
        
        # Add quality-related issues
        if quality_score < 0.6:
            validation.issues.append(ValidationIssue(
                issue_type="low_quality",
                severity="medium",
                description=f"Response quality score is low ({quality_score:.2f})",
                suggestion="Consider improving empathy, professionalism, or completeness"
            ))
        
        return validation
    
    def _calculate_empathy_score(self, response: str) -> float:
        """Calculate empathy score based on language used"""
        empathy_indicators = self.quality_indicators["positive_indicators"]["empathy"]
        dismissive_indicators = self.quality_indicators["negative_indicators"]["dismissive"]
        
        empathy_count = sum(1 for indicator in empathy_indicators if indicator in response)
        dismissive_count = sum(1 for indicator in dismissive_indicators if indicator in response)
        
        # Base score with bonus for empathy, penalty for dismissiveness
        base_score = 0.5
        empathy_bonus = min(0.4, empathy_count * 0.1)
        dismissive_penalty = min(0.3, dismissive_count * 0.1)
        
        return max(0.0, min(1.0, base_score + empathy_bonus - dismissive_penalty))
    
    def _calculate_professionalism_score(self, response: str) -> float:
        """Calculate professionalism score"""
        professional_indicators = self.quality_indicators["positive_indicators"]["professional_language"]
        unprofessional_indicators = self.quality_indicators["negative_indicators"]["unprofessional"]
        
        professional_count = sum(1 for indicator in professional_indicators if indicator in response)
        unprofessional_count = sum(1 for indicator in unprofessional_indicators if indicator in response)
        
        base_score = 0.6
        professional_bonus = min(0.3, professional_count * 0.1)
        unprofessional_penalty = min(0.4, unprofessional_count * 0.15)
        
        return max(0.0, min(1.0, base_score + professional_bonus - unprofessional_penalty))
    
    def _calculate_accuracy_score(self, response: str) -> float:
        """Calculate accuracy score based on appropriate caution and evidence"""
        evidence_indicators = self.quality_indicators["positive_indicators"]["evidence_based"]
        overconfident_indicators = self.quality_indicators["negative_indicators"]["overconfidence"]
        caution_indicators = self.quality_indicators["positive_indicators"]["appropriate_caution"]
        
        evidence_count = sum(1 for indicator in evidence_indicators if indicator in response)
        overconfident_count = sum(1 for indicator in overconfident_indicators if indicator in response)
        caution_count = sum(1 for indicator in caution_indicators if indicator in response)
        
        base_score = 0.7
        evidence_bonus = min(0.2, evidence_count * 0.1)
        caution_bonus = min(0.2, caution_count * 0.05)
        overconfident_penalty = min(0.5, overconfident_count * 0.2)
        
        return max(0.0, min(1.0, base_score + evidence_bonus + caution_bonus - overconfident_penalty))
    
    def _calculate_completeness_score(self, response: str, original_message: str) -> float:
        """Calculate completeness score based on response length and content"""
        # Basic completeness metrics
        word_count = len(response.split())
        
        # Optimal length is 50-300 words for medical responses
        if word_count < 20:
            length_score = 0.3
        elif word_count < 50:
            length_score = 0.6
        elif word_count <= 300:
            length_score = 1.0
        elif word_count <= 500:
            length_score = 0.8
        else:
            length_score = 0.6  # Too long
        
        # Check for key components
        has_explanation = len([word for word in response.split() if word.lower() in self.medical_terms]) >= 2
        has_recommendations = any(word in response.lower() for word in ["recommend", "suggest", "consider", "should"])
        has_next_steps = any(phrase in response.lower() for phrase in ["next step", "follow up", "contact", "see"])
        
        component_score = (has_explanation + has_recommendations + has_next_steps) / 3
        
        return (length_score * 0.6 + component_score * 0.4)
    
    def _determine_quality_rating(self, quality_score: float) -> ResponseQuality:
        """Determine quality rating from score"""
        if quality_score >= 0.9:
            return ResponseQuality.EXCELLENT
        elif quality_score >= 0.75:
            return ResponseQuality.GOOD
        elif quality_score >= 0.6:
            return ResponseQuality.ACCEPTABLE
        elif quality_score >= 0.4:
            return ResponseQuality.POOR
        else:
            return ResponseQuality.UNACCEPTABLE
    
    def _assess_safety_level(self, validation: ResponseValidation) -> ResponseValidation:
        """Assess overall safety level of the response"""
        high_severity_issues = [issue for issue in validation.issues if issue.severity == "high"]
        medium_severity_issues = [issue for issue in validation.issues if issue.severity == "medium"]
        
        if high_severity_issues:
            if any("prohibited" in issue.issue_type for issue in high_severity_issues):
                validation.safety_level = SafetyLevel.BLOCKED if not validation.content_filtered else SafetyLevel.UNSAFE
            else:
                validation.safety_level = SafetyLevel.UNSAFE
        elif medium_severity_issues or validation.quality_rating == ResponseQuality.UNACCEPTABLE:
            validation.safety_level = SafetyLevel.CAUTION
        else:
            validation.safety_level = SafetyLevel.SAFE
        
        return validation
    
    def _determine_validation_result(self, validation: ResponseValidation) -> ValidationResult:
        """Determine overall validation result"""
        if validation.safety_level == SafetyLevel.BLOCKED:
            return ValidationResult.FAILED
        elif validation.content_filtered or validation.disclaimer_added:
            return ValidationResult.MODIFIED
        elif validation.issues and any(issue.severity == "high" for issue in validation.issues):
            return ValidationResult.WARNING
        else:
            return ValidationResult.PASSED
    
    def _log_validation_results(self, validation: ResponseValidation, original_message: str):
        """Log validation results for monitoring"""
        log_data = {
            "timestamp": validation.timestamp.isoformat(),
            "validation_result": validation.validation_result.value,
            "safety_level": validation.safety_level.value,
            "quality_score": validation.quality_score,
            "quality_rating": validation.quality_rating.value,
            "issues_count": len(validation.issues),
            "modifications_made": len(validation.modifications_made),
            "disclaimer_added": validation.disclaimer_added,
            "content_filtered": validation.content_filtered
        }
        
        if validation.validation_result == ValidationResult.FAILED:
            logger.error(f"AI Response Validation FAILED: {json.dumps(log_data)}")
        elif validation.validation_result == ValidationResult.WARNING:
            logger.warning(f"AI Response Validation WARNING: {json.dumps(log_data)}")
        elif validation.validation_result == ValidationResult.MODIFIED:
            logger.info(f"AI Response Validation MODIFIED: {json.dumps(log_data)}")
        else:
            logger.debug(f"AI Response Validation PASSED: {json.dumps(log_data)}")


# Global instance
ai_response_validator = AIResponseValidator()