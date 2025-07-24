from flask import Flask
from app.models import User
from config import get_config
from app.database import db, init_db
from app.logging import setup_logging
from flask_login import LoginManager
from flask_mail import Mail
from app.intent_analyzer import create_intent_analyzer
import os

# Initialize extensions
mail = Mail()


def create_app(config_class=None):
    app = Flask(__name__)
    
    # Load config
    if config_class is None:
        config_class = get_config()
    app.config.from_object(config_class)
    
    # Initialize database
    init_db(app)
    app.db = db  # For backwards compatibility if needed

    # Logging
    setup_logging(app)
    
    # Login management
    login_manager = LoginManager()
    login_manager.init_app(app)
    
    # Mail initialization
    mail.init_app(app)

    # Set up login manager
    login_manager.login_view = 'auth.initiate_auth'
    login_manager.login_message = 'Please log in to access this page.'
    login_manager.login_message_category = 'info'

    @login_manager.user_loader
    def load_user(user_id):
        from app.models import User
        return User.query.get(int(user_id))

    # Initialize Intent Analyzer as singleton
    def init_intent_analyzer():
        """Initialize the intent analyzer based on configuration."""
        provider_type = os.getenv('INTENT_PROVIDER', 'openai')
        
        if provider_type == 'openai':
            api_key = os.getenv('OPENAI_API_KEY')
            model = os.getenv('OPENAI_MODEL', 'gpt-4o')
            return create_intent_analyzer('openai', api_key=api_key, model=model)
        elif provider_type == 'anthropic':
            api_key = os.getenv('ANTHROPIC_API_KEY')
            model = os.getenv('ANTHROPIC_MODEL', 'claude-3-sonnet-20240229')
            return create_intent_analyzer('anthropic', api_key=api_key, model=model)
        else:
            # Default to mock provider
            return create_intent_analyzer('mock')
    
    # Store intent analyzer in app context
    app.intent_analyzer = init_intent_analyzer()
    
    # Register blueprints
    from app.routes.auth import auth_bp
    app.register_blueprint(auth_bp)

    return app
