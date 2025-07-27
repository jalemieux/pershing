import pytest
import os
import tempfile
from unittest.mock import Mock, patch
from app.chat_llm_providers import (
    ChatLLMProvider, 
    ChatOpenAIProvider, 
    ChatAnthropicProvider, 
    ChatMockProvider,
    get_chat_llm_provider
)

class TestChatLLMProviders:
    """Test suite for chat LLM providers."""
    
    def test_chat_mock_provider(self):
        """Test the mock chat provider."""
        provider = ChatMockProvider()
        
        messages = [
            {"role": "user", "content": "Hello, AI!"}
        ]
        
        response = provider.generate_response(messages)
        
        assert response['content'] is not None
        assert response['model'] == "chat-mock-model"
        assert response['provider'] == "mock"
        assert response['tokens_used'] is not None
        assert response['metadata']['mock'] == True
    
    def test_chat_mock_provider_with_file(self):
        """Test the mock chat provider with file upload."""
        provider = ChatMockProvider()
        
        messages = [
            {"role": "user", "content": "Analyze this file"}
        ]
        
        # Create a temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix='.txt') as temp_file:
            temp_file.write(b"Test file content")
            temp_file_path = temp_file.name
        
        try:
            response = provider.generate_response(messages, temp_file_path)
            
            assert response['content'] is not None
            assert "uploaded a file" in response['content']
            assert response['metadata']['file_processed'] == True
            
        finally:
            if os.path.exists(temp_file_path):
                os.unlink(temp_file_path)
    
    @patch('openai.OpenAI')
    def test_chat_openai_provider(self, mock_openai):
        """Test the OpenAI chat provider."""
        # Mock OpenAI client
        mock_client = Mock()
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = "AI response"
        mock_response.usage.total_tokens = 100
        mock_response.usage.prompt_tokens = 50
        mock_response.usage.completion_tokens = 50
        mock_response.choices[0].finish_reason = "stop"
        
        mock_client.chat.completions.create.return_value = mock_response
        mock_openai.return_value = mock_client
        
        provider = ChatOpenAIProvider(api_key="test-key", model="gpt-4o")
        
        messages = [
            {"role": "user", "content": "Hello, AI!"}
        ]
        
        response = provider.generate_response(messages)
        
        assert response['content'] == "AI response"
        assert response['model'] == "gpt-4o"
        assert response['provider'] == "openai"
        assert response['tokens_used'] == 100
        assert response['metadata']['finish_reason'] == "stop"
    
    @patch('anthropic.Anthropic')
    def test_chat_anthropic_provider(self, mock_anthropic):
        """Test the Anthropic chat provider."""
        # Mock Anthropic client
        mock_client = Mock()
        mock_response = Mock()
        mock_response.content = [Mock()]
        mock_response.content[0].text = "AI response"
        mock_response.usage.input_tokens = 50
        mock_response.usage.output_tokens = 50
        
        mock_client.messages.create.return_value = mock_response
        mock_anthropic.return_value = mock_client
        
        provider = ChatAnthropicProvider(api_key="test-key", model="claude-3-sonnet-20240229")
        
        messages = [
            {"role": "user", "content": "Hello, AI!"}
        ]
        
        response = provider.generate_response(messages)
        
        assert response['content'] == "AI response"
        assert response['model'] == "claude-3-sonnet-20240229"
        assert response['provider'] == "anthropic"
        assert response['tokens_used'] == 100
        assert response['metadata']['input_tokens'] == 50
        assert response['metadata']['output_tokens'] == 50
    
    @patch.dict(os.environ, {'CHAT_PROVIDER': 'mock'})
    def test_get_chat_llm_provider_mock(self):
        """Test getting the mock chat provider."""
        provider = get_chat_llm_provider()
        
        assert isinstance(provider, ChatMockProvider)
    
    @patch.dict(os.environ, {'CHAT_PROVIDER': 'openai', 'OPENAI_API_KEY': 'test-key'})
    @patch('app.chat_llm_providers.ChatOpenAIProvider')
    def test_get_chat_llm_provider_openai(self, mock_openai_provider):
        """Test getting the OpenAI chat provider."""
        mock_provider = Mock()
        mock_openai_provider.return_value = mock_provider
        
        provider = get_chat_llm_provider()
        
        assert provider == mock_provider
        mock_openai_provider.assert_called_once_with(api_key='test-key', model='gpt-4o')
    
    @patch.dict(os.environ, {'CHAT_PROVIDER': 'anthropic', 'ANTHROPIC_API_KEY': 'test-key'})
    @patch('app.chat_llm_providers.ChatAnthropicProvider')
    def test_get_chat_llm_provider_anthropic(self, mock_anthropic_provider):
        """Test getting the Anthropic chat provider."""
        mock_provider = Mock()
        mock_anthropic_provider.return_value = mock_provider
        
        provider = get_chat_llm_provider()
        
        assert provider == mock_provider
        mock_anthropic_provider.assert_called_once_with(api_key='test-key', model='claude-3-sonnet-20240229')
    
    @patch.dict(os.environ, {'CHAT_PROVIDER': 'openai'})
    def test_get_chat_llm_provider_openai_no_key(self):
        """Test getting OpenAI provider when no API key is available."""
        provider = get_chat_llm_provider()
        
        assert isinstance(provider, ChatMockProvider)
    
    @patch.dict(os.environ, {'CHAT_PROVIDER': 'anthropic'})
    def test_get_chat_llm_provider_anthropic_no_key(self):
        """Test getting Anthropic provider when no API key is available."""
        provider = get_chat_llm_provider()
        
        assert isinstance(provider, ChatMockProvider)
    
    def test_chat_llm_provider_abstract(self):
        """Test that ChatLLMProvider is abstract."""
        with pytest.raises(TypeError):
            ChatLLMProvider() 