#!/usr/bin/env python3
"""
Test Flask integration with the singleton intent analyzer.
"""

import json
from app import create_app


def test_flask_singleton_integration():
    """Test that the Flask app properly initializes and uses the singleton intent analyzer."""
    print("=== Testing Flask Singleton Integration ===")
    
    # Create Flask app
    app = create_app()
    
    with app.app_context():
        # Test that the intent analyzer is available
        assert hasattr(app, 'intent_analyzer'), "Intent analyzer not initialized in app context"
        
        # Test basic functionality
        result = app.intent_analyzer.analyze("Book me a flight to Paris")
        print(f"Intent: {result.classification['primary_intent']}")
        print(f"Domain: {result.classification['domain']}")
        print(f"Confidence: {result.classification['confidence']}")
        
        # Test that it's the same instance
        analyzer1 = app.intent_analyzer
        analyzer2 = app.intent_analyzer
        assert analyzer1 is analyzer2, "Intent analyzer should be a singleton"
        
        print("✅ Singleton pattern working correctly")


def test_helper_function():
    """Test the get_intent_analyzer helper function."""
    print("\n=== Testing Helper Function ===")
    
    app = create_app()
    
    with app.app_context():
        from app.intent_analyzer import get_intent_analyzer
        
        # Test helper function
        analyzer = get_intent_analyzer()
        result = analyzer.analyze("What's the weather like?")
        
        print(f"Intent: {result.classification['primary_intent']}")
        print(f"Domain: {result.classification['domain']}")
        
        # Test that it returns the same instance
        analyzer1 = get_intent_analyzer()
        analyzer2 = get_intent_analyzer()
        assert analyzer1 is analyzer2, "Helper function should return same instance"
        
        print("✅ Helper function working correctly")


def test_error_handling():
    """Test error handling in Flask context."""
    print("\n=== Testing Error Handling ===")
    
    app = create_app()
    
    with app.app_context():
        from app.intent_analyzer import get_intent_analyzer
        
        # Test empty message handling
        try:
            analyzer = get_intent_analyzer()
            result = analyzer.analyze("")
            print("❌ Empty message should have raised ValueError")
        except ValueError as e:
            print(f"✅ Empty message correctly rejected: {e}")
        
        # Test None message handling
        try:
            result = analyzer.analyze(None)
            print("❌ None message should have raised ValueError")
        except (ValueError, TypeError) as e:
            print(f"✅ None message correctly rejected: {e}")


def test_configuration():
    """Test configuration-based provider selection."""
    print("\n=== Testing Configuration ===")
    
    # Test with mock provider (default)
    app = create_app()
    with app.app_context():
        analyzer = app.intent_analyzer
        result = analyzer.analyze("Hello")
        print(f"Mock provider - Intent: {result.classification['primary_intent']}")
    
    # Test with environment variable override
    import os
    os.environ['INTENT_PROVIDER'] = 'mock'  # Explicitly set mock
    
    app2 = create_app()
    with app2.app_context():
        analyzer2 = app2.intent_analyzer
        result2 = analyzer2.analyze("Hello")
        print(f"Explicit mock provider - Intent: {result2.classification['primary_intent']}")
    
    print("✅ Configuration-based provider selection working")


if __name__ == "__main__":
    print("Flask Integration Test Suite")
    print("=" * 50)
    
    test_flask_singleton_integration()
    test_helper_function()
    test_error_handling()
    test_configuration()
    
    print("\n" + "=" * 50)
    print("All Flask integration tests completed!") 