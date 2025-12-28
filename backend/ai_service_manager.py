"""
AI Service Manager for MyDoc AI Medical Assistant

This module provides a comprehensive AI service management system with intelligent
fallback chains, health monitoring, and error handling for multiple AI providers.
"""

import logging
import asyncio
import time
from datetime import datetime, timezone, timedelta
from typing import Optional, Dict, Any, List, Tuple, Union
from enum import Enum
from dataclasses import dataclass, field
from abc import ABC, abstractmethod
import requests
import json

from config import settings

logger = logging.getLogger(__name__)


class AIProviderStatus(Enum):
    """AI Provider status enumeration"""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNAVAILABLE = "unavailable"
    UNKNOWN = "unknown"


class AIProviderType(Enum):
    """AI Provider type enumeration"""
    JAN_AI = "jan_ai"
    OLLAMA = "ollama"
    PERPLEXITY = "perplexity"
    HUGGINGFACE = "huggingface"


@dataclass
class AIResponse:
    """Standardized AI response container"""
    content: str
    provider: AIProviderType
    confidence_score: float = 0.0
    response_time: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)
    emergency_detected: bool = False
    validation_passed: bool = True
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass
class ProviderHealth:
    """Provider health status container"""
    status: AIProviderStatus
    last_check: datetime
    response_time: float
    success_rate: float
    error_count: int
    consecutive_failures: int
    last_error: Optional[str] = None


class BaseAIProvider(ABC):
    """Abstract base class for AI providers"""
    
    def __init__(self, provider_type: AIProviderType, config: Dict[str, Any]):
        self.provider_type = provider_type
        self.config = config
        self.health = ProviderHealth(
            status=AIProviderStatus.UNKNOWN,
            last_check=datetime.now(timezone.utc),
            response_time=0.0,
            success_rate=1.0,
            error_count=0,
            consecutive_failures=0
        )
        
    @abstractmethod
    async def generate_response(self, message: str, context: Dict[str, Any] = None) -> AIResponse:
        """Generate AI response for the given message"""
        pass
        
    @abstractmethod
    async def health_check(self) -> bool:
        """Check if the provider is healthy and available"""
        pass
        
    def update_health_metrics(self, success: bool, response_time: float, error: str = None):
        """Update provider health metrics"""
        self.health.last_check = datetime.now(timezone.utc)
        self.health.response_time = response_time
        
        if success:
            self.health.consecutive_failures = 0
            # Update success rate (exponential moving average)
            self.health.success_rate = 0.9 * self.health.success_rate + 0.1 * 1.0
            
            if self.health.success_rate > 0.8:
                self.health.status = AIProviderStatus.HEALTHY
            elif self.health.success_rate > 0.5:
                self.health.status = AIProviderStatus.DEGRADED
            else:
                self.health.status = AIProviderStatus.UNAVAILABLE
        else:
            self.health.consecutive_failures += 1
            self.health.error_count += 1
            self.health.last_error = error
            # Update success rate
            self.health.success_rate = 0.9 * self.health.success_rate + 0.1 * 0.0
            
            if self.health.consecutive_failures >= 3:
                self.health.status = AIProviderStatus.UNAVAILABLE
            elif self.health.success_rate < 0.5:
                self.health.status = AIProviderStatus.DEGRADED


