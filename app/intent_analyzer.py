from abc import ABC, abstractmethod
from datetime import datetime
from typing import Dict, List, Any, Optional
import json
import uuid


class IntentResult:
    """
    Structured intent analysis result.
    """
    
    def __init__(self, raw_message: str, **kwargs):
        self.id = kwargs.get('id', f"intent_{uuid.uuid4().hex[:8]}")
        self.timestamp = kwargs.get('timestamp', datetime.utcnow().isoformat())
        self.raw_message = raw_message
        self.classification = kwargs.get('classification', {})
        self.entities = kwargs.get('entities', [])
        self.slots = kwargs.get('slots', {})
        self.context = kwargs.get('context', {})
        self.constraints = kwargs.get('constraints', [])
        self.disambiguation = kwargs.get('disambiguation', {})
        self.fulfillment = kwargs.get('fulfillment', {})
        self.metadata = kwargs.get('metadata', {})
        self.natural_language_intent = kwargs.get('natural_language_intent', '')
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the intent result to a dictionary."""
        return {
            "intent": {
                "id": self.id,
                "timestamp": self.timestamp,
                "raw_message": self.raw_message,
                "classification": self.classification,
                "entities": self.entities,
                "slots": self.slots,
                "context": self.context,
                "constraints": self.constraints,
                "disambiguation": self.disambiguation,
                "fulfillment": self.fulfillment,
                "metadata": self.metadata,
                "natural_language_intent": self.natural_language_intent
            }
        }
    
    def to_json(self) -> str:
        """Convert the intent result to JSON string."""
        return json.dumps(self.to_dict(), indent=2)


class LLMProvider(ABC):
    """
    Abstract base class for LLM providers.
    """
    
    @abstractmethod
    def analyze_intent(self, message: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Analyze intent using the underlying LLM.
        
        Args:
            message: The natural language message to analyze
            context: Optional context information
            
        Returns:
            Dictionary containing the structured intent analysis
        """
        pass


