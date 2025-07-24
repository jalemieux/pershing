# Intent Analyzer Best Practices

## Overview

This document outlines the best practices for using the Intent Analyzer in Flask applications, covering different initialization patterns and their trade-offs.

## Recommended Approach: Singleton Pattern

### ✅ **Best Practice: App-Level Singleton**

Initialize the intent analyzer once during app creation and store it in the app context.

```python
# In app/__init__.py
def create_app(config_class=None):
    app = Flask(__name__)
    
    # ... other initialization code ...
    
    # Initialize Intent Analyzer as singleton
    def init_intent_analyzer():
        provider_type = os.getenv('INTENT_PROVIDER', 'mock')
        
        if provider_type == 'openai':
            api_key = os.getenv('OPENAI_API_KEY')
            model = os.getenv('OPENAI_MODEL', 'gpt-4')
            return create_intent_analyzer('openai', api_key=api_key, model=model)
        elif provider_type == 'anthropic':
            api_key = os.getenv('ANTHROPIC_API_KEY')
            model = os.getenv('ANTHROPIC_MODEL', 'claude-3-sonnet-20240229')
            return create_intent_analyzer('anthropic', api_key=api_key, model=model)
        else:
            return create_intent_analyzer('mock')
    
    # Store intent analyzer in app context
    app.intent_analyzer = init_intent_analyzer()
    
    return app
```

### Usage in Route Handlers

```python
# In route handlers
from app.intent_analyzer import get_intent_analyzer

@app.route('/analyze', methods=['POST'])
def analyze_intent():
    intent_analyzer = get_intent_analyzer()
    result = intent_analyzer.analyze(request.json['message'])
    return jsonify(result.to_dict())
```

## Alternative Approaches

### ❌ **Not Recommended: Per-Request Instantiation**

```python
@app.route('/analyze', methods=['POST'])
def analyze_intent():
    # DON'T DO THIS - creates new instance every request
    analyzer = create_intent_analyzer('mock')
    result = analyzer.analyze(request.json['message'])
    return jsonify(result.to_dict())
```

**Problems:**
- Performance overhead from repeated initialization
- Resource waste (API clients, connections)
- No connection pooling benefits
- Slower response times

### ⚠️ **Conditional: Lazy Initialization**

```python
# In app/__init__.py
def create_app(config_class=None):
    app = Flask(__name__)
    
    # Lazy initialization
    app._intent_analyzer = None
    
    def get_intent_analyzer():
        if app._intent_analyzer is None:
            app._intent_analyzer = create_intent_analyzer('mock')
        return app._intent_analyzer
    
    app.get_intent_analyzer = get_intent_analyzer
    return app
```

**Use Cases:**
- When initialization is expensive
- When you want to defer initialization until first use
- When configuration depends on runtime values

### ⚠️ **Conditional: Request-Level Caching**

```python
from functools import lru_cache
from flask import g

def get_intent_analyzer():
    if not hasattr(g, 'intent_analyzer'):
        g.intent_analyzer = create_intent_analyzer('mock')
    return g.intent_analyzer
```

**Use Cases:**
- When you need request-specific configuration
- When using different providers per request
- When testing with different configurations

## Configuration Management

### Environment-Based Configuration

```bash
# .env.development
INTENT_PROVIDER=mock

# .env.production
INTENT_PROVIDER=openai
OPENAI_API_KEY=your-api-key
OPENAI_MODEL=gpt-4
```

### Configuration Class

```python
# config.py
class Config:
    INTENT_PROVIDER = os.getenv('INTENT_PROVIDER', 'mock')
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
    OPENAI_MODEL = os.getenv('OPENAI_MODEL', 'gpt-4')
    ANTHROPIC_API_KEY = os.getenv('ANTHROPIC_API_KEY')
    ANTHROPIC_MODEL = os.getenv('ANTHROPIC_MODEL', 'claude-3-sonnet-20240229')
```

## Performance Considerations

### Memory Usage

| Approach | Memory Impact | Performance | Complexity |
|----------|---------------|-------------|------------|
| Singleton | Low | High | Low |
| Per-Request | High | Low | Low |
| Lazy Init | Low | High | Medium |
| Request Cache | Medium | High | Medium |

### Connection Pooling

For real LLM providers (OpenAI, Anthropic), the singleton approach enables:

- Connection reuse
- Rate limiting management
- Retry logic optimization
- Cost optimization

## Error Handling

### Singleton Pattern with Error Recovery

```python
def get_intent_analyzer():
    """Get intent analyzer with error recovery."""
    from flask import current_app
    
    try:
        return current_app.intent_analyzer
    except AttributeError:
        # Fallback to mock if not initialized
        return create_intent_analyzer('mock')
    except Exception as e:
        # Log error and return mock
        current_app.logger.error(f"Intent analyzer error: {e}")
        return create_intent_analyzer('mock')
```

## Testing Considerations

### Unit Testing

```python
def test_intent_analyzer():
    app = create_app('testing')
    with app.app_context():
        analyzer = get_intent_analyzer()
        result = analyzer.analyze("Book a flight")
        assert result.classification['primary_intent'] == 'book_flight'
```

### Integration Testing

```python
def test_intent_analysis_endpoint(client):
    response = client.post('/intent-collection/analyze', 
                          json={'userInput': 'Book a flight'})
    assert response.status_code == 200
    data = response.get_json()
    assert data['success'] == True
```

## Production Deployment

### Environment Variables

```bash
# Production environment
export INTENT_PROVIDER=openai
export OPENAI_API_KEY=sk-...
export OPENAI_MODEL=gpt-4

# Development environment
export INTENT_PROVIDER=mock
```

### Health Checks

```python
@app.route('/health/intent-analyzer')
def health_check():
    try:
        analyzer = get_intent_analyzer()
        # Test with simple message
        result = analyzer.analyze("test")
        return jsonify({'status': 'healthy', 'provider': 'working'})
    except Exception as e:
        return jsonify({'status': 'unhealthy', 'error': str(e)}), 500
```

## Monitoring and Logging

### Performance Monitoring

```python
import time

def analyze_with_monitoring(message):
    start_time = time.time()
    analyzer = get_intent_analyzer()
    result = analyzer.analyze(message)
    processing_time = (time.time() - start_time) * 1000
    
    # Log performance metrics
    current_app.logger.info(f"Intent analysis completed in {processing_time:.2f}ms")
    
    return result
```

### Error Tracking

```python
def safe_analyze(message):
    try:
        analyzer = get_intent_analyzer()
        return analyzer.analyze(message)
    except Exception as e:
        current_app.logger.error(f"Intent analysis failed: {e}")
        # Return fallback response
        return IntentResult(message, classification={'primary_intent': 'error'})
```

## Summary

### ✅ **Recommended Pattern**

1. **Initialize once** during app creation
2. **Store in app context** for easy access
3. **Use helper function** `get_intent_analyzer()` in routes
4. **Configure via environment variables**
5. **Handle errors gracefully** with fallbacks

### Key Benefits

- **Performance**: No repeated initialization
- **Resource Efficiency**: Single instance shared
- **Thread Safety**: Flask app context handles this
- **Maintainability**: Centralized configuration
- **Testability**: Easy to mock and test

### When to Use Alternatives

- **Lazy Init**: When initialization is expensive or depends on runtime config
- **Request Cache**: When you need request-specific configurations
- **Per-Request**: Only for testing or prototyping

This approach provides the best balance of performance, maintainability, and resource efficiency for most Flask applications. 