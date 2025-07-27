import pytest
import json
import tempfile
import os
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, timedelta
from app.chat_service import ChatService, get_chat_service
from app.models import Conversation, Message, User
from app.database import db

class TestChatService:
    """Test suite for ChatService."""
    
    @pytest.fixture
    def chat_service(self):
        """Create a chat service instance for testing."""
        return ChatService()
    
    @pytest.fixture
    def mock_user(self, app):
        """Create a mock user for testing."""
        with app.app_context():
            user = User(email="test@example.com")
            db.session.add(user)
            db.session.commit()
            yield user
            db.session.delete(user)
            db.session.commit()
    
    @pytest.fixture
    def mock_conversation(self, app, mock_user):
        """Create a mock conversation for testing."""
        with app.app_context():
            conversation = Conversation(
                user_id=mock_user.id,
                title="Test Conversation",
                conversation_type="text"
            )
            db.session.add(conversation)
            db.session.commit()
            yield conversation
            db.session.delete(conversation)
            db.session.commit()
    
    def test_create_conversation(self, app, chat_service, mock_user):
        """Test creating a new conversation."""
        with app.app_context():
            conversation = chat_service.create_conversation(
                user_id=mock_user.id,
                title="New Test Conversation",
                conversation_type="text"
            )
            
            assert conversation is not None
            assert conversation.user_id == mock_user.id
            assert conversation.title == "New Test Conversation"
            assert conversation.conversation_type == "text"
            assert conversation.is_active == True
            
            # Cleanup
            db.session.delete(conversation)
            db.session.commit()
    
    def test_get_user_conversations(self, app, chat_service, mock_user, mock_conversation):
        """Test retrieving user conversations."""
        with app.app_context():
            conversations = chat_service.get_user_conversations(mock_user.id)
            
            assert len(conversations) >= 1
            assert any(conv.id == mock_conversation.id for conv in conversations)
    
    def test_get_conversation_messages(self, app, chat_service, mock_user, mock_conversation):
        """Test retrieving conversation messages."""
        with app.app_context():
            # Add a test message
            message = Message(
                conversation_id=mock_conversation.id,
                role="user",
                content="Test message",
                content_type="text"
            )
            db.session.add(message)
            db.session.commit()
            
            messages = chat_service.get_conversation_messages(mock_conversation.id, mock_user.id)
            
            assert len(messages) >= 1
            assert any(msg.content == "Test message" for msg in messages)
            
            # Cleanup
            db.session.delete(message)
            db.session.commit()
    
    def test_add_message(self, app, chat_service, mock_conversation):
        """Test adding a message to a conversation."""
        with app.app_context():
            message = chat_service.add_message(
                conversation_id=mock_conversation.id,
                role="user",
                content="Test message content",
                content_type="text"
            )
            
            assert message is not None
            assert message.conversation_id == mock_conversation.id
            assert message.role == "user"
            assert message.content == "Test message content"
            assert message.content_type == "text"
            
            # Cleanup
            db.session.delete(message)
            db.session.commit()
    
    @patch('app.chat_service.get_chat_llm_provider')
    def test_process_user_message(self, mock_get_llm_provider, app, chat_service, mock_user, mock_conversation):
        """Test processing a user message and generating AI response."""
        with app.app_context():
            # Mock LLM provider
            mock_provider = Mock()
            mock_provider.generate_response.return_value = {
                'content': 'AI response',
                'model': 'test-model',
                'provider': 'test-provider',
                'tokens_used': 100,
                'metadata': {}
            }
            mock_get_llm_provider.return_value = mock_provider
            
            user_message, assistant_message = chat_service.process_user_message(
                user_id=mock_user.id,
                conversation_id=mock_conversation.id,
                message_content="Hello, AI!"
            )
            
            assert user_message is not None
            assert assistant_message is not None
            assert user_message.role == "user"
            assert user_message.content == "Hello, AI!"
            assert assistant_message.role == "assistant"
            assert assistant_message.content == "AI response"
            
            # Verify LLM was called
            mock_provider.generate_response.assert_called_once()
            
            # Cleanup
            db.session.delete(user_message)
            db.session.delete(assistant_message)
            db.session.commit()
    
    def test_handle_file_upload(self, app, chat_service, mock_conversation):
        """Test handling file upload."""
        with app.app_context():
            # Create temporary file
            with tempfile.NamedTemporaryFile(delete=False, suffix='.txt') as temp_file:
                temp_file.write(b"Test file content")
                temp_file_path = temp_file.name
            
            try:
                file_data = {
                    'name': 'test.txt',
                    'content': 'VGVzdCBmaWxlIGNvbnRlbnQ='  # base64 of "Test file content"
                }
                
                file_path, file_name, file_size = chat_service._handle_file_upload(
                    file_data, mock_conversation.id
                )
                
                assert file_path is not None
                assert file_name == "test.txt"
                assert file_size == 17  # Length of "Test file content"
                assert os.path.exists(file_path)
                
                # Cleanup
                if os.path.exists(file_path):
                    os.remove(file_path)
                    
            finally:
                if os.path.exists(temp_file_path):
                    os.unlink(temp_file_path)
    
    def test_get_conversation_context(self, app, chat_service, mock_conversation):
        """Test getting conversation context for AI processing."""
        with app.app_context():
            # Add test messages
            messages = [
                Message(conversation_id=mock_conversation.id, role="user", content="Hello"),
                Message(conversation_id=mock_conversation.id, role="assistant", content="Hi there!"),
                Message(conversation_id=mock_conversation.id, role="user", content="How are you?")
            ]
            
            for msg in messages:
                db.session.add(msg)
            db.session.commit()
            
            context = chat_service._get_conversation_context(mock_conversation.id)
            
            assert len(context) == 3
            assert context[0]['role'] == "user"
            assert context[0]['content'] == "Hello"
            assert context[1]['role'] == "assistant"
            assert context[1]['content'] == "Hi there!"
            
            # Cleanup
            for msg in messages:
                db.session.delete(msg)
            db.session.commit()
    
    def test_delete_conversation(self, app, chat_service, mock_user, mock_conversation):
        """Test deleting a conversation."""
        with app.app_context():
            success = chat_service.delete_conversation(mock_conversation.id, mock_user.id)
            
            assert success == True
            
            # Verify conversation is soft deleted
            conversation = Conversation.query.get(mock_conversation.id)
            assert conversation.is_active == False
    
    def test_rename_conversation(self, app, chat_service, mock_user, mock_conversation):
        """Test renaming a conversation."""
        with app.app_context():
            new_title = "Renamed Conversation"
            success = chat_service.rename_conversation(mock_conversation.id, mock_user.id, new_title)
            
            assert success == True
            
            # Verify conversation is renamed
            conversation = Conversation.query.get(mock_conversation.id)
            assert conversation.title == new_title
    
    def test_conversation_title_update(self, app, chat_service, mock_user, mock_conversation):
        """Test automatic conversation title update from messages."""
        with app.app_context():
            # Add a user message
            message = Message(
                conversation_id=mock_conversation.id,
                role="user",
                content="This is a test message for conversation title generation"
            )
            db.session.add(message)
            db.session.commit()
            
            # Update conversation title
            mock_conversation.update_title_from_messages()
            db.session.commit()
            
            # Verify title was updated
            conversation = Conversation.query.get(mock_conversation.id)
            assert "test message" in conversation.title.lower()
            
            # Cleanup
            db.session.delete(message)
            db.session.commit()
    
    def test_message_file_detection(self, app, mock_conversation):
        """Test file message detection."""
        with app.app_context():
            # Test text message
            text_message = Message(
                conversation_id=mock_conversation.id,
                role="user",
                content="Text message",
                content_type="text"
            )
            assert text_message.is_file_message() == False
            
            # Test file message
            file_message = Message(
                conversation_id=mock_conversation.id,
                role="user",
                content="File message",
                content_type="file",
                file_path="/path/to/file.txt"
            )
            assert file_message.is_file_message() == True
    
    def test_get_chat_service_singleton(self, app):
        """Test that get_chat_service returns a singleton instance."""
        with app.app_context():
            service1 = get_chat_service()
            service2 = get_chat_service()
            
            assert service1 is service2
            assert isinstance(service1, ChatService)

