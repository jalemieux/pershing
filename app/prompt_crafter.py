from abc import ABC, abstractmethod
from datetime import datetime
from typing import Dict, List, Any, Optional
import json
import uuid
from flask import current_app


class PromptResult:
    """
    Structured prompt generation result.
    """
    
    def __init__(self, raw_input: str, **kwargs):
        self.id = kwargs.get('id', f"prompt_{uuid.uuid4().hex[:8]}")
        self.timestamp = kwargs.get('timestamp', datetime.utcnow().isoformat())
        self.raw_input = raw_input
        self.prompts = kwargs.get('prompts', [])
        self.prompt_types = kwargs.get('prompt_types', [])
        self.prompt_names = kwargs.get('prompt_names', [])  # New field for prompt names
        self.metadata = kwargs.get('metadata', {})
        self.context = kwargs.get('context', {})
        # New field for multi-provider results
        self.provider_results = kwargs.get('provider_results', {})
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the prompt result to a dictionary."""
        return {
            "prompt_result": {
                "id": self.id,
                "timestamp": self.timestamp,
                "raw_input": self.raw_input,
                "prompts": self.prompts,
                "prompt_types": self.prompt_types,
                "prompt_names": self.prompt_names,  # Include prompt names
                "metadata": self.metadata,
                "context": self.context,
                "provider_results": self.provider_results
            }
        }
    
    def to_json(self) -> str:
        """Convert the prompt result to JSON string."""
        return json.dumps(self.to_dict(), indent=2)


class PromptLLMProvider(ABC):
    """
    Abstract base class for LLM providers used in prompt crafting.
    """
    
    @abstractmethod
    def generate_prompt(self, user_input: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Generate prompts using the underlying LLM.
        
        Args:
            user_input: The user's idea or request
            context: Optional context information
            
        Returns:
            Dictionary containing the generated prompts and metadata
        """
        pass


