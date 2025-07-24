#!/usr/bin/env python3
"""
Test script for the IntentAnalyzer class.
Demonstrates how to use different LLM providers for intent analysis.
"""

from app.intent_analyzer import create_intent_analyzer, IntentAnalyzer
from app.llm_providers import OpenAIProvider, AnthropicProvider
from app.intent_analyzer import MockLLMProvider


def test_mock_provider():
    """Test the mock LLM provider."""
    print("=== Testing Mock LLM Provider ===")
    
    # Create analyzer with mock provider
    analyzer = create_intent_analyzer('mock')
    
    # Test messages
    test_messages = [
        "Book me a flight to New York for tomorrow morning",
        "What's the weather like today?",
        "I need help with my account",
        "Hello, how are you?"
    ]
    
    for message in test_messages:
        print(f"\nInput: {message}")
        result = analyzer.analyze(message)
        print(f"Intent: {result.classification['primary_intent']}")
        print(f"Domain: {result.classification['domain']}")
        print(f"Confidence: {result.classification['confidence']}")
        print(f"Entities: {len(result.entities)} found")
        print(f"Missing slots: {result.slots['missing']}")


def test_openai_provider():
    """Test the OpenAI provider (mock implementation)."""
    print("\n=== Testing OpenAI Provider (Mock) ===")
    
    # Create analyzer with OpenAI provider (using mock implementation)
    analyzer = create_intent_analyzer('openai', api_key='mock_key', model='gpt-4')
    
    test_message = "Book me a flight to New York for tomorrow morning, preferably before 10 AM"
    print(f"\nInput: {test_message}")
    
    result = analyzer.analyze(test_message)
    print(f"Intent: {result.classification['primary_intent']}")
    print(f"Domain: {result.classification['domain']}")
    print(f"Confidence: {result.classification['confidence']}")
    print(f"Entities: {len(result.entities)} found")
    
    # Print the full structured result
    print("\nFull structured result:")
    print(result.to_json())


def test_batch_analysis():
    """Test batch analysis functionality."""
    print("\n=== Testing Batch Analysis ===")
    
    analyzer = create_intent_analyzer('mock')
    
    messages = [
        "Book a flight to Paris next week",
        "What's the weather in London?",
        "Help me reset my password",
        "Show me my recent transactions"
    ]
    
    results = analyzer.analyze_batch(messages)
    
    for i, result in enumerate(results):
        print(f"\nMessage {i+1}: {messages[i]}")
        print(f"Intent: {result.classification['primary_intent']}")
        print(f"Confidence: {result.classification['confidence']}")


def test_custom_provider():
    """Test creating analyzer with custom provider."""
    print("\n=== Testing Custom Provider ===")
    
    # Create a custom provider instance
    custom_provider = MockLLMProvider()
    analyzer = IntentAnalyzer(custom_provider)
    
    message = "I want to book a hotel in Tokyo for next month"
    result = analyzer.analyze(message)
    
    print(f"Input: {message}")
    print(f"Intent: {result.classification['primary_intent']}")
    print(f"Domain: {result.classification['domain']}")


def test_error_handling():
    """Test error handling."""
    print("\n=== Testing Error Handling ===")
    
    analyzer = create_intent_analyzer('mock')
    
    # Test empty message
    try:
        result = analyzer.analyze("")
        print("Empty message test failed - should have raised ValueError")
    except ValueError as e:
        print(f"Empty message correctly rejected: {e}")
    
    # Test None message
    try:
        result = analyzer.analyze(None)
        print("None message test failed - should have raised ValueError")
    except (ValueError, TypeError) as e:
        print(f"None message correctly rejected: {e}")


if __name__ == "__main__":
    print("Intent Analyzer Test Suite")
    print("=" * 50)
    
    # Run all tests
    test_mock_provider()
    test_openai_provider()
    test_batch_analysis()
    test_custom_provider()
    test_error_handling()
    
    print("\n" + "=" * 50)
    print("All tests completed!") 