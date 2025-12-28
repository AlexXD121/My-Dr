import requests
import json
import logging
from typing import Optional, Dict, Any, Tuple, List
from datetime import datetime, timezone
from config import settings
from validation import sanitize_text

logger = logging.getLogger(__name__)

conversation_history = [
    {
        "role": "system",
        "content": (
            "You are MyDoc — a professional AI medical assistant designed to provide helpful medical information and guidance. "
            "You are knowledgeable about medical conditions, symptoms, treatments, and general health advice.\n\n"
            "IMPORTANT GUIDELINES:\n"
            "- Always remind users that you are an AI assistant and cannot replace professional medical diagnosis or treatment\n"
            "- For serious symptoms or emergencies, always advise users to seek immediate medical attention\n"
            "- Provide evidence-based medical information when possible\n"
            "- Be empathetic and understanding when discussing health concerns\n"
            "- Ask relevant follow-up questions to better understand symptoms\n"
            "- Suggest when users should consult with healthcare professionals\n"
            "- Provide general health and wellness advice\n"
            "- Help users understand medical terminology and procedures\n\n"
            "WHAT YOU CAN DO:\n"
            "- Explain medical conditions and symptoms\n"
            "- Provide general health advice and wellness tips\n"
            "- Help interpret basic medical information\n"
            "- Suggest when to seek medical care\n"
            "- Discuss preventive health measures\n"
            "- Explain medication basics (but not prescribe)\n\n"
            "WHAT YOU CANNOT DO:\n"
            "- Provide specific medical diagnoses\n"
            "- Prescribe medications or treatments\n"
            "- Replace professional medical consultation\n"
            "- Handle medical emergencies (always direct to emergency services)\n\n"
            "Always maintain a professional, caring, and informative tone. "
            "Use clear, understandable language and avoid overly technical jargon unless necessary."
        )
    }
]


def call_local_ai_model(message):
    """Call local AI model for medical consultation"""
    try:
        from local_ai import local_ai
        return local_ai.medical_consultation(message)
    except Exception as e:
        print(f"❌ Local AI Exception: {e}")
        return None


def call_huggingface_medical_api(message):
    """Call Hugging Face API with medical-focused models"""
    medical_models = [
        "microsoft/DialoGPT-medium",
        "facebook/blenderbot-400M-distill"
    ]
    
    for model in medical_models:
        try:
            headers = {
                "Authorization": f"Bearer {settings.huggingface_api_key}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "inputs": f"As a medical AI assistant, provide helpful information about: {message}",
                "parameters": {
                    "max_new_tokens": 200,
                    "temperature": 0.4,  # Lower temperature for medical accuracy
                    "do_sample": True
                }
            }
            
            model_url = f"https://api-inference.huggingface.co/models/{model}"
            
            response = requests.post(
                model_url,
                headers=headers,
                json=payload,
                timeout=15
            )
            
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, list) and len(data) > 0:
                    reply = data[0].get("generated_text", "").strip()
                    if reply:
                        return reply
                        
            elif response.status_code == 503:
                print(f"Model {model} is loading, trying next...")
                continue
            else:
                print(f"❌ HF API Error for {model}: {response.status_code}")
                continue
                
        except Exception as e:
            print(f"❌ HF API Exception for {model}: {e}")
            continue
    
    return None


def ask_mydoc(message: str, user_id: str = None) -> str:
    """
    Main function to get medical advice from MyDoc AI assistant
    
    Args:
        message: User's medical question or concern
        user_id: User ID for context (optional)
        
    Returns:
        AI medical assistant response
    """
    global conversation_history

    # Enhanced sanitization
    message = sanitize_text(message)
    if not message:
        return "Please describe your medical concern or question, and I'll do my best to help you with information and guidance. 🩺"

    # Add user context to message if available
    if user_id:
        # In future, we can load user-specific medical history
        pass

    conversation_history.append({"role": "user", "content": message})

    try:
        # Use local AI model as primary provider for medical consultation
        reply = call_local_ai_model(message)
        
        # If local AI fails, try Hugging Face medical models as backup
        if not reply and hasattr(settings, 'huggingface_api_key') and settings.huggingface_api_key:
            reply = call_huggingface_medical_api(message)
        
        # If all providers fail, return a professional medical fallback
        if not reply:
            fallback_responses = [
                "I'm experiencing some technical difficulties right now. For any urgent medical concerns, please contact your healthcare provider or emergency services immediately. For general health questions, please try again in a moment. 🩺",
                "I'm currently unable to process your medical query due to technical issues. If this is urgent, please seek immediate medical attention. Otherwise, please try again shortly. 💊",
                "Technical issues are preventing me from responding right now. For medical emergencies, call emergency services. For other concerns, please consult with a healthcare professional or try again later. 🏥",
                "I'm having connectivity issues at the moment. Please remember that for any serious medical concerns, it's always best to consult with a qualified healthcare professional. 👨‍⚕️"
            ]
            import random
            return random.choice(fallback_responses)
        
        # Sanitize AI response
        reply = sanitize_text(reply)

        # Add medical disclaimer if not already present
        if "medical professional" not in reply.lower() and "doctor" not in reply.lower():
            reply += "\n\n⚠️ Please remember: This information is for educational purposes only and should not replace professional medical advice. Always consult with a healthcare provider for proper diagnosis and treatment."

        conversation_history.append({"role": "assistant", "content": reply})

        # Limit conversation history size
        if len(conversation_history) > 20:
            conversation_history = [conversation_history[0]] + conversation_history[-19:]

        return reply

    except Exception as e:
        print(f"❌ MyDoc API Error for user {user_id}: {e}")
        return "I'm experiencing technical difficulties. For any urgent medical concerns, please contact your healthcare provider or emergency services immediately. 🚨"


def get_medical_emergency_response() -> str:
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


def detect_medical_emergency(message: str) -> bool:
    """Detect potential medical emergency keywords"""
    emergency_keywords = [
        "chest pain", "heart attack", "stroke", "can't breathe", "difficulty breathing",
        "severe bleeding", "unconscious", "overdose", "poisoning", "severe allergic reaction",
        "anaphylaxis", "seizure", "severe head injury", "broken bone", "emergency",
        "911", "ambulance", "dying", "severe pain", "blood loss"
    ]
    
    message_lower = message.lower()
    return any(keyword in message_lower for keyword in emergency_keywords)


def ask_mydoc_with_emergency_check(message: str, user_id: str = None) -> str:
    """
    MyDoc with emergency detection
    """
    # Check for medical emergency keywords
    if detect_medical_emergency(message):
        return get_medical_emergency_response()
    
    # Otherwise, proceed with normal medical consultation
    return ask_mydoc(message, user_id)