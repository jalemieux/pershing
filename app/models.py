from flask_login import UserMixin
from app.database import db
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
import secrets

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)
    is_admin = db.Column(db.Boolean, default=False)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'created_at': self.created_at.isoformat(),
            'is_admin': self.is_admin
        }
    
    def get_active_sessions(self):
        """Get all active sessions for this user."""
        return UserSession.query.filter_by(
            user_id=self.id
        ).filter(
            UserSession.expires_at > datetime.utcnow()
        ).order_by(UserSession.created_at.desc()).all()
    
    def cleanup_expired_sessions(self):
        """Remove expired sessions for this user."""
        expired_sessions = UserSession.query.filter_by(
            user_id=self.id
        ).filter(
            UserSession.expires_at <= datetime.utcnow()
        ).all()
        
        for session in expired_sessions:
            db.session.delete(session)
        
        if expired_sessions:
            db.session.commit()
        
        return len(expired_sessions)

class SavedPrompt(db.Model):
    """Model for storing user-saved prompts."""
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    name = db.Column(db.String(255), nullable=False)
    original_message = db.Column(db.Text, nullable=False)
    model = db.Column(db.String(100), nullable=False)
    prompt_content = db.Column(db.Text, nullable=False)
    prompt_type = db.Column(db.String(100), nullable=True)
    provider = db.Column(db.String(100), nullable=True)
    prompt_metadata = db.Column(db.Text, nullable=True)  # JSON string for additional data
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationship
    user = db.relationship('User', backref=db.backref('saved_prompts', lazy=True))
    
    def to_dict(self):
        """Convert the saved prompt to a dictionary."""
        return {
            'id': self.id,
            'name': self.name,
            'original_message': self.original_message,
            'model': self.model,
            'prompt_content': self.prompt_content,
            'prompt_type': self.prompt_type,
            'provider': self.provider,
            'prompt_metadata': self.prompt_metadata,
            'created_at': self.created_at.isoformat()
        }

class VerificationCode(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), nullable=False)
    code_hash = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    expires_at = db.Column(db.DateTime)
    attempts = db.Column(db.Integer, default=0)
    used = db.Column(db.Boolean, default=False)
    
    def __init__(self, email):
        self.email = email
        self.code = str(secrets.randbelow(1000000)).zfill(6)  # Generate 6-digit code
        self.code_hash = generate_password_hash(self.code)
        self.expires_at = datetime.utcnow() + timedelta(minutes=10)
    
    def verify_code(self, code):
        return check_password_hash(self.code_hash, code)
    
    def is_expired(self):
        return datetime.utcnow() > self.expires_at
    
    def increment_attempts(self):
        self.attempts += 1
        return self.attempts >= 3

