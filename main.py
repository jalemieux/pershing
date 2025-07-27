from flask import jsonify, request, redirect, url_for, flash, render_template
from app import create_app
from app.database import db
from app.models import User, UserSession
from flask_login import login_user, logout_user, login_required, current_user
from datetime import datetime, timedelta
import json
from functools import wraps
from app.models import SavedPrompt

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
    active_sessions = current_user.get_active_sessions()
    
    # Get user statistics using the session manager
    from app.session_manager import get_user_session_stats
    session_stats = get_user_session_stats(current_user.id)
    
    # Get account age
    account_age = (datetime.utcnow() - current_user.created_at).days
    
    dashboard_data = {
        'user': current_user,
        'active_sessions': active_sessions,
        'total_sessions': session_stats['total_sessions'],
        'recent_sessions': session_stats['recent_sessions'],
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

@app.route('/prompt-crafting')
@login_required
def prompt_crafting():
    return render_template('prompt_crafting.html', user=current_user)

@app.route('/prompt-crafting/generate', methods=['POST'])
@login_required
def generate_prompts():
    """
    Generate prompts based on user input using multiple LLM providers.
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
        
        # Generate prompts using the multi-provider prompt crafter
        from app.prompt_crafter import get_multi_provider_prompt_crafter
        prompts_crafter = get_multi_provider_prompt_crafter()
        prompt_result = prompts_crafter.craft_prompts_multi_provider(user_input)
        
        # Log the prompt generation request
        app.logger.info(f"Multi-provider prompt generation requested for user {current_user.id}: {user_input[:100]}...")
        
        return jsonify({
            'success': True,
            'prompt_result': prompt_result.to_dict(),
            'message': 'Prompts generated successfully from multiple providers'
        })
        
    except Exception as e:
        app.logger.error(f"Error generating prompts: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Internal server error during prompt generation'
        }), 500

@app.route('/prompt-crafting/save', methods=['POST'])
@login_required
def save_prompt():
    """
    Save a generated prompt to the database.
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({
                'success': False,
                'error': 'No data provided'
            }), 400
        
        # Extract data from the request
        original_message = data.get('original_message', '')
        prompt_content = data.get('prompt_content', '')
        prompt_name = data.get('prompt_name', 'Generated Prompt')  # Get prompt name
        model = data.get('model', 'Unknown')
        prompt_type = data.get('prompt_type', '')
        provider = data.get('provider', '')
        prompt_metadata = data.get('metadata', '')
        
        if not original_message or not prompt_content:
            return jsonify({
                'success': False,
                'error': 'Original message and prompt content are required'
            }), 400
        
        # Generate a name based on the prompt name and model, or use the provided name
        name = prompt_name if prompt_name and prompt_name != 'Generated Prompt' else f"{original_message[:50]}{'...' if len(original_message) > 50 else ''} - {model}"
        
        # Create the saved prompt
        saved_prompt = SavedPrompt(
            user_id=current_user.id,
            name=name,
            original_message=original_message,
            model=model,
            prompt_content=prompt_content,
            prompt_type=prompt_type,
            provider=provider,
            prompt_metadata=prompt_metadata
        )
        
        db.session.add(saved_prompt)
        db.session.commit()
        
        app.logger.info(f"Prompt saved for user {current_user.id}: {name}")
        
        return jsonify({
            'success': True,
            'message': 'Prompt saved successfully',
            'saved_prompt': saved_prompt.to_dict()
        })
        
    except Exception as e:
        app.logger.error(f"Error saving prompt: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Internal server error while saving prompt'
        }), 500

@app.route('/prompt-crafting/saved', methods=['GET'])
@login_required
def get_saved_prompts():
    """
    Get all saved prompts for the current user.
    """
    try:
        saved_prompts = SavedPrompt.query.filter_by(user_id=current_user.id).order_by(SavedPrompt.created_at.desc()).all()
        
        return jsonify({
            'success': True,
            'saved_prompts': [prompt.to_dict() for prompt in saved_prompts]
        })
        
    except Exception as e:
        app.logger.error(f"Error retrieving saved prompts: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Internal server error while retrieving saved prompts'
        }), 500