class MockLLMProvider(LLMProvider):
    """
    Mock LLM provider for testing and development.
    """
    
    def analyze_intent(self, message: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Mock implementation that returns a structured intent analysis.
        """
        # Simple keyword-based classification for demonstration
        message_lower = message.lower()
        
        # Determine primary intent based on keywords
        if any(word in message_lower for word in ['book', 'reserve', 'schedule']):
            primary_intent = "book_flight"
            domain = "travel"
            category = "transaction"
        elif any(word in message_lower for word in ['weather', 'temperature']):
            primary_intent = "get_weather"
            domain = "weather"
            category = "information"
        elif any(word in message_lower for word in ['help', 'support']):
            primary_intent = "get_help"
            domain = "support"
            category = "information"
        else:
            primary_intent = "general_inquiry"
            domain = "general"
            category = "information"
        
        # Extract basic entities (simplified)
        entities = []
        if 'new york' in message_lower or 'nyc' in message_lower:
            entities.append({
                "type": "destination",
                "value": "New York",
                "normalized_value": "NYC",
                "confidence": 0.98
            })
        
        if 'tomorrow' in message_lower:
            entities.append({
                "type": "date",
                "value": "tomorrow",
                "normalized_value": "2025-07-24",
                "confidence": 0.92
            })
        
        if 'morning' in message_lower or 'am' in message_lower:
            entities.append({
                "type": "time",
                "value": "morning",
                "normalized_value": "morning",
                "confidence": 0.85
            })
        
        # Determine slots based on entities
        required_slots = {}
        optional_slots = {}
        missing_slots = []
        
        if primary_intent == "book_flight":
            if not any(e["type"] == "destination" for e in entities):
                missing_slots.append("destination")
            if not any(e["type"] == "date" for e in entities):
                missing_slots.append("departure_date")
        
        # Generate natural language intent description
        natural_language_intent = self._generate_natural_language_intent(
            primary_intent, domain, category, entities, message
        )
        
        # Build the result
        return {
            "classification": {
                "primary_intent": primary_intent,
                "domain": domain,
                "category": category,
                "confidence": 0.85
            },
            "entities": entities,
            "slots": {
                "required": required_slots,
                "optional": optional_slots,
                "missing": missing_slots
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
                "action_type": "placeholder",
                "service": "placeholder_service",
                "required_fields_complete": len(missing_slots) == 0,
                "next_steps": ["placeholder_step"]
            },
            "metadata": {
                "language": "en",
                "sentiment": "neutral",
                "urgency": "medium",
                "processing_time_ms": 100
            },
            "natural_language_intent": natural_language_intent
        }
    
    def _generate_natural_language_intent(self, primary_intent: str, domain: str, category: str, 
                                        entities: List[Dict], original_message: str) -> str:
        """
        Generate a natural language description of the intent.
        
        Args:
            primary_intent: The primary intent identifier
            domain: The domain of the intent
            category: The category of the intent
            entities: List of extracted entities
            original_message: The original user message
            
        Returns:
            Natural language description of the intent
        """
        # Extract key information from entities
        destinations = [e for e in entities if e["type"] == "destination"]
        dates = [e for e in entities if e["type"] == "date"]
        times = [e for e in entities if e["type"] == "time"]
        
        # Generate natural language descriptions based on intent type
        if primary_intent == "book_flight":
            if destinations and dates:
                return f"User wants to book a flight to {destinations[0]['value']} on {dates[0]['value']}"
            elif destinations:
                return f"User wants to book a flight to {destinations[0]['value']}"
            elif dates:
                return f"User wants to book a flight on {dates[0]['value']}"
            else:
                return "User wants to book a flight"
        
        elif primary_intent == "get_weather":
            if destinations:
                return f"User wants to know the weather in {destinations[0]['value']}"
            else:
                return "User wants to know the weather information"
        
        elif primary_intent == "get_help":
            return "User is seeking help or support"
        
        else:
            # For general inquiries, try to extract some context from the message
            if destinations:
                return f"User is making a general inquiry about {destinations[0]['value']}"
            elif dates:
                return f"User is making a general inquiry about {dates[0]['value']}"
            else:
                return "User is making a general inquiry"


class IntentAnalyzer:
    """
    Main intent analyzer class that provides abstraction to LLM providers.
    """
    
    def __init__(self, llm_provider: LLMProvider):
        """
        Initialize the intent analyzer with a specific LLM provider.
        
        Args:
            llm_provider: The LLM provider to use for intent analysis
        """
        self.llm_provider = llm_provider
    
    def analyze(self, message: str, context: Optional[Dict[str, Any]] = None) -> IntentResult:
        """
        Analyze the intent of a natural language message.
        
        Args:
            message: The natural language message to analyze
            context: Optional context information for the analysis
            
        Returns:
            IntentResult object containing the structured intent analysis
        """
        if not message or not message.strip():
            raise ValueError("Message cannot be empty")
        
        # Get the structured analysis from the LLM provider
        analysis_result = self.llm_provider.analyze_intent(message, context)
        
        # Create and return the IntentResult
        return IntentResult(
            raw_message=message,
            **analysis_result
        )
    
    def analyze_batch(self, messages: List[str], context: Optional[Dict[str, Any]] = None) -> List[IntentResult]:
        """
        Analyze multiple messages in batch.
        
        Args:
            messages: List of natural language messages to analyze
            context: Optional context information for the analysis
            
        Returns:
            List of IntentResult objects
        """
        results = []
        for message in messages:
            try:
                result = self.analyze(message, context)
                results.append(result)
            except Exception as e:
                # Log error and continue with other messages
                print(f"Error analyzing message '{message}': {str(e)}")
                continue
        
        return results


def get_intent_analyzer():
    """
    Get the intent analyzer instance from the current Flask app context.
    This is the recommended way to access the intent analyzer in route handlers.
    
    Returns:
        IntentAnalyzer instance
        
    Raises:
        RuntimeError: If called outside of Flask app context
    """
    from flask import current_app
    if not current_app:
        raise RuntimeError("get_intent_analyzer() must be called within Flask app context")
    return current_app.intent_analyzer


# Factory function for creating intent analyzers
def create_intent_analyzer(provider_type: str = "mock", **kwargs) -> IntentAnalyzer:
    """
    Factory function to create intent analyzers with different providers.
    
    Args:
        provider_type: Type of LLM provider ("mock", "openai", "anthropic", etc.)
        **kwargs: Additional arguments for the specific provider
        
    Returns:
        IntentAnalyzer instance
    """
    if provider_type == "mock":
        provider = MockLLMProvider()
    elif provider_type == "openai":
        from .llm_providers import OpenAIProvider
        api_key = kwargs.get('api_key')
        if not api_key:
            raise ValueError("OpenAI provider requires 'api_key' parameter")
        model = kwargs.get('model', 'gpt-4')
        provider = OpenAIProvider(api_key=api_key, model=model)
    elif provider_type == "anthropic":
        from .llm_providers import AnthropicProvider
        api_key = kwargs.get('api_key')
        if not api_key:
            raise ValueError("Anthropic provider requires 'api_key' parameter")
        model = kwargs.get('model', 'claude-3-sonnet-20240229')
        provider = AnthropicProvider(api_key=api_key, model=model)
    else:
        raise ValueError(f"Unknown provider type: {provider_type}")
    
    return IntentAnalyzer(provider) 