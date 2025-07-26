#!/usr/bin/env python3
"""
Test script for the multi-provider prompt crafter.
"""

import os
import sys
from datetime import datetime

# Add the app directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

from app.prompt_crafter import create_multi_provider_prompt_crafter, MockPromptLLMProvider


def test_multi_provider_prompt_crafter():
    """Test the multi-provider prompt crafter with mock providers."""
    
    print("Testing Multi-Provider Prompt Crafter")
    print("=" * 50)
    
    # Create mock providers
    class MockProvider1(MockPromptLLMProvider):
        def generate_prompt(self, user_input: str, context=None):
            result = super().generate_prompt(user_input, context)
            result["metadata"]["provider"] = "mock1"
            return result
    
    class MockProvider2(MockPromptLLMProvider):
        def generate_prompt(self, user_input: str, context=None):
            result = super().generate_prompt(user_input, context)
            result["metadata"]["provider"] = "mock2"
            return result
    
    # Create the multi-provider crafter
    from app.prompt_crafter import MultiProviderPromptCrafter
    providers = {
        "mock1": MockProvider1(),
        "mock2": MockProvider2()
    }
    
    multi_crafter = MultiProviderPromptCrafter(providers)
    
    # Test input
    test_input = "Write a blog post about sustainable living"
    
    print(f"Test input: {test_input}")
    print()
    
    # Generate prompts
    try:
        result = multi_crafter.craft_prompts_multi_provider(test_input)
        
        print("✅ Multi-provider prompt generation successful!")
        print()
        
        # Display results
        print("Results Summary:")
        print(f"- Total prompts: {len(result.prompts)}")
        print(f"- Providers used: {result.metadata.get('providers_used', [])}")
        print(f"- Successful providers: {result.metadata.get('successful_providers', [])}")
        print(f"- Processing time: {result.metadata.get('processing_time_ms', 0)}ms")
        print()
        
        # Display provider-specific results
        print("Provider Results:")
        for provider_name, provider_result in result.provider_results.items():
            print(f"\n📋 {provider_name.upper()}:")
            print(f"   - Prompts generated: {len(provider_result.get('prompts', []))}")
            print(f"   - Processing time: {provider_result.get('metadata', {}).get('processing_time_ms', 0)}ms")
            print(f"   - Provider: {provider_result.get('metadata', {}).get('provider', 'unknown')}")
            
            if 'error' in provider_result:
                print(f"   - ❌ Error: {provider_result['error']}")
            else:
                print("   - ✅ Success")
        
        print()
        
        # Display all prompts
        print("All Generated Prompts:")
        for i, prompt in enumerate(result.prompts):
            prompt_type = result.prompt_types[i] if i < len(result.prompt_types) else "unknown"
            print(f"\n🔹 Prompt {i+1} ({prompt_type}):")
            print("-" * 40)
            print(prompt)
            print("-" * 40)
        
        # Test JSON export
        json_result = result.to_json()
        print(f"\n📄 JSON Export Length: {len(json_result)} characters")
        
        return True
        
    except Exception as e:
        print(f"❌ Error during multi-provider prompt generation: {str(e)}")
        return False


def test_single_provider_fallback():
    """Test fallback to single provider when multi-provider fails."""
    
    print("\nTesting Single Provider Fallback")
    print("=" * 50)
    
    # Create a multi-provider crafter with no valid providers
    providers_config = {}
    
    try:
        multi_crafter = create_multi_provider_prompt_crafter(providers_config)
        
        test_input = "Create a marketing campaign"
        result = multi_crafter.craft_prompts_multi_provider(test_input)
        
        print("✅ Fallback to mock provider successful!")
        print(f"- Providers used: {result.metadata.get('providers_used', [])}")
        print(f"- Prompts generated: {len(result.prompts)}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error during fallback test: {str(e)}")
        return False


if __name__ == "__main__":
    print("Multi-Provider Prompt Crafter Test Suite")
    print("=" * 60)
    print(f"Started at: {datetime.now()}")
    print()
    
    # Run tests
    test1_success = test_multi_provider_prompt_crafter()
    test2_success = test_single_provider_fallback()
    
    print("\n" + "=" * 60)
    print("Test Results:")
    print(f"Multi-provider test: {'✅ PASSED' if test1_success else '❌ FAILED'}")
    print(f"Fallback test: {'✅ PASSED' if test2_success else '❌ FAILED'}")
    
    if test1_success and test2_success:
        print("\n🎉 All tests passed!")
        sys.exit(0)
    else:
        print("\n💥 Some tests failed!")
        sys.exit(1) 