@app.route('/prompt-crafting/saved/<int:prompt_id>', methods=['GET'])
@login_required
def get_saved_prompt(prompt_id):
    """
    Get a specific saved prompt by ID.
    """
    try:
        saved_prompt = SavedPrompt.query.filter_by(id=prompt_id, user_id=current_user.id).first()
        
        if not saved_prompt:
            return jsonify({
                'success': False,
                'error': 'Prompt not found'
            }), 404
        
        return jsonify({
            'success': True,
            'saved_prompt': saved_prompt.to_dict()
        })
        
    except Exception as e:
        app.logger.error(f"Error retrieving saved prompt: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Internal server error while retrieving saved prompt'
        }), 500

@app.route('/prompt-crafting/saved/<int:prompt_id>/view')
@login_required
def view_saved_prompt(prompt_id):
    """
    View a specific saved prompt in a dedicated page.
    """
    try:
        saved_prompt = SavedPrompt.query.filter_by(id=prompt_id, user_id=current_user.id).first()
        
        if not saved_prompt:
            flash('Prompt not found', 'error')
            return redirect(url_for('prompt_crafting'))
        
        return render_template('saved_prompt_view.html', user=current_user, saved_prompt=saved_prompt)
        
    except Exception as e:
        app.logger.error(f"Error viewing saved prompt: {str(e)}")
        flash('Error loading prompt', 'error')
        return redirect(url_for('prompt_crafting'))

@app.route('/chat')
@login_required
def chat():
    """Chat interface page."""
    return render_template('chat.html', user=current_user)

@app.route('/prompt-crafting/saved/<int:prompt_id>', methods=['DELETE'])
@login_required
def delete_saved_prompt(prompt_id):
    """
    Delete a saved prompt by ID.
    """
    try:
        saved_prompt = SavedPrompt.query.filter_by(id=prompt_id, user_id=current_user.id).first()
        
        if not saved_prompt:
            return jsonify({
                'success': False,
                'error': 'Prompt not found'
            }), 404
        
        db.session.delete(saved_prompt)
        db.session.commit()
        
        app.logger.info(f"Prompt deleted for user {current_user.id}: {saved_prompt.name}")
        
        return jsonify({
            'success': True,
            'message': 'Prompt deleted successfully'
        })
        
    except Exception as e:
        app.logger.error(f"Error deleting saved prompt: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Internal server error while deleting saved prompt'
        }), 500

# @app.route('/login', methods=['GET', 'POST'])
# def login():
#     if current_user.is_authenticated:
#         return redirect(url_for('home'))
        
#     if request.method == 'POST':
#         username = request.form.get('username')
#         password = request.form.get('password')
        
#         user = User.query.filter_by(username=username).first()
        
#         if user is None or not user.check_password(password):
#             flash('Invalid username or password')
#             return redirect(url_for('login'))
        
#         # Create a UserSession for tracking (always persistent)
#         device_info = request.headers.get('User-Agent', 'Unknown')
#         user_session = UserSession(user.id, remember=True, device_info=device_info)
#         db.session.add(user_session)
        
#         # Always use persistent sessions
#         login_user(user, remember=True)
#         db.session.commit()
        
#         return redirect(url_for('home'))
    
#     return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    # Clean up any active sessions for this user (optional)
    # You could add session cleanup logic here if needed
    logout_user()
    return redirect(url_for('auth.initiate_auth'))

# @app.route('/register', methods=['GET', 'POST'])
# def register():
#     if current_user.is_authenticated:
#         return redirect(url_for('home'))
        
#     if request.method == 'POST':
#         username = request.form.get('username')
#         email = request.form.get('email')
#         password = request.form.get('password')
        
#         if User.query.filter_by(username=username).first():
#             flash('Username already exists')
#             return redirect(url_for('register'))
            
#         if User.query.filter_by(email=email).first():
#             flash('Email already exists')
#             return redirect(url_for('register'))
        
#         user = User(username=username, email=email)
#         user.set_password(password)
        
#         db.session.add(user)
#         db.session.commit()
        
#         flash('Registration successful! Please login.')
#         return redirect(url_for('login'))
    
#     return render_template('register.html')

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