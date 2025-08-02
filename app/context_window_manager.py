from typing import List, Dict, Optional
from app.models import Message, Conversation
from app.database import db


class ContextWindowManager:
    """
    Manages context window optimization for LLM conversations.
    
    This class implements various strategies for selecting which messages
    to include in the context sent to LLM providers, balancing relevance,
    performance, and token limits.
    """
    
    def __init__(self):
        self.default_max_messages = 20
        self.default_max_tokens = 6000  # Conservative estimate
    
    def get_context(self, conversation_id: int, strategy: str = "recent", **kwargs) -> List[Dict]:
        """
        Get conversation context using the specified strategy.
        
        Args:
            conversation_id: ID of the conversation
            strategy: Context selection strategy ('all', 'recent', 'sliding', 'semantic', 'token_aware')
            **kwargs: Strategy-specific parameters
        
        Returns:
            List of message dictionaries for LLM context
        """
        if strategy == "all":
            return self._get_all_messages(conversation_id)
        elif strategy == "recent":
            max_messages = kwargs.get('max_messages', self.default_max_messages)
            return self._get_recent_messages(conversation_id, max_messages)
        elif strategy == "sliding":
            window_size = kwargs.get('window_size', 15)
            overlap = kwargs.get('overlap', 5)
            return self._get_sliding_window(conversation_id, window_size, overlap)
        elif strategy == "semantic":
            current_message = kwargs.get('current_message', '')
            return self._get_semantic_context(conversation_id, current_message)
        elif strategy == "token_aware":
            max_tokens = kwargs.get('max_tokens', self.default_max_tokens)
            return self._get_token_aware_context(conversation_id, max_tokens)
        else:
            raise ValueError(f"Unknown strategy: {strategy}")
    
    def _get_all_messages(self, conversation_id: int) -> List[Dict]:
        """
        Get all messages for the conversation.
        
        This is the simplest strategy - returns all messages in chronological order.
        Use with caution for long conversations as it may exceed token limits.
        """
        messages = Message.query.filter_by(conversation_id=conversation_id).order_by(Message.created_at.asc()).all()
        
        context = []
        for msg in messages:
            context.append({
                'role': msg.role,
                'content': msg.content,
                'content_type': msg.content_type,
                'file_path': msg.file_path if msg.is_file_message() else None
            })
        
        return context
    
    def _get_recent_messages(self, conversation_id: int, max_messages: int) -> List[Dict]:
        """
        Get the most recent messages with smart context selection.
        
        For long conversations, includes early context (system setup) and recent messages.
        """
        all_messages = Message.query.filter_by(conversation_id=conversation_id).order_by(Message.created_at.asc()).all()
        
        if len(all_messages) <= max_messages:
            messages = all_messages
        else:
            # Smart context selection: prioritize recent messages but include some earlier context
            if len(all_messages) > max_messages * 2:
                # Include first few messages (system/buddy setup) and recent messages
                early_messages = all_messages[:3]  # First 3 messages (usually system setup)
                recent_messages = all_messages[-(max_messages-3):]  # Recent messages minus the 3 we took from early
                messages = early_messages + recent_messages
            else:
                messages = all_messages[-max_messages:]
        
        context = []
        for msg in messages:
            context.append({
                'role': msg.role,
                'content': msg.content,
                'content_type': msg.content_type,
                'file_path': msg.file_path if msg.is_file_message() else None
            })
        
        return context
    
    def _get_sliding_window(self, conversation_id: int, window_size: int, overlap: int) -> List[Dict]:
        """
        Get messages using a sliding window approach.
        
        This maintains some continuity by overlapping with previous context.
        """
        all_messages = Message.query.filter_by(conversation_id=conversation_id).order_by(Message.created_at.asc()).all()
        
        if len(all_messages) <= window_size:
            messages = all_messages
        else:
            # For now, just get the most recent window_size messages
            # In a more sophisticated implementation, we'd track the previous window
            messages = all_messages[-window_size:]
        
        context = []
        for msg in messages:
            context.append({
                'role': msg.role,
                'content': msg.content,
                'content_type': msg.content_type,
                'file_path': msg.file_path if msg.is_file_message() else None
            })
        
        return context
    
    def _get_semantic_context(self, conversation_id: int, current_message: str) -> List[Dict]:
        """
        Get context based on semantic similarity to current message.
        
        This would use embeddings to find the most relevant historical messages.
        For now, falls back to recent messages strategy.
        """
        # TODO: Implement semantic similarity using embeddings
        # For now, use recent messages as fallback
        return self._get_recent_messages(conversation_id, self.default_max_messages)
    
    def _get_token_aware_context(self, conversation_id: int, max_tokens: int) -> List[Dict]:
        """
        Get context while respecting token limits.
        
        Estimates token usage and builds context intelligently.
        """
        all_messages = Message.query.filter_by(conversation_id=conversation_id).order_by(Message.created_at.asc()).all()
        
        context = []
        estimated_tokens = 0
        
        # Start with system messages (first few)
        system_messages = all_messages[:3]
        for msg in system_messages:
            msg_tokens = self._estimate_tokens(msg.content)
            if estimated_tokens + msg_tokens <= max_tokens:
                context.append({
                    'role': msg.role,
                    'content': msg.content,
                    'content_type': msg.content_type,
                    'file_path': msg.file_path if msg.is_file_message() else None
                })
                estimated_tokens += msg_tokens
        
        # Add recent messages until we hit token limit
        recent_messages = all_messages[3:]  # Skip system messages we already added
        for msg in reversed(recent_messages):  # Start from most recent
            msg_tokens = self._estimate_tokens(msg.content)
            if estimated_tokens + msg_tokens <= max_tokens:
                context.insert(-len(system_messages), {  # Insert before system messages
                    'role': msg.role,
                    'content': msg.content,
                    'content_type': msg.content_type,
                    'file_path': msg.file_path if msg.is_file_message() else None
                })
                estimated_tokens += msg_tokens
            else:
                break
        
        return context
    
    def _estimate_tokens(self, text: str) -> int:
        """
        Estimate token count for a text string.
        
        This is a rough approximation. For more accuracy, use the actual tokenizer
        of the LLM provider being used.
        """
        # Rough estimate: 1 token ≈ 4 characters for English text
        return len(text) // 4 + 1


# Singleton instance
_context_window_manager = None

def get_context_window_manager() -> ContextWindowManager:
    """Get the singleton context window manager instance."""
    global _context_window_manager
    if _context_window_manager is None:
        _context_window_manager = ContextWindowManager()
    return _context_window_manager 