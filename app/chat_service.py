import os
import json
import time
from datetime import datetime
from typing import List, Dict, Optional, Tuple
from flask import current_app
from app.database import db
from app.models import Conversation, Message, User
from app.chat_llm_providers import get_chat_llm_provider
from app.context_window_manager import get_context_window_manager
import base64
from werkzeug.utils import secure_filename

class ChatService:
    """Service for handling chat operations and AI responses."""
    
    def __init__(self):
        self.llm_provider = get_chat_llm_provider()
        self.context_manager = get_context_window_manager()
        self.upload_folder = os.path.join(current_app.root_path, 'uploads', 'chat')
        os.makedirs(self.upload_folder, exist_ok=True)
    
    def create_conversation(self, user_id: int, title: str = "New Conversation", conversation_type: str = "text", buddy_id: int = None) -> Conversation:
        """Create a new conversation for a user."""
        conversation = Conversation(
            user_id=user_id,
            title=title,
            conversation_type=conversation_type,
            buddy_id=buddy_id
        )
        db.session.add(conversation)
        db.session.commit()
        current_app.logger.info(f"Created conversation {conversation.id} for user {user_id}")
        return conversation
    
    def get_user_conversations(self, user_id: int, limit: int = 50) -> List[Conversation]:
        """Get all conversations for a user."""
        return Conversation.query.filter_by(
            user_id=user_id,
            is_active=True
        ).order_by(Conversation.updated_at.desc()).limit(limit).all()
    
    def get_conversation_messages(self, conversation_id: int, user_id: int, limit: int = 100) -> List[Message]:
        """Get messages for a specific conversation."""
        conversation = Conversation.query.filter_by(
            id=conversation_id,
            user_id=user_id
        ).first()
        
        if not conversation:
            return []
        
        return Message.query.filter_by(conversation_id=conversation_id).order_by(Message.created_at.asc()).limit(limit).all()
    
    def add_message(self, conversation_id: int, role: str, content: str, content_type: str = "text", 
                   file_path: str = None, file_name: str = None, file_size: int = None,
                   model_used: str = None, provider_used: str = None, tokens_used: int = None,
                   response_time: float = None, message_metadata: Dict = None) -> Message:
        """Add a message to a conversation."""
        message = Message(
            conversation_id=conversation_id,
            role=role,
            content=content,
            content_type=content_type,
            file_path=file_path,
            file_name=file_name,
            file_size=file_size,
            model_used=model_used,
            provider_used=provider_used,
            tokens_used=tokens_used,
            response_time=response_time,
            message_metadata=json.dumps(message_metadata) if message_metadata else None
        )
        
        db.session.add(message)
        
        # Update conversation timestamp
        conversation = Conversation.query.get(conversation_id)
        if conversation:
            conversation.updated_at = datetime.utcnow()
        
        db.session.commit()
        current_app.logger.info(f"Added message {message.id} to conversation {conversation_id}")
        return message
    
    def process_user_message(self, user_id: int, conversation_id: int, message_content: str, 
                           file_data: Optional[Dict] = None) -> Tuple[Message, Message]:
        """Process a user message and generate AI response."""
        start_time = time.time()
        
        # Add user message
        user_message = self.add_message(
            conversation_id=conversation_id,
            role="user",
            content=message_content,
            content_type="text"
        )
        
        # Handle file upload if present
        file_path = None
        file_name = None
        file_size = None
        
        if file_data:
            file_path, file_name, file_size = self._handle_file_upload(file_data, conversation_id)
            # Add file message
            file_message = self.add_message(
                conversation_id=conversation_id,
                role="user",
                content=f"Uploaded file: {file_name}",
                content_type="file",
                file_path=file_path,
                file_name=file_name,
                file_size=file_size
            )
        
        # Get conversation context using the context window manager
        context_messages = self.context_manager.get_context(conversation_id, strategy="all")
        
        # Generate AI response
        ai_response = self._generate_ai_response(context_messages, file_path, conversation_id)
        
        response_time = time.time() - start_time
        
        # Add AI response
        assistant_message = self.add_message(
            conversation_id=conversation_id,
            role="assistant",
            content=ai_response['content'],
            model_used=ai_response.get('model'),
            provider_used=ai_response.get('provider'),
            tokens_used=ai_response.get('tokens_used'),
            response_time=response_time,
            message_metadata=ai_response.get('metadata')
        )
        
        # Update conversation title if it's the first message
        conversation = Conversation.query.get(conversation_id)
        if conversation and len(conversation.messages) <= 4:  # First few messages
            conversation.update_title_from_messages()
            db.session.commit()
        
        return user_message, assistant_message
    
    def send_message(self, conversation_id: int, user_id: int, message_content: str, 
                    file_data: Optional[Dict] = None) -> Dict:
        """Send a message and get a response. Returns a dictionary with user and assistant messages."""
        try:
            user_message, assistant_message = self.process_user_message(
                user_id=user_id,
                conversation_id=conversation_id,
                message_content=message_content,
                file_data=file_data
            )
            
            if assistant_message:
                return {
                    'user_message': user_message.to_dict(),
                    'assistant_message': assistant_message.to_dict(),
                    'conversation': Conversation.query.get(conversation_id).to_dict()
                }
            else:
                return {
                    'user_message': user_message.to_dict(),
                    'assistant_message': None,
                    'conversation': Conversation.query.get(conversation_id).to_dict()
                }
                
        except Exception as e:
            current_app.logger.error(f"Error sending message: {str(e)}")
            raise
    
    def _handle_file_upload(self, file_data: Dict, conversation_id: int) -> Tuple[str, str, int]:
        """Handle file upload and return file path, name, and size."""
        try:
            # Decode base64 file data
            file_content = base64.b64decode(file_data['content'])
            file_name = secure_filename(file_data['name'])
            
            # Create conversation-specific folder
            conversation_folder = os.path.join(self.upload_folder, str(conversation_id))
            os.makedirs(conversation_folder, exist_ok=True)
            
            # Save file
            file_path = os.path.join(conversation_folder, file_name)
            with open(file_path, 'wb') as f:
                f.write(file_content)
            
            file_size = len(file_content)
            current_app.logger.info(f"File uploaded: {file_path} ({file_size} bytes)")
            
            return file_path, file_name, file_size
            
        except Exception as e:
            current_app.logger.error(f"Error handling file upload: {str(e)}")
            raise ValueError("Failed to process file upload")
    

    
    def _generate_ai_response(self, context_messages: List[Dict], file_path: Optional[str] = None, conversation_id: int = None) -> Dict:
        """Generate AI response using the configured LLM provider."""
        try:
            # Check if this is a buddy conversation
            buddy_prompt = None
            if conversation_id:
                conversation = Conversation.query.get(conversation_id)
                if conversation and conversation.buddy_id:
                    from app.models import Buddy
                    buddy = Buddy.query.get(conversation.buddy_id)
                    if buddy:
                        buddy_prompt = buddy.initial_prompt
            
            # Prepare system prompt
            if buddy_prompt:
                system_prompt = buddy_prompt
            else:
                system_prompt = """You are a helpful AI assistant. Provide clear, accurate, and helpful responses to user questions. 
                If a file is uploaded, analyze it and provide relevant insights. Be conversational but professional."""
            
            # Prepare messages for LLM
            messages = [{"role": "system", "content": system_prompt}]
            
            for msg in context_messages:
                if msg['role'] in ['user', 'assistant']:
                    messages.append({
                        "role": msg['role'],
                        "content": msg['content']
                    })
            
            # Generate response
            response = self.llm_provider.generate_response(
                messages=messages,
                file_path=file_path
            )
            
            return {
                'content': response['content'],
                'model': response.get('model'),
                'provider': response.get('provider'),
                'tokens_used': response.get('tokens_used'),
                'metadata': response.get('metadata', {})
            }
            
        except Exception as e:
            current_app.logger.error(f"Error generating AI response: {str(e)}")
            return {
                'content': "I apologize, but I encountered an error while processing your request. Please try again.",
                'model': None,
                'provider': None,
                'tokens_used': None,
                'metadata': {'error': str(e)}
            }
    
    def delete_conversation(self, conversation_id: int, user_id: int) -> bool:
        """Delete a conversation (soft delete)."""
        conversation = Conversation.query.filter_by(
            id=conversation_id,
            user_id=user_id
        ).first()
        
        if conversation:
            conversation.is_active = False
            db.session.commit()
            current_app.logger.info(f"Deleted conversation {conversation_id} for user {user_id}")
            return True
        
        return False
    
    def rename_conversation(self, conversation_id: int, user_id: int, new_title: str) -> bool:
        """Rename a conversation."""
        conversation = Conversation.query.filter_by(
            id=conversation_id,
            user_id=user_id
        ).first()
        
        if conversation:
            conversation.title = new_title
            db.session.commit()
            current_app.logger.info(f"Renamed conversation {conversation_id} to '{new_title}'")
            return True
        
        return False

# Singleton instance
_chat_service = None

def get_chat_service() -> ChatService:
    """Get the singleton chat service instance."""
    global _chat_service
    if _chat_service is None:
        _chat_service = ChatService()
    return _chat_service 