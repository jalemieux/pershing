from flask import jsonify, request, redirect, url_for, flash, render_template
from app import create_app
from app.database import db
from app.models import User, UserSession
from flask_login import login_user, logout_user, login_required, current_user
from datetime import datetime, timedelta
import json
from functools import wraps

app = create_app()

# Admin decorator
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            return redirect(url_for('login'))
        if not current_user.is_admin:
            flash('Access denied. Admin privileges required.', 'error')
            return redirect(url_for('home'))
        return f(*args, **kwargs)
    return decorated_function

# Custom Jinja filter for JSON parsing
@app.template_filter('from_json')
def from_json_filter(value):
    try:
        return json.loads(value)
    except (ValueError, TypeError):
        return {}

@app.route('/')
@login_required
def home():
    users = User.query.all()
    return render_template('home.html', users=users)

@app.route('/dashboard')
@login_required
@admin_required
def dashboard():
    # Get user's active sessions
    active_sessions = UserSession.query.filter_by(
        user_id=current_user.id
    ).filter(
        UserSession.expires_at > datetime.utcnow()
    ).order_by(UserSession.created_at.desc()).all()
    
    # Get user statistics
    total_sessions = UserSession.query.filter_by(user_id=current_user.id).count()
    recent_sessions = UserSession.query.filter_by(
        user_id=current_user.id
    ).filter(
        UserSession.created_at >= datetime.utcnow() - timedelta(days=7)
    ).count()
    
    # Get account age
    account_age = (datetime.utcnow() - current_user.created_at).days
    
    dashboard_data = {
        'user': current_user,
        'active_sessions': active_sessions,
        'total_sessions': total_sessions,
        'recent_sessions': recent_sessions,
        'account_age': account_age
    }
    
    return render_template('dashboard.html', **dashboard_data)

@app.route('/intent-collection')
@login_required
def intent_collection():
    return render_template('intent_collection.html', user=current_user)

@app.route('/intent-collection/analyze', methods=['POST'])
@login_required
def analyze_intent():
    """
    Process intent analysis form submission using the IntentAnalyzer.
    """
    try:
        # Get the form data
        data = request.get_json()
        if not data:
            # Fallback to form data if JSON is not available
            user_input = request.form.get('userInput', '')
        else:
            user_input = data.get('userInput', '')
        
        if not user_input:
            return jsonify({
                'success': False,
                'error': 'No user input provided'
            }), 400
        
        # Use the singleton intent analyzer from app context
        from app.intent_analyzer import get_intent_analyzer
        intent_analyzer = get_intent_analyzer()
        intent_result = intent_analyzer.analyze(user_input)
        
        # Log the analysis request
        app.logger.info(f"Intent analysis requested for user {current_user.id}: {user_input[:100]}...")
        
        return jsonify({
            'success': True,
            'intent': intent_result.to_dict(),
            'message': 'Intent analysis completed successfully'
        })
        
    except Exception as e:
        app.logger.error(f"Error processing intent analysis: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Internal server error during intent analysis'
        }), 500

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
        
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        remember = request.form.get('remember', False) == 'on'
        
        user = User.query.filter_by(username=username).first()
        
        if user is None or not user.check_password(password):
            flash('Invalid username or password')
            return redirect(url_for('login'))
        
        login_user(user, remember=remember)
        return redirect(url_for('home'))
    
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
        
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        
        if User.query.filter_by(username=username).first():
            flash('Username already exists')
            return redirect(url_for('register'))
            
        if User.query.filter_by(email=email).first():
            flash('Email already exists')
            return redirect(url_for('register'))
        
        user = User(username=username, email=email)
        user.set_password(password)
        
        db.session.add(user)
        db.session.commit()
        
        flash('Registration successful! Please login.')
        return redirect(url_for('login'))
    
    return render_template('register.html')

# Sample routes
@app.route('/users', methods=['GET'])
@login_required
def get_users():
    users = User.query.all()
    return jsonify([user.to_dict() for user in users])

@app.route('/users', methods=['POST'])
@login_required
def create_user():
    data = request.get_json()
    
    new_user = User(
        username=data['username'],
        email=data['email']
    )
    
    db.session.add(new_user)
    db.session.commit()
    
    return jsonify(new_user.to_dict()), 201

@app.route('/users/<int:user_id>', methods=['GET'])
@login_required
def get_user(user_id):
    user = User.query.get_or_404(user_id)
    return jsonify(user.to_dict())

if __name__ == '__main__':
    app.run(debug=True) 