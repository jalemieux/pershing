#!/usr/bin/env python3
"""
Test script for OpenAI LLM Provider with Structured Outputs.

This script demonstrates how to use the OpenAI provider for intent analysis.
Make sure to set your OpenAI API key in the environment variable OPENAI_API_KEY.
"""

import os
import sys
from dotenv import load_dotenv

# Add the app directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

from app.llm_providers import OpenAIProvider
from app.intent_analyzer import IntentAnalyzer

def test_openai_provider():
    """Test the OpenAI provider with various messages."""
    
    # Load environment variables
    load_dotenv()
    
    # Get API key from environment
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        print("❌ Error: OPENAI_API_KEY environment variable not set")
        print("Please set your OpenAI API key:")
        print("export OPENAI_API_KEY='your-api-key-here'")
        return
    
    print("🔑 OpenAI API key found")
    
    # Create the OpenAI provider
    try:
        provider = OpenAIProvider(api_key=api_key, model="gpt-4o-2024-08-06")
        analyzer = IntentAnalyzer(provider)
        print("✅ OpenAI provider initialized successfully")
    except Exception as e:
        print(f"❌ Error initializing OpenAI provider: {e}")
        return
    
    # Test messages
    test_messages = [
        "I want to book a flight to New York tomorrow morning",
        "What's the weather like in San Francisco?",
        "Can you help me with my account?",
        "Hello, how are you?",
        "I need to schedule a meeting for next week",
        "Book me a hotel in Paris for next weekend",
        "What's the traffic like on the 101?",
        "Set a reminder for my dentist appointment"
    ]
    
    print("\n🧪 Testing OpenAI Intent Analysis with Structured Outputs")
    print("=" * 60)
    
    for i, message in enumerate(test_messages[:1], 1):
        print(f"\n📝 Test {i}: '{message}'")
        print("-" * 50)
        
        try:
            # Analyze the intent
            result = analyzer.analyze(message)
            
            # Display the results
            print(f"✅ Analysis completed in {result.metadata.get('processing_time_ms', 0)}ms")
            print(f"🎯 Primary Intent: {result.classification.get('primary_intent', 'unknown')}")
            print(f"🏷️  Domain: {result.classification.get('domain', 'unknown')}")
            print(f"📊 Confidence: {result.classification.get('confidence', 0):.2f}")
            
            # Show entities
            entities = result.entities
            if entities:
                print(f"🏷️  Entities ({len(entities)}):")
                for entity in entities:
                    print(f"    - {entity['type']}: {entity['value']} → {entity['normalized_value']} (conf: {entity['confidence']:.2f})")
            else:
                print("🏷️  Entities: None found")
            
            # Show slots
            slots = result.slots
            if slots.get('missing'):
                print(f"❌ Missing slots: {slots['missing']}")
            if slots.get('required'):
                print(f"✅ Required slots: {slots['required']}")
            if slots.get('optional'):
                print(f"📋 Optional slots: {slots['optional']}")
            
            # Show fulfillment
            fulfillment = result.fulfillment
            print(f"🎯 Action: {fulfillment.get('action_type', 'unknown')}")
            print(f"🔧 Service: {fulfillment.get('service', 'unknown')}")
            print(f"✅ Complete: {fulfillment.get('required_fields_complete', False)}")
            
            # Show metadata
            metadata = result.metadata
            print(f"🌐 Language: {metadata.get('language', 'unknown')}")
            print(f"😊 Sentiment: {metadata.get('sentiment', 'unknown')}")
            print(f"⚡ Urgency: {metadata.get('urgency', 'unknown')}")
            
        except Exception as e:
            print(f"❌ Error analyzing message: {e}")
            continue
    
    print("\n" + "=" * 60)
    print("✅ OpenAI provider test completed!")

def test_error_handling():
    """Test error handling with invalid API key."""
    print("\n🧪 Testing Error Handling")
    print("=" * 30)
    
    try:
        # Try with invalid API key
        provider = OpenAIProvider(api_key="invalid-key", model="gpt-4o-2024-08-06")
        analyzer = IntentAnalyzer(provider)
        
        result = analyzer.analyze("Hello world")
        
        print(f"❌ Expected error but got result: {result.classification}")
        
    except Exception as e:
        print(f"✅ Error handling working: {e}")

def test_structured_output_validation():
    """Test that the structured output validation is working correctly."""
    print("\n🧪 Testing Structured Output Validation")
    print("=" * 40)
    
    # Load environment variables
    load_dotenv()
    
    # Get API key from environment
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        print("❌ Skipping validation test - no API key")
        return
    
    try:
        provider = OpenAIProvider(api_key=api_key, model="gpt-4o-2024-08-06")
        analyzer = IntentAnalyzer(provider)
        
        # Test with a simple message
        result = analyzer.analyze("Book a flight to London")
        
        # Check that all required fields are present
        required_fields = [
            'classification', 'entities', 'slots', 'context', 
            'constraints', 'disambiguation', 'fulfillment', 'metadata'
        ]
        
        missing_fields = []
        for field in required_fields:
            if field not in result.__dict__:
                missing_fields.append(field)
        
        if missing_fields:
            print(f"❌ Missing required fields: {missing_fields}")
        else:
            print("✅ All required fields present")
            
        # Check classification structure
        classification = result.classification
        if all(key in classification for key in ['primary_intent', 'domain', 'category', 'confidence']):
            print("✅ Classification structure valid")
        else:
            print("❌ Classification structure invalid")
            
        # Check metadata structure
        metadata = result.metadata
        if all(key in metadata for key in ['language', 'sentiment', 'urgency', 'processing_time_ms']):
            print("✅ Metadata structure valid")
        else:
            print("❌ Metadata structure invalid")
            
    except Exception as e:
        print(f"❌ Validation test failed: {e}")

def test_model_compatibility():
    """Test different model compatibility."""
    print("\n🧪 Testing Model Compatibility")
    print("=" * 35)
    
    # Load environment variables
    load_dotenv()
    
    # Get API key from environment
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        print("❌ Skipping model test - no API key")
        return
    
    models_to_test = [
        "gpt-4o-2024-08-06",
        "gpt-4o-mini",
        "gpt-4-turbo"
    ]
    
    for model in models_to_test:
        try:
            print(f"\n🔧 Testing model: {model}")
            provider = OpenAIProvider(api_key=api_key, model=model)
            analyzer = IntentAnalyzer(provider)
            
            result = analyzer.analyze("Book a flight to Tokyo")
            
            if result.classification.get('primary_intent'):
                print(f"✅ {model} - Success")
                print(f"   Intent: {result.classification['primary_intent']}")
                print(f"   Confidence: {result.classification['confidence']:.2f}")
            else:
                print(f"❌ {model} - No intent detected")
                
        except Exception as e:
            print(f"❌ {model} - Error: {e}")

if __name__ == "__main__":
    print("🚀 OpenAI LLM Provider Test with Structured Outputs")
    print("=" * 50)
    
    # Test with valid API key
    test_openai_provider()
    
    # Test structured output validation
    test_structured_output_validation()
    
    # Test model compatibility
    test_model_compatibility()
    
    # Test error handling
    test_error_handling() 