class TestChatRoutes:
    """Test suite for chat routes."""
    
    def test_get_conversations_route(self, client, auth_headers):
        """Test GET /api/chat/conversations route."""
        response = client.get('/api/chat/conversations', headers=auth_headers)
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] == True
        assert 'conversations' in data
    
    def test_create_conversation_route(self, client, auth_headers):
        """Test POST /api/chat/conversations route."""
        data = {
            'title': 'Test Conversation',
            'type': 'text'
        }
        
        response = client.post(
            '/api/chat/conversations',
            headers=auth_headers,
            json=data
        )
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] == True
        assert 'conversation' in data
    
    def test_send_message_route(self, client, auth_headers, mock_conversation):
        """Test POST /api/chat/conversations/<id>/messages route."""
        data = {
            'message': 'Hello, AI!'
        }
        
        response = client.post(
            f'/api/chat/conversations/{mock_conversation.id}/messages',
            headers=auth_headers,
            json=data
        )
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] == True
        assert 'user_message' in data
        assert 'assistant_message' in data
    
    def test_delete_conversation_route(self, client, auth_headers, mock_conversation):
        """Test DELETE /api/chat/conversations/<id> route."""
        response = client.delete(
            f'/api/chat/conversations/{mock_conversation.id}',
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] == True
    
    def test_rename_conversation_route(self, client, auth_headers, mock_conversation):
        """Test PUT /api/chat/conversations/<id>/rename route."""
        data = {
            'title': 'Renamed Conversation'
        }
        
        response = client.put(
            f'/api/chat/conversations/{mock_conversation.id}/rename',
            headers=auth_headers,
            json=data
        )
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] == True
    
    def test_get_chat_stats_route(self, client, auth_headers):
        """Test GET /api/chat/stats route."""
        response = client.get('/api/chat/stats', headers=auth_headers)
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] == True
        assert 'stats' in data
        assert 'total_conversations' in data['stats']
        assert 'total_messages' in data['stats'] 