"""
Example configuration for OpenAI LLM Provider integration.

This file shows how to configure the OpenAI provider in your Flask application.
Copy the relevant parts to your actual config.py file.
"""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Config:
    """Base configuration class."""
    
    # OpenAI Configuration
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
    OPENAI_MODEL = os.getenv('OPENAI_MODEL', 'gpt-4')
    
    # Intent Analyzer Configuration
    INTENT_ANALYZER_PROVIDER = os.getenv('INTENT_ANALYZER_PROVIDER', 'openai')
    INTENT_ANALYZER_CONFIG = {
        'openai': {
            'api_key': OPENAI_API_KEY,
            'model': OPENAI_MODEL,
        },
        'mock': {
            # Mock provider doesn't need additional config
        }
    }

class DevelopmentConfig(Config):
    """Development configuration."""
    DEBUG = True
    INTENT_ANALYZER_PROVIDER = 'openai'  # Use OpenAI in development

class ProductionConfig(Config):
    """Production configuration."""
    DEBUG = False
    INTENT_ANALYZER_PROVIDER = 'openai'  # Use OpenAI in production

class TestingConfig(Config):
    """Testing configuration."""
    TESTING = True
    INTENT_ANALYZER_PROVIDER = 'mock'  # Use mock provider for testing

# Configuration mapping
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}

def get_config():
    """Get the appropriate configuration based on environment."""
    config_name = os.getenv('FLASK_ENV', 'development')
    return config.get(config_name, config['default']) 