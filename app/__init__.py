from flask import Flask
from app.models import User
from config import get_config
from app.database import db, init_db
from app.logging import setup_logging
from flask_login import LoginManager
from flask_mail import Mail
from app.intent_analyzer import create_intent_analyzer
from app.prompt_crafter import create_multi_provider_prompt_crafter
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
        app.logger.info(f"Loading user {user_id}")
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
    
    # Initialize Multi-Provider Prompt Crafter as singleton
    def init_multi_provider_prompt_crafter():
        """Initialize the multi-provider prompt crafter based on configuration."""
        providers_config = {}
        
        # Add OpenAI provider if API key is available
        openai_api_key = os.getenv('OPENAI_API_KEY')
        if openai_api_key:
            providers_config['openai'] = {
                'api_key': openai_api_key,
                'model': os.getenv('OPENAI_MODEL', 'gpt-4o-2024-08-06')
            }
        
        # Add Anthropic provider if API key is available
        anthropic_api_key = os.getenv('ANTHROPIC_API_KEY')
        if anthropic_api_key:
            providers_config['anthropic'] = {
                'api_key': anthropic_api_key,
                'model': os.getenv('ANTHROPIC_MODEL', 'claude-3-sonnet-20240229')
            }
        
        # If no API keys are available, use mock provider
        if not providers_config:
            providers_config['mock'] = {}
        
        return create_multi_provider_prompt_crafter(providers_config)
    
    # Store multi-provider prompt crafter in app context
    app.multi_provider_prompt_crafter = init_multi_provider_prompt_crafter()
    
    # # Also keep the single provider prompt crafter for backward compatibility
    # def init_prompt_crafter():
    #     """Initialize the single provider prompt crafter based on configuration."""
    #     provider_type = os.getenv('PROMPT_PROVIDER', 'mock')
        
    #     if provider_type == 'openai':
    #         api_key = os.getenv('OPENAI_API_KEY')
    #         model = os.getenv('OPENAI_MODEL', 'gpt-4o-2024-08-06')
    #         return create_prompt_crafter('openai', api_key=api_key, model=model)
    #     else:
    #         # Default to mock provider
    #         return create_prompt_crafter('mock')
    
    # # Store prompt crafter in app context
    # app.prompt_crafter = init_prompt_crafter()
    
    # Register blueprints
    from app.routes.auth import auth_bp
    app.register_blueprint(auth_bp)
    
    # Register chat blueprint
    from app.routes.chat import chat_bp
    app.register_blueprint(chat_bp)

    return app
