"""
Session management utilities for the Flask application.
"""
from app.models import UserSession
from app.database import db
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

def cleanup_expired_sessions():
    """
    Clean up all expired sessions from the database.
    This should be called periodically (e.g., via a cron job).
    """
    try:
        count = UserSession.cleanup_all_expired()
        if count > 0:
            logger.info(f"Cleaned up {count} expired sessions")
        return count
    except Exception as e:
        logger.error(f"Error cleaning up expired sessions: {e}")
        return 0

def get_user_session_stats(user_id):
    """
    Get session statistics for a user.
    """
    try:
        total_sessions = UserSession.query.filter_by(user_id=user_id).count()
        active_sessions = UserSession.query.filter_by(
            user_id=user_id
        ).filter(
            UserSession.expires_at > datetime.utcnow()
        ).count()
        
        recent_sessions = UserSession.query.filter_by(
            user_id=user_id
        ).filter(
            UserSession.created_at >= datetime.utcnow() - timedelta(days=7)
        ).count()
        
        return {
            'total_sessions': total_sessions,
            'active_sessions': active_sessions,
            'recent_sessions': recent_sessions
        }
    except Exception as e:
        logger.error(f"Error getting session stats for user {user_id}: {e}")
        return {
            'total_sessions': 0,
            'active_sessions': 0,
            'recent_sessions': 0
        }

def validate_session_token(token):
    """
    Validate a session token and return the associated user if valid.
    """
    try:
        session = UserSession.query.filter_by(session_token=token).first()
        if session and session.is_valid():
            return session.user_id
        return None
    except Exception as e:
        logger.error(f"Error validating session token: {e}")
        return None 