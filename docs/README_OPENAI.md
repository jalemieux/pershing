# OpenAI LLM Provider for Intent Analysis

This project includes a fully functional OpenAI LLM provider for intent analysis, capable of extracting structured intent information from natural language messages using OpenAI's latest structured output API.

## 🚀 Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Set Up OpenAI API Key

```bash
export OPENAI_API_KEY='your-openai-api-key-here'
```

Or create a `.env` file:
```
OPENAI_API_KEY=your-openai-api-key-here
```

### 3. Run the Demo

```bash
python app.py
```

Visit `http://localhost:5000` to see the intent analysis demo.

## 📁 Project Structure

```
pershing/
├── app/
│   ├── intent_analyzer.py      # Core intent analysis logic
│   ├── llm_providers.py        # OpenAI provider implementation
│   └── templates/
│       └── home.html           # Demo web interface
├── docs/
│   └── openai_provider_guide.md # Comprehensive guide
├── test_openai_provider.py     # Test script
├── config_openai_example.py    # Configuration example
└── app.py                      # Flask application
```

## 🔧 Configuration

### Environment Variables

- `OPENAI_API_KEY`: Your OpenAI API key (required)
- `OPENAI_MODEL`: Model to use (default: `gpt-4o-2024-08-06`)
- `INTENT_ANALYZER_PROVIDER`: Provider type (default: `mock`)

### Flask App Configuration

```python
from app.intent_analyzer import create_intent_analyzer

# Create OpenAI provider
analyzer = create_intent_analyzer(
    provider_type="openai",
    api_key="your-api-key",
    model="gpt-4o-2024-08-06"
)
```

## 🧪 Testing

### Run the Test Script

```bash
python test_openai_provider.py
```

This will test various message types and show detailed results.

### Example Test Messages

- "I want to book a flight to New York tomorrow morning"
- "What's the weather like in San Francisco?"
- "Can you help me with my account?"
- "Hello, how are you?"
- "I need to schedule a meeting for next week"
- "Book me a hotel in Paris for next weekend"
- "What's the traffic like on the 101?"
- "Set a reminder for my dentist appointment"

## 📊 Response Structure

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

## 🔄 API Usage

### Basic Usage

```python
from app.llm_providers import OpenAIProvider
from app.intent_analyzer import IntentAnalyzer

# Create provider
provider = OpenAIProvider(api_key="your-key", model="gpt-4o-2024-08-06")
analyzer = IntentAnalyzer(provider)

# Analyze message
result = analyzer.analyze("I want to book a flight to New York")

# Access results
print(f"Intent: {result.classification['primary_intent']}")
print(f"Confidence: {result.classification['confidence']}")
print(f"Entities: {result.entities}")
```

### Flask Integration

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

## 🛡️ Error Handling

The provider includes comprehensive error handling:

- **API Errors**: Handles OpenAI API errors gracefully
- **Validation Errors**: Pydantic validates all responses
- **Network Errors**: Handles connection issues
- **Fallback Responses**: Returns structured error responses

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

## 💰 Cost Considerations

- **GPT-4o-2024-08-06**: ~$0.005 per 1K tokens (input) + $0.015 per 1K tokens (output)
- **GPT-4o-mini**: ~$0.00015 per 1K tokens (input) + $0.0006 per 1K tokens (output)

Typical intent analysis requests use 200-500 tokens, costing $0.01-$0.05 per request with GPT-4o.

## 🔧 Advanced Configuration

### Structured Outputs

The provider uses OpenAI's new structured output API:

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

### Model Selection

```python
# Use GPT-4o for complex analysis
provider = OpenAIProvider(api_key="key", model="gpt-4o-2024-08-06")

# Use GPT-4o-mini for cost efficiency
provider = OpenAIProvider(api_key="key", model="gpt-4o-mini")
```

### Pydantic Models

The provider uses Pydantic models for validation:

```python
class IntentAnalysisResult(BaseModel):
    classification: Classification
    entities: List[Entity]
    slots: Slots
    # ... other fields
```

## 🚀 Deployment

### Environment Setup

1. Set your OpenAI API key:
```bash
export OPENAI_API_KEY='your-key'
```

2. Configure the provider type:
```bash
export INTENT_ANALYZER_PROVIDER='openai'
```

3. Run the application:
```bash
python app.py
```

### Production Considerations

- Use environment variables for sensitive data
- Implement rate limiting
- Monitor API usage and costs
- Set up proper error logging
- Consider caching for repeated queries

## 🔍 Troubleshooting

### Common Issues

1. **Invalid API Key**
   - Ensure your API key is correct
   - Check that you have sufficient credits

2. **Rate Limits**
   - Implement exponential backoff
   - Monitor your API usage

3. **Validation Errors**
   - The provider handles these automatically with Pydantic
   - Check the response format in the logs

4. **Network Issues**
   - Verify your internet connection
   - Check OpenAI API status

### Debug Mode

Enable debug logging:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## 📚 Documentation

- [OpenAI Provider Guide](docs/openai_provider_guide.md) - Comprehensive guide
- [Intent Analyzer Best Practices](docs/intent_analyzer_best_practices.md) - Best practices
- [Intent Analyzer Usage](docs/intent_analyzer_usage.md) - Usage examples

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License. 