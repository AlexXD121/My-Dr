"""
Enhanced Medical AI Service for MyDoc AI Medical Assistant

This module integrates the AI Service Manager, Emergency Detector, and Response Validator
to provide a comprehensive, safe, and reliable medical AI consultation service.
"""

import logging
import asyncio
from datetime import datetime, timezone
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass, field

from ai_service_manager import ai_service_manager, AIResponse, AIProviderType
from emergency_detector import emergency_detector, EmergencyAssessment, EmergencyLevel
from ai_response_validator import ai_response_validator, ResponseValidation, ValidationResult, SafetyLevel

logger = logging.getLogger(__name__)


@dataclass
class MedicalConsultationRequest:
    """Medical consultation request container"""
    message: str
    user_id: Optional[str] = None
    context: Dict[str, Any] = field(default_factory=dict)
    session_id: Optional[str] = None
    conversation_id: Optional[str] = None


@dataclass
class MedicalConsultationResponse:
    """Comprehensive medical consultation response"""
    response: str
    emergency_assessment: EmergencyAssessment
    validation: ResponseValidation
    ai_metadata: Dict[str, Any]
    consultation_metadata: Dict[str, Any]
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    
    @property
    def is_emergency(self) -> bool:
        """Check if emergency was detected"""
        return self.emergency_assessment.is_emergency
    
    @property
    def is_safe(self) -> bool:
        """Check if response passed safety validation"""
        return self.validation.safety_level in [SafetyLevel.SAFE, SafetyLevel.CAUTION]
    
    @property
    def needs_human_review(self) -> bool:
        """Check if response needs human review"""
        return (
            self.emergency_assessment.emergency_level in [EmergencyLevel.HIGH, EmergencyLevel.CRITICAL] or
            self.validation.safety_level == SafetyLevel.UNSAFE or
            self.validation.validation_result == ValidationResult.FAILED
        )


