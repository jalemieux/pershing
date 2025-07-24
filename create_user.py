#!/usr/bin/env python3
"""
Script to create a regular user for testing purposes.
Run this script to create a regular user in the database.
"""

from app import create_app
from app.database import db
from app.models import User

def create_regular_user():
    app = create_app()
    
    with app.app_context():
        # Check if regular user already exists
        user_email = "user@example.com"
        existing_user = User.query.filter_by(email=user_email).first()
        
        if existing_user:
            print(f"Regular user already exists: {existing_user.email}")
            return
        
        # Create new regular user
        regular_user = User(
            email=user_email,
            username="user",
            is_admin=False
        )
        regular_user.set_password("user123")
        
        db.session.add(regular_user)
        db.session.commit()
        
        print(f"Regular user created successfully!")
        print(f"Email: {regular_user.email}")
        print(f"Username: {regular_user.username}")
        print(f"Password: user123")
        print(f"Admin status: {regular_user.is_admin}")

if __name__ == "__main__":
    create_regular_user() 