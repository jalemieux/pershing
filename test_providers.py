#!/usr/bin/env python3
"""
Test script to check environment variables and provider initialization.
"""

import os
import sys

# Add the app directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

def test_environment():
    """Test environment variables."""
    print("Environment Variables Test")
    print("=" * 40)
    
    # Check for API keys
    openai_key = os.getenv('OPENAI_API_KEY')
    anthropic_key = os.getenv('ANTHROPIC_API_KEY')
    
    print(f"OpenAI API Key: {'✅ Found' if openai_key else '❌ Not found'}")
    print(f"Anthropic API Key: {'✅ Found' if anthropic_key else '❌ Not found'}")
    
    # Check for model configurations
    openai_model = os.getenv('OPENAI_MODEL', 'gpt-4o-2024-08-06')
    anthropic_model = os.getenv('ANTHROPIC_MODEL', 'claude-3-sonnet-20240229')
    
    print(f"OpenAI Model: {openai_model}")
    print(f"Anthropic Model: {anthropic_model}")
    
    return openai_key is not None or anthropic_key is not None

def test_provider_creation():
    """Test provider creation."""
    print("\nProvider Creation Test")
    print("=" * 40)
    
    try:
        from app.prompt_crafter import create_multi_provider_prompt_crafter
        
        # Create providers config based on environment
        providers_config = {}
        
        openai_key = os.getenv('OPENAI_API_KEY')
        if openai_key:
            providers_config['openai'] = {
                'api_key': openai_key,
                'model': os.getenv('OPENAI_MODEL', 'gpt-4o-2024-08-06')
            }
        
        anthropic_key = os.getenv('ANTHROPIC_API_KEY')
        if anthropic_key:
            providers_config['anthropic'] = {
                'api_key': anthropic_key,
                'model': os.getenv('ANTHROPIC_MODEL', 'claude-3-sonnet-20240229')
            }
        
        if not providers_config:
            providers_config['mock'] = {}
        
        print(f"Creating providers with config: {list(providers_config.keys())}")
        
        # Create the multi-provider crafter
        multi_crafter = create_multi_provider_prompt_crafter(providers_config)
        
        print(f"✅ Multi-provider crafter created successfully")
        print(f"Available providers: {list(multi_crafter.providers.keys())}")
        
        # Test prompt generation
        test_input = "Write a blog post about AI"
        print(f"\nTesting prompt generation with input: {test_input}")
        
        result = multi_crafter.craft_prompts_multi_provider(test_input)
        
        print(f"✅ Prompt generation successful!")
        print(f"Total prompts generated: {len(result.prompts)}")
        print(f"Providers used: {result.metadata.get('providers_used', [])}")
        print(f"Successful providers: {result.metadata.get('successful_providers', [])}")
        
        # Show provider results
        for provider_name, provider_result in result.provider_results.items():
            print(f"\n📋 {provider_name}:")
            if 'error' in provider_result:
                print(f"   ❌ Error: {provider_result['error']}")
            else:
                print(f"   ✅ Success - {len(provider_result.get('prompts', []))} prompts")
        
        return True
        
    except Exception as e:
        print(f"❌ Error during provider creation test: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("Provider Environment Test")
    print("=" * 60)
    
    # Test environment
    env_ok = test_environment()
    
    # Test provider creation
    provider_ok = test_provider_creation()
    
    print("\n" + "=" * 60)
    print("Test Results:")
    print(f"Environment: {'✅ PASSED' if env_ok else '❌ FAILED'}")
    print(f"Provider Creation: {'✅ PASSED' if provider_ok else '❌ FAILED'}")
    
    if env_ok and provider_ok:
        print("\n🎉 All tests passed!")
        sys.exit(0)
    else:
        print("\n💥 Some tests failed!")
        sys.exit(1) 