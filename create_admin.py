#!/usr/bin/env python3
"""
Script to create an admin user for testing purposes.
Run this script to create an admin user in the database.
"""

import secrets
import string
from app import create_app
from app.database import db
from app.models import User

def generate_secure_password(length=12):
    """Generate a secure random password with letters, digits, and symbols."""
    alphabet = string.ascii_letters + string.digits + "!@#$%^&*"
    return ''.join(secrets.choice(alphabet) for _ in range(length))

def create_admin_user():
    app = create_app()
    
    with app.app_context():
        # Check if admin user already exists
        admin_email = "admin@example.com"
        existing_admin = User.query.filter_by(email=admin_email).first()
        
        if existing_admin:
            print(f"Admin user already exists: {existing_admin.email}")
            if not existing_admin.is_admin:
                existing_admin.is_admin = True
                db.session.commit()
                print("Updated existing user to admin status")
            return
        
        # Generate a secure password
        password = generate_secure_password()
        
        # Create new admin user
        admin_user = User(
            email=admin_email,
            username="admin",
            is_admin=True
        )
        admin_user.set_password(password)
        
        db.session.add(admin_user)
        db.session.commit()
        
        print(f"Admin user created successfully!")
        print(f"Email: {admin_user.email}")
        print(f"Username: {admin_user.username}")
        print(f"Password: {password}")
        print(f"Admin status: {admin_user.is_admin}")
        print("\nIMPORTANT: Please save this password securely!")

if __name__ == "__main__":
    create_admin_user() 