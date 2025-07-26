#!/usr/bin/env python3
"""
Test script for the OpenAI prompt provider functionality.
"""

import sys
import os

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.llm_providers import OpenAIPromptProvider


def test_openai_prompt_provider():
    """Test the OpenAI prompt provider with mock API key."""
    print("Testing OpenAI Prompt Provider...")
    
    # Create a prompt provider with mock API key (this will trigger fallback)
    prompt_provider = OpenAIPromptProvider(api_key="mock_key", model="gpt-4o-2024-08-06")
    
    # Test input
    test_input = "I want to write a blog post about sustainable living"
    
    print(f"Input: {test_input}")
    print("-" * 50)
    
    # Generate prompt (this will use fallback since we don't have a real API key)
    result = prompt_provider.generate_prompt(test_input)
    
    # Display results
    print(f"Generated {len(result['prompts'])} prompts:")
    print(f"Prompt types: {result['prompt_types']}")
    print(f"Metadata: {result['metadata']}")
    print()
    
    for i, prompt in enumerate(result['prompts'], 1):
        print(f"Prompt {i} ({result['prompt_types'][i-1]}):")
        print(prompt)
        print("-" * 30)
    
    print("\nOpenAI Prompt Provider test completed successfully!")


if __name__ == "__main__":
    test_openai_prompt_provider() 