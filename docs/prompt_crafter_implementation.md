# Prompt Crafter Implementation

## Overview

The prompt crafter is a new module that follows the same architectural pattern as the intent analyzer. It provides a structured way to generate multiple prompts based on user input using LLM providers.

## Architecture

### Core Components

1. **PromptResult** - Structured result containing generated prompts and metadata
2. **PromptLLMProvider** - Abstract base class for LLM providers
3. **MockPromptLLMProvider** - Mock implementation for testing
4. **PromptCrafter** - Main class that orchestrates prompt generation
5. **Factory Functions** - For creating prompt crafters with different providers

### Key Features

- **Multiple Prompt Types**: Generates 3 different types of prompts:
  - Direct and specific
  - Creative and exploratory  
  - Structured and systematic
- **Batch Processing**: Can process multiple inputs at once
- **Provider Abstraction**: Supports different LLM providers (mock, OpenAI, Anthropic)
- **Structured Results**: Returns well-formatted results with metadata

## Usage

### Basic Usage

```python
from app.prompt_crafter import get_prompt_crafter

# Get the prompt crafter from Flask app context
prompt_crafter = get_prompt_crafter()

# Generate prompts
result = prompt_crafter.craft_prompts("I want to write a blog post about AI")

# Access results
print(f"Generated {len(result.prompts)} prompts")
for i, prompt in enumerate(result.prompts, 1):
    print(f"Prompt {i}: {prompt}")
```

### Batch Processing

```python
inputs = ["Write a story", "Create a marketing campaign", "Design a UI"]
results = prompt_crafter.craft_prompts_batch(inputs)

for result in results:
    print(f"Input: {result.raw_input}")
    print(f"Generated {len(result.prompts)} prompts")
```

## Integration

### Flask App Integration

The prompt crafter is integrated into the Flask app as a singleton:

```python
# In app/__init__.py
app.prompt_crafter = init_prompt_crafter()
```

### Route Handler Usage

```python
@app.route('/prompt-crafting/generate', methods=['POST'])
@login_required
def generate_prompts():
    from app.prompt_crafter import get_prompt_crafter
    
    prompt_crafter = get_prompt_crafter()
    result = prompt_crafter.craft_prompts(user_input)
    
    return jsonify({
        'success': True,
        'prompts': result.prompts
    })
```

## Frontend Integration

### Template Structure

The prompt crafting page (`prompt_crafting.html`) follows the same pattern as the intent collection page:

- **Left Panel**: Text area for user input
- **Right Panel**: Display area for generated prompts
- **Responsive Design**: Uses Tailwind CSS for styling

### JavaScript Functionality

- Form submission with loading states
- AJAX requests to backend
- Dynamic prompt display with copy functionality
- Error handling and user feedback

## Configuration

### Environment Variables

- `PROMPT_PROVIDER`: Provider type (mock, openai, anthropic)
- `OPENAI_API_KEY`: OpenAI API key (if using OpenAI)
- `ANTHROPIC_API_KEY`: Anthropic API key (if using Anthropic)
- `OPENAI_MODEL`: OpenAI model name
- `ANTHROPIC_MODEL`: Anthropic model name

### Default Configuration

- **Provider**: Mock (for development/testing)
- **Model**: gpt-4o-2024-08-06 (OpenAI) or claude-3-sonnet-20240229 (Anthropic)

## OpenAI Integration

### Features

- **Real API Integration**: Connects to OpenAI's GPT-4o model
- **Structured Outputs**: Uses Pydantic models for reliable, type-safe responses
- **Structured Prompts**: Generates 3 distinct prompt types with specific characteristics
- **Context Awareness**: Incorporates user preferences and previous prompts
- **Error Handling**: Graceful fallback to mock prompts if API fails
- **Performance Tracking**: Measures processing time and token usage

### Structured Output Approach

The OpenAI provider uses Pydantic models for structured outputs:

```python
class PromptMetadata(BaseModel):
    language: str
    prompt_count: int
    processing_time_ms: int
    provider: str
    model: str
    tokens_used: Optional[int]

class PromptGenerationResult(BaseModel):
    prompts: List[str]
    prompt_types: List[str]
    metadata: PromptMetadata
```

This ensures:
- **Type Safety**: All responses are validated against the schema
- **Consistency**: Structured format across all API calls
- **Reliability**: Automatic parsing and validation
- **Error Handling**: Clear error messages for malformed responses

### Usage

```python
# Set environment variable
export OPENAI_API_KEY="your-api-key-here"

# Update Flask app configuration
export PROMPT_PROVIDER="openai"

# The prompt crafter will automatically use OpenAI
```

### Prompt Types Generated

1. **Direct and Specific**: Focused on actionable, detailed prompts
2. **Creative and Exploratory**: Open-ended, innovative approaches
3. **Structured and Systematic**: Step-by-step, organized prompts

## Testing

### Test Script

Run the test script to verify functionality:

```bash
python test_prompt_crafter.py
```

### Test Coverage

- Single prompt generation
- Batch processing
- Error handling
- Result structure validation

## Future Enhancements

### Planned Features

1. **Real LLM Integration**: Connect to actual OpenAI/Anthropic APIs
2. **Custom Prompt Types**: Allow users to specify prompt types
3. **Prompt Templates**: Pre-defined templates for common use cases
4. **Prompt History**: Save and retrieve previous prompts
5. **Prompt Evaluation**: Rate and improve generated prompts
6. **Advanced Context**: Include conversation history and user preferences

### Provider Extensions

- **OpenAIPromptProvider**: ✅ OpenAI-specific implementation with real API integration and structured outputs
- **MockPromptLLMProvider**: Mock implementation for testing and development
- **Custom Providers**: Support for other LLM services

## File Structure

```
app/
├── prompt_crafter.py          # Main prompt crafter module
├── llm_providers.py          # LLM provider implementations
├── templates/
│   └── prompt_crafting.html  # Frontend template
└── __init__.py               # Flask app initialization

main.py                       # Route handlers
test_prompt_crafter.py        # Test script
```

## Navigation Integration

The prompt crafting feature is integrated into the navigation:

- **Main Navigation**: Added to desktop and mobile menus
- **Home Page**: Featured card with direct link
- **Dashboard**: Quick action button for admin users

## Error Handling

- **Input Validation**: Ensures non-empty user input
- **Provider Errors**: Graceful fallback to mock provider
- **Network Errors**: User-friendly error messages
- **Batch Processing**: Continues processing on individual failures 