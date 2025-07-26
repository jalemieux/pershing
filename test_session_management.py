#!/usr/bin/env python3
"""
Test script for session management functionality.
"""
import os
import sys
from datetime import datetime, timedelta

# Add the current directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from app.database import db
from app.models import User, UserSession
from app.session_manager import cleanup_expired_sessions, get_user_session_stats

def test_session_management():
    """Test session management functionality."""
    app = create_app()
    
    with app.app_context():
        print("Testing session management...")
        
        # Create a test user
        test_user = User.query.filter_by(email='test@example.com').first()
        if not test_user:
            test_user = User(email='test@example.com', username='testuser')
            db.session.add(test_user)
            db.session.commit()
            print(f"Created test user: {test_user.email}")
        
        # Create some test sessions
        print("\nCreating test sessions...")
        
        # Valid session (90 days)
        valid_session = UserSession(test_user.id, remember=True, device_info='Test Browser')
        db.session.add(valid_session)
        
        # Expired session (1 day ago)
        expired_session = UserSession(test_user.id, remember=False, device_info='Old Browser')
        expired_session.expires_at = datetime.utcnow() - timedelta(days=1)
        db.session.add(expired_session)
        
        # Another valid session (30 days)
        another_valid = UserSession(test_user.id, remember=False, device_info='Mobile Browser')
        db.session.add(another_valid)
        
        db.session.commit()
        print("Created test sessions")
        
        # Test session statistics
        print("\nTesting session statistics...")
        stats = get_user_session_stats(test_user.id)
        print(f"Total sessions: {stats['total_sessions']}")
        print(f"Active sessions: {stats['active_sessions']}")
        print(f"Recent sessions: {stats['recent_sessions']}")
        
        # Test user's active sessions
        print("\nTesting user's active sessions...")
        active_sessions = test_user.get_active_sessions()
        print(f"User has {len(active_sessions)} active sessions")
        
        for session in active_sessions:
            print(f"  - Session {session.id}: {session.device_info} (expires: {session.expires_at})")
        
        # Test session cleanup
        print("\nTesting session cleanup...")
        cleaned_count = cleanup_expired_sessions()
        print(f"Cleaned up {cleaned_count} expired sessions")
        
        # Check stats after cleanup
        stats_after = get_user_session_stats(test_user.id)
        print(f"Active sessions after cleanup: {stats_after['active_sessions']}")
        
        # Clean up test data
        print("\nCleaning up test data...")
        UserSession.query.filter_by(user_id=test_user.id).delete()
        db.session.delete(test_user)
        db.session.commit()
        print("Test completed successfully!")

if __name__ == '__main__':
    test_session_management() 