class JanAIProvider(BaseAIProvider):
    """Jan AI provider implementation"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(AIProviderType.JAN_AI, config)
        self.base_url = config.get('base_url', settings.jan_url)
        self.api_key = config.get('api_key', settings.jan_api_key)
        self.model = config.get('model', settings.jan_model)
        self.timeout = config.get('timeout', 30)
        
    async def health_check(self) -> bool:
        """Check Jan AI health"""
        try:
            response = requests.get(
                f"{self.base_url}/v1/models",
                headers={"Authorization": f"Bearer {self.api_key}"},
                timeout=5
            )
            return response.status_code == 200
        except Exception as e:
            logger.debug(f"Jan AI health check failed: {e}")
            return False
            
    async def generate_response(self, message: str, context: Dict[str, Any] = None) -> AIResponse:
        """Generate response using Jan AI"""
        start_time = time.time()
        
        try:
            # Build system prompt for medical consultation
            system_prompt = self._build_medical_system_prompt(context)
            
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": message}
            ]
            
            payload = {
                "model": self.model,
                "messages": messages,
                "temperature": 0.3,  # Lower temperature for medical accuracy
                "max_tokens": 400,
                "stream": False
            }
            
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.api_key}"
            }
            
            response = requests.post(
                f"{self.base_url}/v1/chat/completions",
                json=payload,
                headers=headers,
                timeout=self.timeout
            )
            
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                result = response.json()
                content = result["choices"][0]["message"]["content"].strip()
                
                self.update_health_metrics(True, response_time)
                
                return AIResponse(
                    content=content,
                    provider=self.provider_type,
                    confidence_score=0.9,  # Jan AI is our primary, high confidence
                    response_time=response_time,
                    metadata={
                        "model": self.model,
                        "tokens_used": result.get("usage", {}).get("total_tokens", 0)
                    }
                )
            else:
                error_msg = f"Jan AI API error: {response.status_code} - {response.text}"
                self.update_health_metrics(False, response_time, error_msg)
                raise Exception(error_msg)
                
        except Exception as e:
            response_time = time.time() - start_time
            error_msg = f"Jan AI error: {str(e)}"
            self.update_health_metrics(False, response_time, error_msg)
            raise Exception(error_msg)
    
    def _build_medical_system_prompt(self, context: Dict[str, Any] = None) -> str:
        """Build medical system prompt with context"""
        base_prompt = """You are MyDoc AI, a professional medical assistant designed to provide helpful medical information and guidance.

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

Always maintain a professional, caring, and informative tone."""
        
        if context:
            medical_history = context.get('medical_history', '')
            if medical_history:
                base_prompt += f"\n\nUser's Medical Context: {medical_history}"
                
        return base_prompt


class PerplexityProvider(BaseAIProvider):
    """Perplexity AI provider implementation"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(AIProviderType.PERPLEXITY, config)
        self.api_key = config.get('api_key', getattr(settings, 'perplexity_api_key', None))
        self.model = config.get('model', 'llama-3.1-sonar-small-128k-online')
        self.timeout = config.get('timeout', 30)
        
    async def health_check(self) -> bool:
        """Check Perplexity health"""
        if not self.api_key:
            return False
            
        try:
            response = requests.post(
                "https://api.perplexity.ai/chat/completions",
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": self.model,
                    "messages": [{"role": "user", "content": "Hello"}],
                    "max_tokens": 10
                },
                timeout=5
            )
            return response.status_code == 200
        except Exception as e:
            logger.debug(f"Perplexity health check failed: {e}")
            return False
            
    async def generate_response(self, message: str, context: Dict[str, Any] = None) -> AIResponse:
        """Generate response using Perplexity AI"""
        if not self.api_key:
            raise Exception("Perplexity API key not configured")
            
        start_time = time.time()
        
        try:
            # Build medical-focused prompt
            medical_prompt = f"""As a medical AI assistant, provide helpful and accurate medical information about: {message}

Please ensure your response:
- Is medically accurate and evidence-based
- Includes appropriate medical disclaimers
- Suggests consulting healthcare professionals when appropriate
- Is empathetic and understanding
- Avoids providing specific diagnoses or prescriptions"""

            payload = {
                "model": self.model,
                "messages": [{"role": "user", "content": medical_prompt}],
                "temperature": 0.3,
                "max_tokens": 400
            }
            
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            response = requests.post(
                "https://api.perplexity.ai/chat/completions",
                json=payload,
                headers=headers,
                timeout=self.timeout
            )
            
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                result = response.json()
                content = result["choices"][0]["message"]["content"].strip()
                
                self.update_health_metrics(True, response_time)
                
                return AIResponse(
                    content=content,
                    provider=self.provider_type,
                    confidence_score=0.7,  # Medium confidence for fallback
                    response_time=response_time,
                    metadata={
                        "model": self.model,
                        "tokens_used": result.get("usage", {}).get("total_tokens", 0)
                    }
                )
            else:
                error_msg = f"Perplexity API error: {response.status_code} - {response.text}"
                self.update_health_metrics(False, response_time, error_msg)
                raise Exception(error_msg)
                
        except Exception as e:
            response_time = time.time() - start_time
            error_msg = f"Perplexity error: {str(e)}"
            self.update_health_metrics(False, response_time, error_msg)
            raise Exception(error_msg)


