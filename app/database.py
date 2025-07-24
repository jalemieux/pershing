from flask_sqlalchemy import SQLAlchemy

# Initialize SQLAlchemy instance
db = SQLAlchemy()

def init_db(app):
    """Initialize the database with the app"""
    db.init_app(app)
    
    # Import models here to avoid circular imports
    from app.models import User
    
    # Create tables
    with app.app_context():
        db.drop_all()
        db.create_all() 