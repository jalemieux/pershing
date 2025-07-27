from flask import Blueprint, request, jsonify, render_template, redirect, url_for, flash, current_app
from flask_login import login_user, logout_user, login_required, current_user
from app.models import User, VerificationCode, UserSession
from app.email_service import EmailService
from app.database import db
from datetime import datetime, timedelta

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/auth/initiate', methods=['GET', 'POST'])
def initiate_auth():
    # If user is already authenticated, redirect to home

    if current_user.is_authenticated:
        current_app.logger.info(f"Authenticated user {current_user.id} attempted to access initiate_auth, redirecting to home")
        return redirect(url_for('home'))
        
    if request.method == 'GET':
        current_app.logger.debug("GET request to initiate_auth page")
        return render_template('auth/initiate.html')
    
    email = request.form.get('email')
    if not email:
        current_app.logger.warning("Initiate auth attempted without email")
        flash('Email is required')
        return redirect(url_for('auth.initiate_auth'))
    
    current_app.logger.info(f"Auth initiation requested for email: {email}")
    
    # Rate limiting check
    one_hour_ago = datetime.utcnow() - timedelta(hours=1)
    recent_codes = VerificationCode.query.filter(
        VerificationCode.email == email,
        VerificationCode.created_at >= one_hour_ago
    ).count()
    
    if recent_codes >= 5:
        current_app.logger.warning(f"Rate limit exceeded for email: {email} (attempts: {recent_codes})")
        flash('Too many code requests. Please try again later.')
        return redirect(url_for('auth.initiate_auth'))
    
    # Create or get user
    user = User.query.filter_by(email=email).first()
    if not user:
        current_app.logger.info(f"Creating new user for email: {email}")
        user = User(email=email)
        db.session.add(user)
    else:
        current_app.logger.info(f"Existing user found for email: {email} (user_id: {user.id})")
    
    # Generate and save verification code
    verification = VerificationCode(email)
    db.session.add(verification)
    db.session.commit()
    
    current_app.logger.info(f"Verification code generated for email: {email} (code_id: {verification.id})")
    
    # Send verification code
    if EmailService.send_verification_code(email, verification.code):
        current_app.logger.info(f"Verification code sent successfully to: {email}")
        return redirect(url_for('auth.verify_code', email=email))
    else:
        current_app.logger.error(f"Failed to send verification code to: {email}")
        flash('Error sending verification code. Please try again.')
        return redirect(url_for('auth.initiate_auth'))

@auth_bp.route('/auth/verify', methods=['GET', 'POST'])
def verify_code():
    # # If user is already authenticated, redirect to home
    if current_user.is_authenticated:
        current_app.logger.info(f"Authenticated user {current_user.id} attempted to access verify_code, redirecting to home")
        return redirect(url_for('home'))
        
    email = request.args.get('email')
    if not email:
        current_app.logger.warning("Verify code accessed without email parameter")
        return redirect(url_for('auth.initiate_auth'))
    
    if request.method == 'GET':
        current_app.logger.debug(f"GET request to verify_code page for email: {email}")
        return render_template('auth/verify.html', email=email)
    
    code = request.form.get('code')
    
    if not code:
        current_app.logger.warning(f"Verification attempted without code for email: {email}")
        flash('Verification code is required')
        return redirect(url_for('auth.verify_code', email=email))
    
    current_app.logger.info(f"Verification attempt for email: {email}")
    
    verification = VerificationCode.query.filter_by(
        email=email,
        used=False
    ).order_by(VerificationCode.created_at.desc()).first()
    
    if not verification:
        current_app.logger.warning(f"No verification code found for email: {email}")
        flash('No verification code found. Please request a new one.')
        return redirect(url_for('auth.initiate_auth'))
    
    if verification.is_expired():
        current_app.logger.warning(f"Expired verification code used for email: {email} (code_id: {verification.id})")
        flash('Verification code has expired. Please request a new one.')
        return redirect(url_for('auth.initiate_auth'))
    
    if verification.increment_attempts():
        current_app.logger.warning(f"Too many attempts for verification code (code_id: {verification.id}, email: {email})")
        flash('Too many invalid attempts. Please request a new code.')
        return redirect(url_for('auth.initiate_auth'))
    
    if not verification.verify_code(code):
        db.session.commit()  # Save the attempt increment
        current_app.logger.warning(f"Invalid verification code provided for email: {email} (code_id: {verification.id})")
        flash('Invalid verification code')
        return redirect(url_for('auth.verify_code', email=email))
    
    # Code is valid - mark as used
    verification.used = True
    current_app.logger.info(f"Verification code validated successfully for email: {email} (code_id: {verification.id})")
    
    # Get or create user
    user = User.query.filter_by(email=email).first()
    if not user:
        current_app.logger.info(f"Creating new user during verification for email: {email}")
        user = User(email=email)
        db.session.add(user)
    current_app.logger.info(f"User created: {user.email}")

    # Create a UserSession for tracking (always persistent)
    # device_info = request.headers.get('User-Agent', 'Unknown')
    # user_session = UserSession(user.id, remember=True, device_info=device_info)
    # db.session.add(user_session)
    
    # Log user in with persistent session (always remember=True)
    login_user(user, remember=True, duration=timedelta(days=90), force=True, fresh=False)
    
    db.session.commit()
    
    current_app.logger.info(f"User successfully authenticated: {email} (user_id: {user.id})")
    
    return redirect(url_for('home'))

@auth_bp.route('/auth/logout')
@login_required
def logout():
    user_id = current_user.id
    user_email = current_user.email
    
    current_app.logger.info(f"User logout initiated: {user_email} (user_id: {user_id})")
    
    # Clean up any active sessions for this user (optional)
    # You could add session cleanup logic here if needed
    logout_user()
    
    current_app.logger.info(f"User successfully logged out: {user_email} (user_id: {user_id})")
    return redirect(url_for('auth.initiate_auth')) 