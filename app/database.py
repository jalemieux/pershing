from flask_sqlalchemy import SQLAlchemy
import os

# Initialize SQLAlchemy instance
db = SQLAlchemy()

def init_db(app):
    """Initialize the database with the app"""
    db.init_app(app)
    
    # Import models here to avoid circular imports
    from app.models import User, VerificationCode, UserSession
    
    #Create tables
    with app.app_context():
        # Only drop and recreate tables in development mode
        if app.config.get('DEBUG', False) or os.environ.get('FLASK_ENV') == 'development':
            db.drop_all()
            db.create_all()
            print("Development mode: Dropped and recreated all tables")
        else:
            # In production/testing, only create tables if they don't exist
            db.create_all()
            print("Production mode: Created tables (if they don't exist)") 