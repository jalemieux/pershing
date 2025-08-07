# OpenAI Prompt Provider Setup Guide

## Overview

The OpenAI Prompt Provider enables real AI-powered prompt generation using OpenAI's GPT-4o model. This guide will help you set up and configure the provider.

## Prerequisites

1. **OpenAI API Key**: You need a valid OpenAI API key
2. **Python Environment**: Ensure you have the required dependencies installed
3. **Environment Variables**: Configure your environment properly

## Setup Steps

### 1. Get OpenAI API Key

1. Visit [OpenAI Platform](https://platform.openai.com/)
2. Sign up or log in to your account
3. Navigate to "API Keys" section
4. Create a new API key
5. Copy the key (it starts with `sk-`)

### 2. Configure Environment Variables

Set the following environment variables:

```bash
# Required: Your OpenAI API key
export OPENAI_API_KEY="sk-your-api-key-here"

# Optional: Specify the provider (defaults to mock if not set)
export PROMPT_PROVIDER="openai"

# Optional: Specify the model (defaults to gpt-4o-2024-08-06)
export OPENAI_MODEL="gpt-4o-2024-08-06"
```

### 3. Update Your Application

The Flask app will automatically detect the configuration and use the OpenAI provider.

## Testing the Setup

### 1. Test the Provider Directly

```bash
python test_openai_prompt_provider.py
```

Expected output:
```
Testing OpenAI Prompt Provider...
Input: I want to write a blog post about artificial intelligence...
Generated 3 prompts:
Provider: openai
Model: gpt-4o-2024-08-06
Processing time: 7838ms
Tokens used: 532
```

### 2. Test Through the Web Interface

1. Start your Flask application
2. Navigate to the Prompt Crafting page
3. Enter your input and click "Generate Prompts"
4. Verify that you get 3 distinct, high-quality prompts

## Configuration Options

### Model Selection

Available models:
- `gpt-4o-2024-08-06` (default) - Latest GPT-4o model
- `gpt-4o` - GPT-4o model
- `gpt-4-turbo` - GPT-4 Turbo model
- `gpt-3.5-turbo` - GPT-3.5 Turbo model

### Temperature Settings

The provider uses a temperature of 0.7 for balanced creativity and consistency. You can modify this in the `OpenAIPromptProvider` class:

```python
response = self.client.chat.completions.create(
    model=self.model,
    messages=messages,
    #max_tokens=1000,
    temperature=0.7  # Adjust this value (0.0-1.0)
)
```

### Token Limits

The provider is configured with:
- **Max Tokens**: 1000 (adjustable)
- **System Prompt**: ~200 tokens
- **User Prompt**: ~100-200 tokens
- **Response**: ~600-800 tokens

## Error Handling

### Common Issues

1. **Invalid API Key**
   ```
   Error: Invalid API key
   ```
   Solution: Verify your API key is correct and has sufficient credits

2. **Rate Limiting**
   ```
   Error: Rate limit exceeded
   ```
   Solution: Wait a moment and try again, or upgrade your OpenAI plan

3. **Network Issues**
   ```
   Error: Connection timeout
   ```
   Solution: Check your internet connection and try again

### Fallback Behavior

If the OpenAI API fails, the provider automatically falls back to mock prompts:

```python
# The provider will return fallback prompts
result = {
    "prompts": ["Fallback prompt 1", "Fallback prompt 2", "Fallback prompt 3"],
    "metadata": {
        "provider": "openai_fallback",
        "error": "API call failed, using fallback prompts"
    }
}
```

## Cost Considerations

### Token Usage

- **System Prompt**: ~200 tokens
- **User Input**: ~50-200 tokens (depending on input length)
- **Generated Prompts**: ~600-800 tokens total
- **Total per request**: ~850-1200 tokens

### Cost Estimation

With GPT-4o pricing (as of 2024):
- **Input tokens**: $0.0025 per 1K tokens
- **Output tokens**: $0.01 per 1K tokens
- **Typical cost per request**: $0.01-0.02

### Optimization Tips

1. **Shorter inputs**: Reduce token usage by being concise
2. **Batch processing**: Process multiple inputs together
3. **Caching**: Cache similar requests to avoid repeated API calls

## Monitoring and Logging

### Application Logs

The application logs prompt generation requests:

```python
app.logger.info(f"Prompt generation requested for user {current_user.id}: {user_input[:100]}...")
```

### Performance Metrics

The provider tracks:
- Processing time (milliseconds)
- Token usage
- Provider type
- Model used

### Example Log Entry

```
2024-01-15 10:30:45,123 - INFO - Prompt generation requested for user 1: I want to write a blog post about AI...
2024-01-15 10:30:53,456 - INFO - OpenAI API call completed in 7838ms, tokens used: 532
```

## Security Considerations

### API Key Security

1. **Never commit API keys** to version control
2. **Use environment variables** for configuration
3. **Rotate keys regularly** for security
4. **Monitor usage** to detect unauthorized access

### Rate Limiting

- **Requests per minute**: 60 (OpenAI default)
- **Tokens per minute**: 150,000 (OpenAI default)
- **Implement backoff** for rate limit handling

## Troubleshooting

### Debug Mode

Enable debug logging to see detailed API interactions:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

### Common Solutions

1. **API key not working**: Verify the key is active and has credits
2. **Slow responses**: Check your internet connection and OpenAI status
3. **Empty responses**: Check if the API key has the correct permissions
4. **Rate limiting**: Implement exponential backoff in your application

## Support

For issues with:
- **OpenAI API**: Contact OpenAI support
- **Application**: Check the application logs and error messages
- **Configuration**: Verify environment variables are set correctly 