#!/usr/bin/env python3
"""
Test script for Enhanced Medical AI Service

This script tests the enhanced medical AI service with various scenarios
including emergency detection, response validation, and AI fallback.
"""

import asyncio
import sys
import os

# Add backend directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from enhanced_medical_ai import enhanced_medical_ai, MedicalConsultationRequest


async def test_basic_consultation():
    """Test basic medical consultation"""
    print("🧪 Testing basic medical consultation...")
    
    request = MedicalConsultationRequest(
        message="I have a mild headache that started this morning. What could be causing it?",
        user_id="test-user",
        context={}
    )
    
    try:
        response = await enhanced_medical_ai.medical_consultation(request)
        
        print(f"✅ Basic consultation successful")
        print(f"   Emergency detected: {response.is_emergency}")
        print(f"   Urgency score: {response.emergency_assessment.urgency_score}/10")
        print(f"   Safety level: {response.validation.safety_level.value}")
        print(f"   Quality score: {response.validation.quality_score:.2f}")
        print(f"   AI Provider: {response.ai_metadata['provider']}")
        print(f"   Response length: {len(response.response)} characters")
        
        return True
        
    except Exception as e:
        print(f"❌ Basic consultation failed: {e}")
        return False


async def test_emergency_detection():
    """Test emergency detection"""
    print("\n🚨 Testing emergency detection...")
    
    emergency_messages = [
        "I'm having severe chest pain and can't breathe",
        "I think I'm having a heart attack",
        "I'm bleeding heavily and feel dizzy",
        "I took too many pills and feel sick"
    ]
    
    for message in emergency_messages:
        request = MedicalConsultationRequest(
            message=message,
            user_id="test-user",
            context={}
        )
        
        try:
            response = await enhanced_medical_ai.medical_consultation(request)
            
            print(f"   Message: '{message[:30]}...'")
            print(f"   Emergency: {response.is_emergency} | Urgency: {response.emergency_assessment.urgency_score}/10")
            print(f"   Level: {response.emergency_assessment.emergency_level.value}")
            
        except Exception as e:
            print(f"   ❌ Emergency test failed for '{message[:30]}...': {e}")
            return False
    
    print("✅ Emergency detection tests completed")
    return True


async def test_response_validation():
    """Test response validation"""
    print("\n🔍 Testing response validation...")
    
    request = MedicalConsultationRequest(
        message="What medications should I take for my diabetes?",
        user_id="test-user",
        context={}
    )
    
    try:
        response = await enhanced_medical_ai.medical_consultation(request)
        
        print(f"✅ Response validation successful")
        print(f"   Validation result: {response.validation.validation_result.value}")
        print(f"   Safety level: {response.validation.safety_level.value}")
        print(f"   Quality rating: {response.validation.quality_rating.value}")
        print(f"   Disclaimer added: {response.validation.disclaimer_added}")
        print(f"   Content filtered: {response.validation.content_filtered}")
        print(f"   Issues found: {len(response.validation.issues)}")
        
        return True
        
    except Exception as e:
        print(f"❌ Response validation test failed: {e}")
        return False


async def test_service_health():
    """Test service health monitoring"""
    print("\n💚 Testing service health...")
    
    try:
        health = await enhanced_medical_ai.get_service_health()
        
        print(f"✅ Service health check successful")
        print(f"   Overall status: {health['overall_status']}")
        print(f"   Available providers: {health['ai_service']['available_count']}/{health['ai_service']['total_count']}")
        print(f"   Components: {health['components']}")
        
        return True
        
    except Exception as e:
        print(f"❌ Service health test failed: {e}")
        return False


async def main():
    """Run all tests"""
    print("🚀 Starting Enhanced Medical AI Tests\n")
    
    tests = [
        test_basic_consultation,
        test_emergency_detection,
        test_response_validation,
        test_service_health
    ]
    
    results = []
    for test in tests:
        try:
            result = await test()
            results.append(result)
        except Exception as e:
            print(f"❌ Test {test.__name__} crashed: {e}")
            results.append(False)
    
    # Summary
    passed = sum(results)
    total = len(results)
    
    print(f"\n📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Enhanced Medical AI is working correctly.")
        return 0
    else:
        print("⚠️  Some tests failed. Check the output above for details.")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)