from flask import Blueprint, request, jsonify, current_app, render_template
from flask_login import login_required, current_user
from app.buddy_service import get_buddy_service
from app.models import Buddy, Conversation, Message
from app.database import db
import json

buddies_bp = Blueprint('buddies', __name__)

@buddies_bp.route('/buddies')
@login_required
def buddies_dashboard():
    """Main buddies dashboard page."""
    return render_template('buddies/dashboard.html', user=current_user)

@buddies_bp.route('/buddies/create')
@login_required
def create_buddy_page():
    """Page for creating a new buddy."""
    buddy_service = get_buddy_service()
    available_tools = buddy_service.get_available_tools()
    return render_template('buddies/create.html', user=current_user, tools=available_tools)

@buddies_bp.route('/buddies/<int:buddy_id>')
@login_required
def buddy_detail(buddy_id):
    """Buddy detail page."""
    buddy_service = get_buddy_service()
    buddy = buddy_service.get_buddy(buddy_id, current_user.id)
    
    if not buddy:
        return "Buddy not found", 404
    
    return render_template('buddies/detail.html', user=current_user, buddy=buddy)

@buddies_bp.route('/buddies/<int:buddy_id>/conversations')
@login_required
def buddy_conversations(buddy_id):
    """Buddy conversations page."""
    buddy_service = get_buddy_service()
    buddy = buddy_service.get_buddy(buddy_id, current_user.id)
    
    if not buddy:
        return "Buddy not found", 404
    
    # Get conversations for this buddy
    conversations = Conversation.query.filter_by(
        buddy_id=buddy_id,
        user_id=current_user.id,
        is_active=True
    ).order_by(Conversation.updated_at.desc()).all()
    
    return render_template('buddies/conversations.html', user=current_user, buddy=buddy, conversations=conversations)

@buddies_bp.route('/api/buddies', methods=['GET'])
@login_required
def get_buddies():
    """Get all buddies for the current user."""
    try:
        buddy_service = get_buddy_service()
        buddies = buddy_service.get_user_buddies(current_user.id)
        
        return jsonify({
            'success': True,
            'buddies': [buddy.to_dict() for buddy in buddies]
        })
        
    except Exception as e:
        current_app.logger.error(f"Error getting buddies: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Failed to retrieve buddies'
        }), 500

@buddies_bp.route('/api/buddies', methods=['POST'])
@login_required
def create_buddy():
    """Create a new buddy."""
    try:
        data = request.get_json()
        if not data:
            return jsonify({
                'success': False,
                'error': 'No data provided'
            }), 400
        
        name = data.get('name', '').strip()
        initial_prompt = data.get('initial_prompt', '').strip()
        description = data.get('description', '').strip()
        memory_type = data.get('memory_type', 'short_term')
        tools = data.get('tools', [])
        
        if not name:
            return jsonify({
                'success': False,
                'error': 'Buddy name is required'
            }), 400
        
        if not initial_prompt:
            return jsonify({
                'success': False,
                'error': 'Initial prompt is required'
            }), 400
        
        buddy_service = get_buddy_service()
        buddy = buddy_service.create_buddy(
            user_id=current_user.id,
            name=name,
            initial_prompt=initial_prompt,
            description=description,
            memory_type=memory_type,
            tools=tools
        )
        
        return jsonify({
            'success': True,
            'buddy': buddy.to_dict(),
            'message': f'Buddy "{name}" created successfully!'
        })
        
    except Exception as e:
        current_app.logger.error(f"Error creating buddy: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Failed to create buddy'
        }), 500

@buddies_bp.route('/api/buddies/<int:buddy_id>', methods=['GET'])
@login_required
def get_buddy(buddy_id):
    """Get a specific buddy."""
    try:
        buddy_service = get_buddy_service()
        buddy = buddy_service.get_buddy(buddy_id, current_user.id)
        
        if not buddy:
            return jsonify({
                'success': False,
                'error': 'Buddy not found'
            }), 404
        
        return jsonify({
            'success': True,
            'buddy': buddy.to_dict()
        })
        
    except Exception as e:
        current_app.logger.error(f"Error getting buddy: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Failed to retrieve buddy'
        }), 500

