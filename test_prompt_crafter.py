#!/usr/bin/env python3
"""
Test script for the prompt crafter functionality.
"""

import sys
import os

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.prompt_crafter import create_prompt_crafter, PromptResult


def test_prompt_crafter():
    """Test the prompt crafter with mock provider."""
    print("Testing Prompt Crafter...")
    
    # Create a prompt crafter with mock provider
    prompt_crafter = create_prompt_crafter('openai')
    
    # Test input
    test_input = "I want to write a blog post about sustainable living"
    
    print(f"Input: {test_input}")
    print("-" * 50)
    
    # Generate prompts
    result = prompt_crafter.craft_prompts(test_input)
    
    # Display results
    print(f"Generated {len(result.prompts)} prompts:")
    print()
    
    for i, prompt in enumerate(result.prompts, 1):
        print(f"Prompt {i} ({result.prompt_types[i-1]}):")
        print(prompt)
        print("-" * 30)
    
    # Test batch processing
    print("\nTesting batch processing...")
    test_inputs = [
        "Write a story about a robot",
        "Create a marketing campaign",
        "Design a user interface"
    ]
    
    batch_results = prompt_crafter.craft_prompts_batch(test_inputs)
    
    print(f"Generated {len(batch_results)} results from batch processing")
    for i, result in enumerate(batch_results, 1):
        print(f"Batch result {i}: {len(result.prompts)} prompts for '{result.raw_input}'")
    
    print("\nPrompt Crafter test completed successfully!")


if __name__ == "__main__":
    test_prompt_crafter() 