class EnhancedMedicalAI:
    """
    Enhanced Medical AI service that provides comprehensive medical consultations
    with emergency detection, response validation, and intelligent fallback handling.
    """
    
    def __init__(self):
        self.ai_manager = ai_service_manager
        self.emergency_detector = emergency_detector
        self.response_validator = ai_response_validator
        
    async def medical_consultation(self, request: MedicalConsultationRequest) -> MedicalConsultationResponse:
        """
        Provide comprehensive medical consultation with full safety and validation pipeline
        
        Args:
            request: Medical consultation request
            
        Returns:
            MedicalConsultationResponse with complete analysis and safety checks
        """
        start_time = datetime.now(timezone.utc)
        
        try:
            # Step 1: Emergency Detection
            logger.info(f"Starting medical consultation for user {request.user_id}")
            emergency_assessment = self.emergency_detector.detect_emergency(
                request.message, 
                request.context
            )
            
            # Step 2: Handle Critical Emergencies
            if emergency_assessment.emergency_level == EmergencyLevel.CRITICAL:
                logger.critical(f"CRITICAL EMERGENCY detected for user {request.user_id}")
                return self._handle_critical_emergency(request, emergency_assessment, start_time)
            
            # Step 3: Generate AI Response
            try:
                ai_response = await self.ai_manager.generate_medical_consultation(
                    request.message,
                    request.context
                )
                logger.info(f"AI response generated using {ai_response.provider.value}")
                
            except Exception as e:
                logger.error(f"AI generation failed: {e}")
                # Use emergency response as fallback
                ai_response = AIResponse(
                    content=emergency_assessment.emergency_response,
                    provider=AIProviderType.JAN_AI,  # Fallback provider
                    confidence_score=0.5,
                    metadata={"fallback": True, "error": str(e)}
                )
            
            # Step 4: Response Validation and Safety Checks
            validation = self.response_validator.validate_response(
                ai_response.content,
                request.message,
                request.context
            )
            
            # Step 5: Handle Validation Failures
            if validation.validation_result == ValidationResult.FAILED:
                logger.error(f"Response validation failed for user {request.user_id}")
                return self._handle_validation_failure(request, emergency_assessment, validation, start_time)
            
            # Step 6: Enhance Response for High-Risk Situations
            final_response = validation.validated_response
            if emergency_assessment.urgency_score >= 6:
                final_response = self._enhance_response_for_urgency(
                    final_response, 
                    emergency_assessment
                )
            
            # Step 7: Build Consultation Metadata
            consultation_metadata = self._build_consultation_metadata(
                request, emergency_assessment, validation, ai_response, start_time
            )
            
            # Step 8: Log Consultation
            self._log_consultation(request, emergency_assessment, validation, consultation_metadata)
            
            return MedicalConsultationResponse(
                response=final_response,
                emergency_assessment=emergency_assessment,
                validation=validation,
                ai_metadata={
                    "provider": ai_response.provider.value,
                    "confidence_score": ai_response.confidence_score,
                    "response_time": ai_response.response_time,
                    "metadata": ai_response.metadata
                },
                consultation_metadata=consultation_metadata
            )
            
        except Exception as e:
            logger.error(f"Medical consultation failed for user {request.user_id}: {e}")
            return self._handle_consultation_failure(request, str(e), start_time)
    
    def _handle_critical_emergency(
        self, 
        request: MedicalConsultationRequest, 
        emergency_assessment: EmergencyAssessment,
        start_time: datetime
    ) -> MedicalConsultationResponse:
        """Handle critical emergency situations with immediate response"""
        
        # Use emergency response directly
        emergency_response = emergency_assessment.emergency_response
        
        # Create validation for emergency response using the validator
        validation = self.response_validator.validate_response(
            emergency_response,
            request.message,
            request.context
        )
        
        consultation_metadata = {
            "consultation_type": "critical_emergency",
            "response_time": (datetime.now(timezone.utc) - start_time).total_seconds(),
            "emergency_override": True,
            "ai_bypassed": True
        }
        
        logger.critical(f"Critical emergency response provided for user {request.user_id}")
        
        return MedicalConsultationResponse(
            response=emergency_response,
            emergency_assessment=emergency_assessment,
            validation=validation,
            ai_metadata={
                "provider": "emergency_system",
                "confidence_score": 1.0,
                "response_time": 0.0,
                "metadata": {"emergency_override": True}
            },
            consultation_metadata=consultation_metadata
        )
    
    def _handle_validation_failure(
        self,
        request: MedicalConsultationRequest,
        emergency_assessment: EmergencyAssessment,
        validation: ResponseValidation,
        start_time: datetime
    ) -> MedicalConsultationResponse:
        """Handle cases where response validation fails"""
        
        # Use safe fallback response
        fallback_response = self._get_safe_fallback_response(emergency_assessment.urgency_score)
        
        # Create validation for fallback using the validator
        fallback_validation = self.response_validator.validate_response(
            fallback_response,
            request.message,
            request.context
        )
        
        consultation_metadata = {
            "consultation_type": "validation_failure_fallback",
            "response_time": (datetime.now(timezone.utc) - start_time).total_seconds(),
            "original_validation_failed": True,
            "fallback_used": True
        }
        
        return MedicalConsultationResponse(
            response=fallback_response,
            emergency_assessment=emergency_assessment,
            validation=fallback_validation,
            ai_metadata={
                "provider": "fallback_system",
                "confidence_score": 0.5,
                "response_time": 0.0,
                "metadata": {"validation_failure_fallback": True}
            },
            consultation_metadata=consultation_metadata
        )
    
    def _handle_consultation_failure(
        self,
        request: MedicalConsultationRequest,
        error: str,
        start_time: datetime
    ) -> MedicalConsultationResponse:
        """Handle complete consultation system failure"""
        
        # Emergency fallback response
        fallback_response = (
            "I'm experiencing technical difficulties and cannot provide a proper medical consultation right now. "
            "For any urgent medical concerns, please:\n\n"
            "• Contact your healthcare provider immediately\n"
            "• Call emergency services (911/999/112) if this is an emergency\n"
            "• Visit the nearest urgent care center or emergency room\n"
            "• Try again in a few minutes for non-urgent questions\n\n"
            "⚠️ Please do not delay seeking medical attention if you have serious symptoms. "
            "This system failure should not prevent you from getting the medical care you need."
        )
        
        # Create emergency assessment for system failure
        emergency_assessment = EmergencyAssessment(
            is_emergency=True,  # Treat as emergency due to system failure
            urgency_score=5,
            emergency_level=EmergencyLevel.MODERATE,
            detected_keywords=["system failure"],
            categories=[],
            confidence=1.0,
            recommendations=["Seek medical attention due to system unavailability"],
            emergency_response=fallback_response
        )
        
        # Create validation for fallback using the validator
        validation = self.response_validator.validate_response(
            fallback_response,
            request.message,
            request.context
        )
        
        consultation_metadata = {
            "consultation_type": "system_failure",
            "response_time": (datetime.now(timezone.utc) - start_time).total_seconds(),
            "error": error,
            "fallback_used": True
        }
        
        logger.error(f"Complete consultation failure for user {request.user_id}: {error}")
        
        return MedicalConsultationResponse(
            response=fallback_response,
            emergency_assessment=emergency_assessment,
            validation=validation,
            ai_metadata={
                "provider": "system_failure_fallback",
                "confidence_score": 0.0,
                "response_time": 0.0,
                "metadata": {"system_failure": True, "error": error}
            },
            consultation_metadata=consultation_metadata
        )
    
    def _enhance_response_for_urgency(
        self, 
        response: str, 
        emergency_assessment: EmergencyAssessment
    ) -> str:
        """Enhance response for urgent situations"""
        
        if emergency_assessment.urgency_score >= 8:
            urgency_prefix = (
                f"⚠️ URGENT MEDICAL ATTENTION RECOMMENDED ⚠️\n"
                f"Urgency Level: {emergency_assessment.urgency_score}/10\n\n"
            )
            response = urgency_prefix + response
        elif emergency_assessment.urgency_score >= 6:
            urgency_prefix = (
                f"⚡ Medical Attention Recommended ⚡\n"
                f"Urgency Level: {emergency_assessment.urgency_score}/10\n\n"
            )
            response = urgency_prefix + response
        
        # Add specific recommendations
        if emergency_assessment.recommendations:
            response += "\n\n🔸 Specific Recommendations:\n"
            for i, rec in enumerate(emergency_assessment.recommendations[:3], 1):
                response += f"{i}. {rec}\n"
        
        return response
    
    def _get_safe_fallback_response(self, urgency_score: int) -> str:
        """Get safe fallback response based on urgency"""
        
        if urgency_score >= 8:
            return (
                "I'm unable to provide a proper medical assessment right now due to technical issues. "
                "Given the nature of your symptoms, I strongly recommend:\n\n"
                "• Seek immediate medical attention at the nearest emergency room\n"
                "• Call emergency services (911/999/112) if symptoms are severe\n"
                "• Contact your healthcare provider immediately\n\n"
                "⚠️ Please do not delay seeking medical care. This technical issue should not "
                "prevent you from getting the urgent medical attention you may need."
            )
        elif urgency_score >= 5:
            return (
                "I'm experiencing technical difficulties and cannot provide a complete medical consultation. "
                "For your symptoms, I recommend:\n\n"
                "• Contact your healthcare provider as soon as possible\n"
                "• Visit an urgent care center if your doctor is unavailable\n"
                "• Monitor your symptoms closely\n"
                "• Seek emergency care if symptoms worsen\n\n"
                "⚠️ Please consult with a healthcare professional for proper evaluation and guidance."
            )
        else:
            return (
                "I'm currently unable to provide medical advice due to technical issues. "
                "For your health concerns, please:\n\n"
                "• Schedule an appointment with your healthcare provider\n"
                "• Consider a telehealth consultation\n"
                "• Monitor your symptoms and seek care if they worsen\n"
                "• Try using this service again in a few minutes\n\n"
                "⚠️ For any urgent medical concerns, always consult with a healthcare professional."
            )
    
    def _build_consultation_metadata(
        self,
        request: MedicalConsultationRequest,
        emergency_assessment: EmergencyAssessment,
        validation: ResponseValidation,
        ai_response: AIResponse,
        start_time: datetime
    ) -> Dict[str, Any]:
        """Build comprehensive consultation metadata"""
        
        return {
            "consultation_type": "standard_medical",
            "response_time": (datetime.now(timezone.utc) - start_time).total_seconds(),
            "emergency_detected": emergency_assessment.is_emergency,
            "urgency_score": emergency_assessment.urgency_score,
            "emergency_level": emergency_assessment.emergency_level.value,
            "validation_result": validation.validation_result.value,
            "safety_level": validation.safety_level.value,
            "quality_score": validation.quality_score,
            "ai_provider": ai_response.provider.value,
            "ai_confidence": ai_response.confidence_score,
            "modifications_made": len(validation.modifications_made),
            "disclaimer_added": validation.disclaimer_added,
            "content_filtered": validation.content_filtered,
            "user_id": request.user_id,
            "session_id": request.session_id,
            "conversation_id": request.conversation_id
        }
    
    def _log_consultation(
        self,
        request: MedicalConsultationRequest,
        emergency_assessment: EmergencyAssessment,
        validation: ResponseValidation,
        metadata: Dict[str, Any]
    ):
        """Log consultation for monitoring and analysis"""
        
        log_data = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "user_id": request.user_id,
            "urgency_score": emergency_assessment.urgency_score,
            "emergency_level": emergency_assessment.emergency_level.value,
            "validation_result": validation.validation_result.value,
            "safety_level": validation.safety_level.value,
            "quality_score": validation.quality_score,
            "response_time": metadata["response_time"],
            "ai_provider": metadata["ai_provider"]
        }
        
        if emergency_assessment.is_emergency:
            logger.warning(f"Medical consultation with emergency detected: {log_data}")
        elif validation.safety_level == SafetyLevel.UNSAFE:
            logger.error(f"Medical consultation with safety issues: {log_data}")
        else:
            logger.info(f"Medical consultation completed successfully: {log_data}")
    
    async def get_service_health(self) -> Dict[str, Any]:
        """Get comprehensive service health status"""
        
        # Get AI service status
        ai_status = self.ai_manager.get_service_status()
        
        # Get emergency detector stats
        emergency_stats = self.emergency_detector.get_emergency_statistics()
        
        # Perform health checks
        health_results = await self.ai_manager.health_check_all_providers()
        
        return {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "overall_status": "healthy" if ai_status["available_count"] > 0 else "degraded",
            "ai_service": ai_status,
            "emergency_detector": emergency_stats,
            "provider_health": {
                provider.value: health.status.value 
                for provider, health in health_results.items()
            },
            "components": {
                "ai_manager": "operational",
                "emergency_detector": "operational",
                "response_validator": "operational"
            }
        }


# Global instance
enhanced_medical_ai = EnhancedMedicalAI()


# Convenience function for backward compatibility
async def ask_enhanced_mydoc(
    message: str, 
    user_id: str = None, 
    context: Dict[str, Any] = None
) -> str:
    """
    Convenience function for enhanced medical consultation
    
    Args:
        message: User's medical question
        user_id: User identifier
        context: Additional context
        
    Returns:
        Enhanced medical consultation response
    """
    request = MedicalConsultationRequest(
        message=message,
        user_id=user_id,
        context=context or {}
    )
    
    consultation = await enhanced_medical_ai.medical_consultation(request)
    return consultation.response