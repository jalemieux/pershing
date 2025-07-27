# Chat Implementation Documentation

## Overview

The chat functionality is implemented as a separate module that doesn't interfere with the existing LLM providers used for intent analysis and prompt crafting. The chat system uses its own dedicated LLM providers specifically designed for conversational AI interactions.

## Architecture

### Chat LLM Providers (`app/chat_llm_providers.py`)

The chat system uses a separate set of LLM providers that are specifically designed for conversational interactions:

- **ChatLLMProvider**: Abstract base class for chat providers
- **ChatOpenAIProvider**: OpenAI implementation for chat
- **ChatAnthropicProvider**: Anthropic implementation for chat  
- **ChatMockProvider**: Mock provider for testing

### Key Differences from Existing LLM Providers

1. **Separate Configuration**: Uses `CHAT_PROVIDER` environment variable instead of `INTENT_PROVIDER` or `PROMPT_PROVIDER`
2. **Conversational Focus**: Optimized for back-and-forth chat interactions
3. **File Handling**: Built-in support for file uploads and multi-modal conversations
4. **Context Management**: Designed to handle conversation history and context

## Database Schema

### New Tables

#### `conversation`
- `id`: Primary key
- `user_id`: Foreign key to user table
- `title`: Conversation title (auto-generated from first message)
- `created_at`: Timestamp
- `updated_at`: Timestamp (auto-updated)
- `is_active`: Soft delete flag
- `conversation_type`: Type of conversation (text, image, multimodal)

#### `message`
- `id`: Primary key
- `conversation_id`: Foreign key to conversation table
- `role`: Message role (user, assistant, system)
- `content`: Message content
- `content_type`: Type of content (text, image, file)
- `file_path`: Path to uploaded file (if applicable)
- `file_name`: Original filename
- `file_size`: File size in bytes
- `created_at`: Timestamp
- `tokens_used`: Token usage for AI response
- `model_used`: AI model used
- `provider_used`: AI provider used
- `response_time`: Response time in seconds
- `metadata`: JSON metadata

## API Endpoints

### Conversation Management
- `GET /api/chat/conversations` - Get user conversations
- `POST /api/chat/conversations` - Create new conversation
- `GET /api/chat/conversations/<id>` - Get conversation with messages
- `DELETE /api/chat/conversations/<id>` - Delete conversation
- `PUT /api/chat/conversations/<id>/rename` - Rename conversation

### Messaging
- `POST /api/chat/conversations/<id>/messages` - Send message
- `GET /api/chat/conversations/<id>/messages` - Get conversation messages

### Statistics
- `GET /api/chat/stats` - Get chat statistics

## Environment Configuration

```bash
# Chat-specific configuration
CHAT_PROVIDER=openai  # or anthropic, mock
OPENAI_API_KEY=your_openai_key
ANTHROPIC_API_KEY=your_anthropic_key
OPENAI_MODEL=gpt-4o
ANTHROPIC_MODEL=claude-3-sonnet-20240229
```

## Usage Examples

### Creating a Conversation
```python
from app.chat_service import get_chat_service

chat_service = get_chat_service()
conversation = chat_service.create_conversation(
    user_id=1,
    title="My Chat",
    conversation_type="text"
)
```

### Sending a Message
```python
user_message, assistant_message = chat_service.process_user_message(
    user_id=1,
    conversation_id=conversation.id,
    message_content="Hello, AI!"
)
```

### Using the Chat LLM Provider Directly
```python
from app.chat_llm_providers import get_chat_llm_provider

provider = get_chat_llm_provider()
response = provider.generate_response([
    {"role": "user", "content": "Hello!"}
])
```

## File Upload Support

The chat system supports file uploads with automatic processing:

1. **Image Files**: Supported formats (jpg, jpeg, png, gif, webp)
2. **Text Files**: Any text file for analysis
3. **Base64 Encoding**: Files are encoded and sent to AI providers
4. **Storage**: Files are stored in conversation-specific folders

## Testing

### Running Chat Tests
```bash
# Test chat service
pytest test_chat_service.py

# Test chat LLM providers
pytest test_chat_llm_providers.py
```

### Test Coverage
- Chat service functionality
- LLM provider integration
- File upload handling
- Conversation management
- API endpoint testing

## Integration with Existing System

The chat system is designed to be completely independent of the existing LLM providers:

1. **Separate Providers**: Uses `chat_llm_providers.py` instead of `llm_providers.py`
2. **Independent Configuration**: Uses `CHAT_PROVIDER` instead of existing provider configs
3. **No Conflicts**: Doesn't interfere with intent analysis or prompt crafting
4. **Shared Authentication**: Uses existing user authentication system
5. **Shared Database**: Uses existing database connection and models

## Deployment Considerations

### Security
- File upload validation
- Rate limiting on chat endpoints
- Input sanitization
- User authentication required

### Performance
- Database indexing on conversation and message tables
- File storage optimization
- Caching for conversation lists
- Connection pooling

### Scalability
- Horizontal scaling support
- Database read replicas
- Message queue for AI processing
- WebSocket support for real-time updates

## Migration

To add chat functionality to an existing installation:

1. **Run Database Migration**:
```sql
-- Execute migrations/002_add_chat_tables.sql
```

2. **Set Environment Variables**:
```bash
CHAT_PROVIDER=mock  # Start with mock for testing
```

3. **Create Upload Directory**:
```bash
mkdir -p app/uploads/chat
```

4. **Test the Implementation**:
```bash
pytest test_chat_service.py test_chat_llm_providers.py
```

## Troubleshooting

### Common Issues

1. **No API Key**: Falls back to mock provider
2. **File Upload Errors**: Check upload directory permissions
3. **Database Errors**: Ensure migration was run
4. **Authentication Issues**: Verify user is logged in

### Debug Mode

Enable debug logging for chat functionality:
```python
import logging
logging.getLogger('app.chat_service').setLevel(logging.DEBUG)
logging.getLogger('app.chat_llm_providers').setLevel(logging.DEBUG)
``` 