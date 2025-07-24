# OpenAI LLM Provider Guide

This guide explains how to use the OpenAI LLM provider for intent analysis in the Pershing application.

## Overview

The OpenAI provider integrates with OpenAI's GPT models to perform sophisticated intent analysis using structured outputs. It uses Pydantic models and the new `responses.parse()` API to ensure reliable, structured responses.

## Setup

### 1. Install Dependencies

The OpenAI package is already included in `requirements.txt`:

```bash
pip install -r requirements.txt
```

### 2. Set Up API Key

Set your OpenAI API key as an environment variable:

```bash
export OPENAI_API_KEY='your-openai-api-key-here'
```

Or add it to your `.env` file:

```
OPENAI_API_KEY=your-openai-api-key-here
```

### 3. Configure the Provider

In your Flask application, configure the OpenAI provider:

```python
from app.intent_analyzer import create_intent_analyzer

# Create OpenAI provider
analyzer = create_intent_analyzer(
    provider_type="openai",
    api_key="your-api-key",
    model="gpt-4o-2024-08-06"  # or "gpt-4o-mini"
)
```

## Usage

### Basic Usage

```python
from app.llm_providers import OpenAIProvider
from app.intent_analyzer import IntentAnalyzer

# Create the provider
provider = OpenAIProvider(api_key="your-api-key", model="gpt-4o-2024-08-06")
analyzer = IntentAnalyzer(provider)

# Analyze a message
result = analyzer.analyze("I want to book a flight to New York tomorrow")

# Access the results
print(f"Intent: {result.classification['primary_intent']}")
print(f"Confidence: {result.classification['confidence']}")
print(f"Entities: {result.entities}")
```

### Using with Flask

```python
from flask import Flask, request, jsonify
from app.intent_analyzer import get_intent_analyzer

app = Flask(__name__)

@app.route('/analyze', methods=['POST'])
def analyze_intent():
    data = request.get_json()
    message = data.get('message', '')
    
    analyzer = get_intent_analyzer()
    result = analyzer.analyze(message)
    
    return jsonify(result.to_dict())
```

## Configuration Options

### Model Selection

- `gpt-4o-2024-08-06`: Latest GPT-4 model with structured output support
- `gpt-4o-mini`: Faster and cheaper, good for most use cases
- `gpt-4-turbo`: Balanced performance and cost

### Structured Outputs

The provider uses OpenAI's new structured output API with Pydantic models:

```python
response = client.responses.parse(
    model="gpt-4o-2024-08-06",
    input=messages,
    text_format=IntentAnalysisResult
)

result = response.output_parsed
```

This ensures:
- **Reliable JSON parsing**: No manual JSON parsing required
- **Type validation**: Pydantic validates all fields
- **Consistent structure**: Always returns the expected format
- **Error handling**: Automatic validation and error reporting

## Response Structure

The OpenAI provider returns structured data validated by Pydantic models:

```json
{
  "intent": {
    "id": "intent_abc123",
    "timestamp": "2024-01-15T10:30:00",
    "raw_message": "I want to book a flight to New York",
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
      "required": {"destination": "NYC"},
      "optional": {},
      "missing": ["departure_date"]
    },
    "fulfillment": {
      "action_type": "api_call",
      "service": "flight_booking_service",
      "required_fields_complete": false,
      "next_steps": ["collect_missing_slots"]
    },
    "metadata": {
      "language": "en",
      "sentiment": "neutral",
      "urgency": "medium",
      "processing_time_ms": 1250
    }
  }
}
```

## Error Handling

The provider includes comprehensive error handling:

- **API Errors**: Handles OpenAI API errors gracefully
- **Validation Errors**: Pydantic validates all responses
- **Network Errors**: Handles connection issues
- **Fallback Responses**: Returns structured error responses when issues occur

### Error Response Format

```json
{
  "intent": {
    "classification": {
      "primary_intent": "error",
      "domain": "system",
      "category": "error",
      "confidence": 0.0
    },
    "metadata": {
      "error": "OpenAI API error: Invalid API key"
    }
  }
}
```

## Testing

Run the test script to verify your setup:

```bash
python test_openai_provider.py
```

The test script includes:
- Basic functionality testing
- Structured output validation
- Model compatibility testing
- Error handling validation

Make sure your `OPENAI_API_KEY` environment variable is set before running the test.

## Cost Considerations

- **GPT-4o-2024-08-06**: ~$0.005 per 1K tokens (input) + $0.015 per 1K tokens (output)
- **GPT-4o-mini**: ~$0.00015 per 1K tokens (input) + $0.0006 per 1K tokens (output)

Typical intent analysis requests use 200-500 tokens, costing $0.01-$0.05 per request with GPT-4o.

## Best Practices

1. **Use Appropriate Models**: Use GPT-4o-mini for most use cases, GPT-4o for complex analysis
2. **Monitor Usage**: Track API usage to manage costs
3. **Error Handling**: Always handle API errors gracefully
4. **Caching**: Consider caching results for repeated queries
5. **Rate Limiting**: Implement rate limiting to avoid API limits

## Troubleshooting

### Common Issues

1. **Invalid API Key**: Ensure your API key is correct and has sufficient credits
2. **Rate Limits**: Implement exponential backoff for rate limit errors
3. **Validation Errors**: The provider handles these automatically with Pydantic
4. **Network Issues**: Check your internet connection and OpenAI API status

### Debug Mode

Enable debug logging to see detailed API interactions:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## Migration from Mock Provider

To switch from the mock provider to OpenAI:

1. Update your configuration:
```python
# Before
analyzer = create_intent_analyzer(provider_type="mock")

# After
analyzer = create_intent_analyzer(
    provider_type="openai",
    api_key="your-api-key",
    model="gpt-4o-2024-08-06"
)
```

2. Test with a small set of messages first
3. Monitor costs and performance
4. Gradually roll out to production

## Security Considerations

1. **API Key Security**: Never commit API keys to version control
2. **Environment Variables**: Use environment variables for sensitive data
3. **Rate Limiting**: Implement rate limiting to prevent abuse
4. **Input Validation**: Validate user input before sending to API
5. **Error Messages**: Don't expose sensitive information in error messages

## Advanced Configuration

### Custom Pydantic Models

You can customize the Pydantic models in `llm_providers.py`:

```python
class CustomEntity(BaseModel):
    type: str = Field(description="Custom entity type")
    value: str = Field(description="Entity value")
    # Add custom fields as needed
```

### Model Selection

```python
# Use GPT-4o for complex analysis
provider = OpenAIProvider(api_key="key", model="gpt-4o-2024-08-06")

# Use GPT-4o-mini for cost efficiency
provider = OpenAIProvider(api_key="key", model="gpt-4o-mini")
```

### Structured Output Configuration

The provider automatically uses the new structured output API:

```python
response = client.responses.parse(
    model=self.model,
    input=messages,
    text_format=IntentAnalysisResult
)
```

This ensures reliable, validated responses without manual JSON parsing. 