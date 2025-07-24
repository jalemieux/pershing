# Intent Analyzer Documentation

## Overview

The Intent Analyzer provides an abstraction layer for LLM-based intent analysis. It takes natural language input and returns structured intent data that can be used for conversation management, task fulfillment, and user experience optimization.

## Architecture

The system consists of several key components:

1. **IntentAnalyzer**: Main class that provides the public API
2. **LLMProvider**: Abstract base class for LLM implementations
3. **IntentResult**: Structured result object containing the analysis
4. **Factory Functions**: Easy creation of analyzers with different providers

## Quick Start

### Basic Usage

```python
from app.intent_analyzer import create_intent_analyzer

# Create an analyzer with the mock provider
analyzer = create_intent_analyzer('mock')

# Analyze a message
result = analyzer.analyze("Book me a flight to New York for tomorrow morning")

# Access the structured result
print(f"Intent: {result.classification['primary_intent']}")
print(f"Confidence: {result.classification['confidence']}")
print(f"Entities: {len(result.entities)}")
```

### Using Different Providers

```python
# Mock provider (for testing)
analyzer = create_intent_analyzer('mock')

# OpenAI provider (requires API key)
analyzer = create_intent_analyzer('openai', api_key='your-api-key', model='gpt-4')

# Anthropic provider (requires API key)
analyzer = create_intent_analyzer('anthropic', api_key='your-api-key', model='claude-3-sonnet-20240229')
```

## Intent Result Structure

The `IntentResult` object contains the following structured data:

```json
{
  "intent": {
    "id": "intent_12345",
    "timestamp": "2025-07-23T14:30:00Z",
    "raw_message": "Book me a flight to New York for tomorrow morning",
    
    "classification": {
      "primary_intent": "book_flight",
      "domain": "travel",
      "category": "transaction",
      "confidence": 0.95
    },
    
    "entities": [
      {
        "type": "destination",
        "value": "New York",
        "normalized_value": "NYC",
        "confidence": 0.98
      }
    ],
    
    "slots": {
      "required": {
        "destination": "NYC",
        "departure_date": "2025-07-24"
      },
      "optional": {
        "departure_time": "< 10:00"
      },
      "missing": [
        "origin_location"
      ]
    },
    
    "context": {
      "user_preferences": {},
      "conversation_history": [],
      "session_data": {
        "user_location": "San Francisco",
        "device_type": "mobile"
      }
    },
    
    "constraints": [],
    "disambiguation": {
      "required": false,
      "alternatives": [],
      "clarification_needed": []
    },
    
    "fulfillment": {
      "action_type": "api_call",
      "service": "flight_booking_service",
      "required_fields_complete": false,
      "next_steps": [
        "request_origin_location",
        "search_flights"
      ]
    },
    
    "metadata": {
      "language": "en",
      "sentiment": "neutral",
      "urgency": "medium",
      "processing_time_ms": 145
    }
  }
}
```

## API Reference

### IntentAnalyzer

#### Methods

- `analyze(message: str, context: Optional[Dict] = None) -> IntentResult`
  - Analyzes a single message
  - Returns structured intent result

- `analyze_batch(messages: List[str], context: Optional[Dict] = None) -> List[IntentResult]`
  - Analyzes multiple messages
  - Returns list of structured intent results

### IntentResult

#### Properties

- `id`: Unique identifier for the intent
- `timestamp`: ISO timestamp of analysis
- `raw_message`: Original input message
- `classification`: Intent classification data
- `entities`: Extracted entities
- `slots`: Required/optional/missing slots
- `context`: User and session context
- `constraints`: Business rules and constraints
- `disambiguation`: Clarification needs
- `fulfillment`: Action and service information
- `metadata`: Processing metadata

#### Methods

- `to_dict() -> Dict`: Convert to dictionary
- `to_json() -> str`: Convert to JSON string

## Creating Custom LLM Providers

To add a new LLM provider, implement the `LLMProvider` abstract base class:

```python
from app.intent_analyzer import LLMProvider
from typing import Dict, Any, Optional

class CustomLLMProvider(LLMProvider):
    def __init__(self, api_key: str, model: str = "custom-model"):
        self.api_key = api_key
        self.model = model
    
    def analyze_intent(self, message: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        # Your LLM-specific implementation here
        # Return structured data matching the IntentResult format
        
        return {
            "classification": {
                "primary_intent": "custom_intent",
                "domain": "custom_domain",
                "category": "information",
                "confidence": 0.85
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
                "action_type": "custom_action",
                "service": "custom_service",
                "required_fields_complete": True,
                "next_steps": ["custom_step"]
            },
            "metadata": {
                "language": "en",
                "sentiment": "neutral",
                "urgency": "medium",
                "processing_time_ms": 100
            }
        }
```

Then update the factory function to support your provider:

```python
# In app/intent_analyzer.py, update create_intent_analyzer function
elif provider_type == "custom":
    from .llm_providers import CustomLLMProvider
    api_key = kwargs.get('api_key')
    if not api_key:
        raise ValueError("Custom provider requires 'api_key' parameter")
    model = kwargs.get('model', 'custom-model')
    provider = CustomLLMProvider(api_key=api_key, model=model)
```

## Integration with Flask App

The intent analyzer is already integrated into the Flask application. The `/intent-collection/analyze` endpoint uses the mock provider by default:

```python
# In app.py
intent_analyzer = create_intent_analyzer('mock')
intent_result = intent_analyzer.analyze(user_input)
```

To use a different provider, modify the endpoint:

```python
# For OpenAI
intent_analyzer = create_intent_analyzer('openai', api_key=os.getenv('OPENAI_API_KEY'))

# For Anthropic
intent_analyzer = create_intent_analyzer('anthropic', api_key=os.getenv('ANTHROPIC_API_KEY'))
```

## Testing

Run the test suite to verify functionality:

```bash
python test_intent_analyzer.py
```

## Error Handling

The system includes comprehensive error handling:

- Empty or None messages are rejected
- API failures return fallback responses
- Batch processing continues on individual failures
- All errors are logged for debugging

## Performance Considerations

- Processing time is tracked in metadata
- Batch processing is available for multiple messages
- Context can be passed to improve analysis quality
- Provider-specific optimizations can be implemented

## Future Enhancements

- Real OpenAI and Anthropic API integrations
- Caching for repeated analyses
- Conversation history tracking
- Custom entity extraction
- Multi-language support
- Confidence threshold filtering 