@buddies_bp.route('/api/buddies/<int:buddy_id>', methods=['PUT'])
@login_required
def update_buddy(buddy_id):
    """Update a buddy."""
    try:
        data = request.get_json()
        if not data:
            return jsonify({
                'success': False,
                'error': 'No data provided'
            }), 400
        
        buddy_service = get_buddy_service()
        buddy = buddy_service.update_buddy(buddy_id, current_user.id, **data)
        
        return jsonify({
            'success': True,
            'buddy': buddy.to_dict(),
            'message': 'Buddy updated successfully!'
        })
        
    except ValueError as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 404
        
    except Exception as e:
        current_app.logger.error(f"Error updating buddy: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Failed to update buddy'
        }), 500

@buddies_bp.route('/api/buddies/<int:buddy_id>', methods=['DELETE'])
@login_required
def delete_buddy(buddy_id):
    """Delete a buddy."""
    try:
        buddy_service = get_buddy_service()
        buddy = buddy_service.delete_buddy(buddy_id, current_user.id)
        
        return jsonify({
            'success': True,
            'message': f'Buddy "{buddy.name}" deleted successfully!'
        })
        
    except ValueError as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 404
        
    except Exception as e:
        current_app.logger.error(f"Error deleting buddy: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Failed to delete buddy'
        }), 500

@buddies_bp.route('/api/buddies/<int:buddy_id>/conversations', methods=['GET'])
@login_required
def get_buddy_conversations(buddy_id):
    """Get all conversations for a specific buddy."""
    try:
        # Get conversations that have this buddy_id
        conversations = Conversation.query.filter_by(
            buddy_id=buddy_id,
            user_id=current_user.id,
            is_active=True
        ).order_by(Conversation.updated_at.desc()).all()
        
        return jsonify({
            'success': True,
            'conversations': [conv.to_dict() for conv in conversations]
        })
        
    except Exception as e:
        current_app.logger.error(f"Error getting buddy conversations: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Failed to retrieve conversations'
        }), 500

@buddies_bp.route('/api/buddies/<int:buddy_id>/conversations', methods=['POST'])
@login_required
def create_buddy_conversation(buddy_id):
    """Create a new conversation with a buddy."""
    try:
        data = request.get_json() or {}
        title = data.get('title')
        
        buddy_service = get_buddy_service()
        conversation = buddy_service.create_buddy_conversation(buddy_id, current_user.id, title)
        
        return jsonify({
            'success': True,
            'conversation': conversation.to_dict()
        })
        
    except ValueError as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 404
        
    except Exception as e:
        current_app.logger.error(f"Error creating buddy conversation: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Failed to create conversation'
        }), 500

# Note: For buddy conversations, we'll use the existing chat routes
# The conversation will have a buddy_id set, so we can filter accordingly

@buddies_bp.route('/api/buddies/tools', methods=['GET'])
@login_required
def get_available_tools():
    """Get list of available tools for buddies."""
    try:
        buddy_service = get_buddy_service()
        tools = buddy_service.get_available_tools()
        
        return jsonify({
            'success': True,
            'tools': tools
        })
        
    except Exception as e:
        current_app.logger.error(f"Error getting available tools: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Failed to retrieve tools'
        }), 500

@buddies_bp.route('/buddies/<int:buddy_id>/chat')
@login_required
def chat_with_buddy(buddy_id):
    """Chat interface for a specific buddy."""
    buddy_service = get_buddy_service()
    buddy = buddy_service.get_buddy(buddy_id, current_user.id)
    
    if not buddy:
        return "Buddy not found", 404
    
    return render_template('buddies/chat.html', user=current_user, buddy=buddy) 