class OllamaProvider(BaseAIProvider):
    """Ollama provider implementation"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(AIProviderType.OLLAMA, config)
        self.base_url = config.get('base_url', 'http://localhost:11434')
        self.model = config.get('model', 'llama3.2:3b')
        self.timeout = config.get('timeout', 30)
        
    async def health_check(self) -> bool:
        """Check Ollama health"""
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=5)
            return response.status_code == 200
        except Exception as e:
            logger.debug(f"Ollama health check failed: {e}")
            return False
            
    async def generate_response(self, message: str, context: Dict[str, Any] = None) -> AIResponse:
        """Generate response using Ollama"""
        start_time = time.time()
        
        try:
            # Build medical system prompt
            system_prompt = self._build_medical_system_prompt(context)
            prompt = f"{system_prompt}\n\nUser: {message}\n\nMyDoc AI:"
            
            payload = {
                "model": self.model,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": 0.3,  # Lower temperature for medical accuracy
                    "top_p": 0.9,
                    "max_tokens": 400,
                    "stop": ["User:", "Human:"]
                }
            }
            
            response = requests.post(
                f"{self.base_url}/api/generate",
                json=payload,
                timeout=self.timeout,
                headers={"Content-Type": "application/json"}
            )
            
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                result = response.json()
                content = result.get("response", "").strip()
                
                if content:
                    self.update_health_metrics(True, response_time)
                    
                    return AIResponse(
                        content=content,
                        provider=self.provider_type,
                        confidence_score=0.8,  # High confidence for local model
                        response_time=response_time,
                        metadata={
                            "model": self.model,
                            "tokens_used": result.get("eval_count", 0)
                        }
                    )
                else:
                    raise Exception("Empty response from Ollama")
            else:
                error_msg = f"Ollama API error: {response.status_code} - {response.text}"
                self.update_health_metrics(False, response_time, error_msg)
                raise Exception(error_msg)
                
        except Exception as e:
            response_time = time.time() - start_time
            error_msg = f"Ollama error: {str(e)}"
            self.update_health_metrics(False, response_time, error_msg)
            raise Exception(error_msg)
    
    def _build_medical_system_prompt(self, context: Dict[str, Any] = None) -> str:
        """Build medical system prompt with context"""
        base_prompt = """You are MyDoc AI, a professional medical assistant designed to provide helpful medical information and guidance.

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

Always maintain a professional, caring, and informative tone."""
        
        if context:
            medical_history = context.get('medical_history', '')
            if medical_history:
                base_prompt += f"\n\nUser's Medical Context: {medical_history}"
                
        return base_prompt


class HuggingFaceProvider(BaseAIProvider):
    """Hugging Face provider implementation"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(AIProviderType.HUGGINGFACE, config)
        self.api_key = config.get('api_key', getattr(settings, 'huggingface_api_key', None))
        self.models = config.get('models', [
            "microsoft/DialoGPT-medium",
            "facebook/blenderbot-400M-distill"
        ])
        self.timeout = config.get('timeout', 15)
        
    async def health_check(self) -> bool:
        """Check Hugging Face health"""
        if not self.api_key:
            return False
            
        try:
            # Test with the first model
            model = self.models[0] if self.models else "microsoft/DialoGPT-medium"
            response = requests.post(
                f"https://api-inference.huggingface.co/models/{model}",
                headers={"Authorization": f"Bearer {self.api_key}"},
                json={"inputs": "Hello", "parameters": {"max_new_tokens": 5}},
                timeout=5
            )
            return response.status_code in [200, 503]  # 503 means model is loading
        except Exception as e:
            logger.debug(f"HuggingFace health check failed: {e}")
            return False
            
    async def generate_response(self, message: str, context: Dict[str, Any] = None) -> AIResponse:
        """Generate response using Hugging Face models"""
        if not self.api_key:
            raise Exception("HuggingFace API key not configured")
            
        start_time = time.time()
        
        for model in self.models:
            try:
                medical_prompt = f"As a medical AI assistant, provide helpful information about: {message}"
                
                payload = {
                    "inputs": medical_prompt,
                    "parameters": {
                        "max_new_tokens": 200,
                        "temperature": 0.4,
                        "do_sample": True
                    }
                }
                
                headers = {
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                }
                
                response = requests.post(
                    f"https://api-inference.huggingface.co/models/{model}",
                    headers=headers,
                    json=payload,
                    timeout=self.timeout
                )
                
                response_time = time.time() - start_time
                
                if response.status_code == 200:
                    data = response.json()
                    if isinstance(data, list) and len(data) > 0:
                        content = data[0].get("generated_text", "").strip()
                        if content:
                            self.update_health_metrics(True, response_time)
                            
                            return AIResponse(
                                content=content,
                                provider=self.provider_type,
                                confidence_score=0.5,  # Lower confidence for HF models
                                response_time=response_time,
                                metadata={
                                    "model": model,
                                    "attempt": self.models.index(model) + 1
                                }
                            )
                elif response.status_code == 503:
                    logger.info(f"Model {model} is loading, trying next...")
                    continue
                else:
                    logger.warning(f"HF API error for {model}: {response.status_code}")
                    continue
                    
            except Exception as e:
                logger.warning(f"HF API exception for {model}: {e}")
                continue
        
        # If all models failed
        response_time = time.time() - start_time
        error_msg = "All HuggingFace models failed"
        self.update_health_metrics(False, response_time, error_msg)
        raise Exception(error_msg)


