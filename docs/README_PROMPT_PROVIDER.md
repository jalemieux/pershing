# Default Prompt Provider Configuration

## Overview

The AI prompt tweaking feature uses a configurable default provider that can be set through environment variables. This allows you to choose which LLM provider to use for prompt improvements.

## Configuration

### Environment Variable

Set the `DEFAULT_PROMPT_PROVIDER` environment variable in your `.env.development` file:

```bash
# Default prompt provider for AI prompt tweaking
# Options: 'openai', 'anthropic', 'mock'
DEFAULT_PROMPT_PROVIDER=openai
```

### Available Providers

1. **openai** (default) - Uses OpenAI's GPT models
2. **anthropic** - Uses Anthropic's Claude models  
3. **mock** - Uses mock implementation for testing

### Provider-Specific Configuration

#### OpenAI Provider
```bash
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_MODEL=gpt-4o-2024-08-06
```

#### Anthropic Provider
```bash
ANTHROPIC_API_KEY=your_anthropic_api_key_here
ANTHROPIC_MODEL=claude-3-sonnet-20240229
```

## Usage

Once configured, the system will automatically use the specified provider for prompt improvements. If the configured provider is not available (e.g., missing API key), the system will fall back to the mock implementation.

## Example Configuration

```bash
# .env.development
DEFAULT_PROMPT_PROVIDER=openai
OPENAI_API_KEY=sk-your-key-here
OPENAI_MODEL=gpt-4o-2024-08-06
FLASK_ENV=development
SECRET_KEY=your-secret-key
DATABASE_URL=sqlite:///app.db
```

## Error Handling

- If the configured provider is not available, the system returns an error with details about the configuration issue
- If the provider doesn't support the `improve_prompt` method, the system returns an error
- This ensures that configuration issues are immediately apparent and can be fixed

## Troubleshooting

### Common Error Messages

1. **"Default provider 'openai' is not available"**
   - Check that your API key is set correctly
   - Verify the provider name in your configuration
   - Ensure the provider is properly initialized

2. **"Provider 'openai' doesn't support prompt improvement"**
   - This indicates a code issue where the provider doesn't implement the required method
   - Check that you're using a supported provider (openai, anthropic)
   - Update to a provider that supports the `improve_prompt` method

3. **"Error using prompt crafter"**
   - Check your API keys and network connectivity
   - Verify that your chosen provider is working correctly
   - Check the application logs for more detailed error information 