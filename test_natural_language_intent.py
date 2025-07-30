#!/usr/bin/env python3
"""
Test script to verify the natural language intent functionality.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.intent_analyzer import create_intent_analyzer, MockLLMProvider


def test_natural_language_intent():
    """Test that the natural language intent is properly generated."""
    
    # Create a mock intent analyzer
    analyzer = create_intent_analyzer("mock")
    
    # Test cases with expected natural language intents
    test_cases = [
        {
            "message": "I want to book a flight to New York tomorrow",
            "expected_intent": "User wants to book a flight to New York on tomorrow"
        },
        {
            "message": "What's the weather like in NYC?",
            "expected_intent": "User wants to know the weather in New York"
        },
        {
            "message": "I need help with my account",
            "expected_intent": "User is seeking help or support"
        },
        {
            "message": "Can you tell me about New York?",
            "expected_intent": "User is making a general inquiry about New York"
        }
    ]
    
    print("Testing natural language intent generation...")
    print("=" * 50)
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\nTest {i}:")
        print(f"Input: {test_case['message']}")
        
        try:
            result = analyzer.analyze(test_case['message'])
            natural_intent = result.natural_language_intent
            
            print(f"Generated: {natural_intent}")
            print(f"Expected: {test_case['expected_intent']}")
            
            # Check if the natural language intent is present
            if natural_intent:
                print("✅ Natural language intent generated successfully")
            else:
                print("❌ Natural language intent is empty")
                
        except Exception as e:
            print(f"❌ Error analyzing message: {e}")
    
    print("\n" + "=" * 50)
    print("Test completed!")


def test_intent_result_structure():
    """Test that the IntentResult structure includes natural_language_intent."""
    
    analyzer = create_intent_analyzer("mock")
    result = analyzer.analyze("Book a flight to Paris")
    
    print("\nTesting IntentResult structure...")
    print("=" * 50)
    
    # Check that the attribute exists
    if hasattr(result, 'natural_language_intent'):
        print("✅ natural_language_intent attribute exists")
    else:
        print("❌ natural_language_intent attribute missing")
    
    # Check that it's included in the dictionary representation
    result_dict = result.to_dict()
    if 'natural_language_intent' in result_dict['intent']:
        print("✅ natural_language_intent included in dictionary representation")
    else:
        print("❌ natural_language_intent missing from dictionary representation")
    
    print(f"Natural language intent: {result.natural_language_intent}")
    print("=" * 50)


if __name__ == "__main__":
    test_natural_language_intent()
    test_intent_result_structure() 