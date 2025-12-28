"""
Local AI integration for MyDoc AI using Ollama/Jan
Supports both Ollama and Jan AI backends
"""
import requests
import json
import logging
from typing import Optional, Dict, Any
from config import settings

logger = logging.getLogger(__name__)


class LocalMedicalAI:
    """Local AI model integration for medical consultations"""
    
    def __init__(self):
        # Use settings from config
        self.ollama_url = "http://localhost:11434/api/generate"
        self.jan_url = f"{settings.jan_url}/v1/chat/completions"
        self.model_name = "llama3.2:3b"  # Default Ollama model
        self.jan_model = settings.jan_model
        self.jan_api_key = settings.jan_api_key
        
        # Medical AI system prompt
        self.system_prompt = """You are MyDoc AI, a professional medical assistant designed to provide helpful medical information and guidance. 

IMPORTANT GUIDELINES:
- Always remind users that you are an AI assistant and cannot replace professional medical diagnosis or treatment
- For serious symptoms or emergencies, always advise users to seek immediate medical attention
- Provide evidence-based medical information when possible
- Be empathetic and understanding when discussing health concerns
- Ask relevant follow-up questions to better understand symptoms
- Suggest when users should consult with healthcare professionals
- Provide general health and wellness advice

WHAT YOU CAN DO:
- Explain medical conditions and symptoms
- Provide general health advice and wellness tips
- Help interpret basic medical information
- Suggest when to seek medical care
- Discuss preventive health measures
- Explain medication basics (but not prescribe)

WHAT YOU CANNOT DO:
- Provide specific medical diagnoses
- Prescribe medications or treatments
- Replace professional medical consultation
- Handle medical emergencies (always direct to emergency services)

Always maintain a professional, caring, and informative tone. Use clear, understandable language."""

    def check_ollama_connection(self) -> bool:
        """Check if Ollama is running and accessible"""
        try:
            response = requests.get("http://localhost:11434/api/tags", timeout=5)
            return response.status_code == 200
        except Exception as e:
            logger.debug(f"Ollama not accessible: {e}")
            return False

    def check_jan_connection(self) -> bool:
        """Check if Jan AI is running and accessible"""
        try:
            response = requests.get(
                f"{settings.jan_url}/v1/models", 
                headers={"Authorization": f"Bearer {self.jan_api_key}"},
                timeout=5
            )
            return response.status_code == 200
        except Exception as e:
            logger.debug(f"Jan AI not accessible: {e}")
            return False

    def medical_consultation_ollama(self, message: str) -> Optional[str]:
        """Get medical consultation response using Ollama"""
        try:
            prompt = f"{self.system_prompt}\n\nUser: {message}\n\nMyDoc AI:"
            
            payload = {
                "model": self.model_name,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": 0.3,  # Lower temperature for more consistent medical advice
                    "top_p": 0.9,
                    "max_tokens": 400,
                    "stop": ["User:", "Human:"]
                }
            }
            
            response = requests.post(
                self.ollama_url, 
                json=payload, 
                timeout=30,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                result = response.json()
                return result.get("response", "").strip()
            else:
                logger.error(f"Ollama API error: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            logger.error(f"Ollama consultation error: {e}")
            return None

    def medical_consultation_jan(self, message: str) -> Optional[str]:
        """Get medical consultation response using Jan AI"""
        try:
            messages = [
                {"role": "system", "content": self.system_prompt},
                {"role": "user", "content": message}
            ]
            
            payload = {
                "model": self.jan_model,
                "messages": messages,
                "temperature": 0.3,
                "max_tokens": 400,
                "stream": False
            }
            
            # Use the working authentication method for Jan AI
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.jan_api_key}"
            }
            
            response = requests.post(
                self.jan_url,
                json=payload,
                timeout=30,
                headers=headers
            )
            
            if response and response.status_code == 200:
                result = response.json()
                return result["choices"][0]["message"]["content"].strip()
            else:
                error_msg = response.text if response else "No response"
                logger.error(f"Jan AI API error: {response.status_code if response else 'No connection'} - {error_msg}")
                return None
                
        except Exception as e:
            logger.error(f"Jan AI consultation error: {e}")
            return None

    def medical_consultation(self, message: str) -> str:
        """
        Main method to get medical consultation response
        Tries Jan AI first, then Ollama as fallback
        """
        # Sanitize input
        message = message.strip()
        if not message:
            return "Please describe your medical concern or question, and I'll do my best to help you with information and guidance. 🩺"

        # Check for emergency keywords
        if self.detect_emergency(message):
            return self.get_emergency_response()

        # Try Jan AI first (primary)
        if self.check_jan_connection():
            logger.info("Using Jan AI for medical consultation")
            response = self.medical_consultation_jan(message)
            if response:
                return self.add_medical_disclaimer(response)
            else:
                logger.warning("Jan AI failed to generate response")

        # Fallback to Ollama
        if self.check_ollama_connection():
            logger.info("Using Ollama for medical consultation (fallback)")
            response = self.medical_consultation_ollama(message)
            if response:
                return self.add_medical_disclaimer(response)
            else:
                logger.warning("Ollama failed to generate response")

        # If both fail, return helpful fallback message
        logger.error("All AI services failed, returning fallback response")
        return self.get_fallback_response()

    def detect_emergency(self, message: str) -> bool:
        """Detect potential medical emergency keywords"""
        emergency_keywords = [
            "chest pain", "heart attack", "stroke", "can't breathe", "difficulty breathing",
            "severe bleeding", "unconscious", "overdose", "poisoning", "severe allergic reaction",
            "anaphylaxis", "seizure", "severe head injury", "broken bone", "emergency",
            "911", "ambulance", "dying", "severe pain", "blood loss", "suicide", "self harm"
        ]
        
        message_lower = message.lower()
        return any(keyword in message_lower for keyword in emergency_keywords)

    def get_emergency_response(self) -> str:
        """Return emergency medical response"""
        return (
            "🚨 MEDICAL EMERGENCY DETECTED 🚨\n\n"
            "If this is a medical emergency, please:\n"
            "• Call emergency services immediately (911 in US, 999 in UK, 112 in EU)\n"
            "• Go to the nearest emergency room\n"
            "• Contact your local emergency medical services\n\n"
            "For urgent but non-emergency medical concerns:\n"
            "• Contact your healthcare provider\n"
            "• Visit an urgent care center\n"
            "• Call a medical helpline in your area\n\n"
            "I'm an AI assistant and cannot provide emergency medical care. "
            "Please seek immediate professional medical attention."
        )

    def add_medical_disclaimer(self, response: str) -> str:
        """Add medical disclaimer if not already present"""
        if "medical professional" not in response.lower() and "healthcare provider" not in response.lower():
            response += "\n\n⚠️ Please remember: This information is for educational purposes only and should not replace professional medical advice. Always consult with a healthcare provider for proper diagnosis and treatment."
        return response

    def get_fallback_response(self) -> str:
        """Return fallback response when AI services are unavailable"""
        fallback_responses = [
            "I'm experiencing some technical difficulties right now. For any urgent medical concerns, please contact your healthcare provider or emergency services immediately. For general health questions, please try again in a moment. 🩺",
            "I'm currently unable to process your medical query due to technical issues. If this is urgent, please seek immediate medical attention. Otherwise, please try again shortly. 💊",
            "Technical issues are preventing me from responding right now. For medical emergencies, call emergency services. For other concerns, please consult with a healthcare professional or try again later. 🏥"
        ]
        import random
        return random.choice(fallback_responses)

    def get_health_status(self) -> Dict[str, Any]:
        """Get status of local AI services"""
        return {
            "ollama_available": self.check_ollama_connection(),
            "jan_available": self.check_jan_connection(),
            "model_name": self.model_name,
            "jan_model": self.jan_model
        }


# Global instance
local_ai = LocalMedicalAI()