#!/usr/bin/env python3
"""
Debug script for AI Service Manager
"""

import asyncio
import sys
import os

# Add backend directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from ai_service_manager import ai_service_manager


async def debug_ai_manager():
    """Debug the AI service manager"""
    print("🔍 Debugging AI Service Manager...")
    
    # Check providers
    print(f"Total providers: {len(ai_service_manager.providers)}")
    
    for i, provider in enumerate(ai_service_manager.providers):
        print(f"Provider {i+1}: {provider.provider_type.value}")
        print(f"  Status: {provider.health.status.value}")
        print(f"  Success rate: {provider.health.success_rate}")
        print(f"  Base URL: {getattr(provider, 'base_url', 'N/A')}")
        print(f"  API Key: {getattr(provider, 'api_key', 'N/A')[:10]}...")
        print(f"  Model: {getattr(provider, 'model', 'N/A')}")
        
        # Test health check
        try:
            is_healthy = await provider.health_check()
            print(f"  Health check result: {is_healthy}")
        except Exception as e:
            print(f"  Health check error: {e}")
        print()
    
    # Run full health check
    print("Running full health check...")
    health_results = await ai_service_manager.health_check_all_providers()
    
    for provider_type, health in health_results.items():
        print(f"{provider_type.value}: {health.status.value}")
    
    # Check available providers
    available = ai_service_manager.get_available_providers()
    print(f"Available providers: {len(available)}")
    
    for provider in available:
        print(f"  - {provider.provider_type.value} ({provider.health.status.value})")
    
    # Test a simple consultation
    if available:
        print("\nTesting consultation...")
        try:
            response = await ai_service_manager.generate_medical_consultation(
                "I have a headache",
                {}
            )
            print(f"✅ Consultation successful!")
            print(f"Provider: {response.provider.value}")
            print(f"Response: {response.content[:100]}...")
        except Exception as e:
            print(f"❌ Consultation failed: {e}")
    else:
        print("❌ No available providers for consultation test")


if __name__ == "__main__":
    asyncio.run(debug_ai_manager())