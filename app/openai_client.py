"""
Centralized OpenAI client for all OpenAI API calls in the application.

This module consolidates all OpenAI API interactions into a single, reusable client
that can be used across different parts of the application.
"""

import os
import json
import time
import base64
import logging
from typing import Dict, Any, Optional, List, Union
from openai import OpenAI
from pydantic import BaseModel
from flask import current_app

# Try to import backoff for retry logic, but make it optional
try:
    import backoff
    HAS_BACKOFF = True
except ImportError:
    HAS_BACKOFF = False
    # Define a simple retry decorator if backoff is not available
    def backoff_on_exception(*args, **kwargs):
        def decorator(func):
            return func
        return decorator
    backoff = type('backoff', (), {'on_exception': backoff_on_exception})


class OpenAIClient:
    """
    Centralized OpenAI client for handling all OpenAI API calls.
    
    This client provides methods for:
    - Intent analysis with structured outputs
    - Prompt generation and improvement
    - Chat completions
    - File processing
    """
    
    def __init__(self, api_key: Optional[str] = None, model: str = "gpt-4o", timeout: int = 60):
        """
        Initialize the OpenAI client.
        
        Args:
            api_key: OpenAI API key (will use environment variable if not provided)
            model: Default model to use for API calls
            timeout: Timeout in seconds for API calls
        """
        self.api_key = api_key or os.getenv('OPENAI_API_KEY')
        if not self.api_key:
            raise ValueError("OpenAI API key is required. Set OPENAI_API_KEY environment variable or pass api_key parameter.")
        
        self.model = model
        self.timeout = timeout
        self.client = OpenAI(
            api_key=self.api_key,
            timeout=timeout
        )
        self.logger = logging.getLogger(__name__)
    
    def _retry_decorator(self, func):
        """Apply retry logic if backoff is available."""
        if HAS_BACKOFF:
            return backoff.on_exception(
                backoff.expo,
                (Exception,),
                max_tries=3,
                max_time=30
            )(func)
        return func
    
    def analyze_intent(self, message: str, context: Optional[Dict[str, Any]] = None, model: Optional[str] = None) -> Dict[str, Any]:
        """
        Analyze intent using OpenAI's API with structured outputs.
        
        Args:
            message: The natural language message to analyze
            context: Optional context information
            model: Model to use (defaults to self.model)
            
        Returns:
            Dictionary containing the structured intent analysis
        """
        return self._retry_decorator(self._analyze_intent_impl)(message, context, model)
    
    def _analyze_intent_impl(self, message: str, context: Optional[Dict[str, Any]] = None, model: Optional[str] = None) -> Dict[str, Any]:
        """Implementation of intent analysis."""
        from .llm_providers import IntentAnalysisResult
        
        start_time = time.time()
        model_to_use = model or self.model
        
        # Build the input messages
        messages = [
            {"role": "system", "content": self._get_intent_analysis_system_prompt()},
            {"role": "user", "content": self._build_intent_analysis_prompt(message, context)}
        ]
        
        try:
            self.logger.info(f"Starting intent analysis with model {model_to_use}")
            
            response = self.client.responses.parse(
                model=model_to_use,
                input=messages,
                text_format=IntentAnalysisResult,
            )
            
            result = response.output_parsed
            
            # Convert to dictionary and add processing time
            result_dict = result.model_dump(mode="json")
            processing_time = int((time.time() - start_time) * 1000)
            result_dict["metadata"]["processing_time_ms"] = processing_time
            
            self.logger.info(f"Intent analysis completed in {processing_time}ms")
            return result_dict
            
        except Exception as e:
            self.logger.error(f"OpenAI intent analysis error: {str(e)}")
            # Return error response
            return self._create_error_response("intent_analysis", str(e))
    
    def generate_prompt(self, user_input: str, context: Optional[Dict[str, Any]] = None, model: Optional[str] = None) -> Dict[str, Any]:
        """
        Generate prompts using OpenAI's API with structured outputs.
        
        Args:
            user_input: The user's idea or request
            context: Optional context information
            model: Model to use (defaults to self.model)
            
        Returns:
            Dictionary containing the generated prompts and metadata
        """
        return self._retry_decorator(self._generate_prompt_impl)(user_input, context, model)
    
    def _generate_prompt_impl(self, user_input: str, context: Optional[Dict[str, Any]] = None, model: Optional[str] = None) -> Dict[str, Any]:
        """Implementation of prompt generation."""
        from .llm_providers import PromptGenerationResult
        
        start_time = time.time()
        model_to_use = model or self.model
        
        # Build the input messages
        messages = [
            {"role": "system", "content": self._get_prompt_generation_system_prompt()},
            {"role": "user", "content": self._build_prompt_generation_prompt(user_input, context)}
        ]
        
        try:
            self.logger.info(f"Starting prompt generation with model {model_to_use}")
            
            response = self.client.responses.parse(
                model=model_to_use,
                input=messages,
                text_format=PromptGenerationResult,
            )
            
            result = response.output_parsed
            
            # Convert structured result to format expected by PromptResult
            complete_prompt = self._build_complete_prompt(result)
            
            # Convert to dictionary format expected by PromptResult
            result_dict = {
                "prompts": [complete_prompt],
                "prompt_names": [result.name],
                "prompt_types": ["structured_complete"],
                "metadata": result.metadata.model_dump(mode="json"),
                "context": context or {}
            }
            
            # Add processing time
            processing_time = int((time.time() - start_time) * 1000)
            result_dict["metadata"]["processing_time_ms"] = processing_time
            
            self.logger.info(f"Prompt generation completed in {processing_time}ms")
            return result_dict
            
        except Exception as e:
            self.logger.error(f"OpenAI prompt generation error: {str(e)}")
            return self._create_error_response("prompt_generation", str(e))
    
    def improve_prompt(self, current_prompt: str, improvement_request: str, model: Optional[str] = None) -> str:
        """
        Improve an existing prompt based on natural language feedback.
        
        Args:
            current_prompt: The existing prompt to improve
            improvement_request: Natural language description of desired improvements
            model: Model to use (defaults to self.model)
            
        Returns:
            Improved prompt string
        """
        return self._retry_decorator(self._improve_prompt_impl)(current_prompt, improvement_request, model)
    
    def _improve_prompt_impl(self, current_prompt: str, improvement_request: str, model: Optional[str] = None) -> str:
        """Implementation of prompt improvement."""
        from .llm_providers import PromptImprovementResult
        
        start_time = time.time()
        model_to_use = model or self.model
        
        # Build the input messages for prompt improvement
        messages = [
            {"role": "system", "content": self._get_prompt_improvement_system_prompt()},
            {"role": "user", "content": self._build_improvement_prompt(current_prompt, improvement_request)}
        ]
        
        try:
            self.logger.info(f"Starting prompt improvement with model {model_to_use}")
            
            response = self.client.responses.parse(
                model=model_to_use,
                input=messages,
                text_format=PromptImprovementResult,
            )
            
            result = response.output_parsed
            
            # Convert structured result to improved prompt string
            improved_prompt = self._build_improved_prompt(result)
            
            processing_time = int((time.time() - start_time) * 1000)
            self.logger.info(f"Prompt improvement completed in {processing_time}ms")
            
            return improved_prompt
            
        except Exception as e:
            self.logger.error(f"OpenAI prompt improvement error: {str(e)}")
            return current_prompt  # Return original prompt on error
    
    def generate_chat_response(self, messages: List[Dict], file_path: Optional[str] = None, model: Optional[str] = None, temperature: float = 0.7, max_tokens: Optional[int] = None) -> Dict:
        """
        Generate a chat response using OpenAI's API.
        
        Args:
            messages: List of message dictionaries with 'role' and 'content'
            file_path: Optional path to a file to include in the request
            model: Model to use (defaults to self.model)
            temperature: Temperature for response generation (0.0-1.0)
            max_tokens: Maximum number of tokens to generate
            
        Returns:
            Dictionary containing the response and metadata
        """
        return self._retry_decorator(self._generate_chat_response_impl)(messages, file_path, model, temperature, max_tokens)
    
    def _generate_chat_response_impl(self, messages: List[Dict], file_path: Optional[str] = None, model: Optional[str] = None, temperature: float = 0.7, max_tokens: Optional[int] = None) -> Dict:
        """Implementation of chat response generation."""
        model_to_use = model or self.model
        
        try:
            self.logger.info(f"Starting chat response generation with model {model_to_use}")
            
            # Prepare messages for OpenAI
            openai_messages = []
            for msg in messages:
                if msg['role'] == 'system':
                    openai_messages.append({"role": "system", "content": msg['content']})
                elif msg['role'] == 'user':
                    if file_path and msg == messages[-1]:  # Last user message with file
                        # Handle file upload using the latest patterns
                        openai_messages.append(self._prepare_message_with_file(msg, file_path))
                    else:
                        openai_messages.append({"role": "user", "content": msg['content']})
                elif msg['role'] == 'assistant':
                    openai_messages.append({"role": "assistant", "content": msg['content']})
            
            # Prepare parameters
            params = {
                "model": model_to_use,
                "messages": openai_messages,
                "temperature": temperature,
            }
            
            if max_tokens:
                params["max_tokens"] = max_tokens
            
            # Make API call
            response = self.client.chat.completions.create(**params)
            
            # Extract response data
            content = response.choices[0].message.content
            usage = response.usage
            
            result = {
                'content': content,
                'model': model_to_use,
                'provider': 'openai',
                'tokens_used': usage.total_tokens if usage else None,
                'metadata': {
                    'finish_reason': response.choices[0].finish_reason,
                    'prompt_tokens': usage.prompt_tokens if usage else None,
                    'completion_tokens': usage.completion_tokens if usage else None
                }
            }
            
            self.logger.info(f"Chat response generated successfully, tokens used: {result['tokens_used']}")
            return result
            
        except Exception as e:
            self.logger.error(f"OpenAI Chat API error: {str(e)}")
            raise
    
    def _prepare_message_with_file(self, message: Dict, file_path: str) -> Dict:
        """
        Prepare a message with file content using the latest OpenAI patterns.
        
        Args:
            message: The message dictionary
            file_path: Path to the file to include
            
        Returns:
            Message dictionary with file content
        """
        try:
            with open(file_path, 'rb') as f:
                file_content = f.read()
            
            # Determine file type
            file_extension = os.path.splitext(file_path)[1].lower()
            
            if file_extension in ['.jpg', '.jpeg', '.png', '.gif', '.webp']:
                # Image file - use base64 encoding
                encoded_image = base64.b64encode(file_content).decode()
                
                return {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": message['content']},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/{file_extension[1:]};base64,{encoded_image}"
                            }
                        }
                    ]
                }
            else:
                # Text file - include as text content
                try:
                    file_text = file_content.decode('utf-8')
                except UnicodeDecodeError:
                    file_text = file_content.decode('utf-8', errors='ignore')
                
                return {
                    "role": "user",
                    "content": f"{message['content']}\n\nFile content:\n{file_text}"
                }
                
        except Exception as e:
            self.logger.error(f"Error preparing file content: {str(e)}")
            # Return original message if file processing fails
            return {"role": "user", "content": message['content']}
    
    # Private helper methods
    
    def _get_intent_analysis_system_prompt(self) -> str:
        """Get the system prompt for intent analysis."""
        return """You are an expert intent analyzer. Your job is to analyze user messages and extract structured intent information.

Analyze the user intent carefully and provide accurate classifications, entity extractions, and slot filling. Be precise with confidence scores and ensure all required fields are present."""
    
    def _build_intent_analysis_prompt(self, message: str, context: Optional[Dict[str, Any]] = None) -> str:
        """Build the prompt for intent analysis."""
        return f"""Analyze the following user message and extract structured intent information.

User message: "{message}"

Context: {json.dumps(context) if context else "None"}"""
    
    def _get_prompt_generation_system_prompt(self) -> str:
        """Get the system prompt for prompt generation."""
        return """You are an expert prompt engineer. Your task is to create clear, effective prompt for AI systems based on the user input. Write a well-structured prompt that will get the best results.

Follow these principles:
- Be specific and detailed about what you want
- Provide context and background information
- Include examples when helpful
- Specify the desired format, length, and style
- Use clear, direct language
- Break complex tasks into steps
- Include any constraints or requirements

Structure your prompt like this:
- Name: A descriptive, concise name for this prompt (max 50 characters)
- Role/Context: Define what role the AI should take
- Task: Clearly state what needs to be done
- Requirements: List specific criteria or constraints
- Format: Specify how the output should be structured
- Examples (if needed): Show what good output looks like"""
    
    def _build_prompt_generation_prompt(self, user_input: str, context: Optional[Dict[str, Any]] = None) -> str:
        """Build the user prompt for prompt generation."""
        return f"""Please write a prompt for: "{user_input}"

Generate a descriptive name for this prompt that captures its purpose and scope."""
    
    def _get_prompt_improvement_system_prompt(self) -> str:
        """Get the system prompt for prompt improvement."""
        return """You are an expert prompt engineer specializing in improving existing prompts. Your task is to enhance prompts based on user feedback while maintaining their core purpose and structure.

When improving prompts:
- Preserve the original intent and purpose
- Incorporate the requested improvements naturally
- Maintain clarity and effectiveness
- Keep the same general structure unless the improvement requires changes
- Ensure the improved prompt is more effective than the original

Analyze the current prompt and the improvement request carefully to create a better version."""
    
    def _build_improvement_prompt(self, current_prompt: str, improvement_request: str) -> str:
        """Build the prompt for prompt improvement."""
        return f"""Current Prompt:
{current_prompt}

Improvement Request:
{improvement_request}"""
    
    def _build_complete_prompt(self, result) -> str:
        """Convert structured PromptGenerationResult into a complete prompt string."""
        prompt_parts = []
        
        # Add role/context
        if hasattr(result, 'role_context') and result.role_context:
            prompt_parts.append(f"Role/Context: {result.role_context}")
        
        # Add task
        if hasattr(result, 'task') and result.task:
            prompt_parts.append(f"Task: {result.task}")
        
        # Add requirements
        if hasattr(result, 'requirements') and result.requirements:
            requirements_text = "\n".join([f"- {req}" for req in result.requirements])
            prompt_parts.append(f"Requirements:\n{requirements_text}")
        
        # Add format
        if hasattr(result, 'format') and result.format:
            prompt_parts.append(f"Format: {result.format}")
        
        # Add examples
        if hasattr(result, 'examples') and result.examples:
            examples_text = "\n".join([f"- {example}" for example in result.examples])
            prompt_parts.append(f"Examples:\n{examples_text}")
        
        return "\n\n".join(prompt_parts)
    
    def _build_improved_prompt(self, result) -> str:
        """Convert structured PromptImprovementResult into an improved prompt string."""
        if hasattr(result, 'improved_prompt') and result.improved_prompt:
            return result.improved_prompt
        return ""
    
    def _create_error_response(self, operation: str, error_message: str) -> Dict[str, Any]:
        """Create a standardized error response."""
        return {
            "error": True,
            "operation": operation,
            "error_message": error_message,
            "metadata": {
                "provider": "openai",
                "model": self.model,
                "processing_time_ms": 0
            }
        }


# Global client instance
_openai_client: Optional[OpenAIClient] = None


def get_openai_client(api_key: Optional[str] = None, model: Optional[str] = None, timeout: Optional[int] = None) -> OpenAIClient:
    """
    Get or create a global OpenAI client instance.
    
    Args:
        api_key: OpenAI API key (optional, will use environment variable if not provided)
        model: Model to use (optional, will use default if not provided)
        timeout: Timeout in seconds (optional, will use default if not provided)
        
    Returns:
        OpenAIClient instance
    """
    global _openai_client
    
    if _openai_client is None:
        _openai_client = OpenAIClient(
            api_key=api_key, 
            model=model or "gpt-4o",
            timeout=timeout or 60
        )
    
    return _openai_client


def reset_openai_client():
    """Reset the global OpenAI client instance (useful for testing)."""
    global _openai_client
    _openai_client = None
