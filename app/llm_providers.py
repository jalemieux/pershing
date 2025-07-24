from typing import Dict, Any, Optional, List
import json
import time
from openai import OpenAI
from pydantic import BaseModel, Field
from .intent_analyzer import LLMProvider


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
            }
        } 