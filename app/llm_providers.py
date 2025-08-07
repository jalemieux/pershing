from typing import Dict, Any, Optional, List
import json
import time
from openai import OpenAI
from pydantic import BaseModel, Field
from .intent_analyzer import LLMProvider
import re


class Entity(BaseModel):
    """Entity extracted from the message."""
    type: str = Field(description="Type of entity (e.g., destination, date, time, location, person)")
    value: str = Field(description="Original text value from the message")
    normalized_value: str = Field(description="Standardized/normalized value")
    confidence: float = Field(description="Confidence score between 0.0 and 1.0", ge=0.0, le=1.0)


class Classification(BaseModel):
    """Intent classification information."""
    primary_intent: str = Field(description="Primary intent (e.g., book_flight, get_weather, get_help, general_inquiry)")
    domain: str = Field(description="Domain (e.g., travel, weather, support, general)")
    category: str = Field(description="Category (e.g., transaction, information, command)")
    confidence: float = Field(description="Confidence score between 0.0 and 1.0", ge=0.0, le=1.0)

class Slot(BaseModel):
    """Key-value pair that captures information needed to execute the intent"""
    name: str = Field(description="Slot name")
    value: str = Field(description="Slot value")
    confidence: float = Field(description="Confidence score between 0.0 and 1.0", ge=0.0, le=1.0)

class Slots(BaseModel):
    """Key-value pairs that capture required and optional information needed to execute the intent"""
    mandatory: List[Slot] = Field(description="Mandatory slots")
    optional: List[Slot] = Field(description="Optional slots")
    missing: List[str] = Field(description="List of missing mandatory slots")




class Disambiguation(BaseModel):
    """Disambiguation information."""
    needed: bool = Field(description="Whether disambiguation is required")
    alternatives: List[str] = Field(description="Alternative interpretations")
    clarification_needed: List[str] = Field(description="Clarification questions needed")


class Fulfillment(BaseModel):
    """Fulfillment information."""
    action_type: str = Field(description="Action type (e.g., api_call, information, command)")
    service: str = Field(description="Service name (e.g., flight_booking_service, weather_service)")
    required_fields_complete: bool = Field(description="Whether all required fields are complete")
    next_steps: List[str] = Field(description="List of next steps to take")


class Metadata(BaseModel):
    """Metadata information."""
    language: str = Field(description="Language code (e.g., en, es, fr)")
    sentiment: str = Field(description="Sentiment (e.g., positive, negative, neutral)")
    urgency: str = Field(description="Urgency level (e.g., low, medium, high)")
    processing_time_ms: int = Field(description="Processing time in milliseconds")


class IntentAnalysisResult(BaseModel):
    """Complete intent analysis result using structured output."""
    classification: Classification = Field(description="Intent classification")
    entities: List[Entity] = Field(description="Extracted entities")
    slots: Slots = Field(description="Slot information")
    constraints: List[str] = Field(description="Constraints or limitations")
    disambiguation: Disambiguation = Field(description="Disambiguation information")
    fulfillment: Fulfillment = Field(description="Fulfillment information")
    metadata: Metadata = Field(description="Metadata information")
    natural_language_intent: str = Field(description="Description of the user's intent in natural language")


# Prompt Crafting Pydantic Models

class PromptMetadata(BaseModel):
    """Metadata for prompt generation."""
    language: str = Field(description="Language code (e.g., en, es, fr)")
    prompt_count: int = Field(description="Number of prompts generated")
    processing_time_ms: int = Field(description="Processing time in milliseconds")
    provider: str = Field(description="Provider used (e.g., openai, mock)")
    model: str = Field(description="Model used for generation")
    tokens_used: Optional[int] = Field(description="Number of tokens used", default=None)
    
    class Config:
        extra = "forbid"


class PromptGenerationResult(BaseModel):
    """Complete prompt generation result using structured output."""
    name: str = Field(description="A descriptive name for the generated prompt")
    role_context: str = Field(description="Role or context for the AI to take")
    task: str = Field(description="Clear statement of what needs to be done")
    requirements: List[str] = Field(description="Specific criteria or constraints")
    format: str = Field(description="How the output should be structured")
    examples: Optional[List[str]] = Field(description="Examples of good output", default=None)
    metadata: PromptMetadata = Field(description="Generation metadata")
    
    class Config:
        extra = "forbid"