class UserSession(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    session_token = db.Column(db.String(255), unique=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    expires_at = db.Column(db.DateTime)
    device_info = db.Column(db.Text)
    
    def __init__(self, user_id, remember=True, device_info=None):
        self.user_id = user_id
        self.session_token = secrets.token_urlsafe(32)
        self.device_info = device_info
        # Always use 90 days since remember is always True
        self.expires_at = datetime.utcnow() + timedelta(days=90)
    
    def is_valid(self):
        return datetime.utcnow() <= self.expires_at
    
    @classmethod
    def cleanup_all_expired(cls):
        """Remove all expired sessions from the database."""
        expired_sessions = cls.query.filter(
            cls.expires_at <= datetime.utcnow()
        ).all()
        
        for session in expired_sessions:
            db.session.delete(session)
        
        if expired_sessions:
            db.session.commit()
        
        return len(expired_sessions) 

class Conversation(db.Model):
    """Model for storing chat conversations."""
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    buddy_id = db.Column(db.Integer, db.ForeignKey('buddy.id'), nullable=True)  # Link to buddy if this is a buddy conversation
    title = db.Column(db.String(255), nullable=False, default='New Conversation')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)
    conversation_type = db.Column(db.String(50), default='text')  # text, image, multimodal
    
    # Relationships
    user = db.relationship('User', backref=db.backref('conversations', lazy=True))
    buddy = db.relationship('Buddy', backref=db.backref('conversations', lazy=True))
    messages = db.relationship('Message', backref='conversation', lazy=True, cascade='all, delete-orphan')
    
    def to_dict(self):
        """Convert conversation to dictionary."""
        return {
            'id': self.id,
            'title': self.title,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'is_active': self.is_active,
            'conversation_type': self.conversation_type,
            'message_count': len(self.messages)
        }
    
    def get_last_message(self):
        """Get the most recent message in this conversation."""
        return Message.query.filter_by(conversation_id=self.id).order_by(Message.created_at.desc()).first()
    
    def update_title_from_messages(self):
        """Update conversation title based on first few messages."""
        first_messages = Message.query.filter_by(conversation_id=self.id).order_by(Message.created_at.asc()).limit(3).all()
        if first_messages:
            # Create title from first user message
            for msg in first_messages:
                if msg.role == 'user':
                    title = msg.content[:50]
                    if len(msg.content) > 50:
                        title += '...'
                    self.title = title
                    break

class Message(db.Model):
    """Model for storing individual chat messages."""
    id = db.Column(db.Integer, primary_key=True)
    conversation_id = db.Column(db.Integer, db.ForeignKey('conversation.id'), nullable=False)
    role = db.Column(db.String(20), nullable=False)  # user, assistant, system
    content = db.Column(db.Text, nullable=False)
    content_type = db.Column(db.String(20), default='text')  # text, image, file
    file_path = db.Column(db.String(500), nullable=True)  # For uploaded files
    file_name = db.Column(db.String(255), nullable=True)
    file_size = db.Column(db.Integer, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    tokens_used = db.Column(db.Integer, nullable=True)
    model_used = db.Column(db.String(100), nullable=True)
    provider_used = db.Column(db.String(100), nullable=True)
    response_time = db.Column(db.Float, nullable=True)  # Response time in seconds
    message_metadata = db.Column(db.Text, nullable=True)  # JSON string for additional data
    
    def to_dict(self):
        """Convert message to dictionary."""
        return {
            'id': self.id,
            'conversation_id': self.conversation_id,
            'role': self.role,
            'content': self.content,
            'content_type': self.content_type,
            'file_path': self.file_path,
            'file_name': self.file_name,
            'file_size': self.file_size,
            'created_at': self.created_at.isoformat(),
            'tokens_used': self.tokens_used,
            'model_used': self.model_used,
            'provider_used': self.provider_used,
            'response_time': self.response_time,
            'metadata': self.message_metadata
        }
    
    def is_file_message(self):
        """Check if this message contains a file."""
        return self.content_type in ['image', 'file'] and self.file_path is not None 

class Buddy(db.Model):
    """Model for storing user-created Buddies."""
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    name = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text, nullable=True)
    initial_prompt = db.Column(db.Text, nullable=False)
    memory_type = db.Column(db.String(50), nullable=False, default='short_term')  # short_term, long_term, task_specific
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = db.relationship('User', backref=db.backref('buddies', lazy=True))
    tools = db.relationship('BuddyTool', backref='buddy', lazy=True, cascade='all, delete-orphan')
    
    def to_dict(self):
        """Convert the buddy to a dictionary."""
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'initial_prompt': self.initial_prompt,
            'memory_type': self.memory_type,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'tools': [tool.to_dict() for tool in self.tools]
        }

class BuddyTool(db.Model):
    """Model for storing tools that Buddies can use."""
    id = db.Column(db.Integer, primary_key=True)
    buddy_id = db.Column(db.Integer, db.ForeignKey('buddy.id'), nullable=False)
    tool_name = db.Column(db.String(255), nullable=False)
    tool_type = db.Column(db.String(100), nullable=False)  # api, database, file_system, etc.
    tool_config = db.Column(db.Text, nullable=True)  # JSON string for tool configuration
    is_enabled = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        """Convert the buddy tool to a dictionary."""
        return {
            'id': self.id,
            'tool_name': self.tool_name,
            'tool_type': self.tool_type,
            'tool_config': self.tool_config,
            'is_enabled': self.is_enabled,
            'created_at': self.created_at.isoformat()
        }

class BuddyMemory(db.Model):
    """Model for storing Buddy memory data."""
    id = db.Column(db.Integer, primary_key=True)
    buddy_id = db.Column(db.Integer, db.ForeignKey('buddy.id'), nullable=False)
    memory_type = db.Column(db.String(50), nullable=False)  # short_term, long_term, task_specific
    memory_key = db.Column(db.String(255), nullable=False)
    memory_value = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    expires_at = db.Column(db.DateTime, nullable=True)  # For short-term memory
    
    # Relationships
    buddy = db.relationship('Buddy', backref=db.backref('memories', lazy=True))
    
    def to_dict(self):
        """Convert the buddy memory to a dictionary."""
        return {
            'id': self.id,
            'memory_type': self.memory_type,
            'memory_key': self.memory_key,
            'memory_value': self.memory_value,
            'created_at': self.created_at.isoformat(),
            'expires_at': self.expires_at.isoformat() if self.expires_at else None
        }
    
    def is_expired(self):
        """Check if this memory entry has expired."""
        if self.expires_at:
            return datetime.utcnow() > self.expires_at
        return False 