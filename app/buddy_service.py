from app.database import db
from app.models import Buddy, BuddyTool, BuddyMemory, Conversation, Message
from app.chat_service import get_chat_service
from app.chat_llm_providers import get_chat_llm_provider
from datetime import datetime, timedelta
import json
import logging

logger = logging.getLogger(__name__)

class BuddyService:
    """Service class for managing Buddies and their conversations."""
    
    def __init__(self):
        self.chat_service = get_chat_service()
        self.llm_provider = get_chat_llm_provider()
    
    def create_buddy(self, user_id, name, initial_prompt, description=None, 
                     memory_type='short_term', tools=None):
        """Create a new Buddy for a user."""
        try:
            buddy = Buddy(
                user_id=user_id,
                name=name,
                description=description,
                initial_prompt=initial_prompt,
                memory_type=memory_type
            )
            
            db.session.add(buddy)
            db.session.flush()  # Get the buddy ID
            
            # Add tools if provided
            if tools:
                for tool_data in tools:
                    tool = BuddyTool(
                        buddy_id=buddy.id,
                        tool_name=tool_data['name'],
                        tool_type=tool_data['type'],
                        tool_config=json.dumps(tool_data.get('config', {}))
                    )
                    db.session.add(tool)
            
            db.session.commit()
            logger.info(f"Created buddy '{name}' for user {user_id}")
            return buddy
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error creating buddy: {str(e)}")
            raise
    
    def get_user_buddies(self, user_id):
        """Get all buddies for a user."""
        return Buddy.query.filter_by(user_id=user_id, is_active=True).all()
    
    def get_buddy(self, buddy_id, user_id=None):
        """Get a specific buddy by ID."""
        query = Buddy.query.filter_by(id=buddy_id, is_active=True)
        if user_id:
            query = query.filter_by(user_id=user_id)
        return query.first()
    
    def update_buddy(self, buddy_id, user_id, **kwargs):
        """Update a buddy's properties."""
        buddy = self.get_buddy(buddy_id, user_id)
        if not buddy:
            raise ValueError("Buddy not found")
        
        for key, value in kwargs.items():
            if hasattr(buddy, key):
                setattr(buddy, key, value)
        
        buddy.updated_at = datetime.utcnow()
        db.session.commit()
        return buddy
    
    def delete_buddy(self, buddy_id, user_id):
        """Soft delete a buddy."""
        buddy = self.get_buddy(buddy_id, user_id)
        if not buddy:
            raise ValueError("Buddy not found")
        
        buddy.is_active = False
        db.session.commit()
        return buddy
    
    def create_buddy_conversation(self, buddy_id, user_id, title=None):
        """Create a new conversation with a buddy using existing chat service."""
        buddy = self.get_buddy(buddy_id, user_id)
        if not buddy:
            raise ValueError("Buddy not found")
        
        if not title:
            title = f"Conversation with {buddy.name}"
        
        # Use existing chat service to create conversation
        conversation = self.chat_service.create_conversation(
            user_id=user_id,
            title=title,
            conversation_type='text',
            buddy_id=buddy_id
        )
        
        # Add system message with buddy's initial prompt
        system_message = Message(
            conversation_id=conversation.id,
            role='system',
            content=buddy.initial_prompt
        )
        db.session.add(system_message)
        db.session.commit()
        
        return conversation
    
    # Note: get_buddy_conversations is now handled directly in the routes
    # to avoid circular dependencies and keep the service focused on buddy management
    
    # Note: send_message_to_buddy is now handled by the existing chat service
    # The chat service will automatically handle buddy conversations when buddy_id is set
    
    def _get_buddy_memory_context(self, buddy_id):
        """Get relevant memory context for a buddy."""
        # Get long-term and task-specific memories
        memories = BuddyMemory.query.filter_by(
            buddy_id=buddy_id,
            memory_type='long_term'
        ).filter(
            (BuddyMemory.expires_at.is_(None)) | 
            (BuddyMemory.expires_at > datetime.utcnow())
        ).order_by(BuddyMemory.created_at.desc()).limit(5).all()
        
        if not memories:
            return None
        
        context_parts = []
        for memory in memories:
            context_parts.append(f"{memory.memory_key}: {memory.memory_value}")
        
        return " | ".join(context_parts)
    
    def _store_buddy_memory(self, buddy_id, user_input, assistant_response):
        """Store relevant information in buddy memory."""
        # Simple implementation - store key insights
        # In a more sophisticated system, you might use NLP to extract key information
        
        # Store the interaction pattern
        memory_key = f"interaction_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"
        memory_value = f"User: {user_input[:100]}... | Assistant: {assistant_response[:100]}..."
        
        memory = BuddyMemory(
            buddy_id=buddy_id,
            memory_type='long_term',
            memory_key=memory_key,
            memory_value=memory_value
        )
        
        db.session.add(memory)
        db.session.commit()
    
    def get_available_tools(self):
        """Get list of available tools that can be assigned to buddies."""
        return [
            {
                'name': 'Web Search',
                'type': 'api',
                'description': 'Search the web for current information',
                'config': {'api_key_required': True}
            },
            {
                'name': 'File System',
                'type': 'file_system',
                'description': 'Read and write files on the system',
                'config': {'permissions': ['read', 'write']}
            },
            {
                'name': 'Database Query',
                'type': 'database',
                'description': 'Query databases for information',
                'config': {'connection_required': True}
            },
            {
                'name': 'Email',
                'type': 'api',
                'description': 'Send and receive emails',
                'config': {'smtp_required': True}
            },
            {
                'name': 'Calendar',
                'type': 'api',
                'description': 'Manage calendar events',
                'config': {'oauth_required': True}
            }
        ]

# Singleton instance
_buddy_service = None

def get_buddy_service():
    """Get the singleton buddy service instance."""
    global _buddy_service
    if _buddy_service is None:
        _buddy_service = BuddyService()
    return _buddy_service 