class PromptImprovementResult(BaseModel):
    """Complete prompt improvement result using structured output."""
    improved_prompt: str = Field(description="The improved prompt")
    improvements_made: List[str] = Field(description="List of specific improvements made to the prompt")
    
    class Config:
        extra = "forbid"


class OpenAIProvider(LLMProvider):
    """
    OpenAI LLM provider for intent analysis using structured outputs.
    """
    
    def __init__(self, api_key: str, model: str = "gpt-4o-2024-08-06"):
        """
        Initialize OpenAI provider.
        
        Args:
            api_key: OpenAI API key
            model: Model to use for analysis
        """
        self.api_key = api_key
        self.model = model
        # Initialize the OpenAI client
        self.client = OpenAI(api_key=api_key)
    
    def analyze_intent(self, message: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Analyze intent using OpenAI's API with structured outputs.
        
        Args:
            message: The natural language message to analyze
            context: Optional context information
            
        Returns:
            Dictionary containing the structured intent analysis
        """
        start_time = time.time()
        
        
        # Build the input messages
        messages = [
            {"role": "system", "content": self._get_system_prompt()},
            {"role": "user", "content": self._build_prompt(message, context)}
        ]
        

        response = self.client.responses.parse(
            model="gpt-4o-2024-08-06",
            input=messages,
            text_format=IntentAnalysisResult,
        )

        result = response.output_parsed

        # Convert to dictionary and add processing time
        result_dict = result.model_dump(mode="json")
        processing_time = int((time.time() - start_time) * 1000)
        result_dict["metadata"]["processing_time_ms"] = processing_time
        
        return result_dict
        
    
    
    def _get_system_prompt(self) -> str:
        """Get the system prompt for the OpenAI API."""
        return """You are an expert intent analyzer. Your job is to analyze user messages and extract structured intent information.

Analyze the user intent carefully and provide accurate classifications, entity extractions, and slot filling. Be precise with confidence scores and ensure all required fields are present.
"""
# The analysis should include:
# - Classification: primary intent, domain, category, and confidence
# - Entities: extracted entities with type, value, normalized_value, and confidence
# - Slots: required, optional, and missing slots
# - Context: user preferences, conversation history, and session data
# - Constraints: any constraints or limitations
# - Disambiguation: whether disambiguation is needed and alternatives
# - Fulfillment: action type, service, completion status, and next steps
# - Metadata: language, sentiment, urgency, and processing info"""
    
    def _build_prompt(self, message: str, context: Optional[Dict[str, Any]] = None) -> str:
        """Build the prompt for the LLM."""
        prompt = f"""Analyze the following user message and extract structured intent information.

User message: "{message}"

Context: {json.dumps(context) if context else "None"}
"""
# Please analyze the intent carefully and provide accurate classifications, entity extractions, and slot filling. Consider the following:

# 1. **Classification**: Determine the primary intent, domain, category, and confidence level
# 2. **Entities**: Extract relevant entities like destinations, dates, times, locations, people, etc.
# 3. **Slots**: Identify required and optional slots, and note any missing required information
# 4. **Context**: Consider user preferences, conversation history, and session data
# 5. **Fulfillment**: Determine the appropriate action type, service, and next steps
# 6. **Metadata**: Analyze language, sentiment, and urgency

# Be precise and accurate in your analysis. Use appropriate confidence scores and ensure all required fields are present."""
        return prompt
    
    


class AnthropicProvider(LLMProvider):
    """
    Anthropic Claude LLM provider for intent analysis.
    """
    
    def __init__(self, api_key: str, model: str = "claude-3-sonnet-20240229"):
        """
        Initialize Anthropic provider.
        
        Args:
            api_key: Anthropic API key
            model: Model to use for analysis
        """
        self.api_key = api_key
        self.model = model
        # Note: In a real implementation, you would import and use the Anthropic client
        # import anthropic
        # self.client = anthropic.Anthropic(api_key=api_key)
    
    def analyze_intent(self, message: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Analyze intent using Anthropic's Claude API.
        
        Args:
            message: The natural language message to analyze
            context: Optional context information
            
        Returns:
            Dictionary containing the structured intent analysis
        """
        # Implementation would be similar to OpenAI but using Anthropic's API
        # For now, return a mock response
        return {
            "classification": {
                "primary_intent": "general_inquiry",
                "domain": "general",
                "category": "information",
                "confidence": 0.80
            },
            "entities": [],
            "slots": {
                "required": {},
                "optional": {},
                "missing": []
            },
            "context": {
                "user_preferences": {},
                "conversation_history": [],
                "session_data": {
                    "user_location": "unknown",
                    "device_type": "desktop"
                }
            },
            "constraints": [],
            "disambiguation": {
                "required": False,
                "alternatives": [],
                "clarification_needed": []
            },
            "fulfillment": {
                "action_type": "information",
                "service": "general_service",
                "required_fields_complete": True,
                "next_steps": ["provide_information"]
            },
            "metadata": {
                "language": "en",
                "sentiment": "neutral",
                "urgency": "medium",
                "processing_time_ms": 150
            },
            "natural_language_intent": "User is making a general inquiry"
        } 

# Prompt Crafter LLM Providers

class OpenAIPromptProvider:
    """
    OpenAI LLM provider for prompt crafting using structured outputs.
    """
    
    def __init__(self, api_key: str, model: str = "gpt-4o-2024-08-06"):
        """
        Initialize OpenAI prompt provider.
        
        Args:
            api_key: OpenAI API key
            model: Model to use for prompt generation
        """
        self.api_key = api_key
        self.model = model
        # Initialize the OpenAI client
        self.client = OpenAI(api_key=api_key)
    
    def generate_prompt(self, user_input: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Generate prompts using OpenAI's API with structured outputs.
        
        Args:
            user_input: The user's idea or request
            context: Optional context information
            
        Returns:
            Dictionary containing the generated prompts and metadata
        """
        start_time = time.time()
        
        # Build the input messages
        messages = [
            {"role": "system", "content": self._get_system_prompt()},
            {"role": "user", "content": self._build_prompt(user_input, context)}
        ]
        
        # Use structured output parsing
        response = self.client.responses.parse(
            model=self.model,
            input=messages,
            text_format=PromptGenerationResult,
        )
        
        result = response.output_parsed
        
        # Convert structured result to format expected by PromptResult
        # Create a complete prompt from the structured components
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
        
        return result_dict
            
       
       
    
    def _get_system_prompt(self) -> str:
        """Get the system prompt for prompt generation."""
        return """
        You are an expert prompt engineer. Your task is to create clear, effective prompt for AI systems base don the user input. Write a well-structured prompt that will get the best results.
Follow these principles:

Be specific and detailed about what you want
Provide context and background information
Include examples when helpful
Specify the desired format, length, and style
Use clear, direct language
Break complex tasks into steps
Include any constraints or requirements

Structure your prompt like this:

Name: A descriptive, concise name for this prompt (max 50 characters)
Role/Context: Define what role the AI should take
Task: Clearly state what needs to be done
Requirements: List specific criteria or constraints
Format: Specify how the output should be structured
Examples (if needed): Show what good output looks like
"""    
    def _build_prompt(self, user_input: str, context: Optional[Dict[str, Any]] = None) -> str:
        """Build the user prompt for the LLM."""
        prompt = f"""Please write a prompt for: "{user_input}"

Generate a descriptive name for this prompt that captures its purpose and scope."""
        return prompt
    
    def _build_complete_prompt(self, result: PromptGenerationResult) -> str:
        """Convert structured PromptGenerationResult into a complete prompt string."""
        prompt_parts = []
        
        # Add role/context
        if result.role_context:
            prompt_parts.append(f"Role/Context: {result.role_context}")
        
        # Add task
        if result.task:
            prompt_parts.append(f"Task: {result.task}")
        
        # Add requirements
        if result.requirements:
            requirements_text = "\n".join([f"- {req}" for req in result.requirements])
            prompt_parts.append(f"Requirements:\n{requirements_text}")
        
        # Add format
        if result.format:
            prompt_parts.append(f"Format: {result.format}")
        
        # Add examples
        if result.examples:
            examples_text = "\n".join([f"- {example}" for example in result.examples])
            prompt_parts.append(f"Examples:\n{examples_text}")
        
        return "\n\n".join(prompt_parts)
    
    def improve_prompt(self, current_prompt: str, improvement_request: str) -> str:
        """
        Improve an existing prompt based on natural language feedback.
        
        Args:
            current_prompt: The existing prompt to improve
            improvement_request: Natural language description of desired improvements
            
        Returns:
            Improved prompt string
        """
        start_time = time.time()
        
        # Build the input messages for prompt improvement
        messages = [
            {"role": "system", "content": self._get_improvement_system_prompt()},
            {"role": "user", "content": self._build_improvement_prompt(current_prompt, improvement_request)}
        ]
        
        # Use structured output parsing for improvement
        response = self.client.responses.parse(
            model=self.model,
            input=messages,
            text_format=PromptImprovementResult,
        )
        
        result = response.output_parsed
        
        # Convert structured result to improved prompt string
        improved_prompt = self._build_improved_prompt(result)
        
        processing_time = int((time.time() - start_time) * 1000)
        print(f"✅ OpenAI provider improved prompt in {processing_time}ms")
        
        return improved_prompt
    
    def _get_improvement_system_prompt(self) -> str:
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
        return f"""
Current Prompt:
{current_prompt}

Improvement Request:
{improvement_request}

"""
    
    def _build_improved_prompt(self, result: 'PromptImprovementResult') -> str:
        """Convert structured PromptImprovementResult into an improved prompt string."""
        prompt_parts = []

        if result.improved_prompt:
            prompt_parts.append(f"{result.improved_prompt}")
        
   
         
        return "\n\n".join(prompt_parts)
    
    


class AnthropicPromptProvider:
    """
    Anthropic Claude LLM provider for prompt crafting using structured outputs.
    """
    
    def __init__(self, api_key: str, model: str = "claude-3-sonnet-20240229"):
        """
        Initialize Anthropic prompt provider.
        
        Args:
            api_key: Anthropic API key
            model: Model to use for prompt generation
        """
        self.api_key = api_key
        self.model = model
        import anthropic
        self.client = anthropic.Anthropic(api_key=api_key)
        
    
    def generate_prompt(self, user_input: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Generate prompts using Anthropic's Claude API.
        
        Args:
            user_input: The user's idea or request
            context: Optional context information
            
        Returns:
            Dictionary containing the generated prompts and metadata
        """
        start_time = time.time()
        
        
        system_prompt = """
You are an expert prompt engineer. Your task is to create a single, clear, and effective prompt for AI systems based on the user input. Write one well-structured prompt that will get the best results.

Follow these principles:
- Be specific and detailed about what you want
- Provide context and background information
- Include examples when helpful
- Specify the desired format, length, and style
- Use clear, direct language
- Break complex tasks into steps
- Include any constraints or requirements

Create ONE comprehensive prompt that includes:
- Name: A descriptive, concise name for this prompt (max 50 characters)
- Role/Context: Define what role the AI should take
- Task: Clearly state what needs to be done
- Requirements: List specific criteria or constraints
- Format: Specify how the output should be structured
- Examples (if needed): Show what good output looks like

Return only the final prompt without any numbering, section headers, or multiple approaches."""
        user_prompt = f"""Please write a prompt for: "{user_input}"""

        # Call Claude API
        response = self.client.messages.create(
            model=self.model,
            #max_tokens=2000,
            system=system_prompt,
            messages=[
                {
                    "role": "user",
                    "content": user_prompt
                }
            ]
        )
        
        print(f"📥 Claude API response received")
        
        # Parse the response to extract a single prompt
        content = response.content[0].text
        prompt, prompt_name = self._parse_claude_response(content)
        
        processing_time = int((time.time() - start_time) * 1000)
        
        print(f"✅ Anthropic provider generated 1 prompt in {processing_time}ms")
        
        return {
            "prompts": [prompt],
            "prompt_names": [prompt_name],
            "prompt_types": ["comprehensive_single"],
            "metadata": {
                "language": "en",
                "prompt_count": 1,
                "processing_time_ms": processing_time,
                "provider": "anthropic",
                "model": self.model,
                "tokens_used": response.usage.input_tokens + response.usage.output_tokens if hasattr(response, 'usage') else None
            },
            "context": context or {}
        }
            
        
            
    
    def _parse_claude_response(self, content: str) -> tuple[str, str]:
        """
        Parse Claude's response to extract a single prompt and its name.
        
        Args:
            content: Raw response from Claude API
            
        Returns:
            Tuple of (prompt_text, prompt_name)
        """
        # Clean up the response
        content = content.strip()
        lines = content.split('\n')
        
        # Initialize variables
        prompt_name = "Claude Generated Prompt"
        cleaned_lines = []
        name_extracted = False
        
        for i, line in enumerate(lines):
            line = line.strip()
            
            # Skip empty lines at the beginning
            if not line and not cleaned_lines:
                continue
            
            # Try to extract name from the first non-empty line
            if not name_extracted and line and 'name:' in line.lower():
                # Extract name from this line
                if ':' in line:
                    prompt_name = line.split(':', 1)[1].strip()
                    name_extracted = True
                    # Don't add this line to the cleaned content
                    continue
            
            # Remove numbered sections (1., 2., 3., etc.)
            if re.match(r'^\d+\.', line):
                line = re.sub(r'^\d+\.\s*', '', line)
            
            # Remove section headers like "Prompt 1:", "Approach:", etc.
            if re.match(r'^(?:Prompt|Approach|Method)\s*\d*:', line, flags=re.IGNORECASE):
                line = re.sub(r'^(?:Prompt|Approach|Method)\s*\d*:\s*', '', line, flags=re.IGNORECASE)
            
            # Skip lines that are just section headers
            if line.lower() in ['role/context:', 'task:', 'requirements:', 'format:', 'examples:']:
                continue
                
            cleaned_lines.append(line)
        
        # Join the cleaned lines into a single prompt
        prompt = '\n'.join(cleaned_lines).strip()
        
        # If no explicit name was found, try to extract from role/context section
        if not name_extracted:
            for line in cleaned_lines:
                if 'role/context:' in line.lower() and ':' in line:
                    context_part = line.split(':', 1)[1].strip()
                    # Create a name from the first few words of context
                    words = context_part.split()[:4]
                    if words:
                        prompt_name = " ".join(words).title()
                        if len(prompt_name) > 50:
                            prompt_name = prompt_name[:47] + "..."
                    break
        
        # If the prompt is empty or too short, provide a fallback
        if not prompt or len(prompt) < 50:
            print("⚠️ Generated prompt is too short, using fallback")
            prompt = "Create a comprehensive and well-structured prompt for the given input that includes role context, task description, requirements, and format specifications."
        
        print(f"✅ Generated single prompt: {len(prompt)} characters with name: {prompt_name}")
        
        return prompt, prompt_name
    
    def improve_prompt(self, current_prompt: str, improvement_request: str) -> str:
        """
        Improve an existing prompt based on natural language feedback using Claude.
        
        Args:
            current_prompt: The existing prompt to improve
            improvement_request: Natural language description of desired improvements
            
        Returns:
            Improved prompt string
        """
        start_time = time.time()
        
        system_prompt = """You are an expert prompt engineer specializing in improving existing prompts. Your task is to enhance prompts based on user feedback while maintaining their core purpose and structure.

When improving prompts:
- Preserve the original intent and purpose
- Incorporate the requested improvements naturally
- Maintain clarity and effectiveness
- Keep the same general structure unless the improvement requires changes
- Ensure the improved prompt is more effective than the original

Analyze the current prompt and the improvement request carefully to create a better version.

Return only the improved prompt without any explanations or meta-commentary."""
        
        user_prompt = f"""Please improve the following prompt based on the user's request.

Current Prompt:
{current_prompt}

Improvement Request:
{improvement_request}

Please provide an improved version that addresses the user's request while maintaining the prompt's core purpose and effectiveness."""

        # Call Claude API
        response = self.client.messages.create(
            model=self.model,
            max_tokens=2000,
            system=system_prompt,
            messages=[
                {
                    "role": "user",
                    "content": user_prompt
                }
            ]
        )
        
        # Extract the improved prompt from Claude's response
        improved_prompt = response.content[0].text.strip()
        
        processing_time = int((time.time() - start_time) * 1000)
        print(f"✅ Anthropic provider improved prompt in {processing_time}ms")
        
        return improved_prompt