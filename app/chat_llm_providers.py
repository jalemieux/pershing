import os
import json
import base64
from abc import ABC, abstractmethod
from typing import List, Dict, Optional
from flask import current_app
import openai
import anthropic
from agents import WebSearchTool


class ChatLLMProvider(ABC):
    """Abstract base class for chat LLM providers."""
    
    @abstractmethod
    def generate_response(self, messages: List[Dict], file_path: Optional[str] = None) -> Dict:
        """Generate a response from the chat LLM provider."""
        pass

class ChatOpenAIProvider(ChatLLMProvider):
    """OpenAI provider implementation for chat."""
    
    def __init__(self, api_key: str, model: str = "gpt-4o"):
        self.client = openai.OpenAI(api_key=api_key)
        self.model = model
    
    def generate_response(self, messages: List[Dict], file_path: Optional[str] = None) -> Dict:
        """Generate response using OpenAI API for chat."""
        try:
            # Prepare messages for OpenAI
            openai_messages = []
            for msg in messages:
                if msg['role'] == 'system':
                    openai_messages.append({"role": "system", "content": msg['content']})
                elif msg['role'] == 'user':
                    if file_path and msg == messages[-1]:  # Last user message with file
                        # Handle file upload
                        with open(file_path, 'rb') as f:
                            file_content = f.read()
                        
                        # Determine file type
                        file_extension = os.path.splitext(file_path)[1].lower()
                        if file_extension in ['.jpg', '.jpeg', '.png', '.gif', '.webp']:
                            # Image file
                            openai_messages.append({
                                "role": "user",
                                "content": [
                                    {"type": "text", "text": msg['content']},
                                    {
                                        "type": "image_url",
                                        "image_url": {
                                            "url": f"data:image/{file_extension[1:]};base64,{base64.b64encode(file_content).decode()}"
                                        }
                                    }
                                ]
                            })
                        else:
                            # Text file
                            file_text = file_content.decode('utf-8', errors='ignore')
                            openai_messages.append({
                                "role": "user",
                                "content": f"{msg['content']}\n\nFile content:\n{file_text}"
                            })
                    else:
                        openai_messages.append({"role": "user", "content": msg['content']})
                elif msg['role'] == 'assistant':
                    openai_messages.append({"role": "assistant", "content": msg['content']})
            
            # Make API call
            response = self.client.chat.completions.create(
                model=self.model,
                messages=openai_messages,
                max_tokens=1000,
                temperature=0.7, 
            )
            
            return {
                'content': response.choices[0].message.content,
                'model': self.model,
                'provider': 'openai',
                'tokens_used': response.usage.total_tokens if response.usage else None,
                'metadata': {
                    'finish_reason': response.choices[0].finish_reason,
                    'prompt_tokens': response.usage.prompt_tokens if response.usage else None,
                    'completion_tokens': response.usage.completion_tokens if response.usage else None
                }
            }
            
        except Exception as e:
            current_app.logger.error(f"OpenAI Chat API error: {str(e)}")
            raise

class ChatAnthropicProvider(ChatLLMProvider):
    """Anthropic provider implementation for chat."""
    
    def __init__(self, api_key: str, model: str = "claude-3-sonnet-20240229"):
        self.client = anthropic.Anthropic(api_key=api_key)
        self.model = model
    
    def generate_response(self, messages: List[Dict], file_path: Optional[str] = None) -> Dict:
        """Generate response using Anthropic API for chat."""
        try:
            # Prepare messages for Anthropic
            anthropic_messages = []
            for msg in messages:
                if msg['role'] == 'system':
                    # Anthropic doesn't support system messages in the same way
                    # We'll prepend it to the first user message
                    continue
                elif msg['role'] == 'user':
                    content = msg['content']
                    if file_path and msg == messages[-1]:  # Last user message with file
                        # Handle file upload
                        with open(file_path, 'rb') as f:
                            file_content = f.read()
                        
                        # Determine file type
                        file_extension = os.path.splitext(file_path)[1].lower()
                        if file_extension in ['.jpg', '.jpeg', '.png', '.gif', '.webp']:
                            # Image file
                            content = [
                                {
                                    "type": "text",
                                    "text": msg['content']
                                },
                                {
                                    "type": "image",
                                    "source": {
                                        "type": "base64",
                                        "media_type": f"image/{file_extension[1:]}",
                                        "data": base64.b64encode(file_content).decode()
                                    }
                                }
                            ]
                        else:
                            # Text file
                            file_text = file_content.decode('utf-8', errors='ignore')
                            content = f"{msg['content']}\n\nFile content:\n{file_text}"
                    
                    anthropic_messages.append({"role": "user", "content": content})
                elif msg['role'] == 'assistant':
                    anthropic_messages.append({"role": "assistant", "content": msg['content']})
            
            # Add system message if present
            system_message = None
            for msg in messages:
                if msg['role'] == 'system':
                    system_message = msg['content']
                    break
            
            # Make API call
            response = self.client.messages.create(
                model=self.model,
                max_tokens=1000,
                messages=anthropic_messages,
                system=system_message
            )
            
            return {
                'content': response.content[0].text,
                'model': self.model,
                'provider': 'anthropic',
                'tokens_used': response.usage.input_tokens + response.usage.output_tokens if response.usage else None,
                'metadata': {
                    'input_tokens': response.usage.input_tokens if response.usage else None,
                    'output_tokens': response.usage.output_tokens if response.usage else None
                }
            }
            
        except Exception as e:
            current_app.logger.error(f"Anthropic Chat API error: {str(e)}")
            raise

class ChatMockProvider(ChatLLMProvider):
    """Mock provider for chat testing and development."""
    
    def __init__(self):
        self.model = "chat-mock-model"
    
    def generate_response(self, messages: List[Dict], file_path: Optional[str] = None) -> Dict:
        """Generate mock response for chat testing."""
        # Get the last user message
        user_message = ""
        for msg in reversed(messages):
            if msg['role'] == 'user':
                user_message = msg['content']
                break
        
        # Generate mock response
        if file_path:
            response_content = f"This is a mock chat response to your message: '{user_message}'. I can see you've uploaded a file: {os.path.basename(file_path)}. In a real implementation, I would analyze this file and provide insights."
        else:
            response_content = f"This is a mock chat response to your message: '{user_message}'. In a real implementation, I would provide a helpful and accurate response."
        
        return {
            'content': response_content,
            'model': self.model,
            'provider': 'mock',
            'tokens_used': len(response_content.split()),
            'metadata': {
                'mock': True,
                'file_processed': file_path is not None
            }
        }

def get_chat_llm_provider() -> ChatLLMProvider:
    """Get the configured chat LLM provider."""
    provider_type = os.getenv('env', 'openai')
    
    if provider_type == 'openai':
        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key:
            current_app.logger.warning("OpenAI API key not found, falling back to mock provider")
            raise Exception("OpenAI API key not found")
        
        model = os.getenv('OPENAI_MODEL', 'gpt-4o')
        return ChatOpenAIProvider(api_key=api_key, model=model)
    
    elif provider_type == 'anthropic':
        api_key = os.getenv('ANTHROPIC_API_KEY')
        if not api_key:
            current_app.logger.warning("Anthropic API key not found, falling back to mock provider")
            return ChatMockProvider()
        
        model = os.getenv('ANTHROPIC_MODEL', 'claude-3-sonnet-20240229')
        return ChatAnthropicProvider(api_key=api_key, model=model)
    
    else:
        # Default to mock provider
        return ChatMockProvider() 