class AIServiceManager:
    """
    Comprehensive AI Service Manager with intelligent fallback chains,
    health monitoring, and automatic failover capabilities.
    """
    
    def __init__(self):
        self.providers: List[BaseAIProvider] = []
        self.health_check_interval = 300  # 5 minutes
        self.last_health_check = datetime.now(timezone.utc) - timedelta(minutes=10)
        self._initialize_providers()
        # Force initial health check
        import asyncio
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                # If loop is already running, schedule the health check
                asyncio.create_task(self.health_check_all_providers())
            else:
                # If no loop is running, run it synchronously
                asyncio.run(self.health_check_all_providers())
        except Exception as e:
            logger.warning(f"Could not run initial health check: {e}")
            # Fallback: manually set Jan AI as healthy if it's accessible
            self._manual_health_check()
        
    def _initialize_providers(self):
        """Initialize AI providers in priority order"""
        # Primary: Jan AI
        jan_config = {
            'base_url': 'http://127.0.0.1:1337',  # Use the exact host from Jan AI
            'api_key': 'mydoc-ai-key',  # Use the exact API key from Jan AI
            'model': 'Llama-3_2-3B-Instruct-IQ4_XS',  # Use the exact model name from Jan AI
            'timeout': 30
        }
        self.providers.append(JanAIProvider(jan_config))
        
        # Secondary: Perplexity (if API key available)
        if hasattr(settings, 'perplexity_api_key') and settings.perplexity_api_key:
            perplexity_config = {
                'api_key': settings.perplexity_api_key,
                'model': 'llama-3.1-sonar-small-128k-online',
                'timeout': 30
            }
            self.providers.append(PerplexityProvider(perplexity_config))
        
        # Tertiary: HuggingFace (if API key available)
        if hasattr(settings, 'huggingface_api_key') and settings.huggingface_api_key:
            hf_config = {
                'api_key': settings.huggingface_api_key,
                'models': [
                    "microsoft/DialoGPT-medium",
                    "facebook/blenderbot-400M-distill"
                ],
                'timeout': 15
            }
            self.providers.append(HuggingFaceProvider(hf_config))
        
        logger.info(f"Initialized {len(self.providers)} AI providers")
    
    def _manual_health_check(self):
        """Manual synchronous health check for initialization"""
        for provider in self.providers:
            try:
                if provider.provider_type == AIProviderType.JAN_AI:
                    # Test Jan AI connection
                    response = requests.get(
                        f"{provider.base_url}/v1/models",
                        headers={"Authorization": f"Bearer {provider.api_key}"},
                        timeout=5
                    )
                    if response.status_code == 200:
                        provider.health.status = AIProviderStatus.HEALTHY
                        provider.health.success_rate = 1.0
                        provider.health.consecutive_failures = 0
                        logger.info(f"Jan AI provider marked as healthy")
                    else:
                        provider.health.status = AIProviderStatus.UNAVAILABLE
                        logger.warning(f"Jan AI provider marked as unavailable")
                elif provider.provider_type == AIProviderType.PERPLEXITY:
                    if hasattr(provider, 'api_key') and provider.api_key:
                        provider.health.status = AIProviderStatus.HEALTHY
                        provider.health.success_rate = 0.8
                elif provider.provider_type == AIProviderType.HUGGINGFACE:
                    if hasattr(provider, 'api_key') and provider.api_key:
                        provider.health.status = AIProviderStatus.HEALTHY
                        provider.health.success_rate = 0.6
            except Exception as e:
                logger.warning(f"Manual health check failed for {provider.provider_type.value}: {e}")
                provider.health.status = AIProviderStatus.UNAVAILABLE
    
    async def health_check_all_providers(self) -> Dict[AIProviderType, ProviderHealth]:
        """Perform health checks on all providers"""
        health_results = {}
        
        for provider in self.providers:
            try:
                is_healthy = await provider.health_check()
                
                if is_healthy:
                    # Provider is healthy
                    if provider.health.status in [AIProviderStatus.UNAVAILABLE, AIProviderStatus.UNKNOWN]:
                        provider.health.status = AIProviderStatus.HEALTHY
                        provider.health.consecutive_failures = 0
                        provider.health.success_rate = max(0.8, provider.health.success_rate)
                    elif provider.health.status == AIProviderStatus.DEGRADED:
                        # Check if it should be promoted to healthy
                        if provider.health.success_rate > 0.8:
                            provider.health.status = AIProviderStatus.HEALTHY
                else:
                    # Provider is not healthy
                    if provider.health.status == AIProviderStatus.HEALTHY:
                        provider.health.status = AIProviderStatus.DEGRADED
                    elif provider.health.status in [AIProviderStatus.DEGRADED, AIProviderStatus.UNKNOWN]:
                        provider.health.status = AIProviderStatus.UNAVAILABLE
                    
                health_results[provider.provider_type] = provider.health
                
            except Exception as e:
                logger.error(f"Health check failed for {provider.provider_type}: {e}")
                provider.health.status = AIProviderStatus.UNAVAILABLE
                health_results[provider.provider_type] = provider.health
        
        self.last_health_check = datetime.now(timezone.utc)
        return health_results
    
    def get_available_providers(self) -> List[BaseAIProvider]:
        """Get list of available providers sorted by health and priority"""
        available = []
        
        for provider in self.providers:
            if provider.health.status in [AIProviderStatus.HEALTHY, AIProviderStatus.DEGRADED]:
                available.append(provider)
        
        # Sort by health status and success rate
        available.sort(key=lambda p: (
            p.health.status == AIProviderStatus.HEALTHY,
            p.health.success_rate
        ), reverse=True)
        
        return available
    
    async def generate_medical_consultation(
        self, 
        message: str, 
        context: Dict[str, Any] = None,
        max_retries: int = 3
    ) -> AIResponse:
        """
        Generate medical consultation response with intelligent fallback
        
        Args:
            message: User's medical question
            context: Additional context (medical history, etc.)
            max_retries: Maximum retry attempts per provider
            
        Returns:
            AIResponse with the consultation response
        """
        # Periodic health check
        if (datetime.now(timezone.utc) - self.last_health_check).seconds > self.health_check_interval:
            await self.health_check_all_providers()
        
        available_providers = self.get_available_providers()
        
        if not available_providers:
            logger.error("No AI providers available")
            raise Exception("All AI services are currently unavailable")
        
        last_error = None
        
        for provider in available_providers:
            for attempt in range(max_retries):
                try:
                    logger.info(f"Attempting consultation with {provider.provider_type.value} (attempt {attempt + 1})")
                    
                    response = await provider.generate_response(message, context)
                    
                    logger.info(f"Successfully generated response using {provider.provider_type.value}")
                    return response
                    
                except Exception as e:
                    last_error = e
                    logger.warning(f"Provider {provider.provider_type.value} failed (attempt {attempt + 1}): {e}")
                    
                    # Wait before retry (exponential backoff)
                    if attempt < max_retries - 1:
                        await asyncio.sleep(2 ** attempt)
        
        # All providers failed
        logger.error(f"All AI providers failed. Last error: {last_error}")
        raise Exception(f"All AI services failed: {last_error}")
    
    def get_service_status(self) -> Dict[str, Any]:
        """Get comprehensive service status"""
        status = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "providers": {},
            "available_count": 0,
            "total_count": len(self.providers),
            "last_health_check": self.last_health_check.isoformat()
        }
        
        for provider in self.providers:
            provider_status = {
                "status": provider.health.status.value,
                "success_rate": provider.health.success_rate,
                "response_time": provider.health.response_time,
                "consecutive_failures": provider.health.consecutive_failures,
                "error_count": provider.health.error_count,
                "last_check": provider.health.last_check.isoformat(),
                "last_error": provider.health.last_error
            }
            
            status["providers"][provider.provider_type.value] = provider_status
            
            if provider.health.status in [AIProviderStatus.HEALTHY, AIProviderStatus.DEGRADED]:
                status["available_count"] += 1
        
        return status


# Global instance
ai_service_manager = AIServiceManager()