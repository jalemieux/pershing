from flask import Blueprint, request, jsonify, current_app
from flask_login import login_required, current_user
from app.chat_service import get_chat_service
from app.models import Conversation, Message
from app.database import db
import json

chat_bp = Blueprint('chat', __name__)

@chat_bp.route('/api/chat/conversations', methods=['GET'])
@login_required
def get_conversations():
    """Get all conversations for the current user."""
    try:
        chat_service = get_chat_service()
        conversations = chat_service.get_user_conversations(current_user.id)
        
        return jsonify({
            'success': True,
            'conversations': [conv.to_dict() for conv in conversations]
        })
        
    except Exception as e:
        current_app.logger.error(f"Error getting conversations: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Failed to retrieve conversations'
        }), 500

@chat_bp.route('/api/chat/conversations', methods=['POST'])
@login_required
def create_conversation():
    """Create a new conversation."""
    try:
        data = request.get_json() or {}
        title = data.get('title', 'New Conversation')
        conversation_type = data.get('type', 'text')
        
        chat_service = get_chat_service()
        conversation = chat_service.create_conversation(
            user_id=current_user.id,
            title=title,
            conversation_type=conversation_type
        )
        
        return jsonify({
            'success': True,
            'conversation': conversation.to_dict()
        })
        
    except Exception as e:
        current_app.logger.error(f"Error creating conversation: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Failed to create conversation'
        }), 500

@chat_bp.route('/api/chat/conversations/<int:conversation_id>/messages', methods=['GET'])
@login_required
def get_messages(conversation_id):
    """Get messages for a specific conversation."""
    try:
        chat_service = get_chat_service()
        messages = chat_service.get_conversation_messages(conversation_id, current_user.id)
        
        return jsonify({
            'success': True,
            'messages': [msg.to_dict() for msg in messages]
        })
        
    except Exception as e:
        current_app.logger.error(f"Error getting messages: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Failed to retrieve messages'
        }), 500

@chat_bp.route('/api/chat/conversations/<int:conversation_id>/messages', methods=['POST'])
@login_required
def send_message(conversation_id):
    """Send a message to a conversation."""
    try:
        data = request.get_json()
        if not data:
            return jsonify({
                'success': False,
                'error': 'No data provided'
            }), 400
        
        message_content = data.get('message', '').strip()
        if not message_content:
            return jsonify({
                'success': False,
                'error': 'Message content is required'
            }), 400
        
        file_data = data.get('file')  # Optional file upload
        
        # Verify conversation belongs to user
        conversation = Conversation.query.filter_by(
            id=conversation_id,
            user_id=current_user.id
        ).first()
        
        if not conversation:
            return jsonify({
                'success': False,
                'error': 'Conversation not found'
            }), 404
        
        chat_service = get_chat_service()
        user_message, assistant_message = chat_service.process_user_message(
            user_id=current_user.id,
            conversation_id=conversation_id,
            message_content=message_content,
            file_data=file_data
        )
        
        return jsonify({
            'success': True,
            'user_message': user_message.to_dict(),
            'assistant_message': assistant_message.to_dict(),
            'conversation': conversation.to_dict()
        })
        
    except ValueError as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400
        
    except Exception as e:
        current_app.logger.error(f"Error sending message: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Failed to send message'
        }), 500

@chat_bp.route('/api/chat/conversations/<int:conversation_id>', methods=['DELETE'])
@login_required
def delete_conversation(conversation_id):
    """Delete a conversation."""
    try:
        chat_service = get_chat_service()
        success = chat_service.delete_conversation(conversation_id, current_user.id)
        
        if success:
            return jsonify({
                'success': True,
                'message': 'Conversation deleted successfully'
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Conversation not found'
            }), 404
            
    except Exception as e:
        current_app.logger.error(f"Error deleting conversation: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Failed to delete conversation'
        }), 500

@chat_bp.route('/api/chat/conversations/<int:conversation_id>/rename', methods=['PUT'])
@login_required
def rename_conversation(conversation_id):
    """Rename a conversation."""
    try:
        data = request.get_json()
        if not data:
            return jsonify({
                'success': False,
                'error': 'No data provided'
            }), 400
        
        new_title = data.get('title', '').strip()
        if not new_title:
            return jsonify({
                'success': False,
                'error': 'Title is required'
            }), 400
        
        chat_service = get_chat_service()
        success = chat_service.rename_conversation(conversation_id, current_user.id, new_title)
        
        if success:
            return jsonify({
                'success': True,
                'message': 'Conversation renamed successfully'
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Conversation not found'
            }), 404
            
    except Exception as e:
        current_app.logger.error(f"Error renaming conversation: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Failed to rename conversation'
        }), 500

@chat_bp.route('/api/chat/conversations/<int:conversation_id>', methods=['GET'])
@login_required
def get_conversation(conversation_id):
    """Get a specific conversation with its messages."""
    try:
        conversation = Conversation.query.filter_by(
            id=conversation_id,
            user_id=current_user.id
        ).first()
        
        if not conversation:
            return jsonify({
                'success': False,
                'error': 'Conversation not found'
            }), 404
        
        chat_service = get_chat_service()
        messages = chat_service.get_conversation_messages(conversation_id, current_user.id)
        
        return jsonify({
            'success': True,
            'conversation': conversation.to_dict(),
            'messages': [msg.to_dict() for msg in messages]
        })
        
    except Exception as e:
        current_app.logger.error(f"Error getting conversation: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Failed to retrieve conversation'
        }), 500

@chat_bp.route('/api/chat/stats', methods=['GET'])
@login_required
def get_chat_stats():
    """Get chat statistics for the current user."""
    try:
        # Get conversation count
        conversation_count = Conversation.query.filter_by(
            user_id=current_user.id,
            is_active=True
        ).count()
        
        # Get message count
        message_count = db.session.query(Message).join(Conversation).filter(
            Conversation.user_id == current_user.id,
            Conversation.is_active == True
        ).count()
        
        # Get recent activity
        recent_conversations = Conversation.query.filter_by(
            user_id=current_user.id,
            is_active=True
        ).order_by(Conversation.updated_at.desc()).limit(5).all()
        
        return jsonify({
            'success': True,
            'stats': {
                'total_conversations': conversation_count,
                'total_messages': message_count,
                'recent_conversations': [conv.to_dict() for conv in recent_conversations]
            }
        })
        
    except Exception as e:
        current_app.logger.error(f"Error getting chat stats: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Failed to retrieve chat statistics'
        }), 500 