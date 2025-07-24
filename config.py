import os
from dotenv import load_dotenv
from datetime import timedelta

flask_env = os.getenv('FLASK_ENV', 'development')
load_dotenv(f'.env.{flask_env}', override=True)


class Config:
    """Base config."""
    # Flask configuration
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-key-please-change-in-production'
    SQLALCHEMY_TRACK_MODIFICATIONS = False 
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')
    # Flask-Mail
    MAIL_SERVER = os.environ.get('MAIL_SERVER', 'smtp.gmail.com')
    MAIL_PORT = int(os.environ.get('MAIL_PORT', 587))
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS', 'true').lower() in ['true', 'on', '1']
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    MAIL_DEFAULT_SENDER = os.environ.get('MAIL_DEFAULT_SENDER', 'noreply@yourdomain.com')
    
    # Session configuration
    PERMANENT_SESSION_LIFETIME = timedelta(days=90)  # For "remember me" functionality
    SESSION_COOKIE_SECURE = True  # Only send cookies over HTTPS
    SESSION_COOKIE_HTTPONLY = True  # Prevent JavaScript access to session cookie
    SESSION_COOKIE_SAMESITE = 'Lax'  # CSRF protection
    
    # Rate limiting
    RATELIMIT_STORAGE_URL = 'memory://'  # Use memory for development, redis for production
    RATELIMIT_DEFAULT = '100/hour'
    RATELIMIT_HEADERS_ENABLED = True

class DevelopmentConfig(Config):
    """Development config."""
    DEBUG = True
    SESSION_COOKIE_SECURE = False
   
    

class TestingConfig(Config):
    """Testing config."""
    TESTING = True
    DEBUG = True
    SESSION_COOKIE_SECURE = False

class ProductionConfig(Config):
    """Production config."""
    DEBUG = False
    SESSION_COOKIE_SECURE = True

# Configuration dictionary
config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
}

def get_config():
    """Get the correct configuration based on environment."""
    flask_env = os.environ.get('FLASK_ENV', 'development')
    return config.get(flask_env)() 