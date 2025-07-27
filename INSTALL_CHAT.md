# Chat Functionality Installation Guide

## Overview

This guide helps you install the dependencies required for the chat functionality.

## Dependencies

The chat functionality requires the following additional dependencies:

### Core Dependencies
- **Pillow**: For image processing (if needed in the future)
- **OpenAI**: For OpenAI API integration
- **Anthropic**: For Anthropic API integration

## Installation Steps

### 1. Install Python Dependencies

```bash
# Install all dependencies including chat requirements
pip install -r requirements.txt
```

### 2. Verify Installation

```bash
# Test that all modules can be imported
python -c "import openai; import anthropic; print('Dependencies installed successfully!')"
```

### 3. Environment Variables

Set up your environment variables for chat functionality:

```bash
# Chat-specific configuration
export CHAT_PROVIDER=mock  # Start with mock for testing
# export CHAT_PROVIDER=openai  # For OpenAI
# export CHAT_PROVIDER=anthropic  # For Anthropic

# API Keys (if using real providers)
# export OPENAI_API_KEY=your_openai_key
# export ANTHROPIC_API_KEY=your_anthropic_key

# Model configuration
export OPENAI_MODEL=gpt-4o
export ANTHROPIC_MODEL=claude-3-sonnet-20240229
```

### 4. Database Setup

Run the database migrations for chat functionality:

```bash
# Run the chat tables migration
psql -d your_database -f migrations/002_add_chat_tables.sql

# If you have an existing database with the old metadata column
psql -d your_database -f migrations/003_rename_metadata_column.sql
```

### 5. Create Upload Directory

```bash
# Create the upload directory for chat files
mkdir -p app/uploads/chat
```

## Testing the Installation

### 1. Run Chat Tests

```bash
# Test the chat functionality
pytest test_chat_service.py test_chat_llm_providers.py -v
```

### 2. Start the Application

```bash
# Start the Flask application
python main.py
```

### 3. Access Chat Interface

1. Navigate to the home page
2. Click on the "AI Chat" card
3. Or go directly to `/chat`

## Troubleshooting

### Common Issues

1. **ModuleNotFoundError: No module named 'PIL'**
   - Solution: `pip install pillow`

2. **ModuleNotFoundError: No module named 'openai'**
   - Solution: `pip install openai`

3. **ModuleNotFoundError: No module named 'anthropic'**
   - Solution: `pip install anthropic`

4. **Database errors**
   - Ensure you've run the migrations
   - Check your database connection

5. **File upload errors**
   - Ensure the upload directory exists: `mkdir -p app/uploads/chat`
   - Check directory permissions

### Verification Commands

```bash
# Check if all required packages are installed
python -c "
import openai
import anthropic
import flask
import sqlalchemy
print('All dependencies installed successfully!')
"

# Test database connection
python -c "
from app.database import db
from app.models import Conversation, Message
print('Database models loaded successfully!')
"
```

## Development Setup

For development, you can use the mock provider which doesn't require API keys:

```bash
export CHAT_PROVIDER=mock
```

This allows you to test the chat functionality without setting up API keys.

## Production Setup

For production, configure a real provider:

```bash
# For OpenAI
export CHAT_PROVIDER=openai
export OPENAI_API_KEY=your_openai_key

# For Anthropic
export CHAT_PROVIDER=anthropic
export ANTHROPIC_API_KEY=your_anthropic_key
``` 