class MockPromptLLMProvider(PromptLLMProvider):
    """
    Mock LLM provider for prompt crafting - for testing and development.
    """
    
    def generate_prompt(self, user_input: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Mock implementation that returns structured prompt generation results.
        """
        # Generate 3 different types of prompts based on the input
        prompts = []
        prompt_types = []
        
        # Prompt 1: Direct and specific
        prompt1 = f"""Create a detailed and specific prompt for: {user_input}

Focus on being direct, clear, and actionable. Include specific details and requirements."""
        prompts.append(prompt1)
        prompt_types.append("direct_specific")
        
        # Prompt 2: Creative and exploratory
        prompt2 = f"""Generate a creative and exploratory prompt for: {user_input}

Focus on open-ended questions, multiple perspectives, and innovative approaches."""
        prompts.append(prompt2)
        prompt_types.append("creative_exploratory")
        
        # Prompt 3: Structured and systematic
        prompt3 = f"""Develop a structured and systematic prompt for: {user_input}

Focus on step-by-step approach, clear organization, and measurable outcomes."""
        prompts.append(prompt3)
        prompt_types.append("structured_systematic")
        
        return {
            "prompts": prompts,
            "prompt_types": prompt_types,
            "metadata": {
                "language": "en",
                "prompt_count": len(prompts),
                "processing_time_ms": 150,
                "provider": "mock"
            },
            "context": context or {}
        }


class MultiProviderPromptCrafter:
    """
    Enhanced prompt crafter that can use multiple LLM providers simultaneously.
    """
    
    def __init__(self, providers: Dict[str, PromptLLMProvider]):
        """
        Initialize the multi-provider prompt crafter.
        
        Args:
            providers: Dictionary mapping provider names to LLM provider instances
        """
        self.providers = providers
    
    def craft_prompts_multi_provider(self, user_input: str, context: Optional[Dict[str, Any]] = None) -> PromptResult:
        """
        Generate prompts using multiple providers simultaneously.
        
        Args:
            user_input: The user's idea or request
            context: Optional context information for the generation
            
        Returns:
            PromptResult object containing results from all providers
        """
        if not user_input or not user_input.strip():
            raise ValueError("User input cannot be empty")
        
        provider_results = {}
        all_prompts = []
        all_prompt_types = []
        all_prompt_names = [] # Initialize for prompt names
        
        # Generate prompts from each provider
        for provider_name, provider in self.providers.items():
            try:
                result = provider.generate_prompt(user_input, context)
                provider_results[provider_name] = result
                
                # Add prompts to the combined list
                if 'prompts' in result:
                    all_prompts.extend(result['prompts'])
                    # Add provider prefix to prompt types
                    prompt_types = result.get('prompt_types', [])
                    for prompt_type in prompt_types:
                        all_prompt_types.append(f"{provider_name}_{prompt_type}")
                
                # Add prompt names to the combined list
                if 'prompt_names' in result:
                    all_prompt_names.extend(result['prompt_names'])
                
            except Exception as e:
                # Log error and continue with other providers
                print(f"Error generating prompts with provider '{provider_name}': {str(e)}")
                provider_results[provider_name] = {
                    "error": str(e),
                    "prompts": [],
                    "prompt_types": [],
                    "prompt_names": [], # Ensure prompt_names is an empty list on error
                    "metadata": {
                        "provider": provider_name,
                        "error": True
                    }
                }
        
        # Create combined metadata
        combined_metadata = {
            "language": "en",
            "prompt_count": len(all_prompts),
            "processing_time_ms": sum(
                result.get('metadata', {}).get('processing_time_ms', 0) 
                for result in provider_results.values() 
                if 'error' not in result.get('metadata', {})
            ),
            "providers_used": list(self.providers.keys()),
            "successful_providers": [
                name for name, result in provider_results.items() 
                if 'error' not in result.get('metadata', {})
            ]
        }
        
        # Create and return the PromptResult
        return PromptResult(
            raw_input=user_input,
            prompts=all_prompts,
            prompt_types=all_prompt_types,
            prompt_names=all_prompt_names, # Pass prompt_names
            metadata=combined_metadata,
            context=context or {},
            provider_results=provider_results
        )


def get_multi_provider_prompt_crafter():
    """
    Get the multi-provider prompt crafter instance from the current Flask app context.
    
    Returns:
        MultiProviderPromptCrafter instance
        
    Raises:
        RuntimeError: If called outside of Flask app context
    """
    from flask import current_app
    if not current_app:
        raise RuntimeError("get_multi_provider_prompt_crafter() must be called within Flask app context")
    return current_app.multi_provider_prompt_crafter


# Factory function for creating multi-provider prompt crafters
def create_multi_provider_prompt_crafter(providers_config: Dict[str, Dict[str, Any]]) -> MultiProviderPromptCrafter:
    """
    Factory function to create multi-provider prompt crafters.
    
    Args:
        providers_config: Dictionary mapping provider names to their configuration
                        Example: {
                            "openai": {"api_key": "...", "model": "gpt-4"},
                            "anthropic": {"api_key": "...", "model": "claude-3-sonnet"}
                        }
        
    Returns:
        MultiProviderPromptCrafter instance
    """
    providers = {}
    
    for provider_name, config in providers_config.items():
        try:
            if provider_name == "openai":
                from .llm_providers import OpenAIPromptProvider
                api_key = config.get('api_key')
                if not api_key:
                    print(f"Warning: Skipping OpenAI provider - no API key provided")
                    continue
                model = config.get('model', 'gpt-4o-2024-08-06')
                providers[provider_name] = OpenAIPromptProvider(api_key=api_key, model=model)
                
            elif provider_name == "anthropic":
                from .llm_providers import AnthropicPromptProvider
                api_key = config.get('api_key')
                if not api_key:
                    print(f"Warning: Skipping Anthropic provider - no API key provided")
                    continue
                model = config.get('model', 'claude-3-sonnet-20240229')
                providers[provider_name] = AnthropicPromptProvider(api_key=api_key, model=model)
                
            
            else:
                print(f"Warning: Unknown provider type '{provider_name}', skipping")
                
        except Exception as e:
            print(f"Error initializing provider '{provider_name}': {str(e)}")
            continue
    
    if not providers:
        raise ValueError("No providers could be initialized")
    
    return MultiProviderPromptCrafter(providers) 