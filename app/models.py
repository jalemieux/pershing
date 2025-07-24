from flask_login import UserMixin
from app.database import db
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
import secrets

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)
    is_admin = db.Column(db.Boolean, default=False)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'created_at': self.created_at.isoformat(),
            'is_admin': self.is_admin
        }

class VerificationCode(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), nullable=False)
    code_hash = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    expires_at = db.Column(db.DateTime)
    attempts = db.Column(db.Integer, default=0)
    used = db.Column(db.Boolean, default=False)
    
    def __init__(self, email):
        self.email = email
        self.code = str(secrets.randbelow(1000000)).zfill(6)  # Generate 6-digit code
        self.code_hash = generate_password_hash(self.code)
        self.expires_at = datetime.utcnow() + timedelta(minutes=10)
    
    def verify_code(self, code):
        return check_password_hash(self.code_hash, code)
    
    def is_expired(self):
        return datetime.utcnow() > self.expires_at
    
    def increment_attempts(self):
        self.attempts += 1
        return self.attempts >= 3

class UserSession(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    session_token = db.Column(db.String(255), unique=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    expires_at = db.Column(db.DateTime)
    device_info = db.Column(db.Text)
    
    def __init__(self, user_id, remember=False, device_info=None):
        self.user_id = user_id
        self.session_token = secrets.token_urlsafe(32)
        self.device_info = device_info
        days = 90 if remember else 30
        self.expires_at = datetime.utcnow() + timedelta(days=days)
    
    def is_valid(self):
        return datetime.utcnow() <= self.expires_at 