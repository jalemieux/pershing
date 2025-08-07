#!/usr/bin/env python3
"""
Script to assign admin role to an existing user.
Usage: python assign_admin.py <user_email>
"""

import sys
from app import create_app
from app.database import db
from app.models import User

def assign_admin_role(user_email):
    """Assign admin role to an existing user by email."""
    app = create_app()
    
    with app.app_context():
        # Find the user by email
        user = User.query.filter_by(email=user_email).first()
        
        if not user:
            print(f"Error: User with email '{user_email}' not found.")
            print("Available users:")
            all_users = User.query.all()
            for u in all_users:
                print(f"  - {u.email} (admin: {u.is_admin})")
            return False
        
        if user.is_admin:
            print(f"User '{user_email}' is already an admin.")
            return True
        
        # Assign admin role
        user.is_admin = True
        db.session.commit()
        
        print(f"Successfully assigned admin role to user: {user.email}")
        print(f"Username: {user.username}")
        print(f"Admin status: {user.is_admin}")
        return True

def main():
    if len(sys.argv) != 2:
        print("Usage: python assign_admin.py <user_email>")
        print("Example: python assign_admin.py user@example.com")
        sys.exit(1)
    
    user_email = sys.argv[1]
    success = assign_admin_role(user_email)
    
    if not success:
        sys.exit(1)

if __name__ == "__main__":
    main() 