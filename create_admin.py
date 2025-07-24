#!/usr/bin/env python3
"""
Script to create an admin user for testing purposes.
Run this script to create an admin user in the database.
"""

from app import create_app
from app.database import db
from app.models import User

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
        
        # Create new admin user
        admin_user = User(
            email=admin_email,
            username="admin",
            is_admin=True
        )
        admin_user.set_password("admin123")
        
        db.session.add(admin_user)
        db.session.commit()
        
        print(f"Admin user created successfully!")
        print(f"Email: {admin_user.email}")
        print(f"Username: {admin_user.username}")
        print(f"Password: admin123")
        print(f"Admin status: {admin_user.is_admin}")

if __name__ == "__main__":
    create_admin_user() 