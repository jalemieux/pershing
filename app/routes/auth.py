from flask import Blueprint, request, jsonify, render_template, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user
from app.models import User, VerificationCode, UserSession
from app.email_service import EmailService
from app.database import db
from datetime import datetime, timedelta
import json

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/auth/initiate', methods=['GET', 'POST'])
def initiate_auth():
    if request.method == 'GET':
        return render_template('auth/initiate.html')
    
    email = request.form.get('email')
    if not email:
        flash('Email is required')
        return redirect(url_for('auth.initiate_auth'))
    
    # Rate limiting check
    one_hour_ago = datetime.utcnow() - timedelta(hours=1)
    recent_codes = VerificationCode.query.filter(
        VerificationCode.email == email,
        VerificationCode.created_at >= one_hour_ago
    ).count()
    
    if recent_codes >= 5:
        flash('Too many code requests. Please try again later.')
        return redirect(url_for('auth.initiate_auth'))
    
    # Create or get user
    user = User.query.filter_by(email=email).first()
    if not user:
        user = User(email=email)
        db.session.add(user)
    
    # Generate and save verification code
    verification = VerificationCode(email)
    db.session.add(verification)
    db.session.commit()
    
    # Send verification code
    if EmailService.send_verification_code(email, verification.code):
        return redirect(url_for('auth.verify_code', email=email))
    else:
        flash('Error sending verification code. Please try again.')
        return redirect(url_for('auth.initiate_auth'))

@auth_bp.route('/auth/verify', methods=['GET', 'POST'])
def verify_code():
    email = request.args.get('email')
    if not email:
        return redirect(url_for('auth.initiate_auth'))
    
    if request.method == 'GET':
        return render_template('auth/verify.html', email=email)
    
    code = request.form.get('code')
    remember = request.form.get('remember', False) == 'on'
    
    if not code:
        flash('Verification code is required')
        return redirect(url_for('auth.verify_code', email=email))
    
    verification = VerificationCode.query.filter_by(
        email=email,
        used=False
    ).order_by(VerificationCode.created_at.desc()).first()
    
    if not verification:
        flash('No verification code found. Please request a new one.')
        return redirect(url_for('auth.initiate_auth'))
    
    if verification.is_expired():
        flash('Verification code has expired. Please request a new one.')
        return redirect(url_for('auth.initiate_auth'))
    
    if verification.increment_attempts():
        flash('Too many invalid attempts. Please request a new code.')
        return redirect(url_for('auth.initiate_auth'))
    
    if not verification.verify_code(code):
        db.session.commit()  # Save the attempt increment
        flash('Invalid verification code')
        return redirect(url_for('auth.verify_code', email=email))
    
    # Code is valid - mark as used
    verification.used = True
    
    # Get or create user
    user = User.query.filter_by(email=email).first()
    if not user:
        user = User(email=email)
        db.session.add(user)
    
    # Create session
    device_info = json.dumps({
        'user_agent': request.user_agent.string,
        'ip': request.remote_addr
    })
    session = UserSession(user.id, remember=remember, device_info=device_info)
    db.session.add(session)
    db.session.commit()
    
    # Log user in
    login_user(user, remember=remember)
    return redirect(url_for('home'))

@auth_bp.route('/auth/logout')
@login_required
def logout():
    # Invalidate current session
    if current_user.is_authenticated:
        UserSession.query.filter_by(
            user_id=current_user.id,
            session_token=request.cookies.get('session')
        ).delete()
        db.session.commit()
    
    logout_user()
    return redirect(url_for('auth.initiate_auth')) 