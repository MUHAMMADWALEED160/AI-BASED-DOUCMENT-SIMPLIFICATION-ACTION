import uuid
from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from werkzeug.security import generate_password_hash, check_password_hash
from models import db, User

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/signup', methods=['GET', 'POST'])
def signup():
    if 'user_id' in session:
        return redirect(url_for('routes.dashboard'))
        
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        password = request.form.get('password')
        
        user = User.query.filter_by(email=email).first()
        if user:
            flash('Email address already exists', 'error')
            return redirect(url_for('auth.signup'))
            
        new_user = User(
            name=name,
            email=email,
            password_hash=generate_password_hash(password, method='pbkdf2:sha256')
        )
        
        db.session.add(new_user)
        db.session.commit()
        
        flash('Account created successfully! Please log in.', 'success')
        return redirect(url_for('auth.login'))
        
    return render_template('signup.html')

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if 'user_id' in session:
        return redirect(url_for('routes.dashboard'))
        
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        remember = True if request.form.get('remember') else False
        
        user = User.query.filter_by(email=email).first()
        
        if not user or not check_password_hash(user.password_hash, password):
            flash('Please check your login details and try again.', 'error')
            return redirect(url_for('auth.login'))
            
        session.permanent = remember
        session['user_id'] = user.id
        session['user_name'] = user.name
        
        return redirect(url_for('routes.dashboard'))
        
    return render_template('login.html')

@auth_bp.route('/logout')
def logout():
    session.pop('user_id', None)
    session.pop('user_name', None)
    flash('You have been logged out.', 'info')
    return redirect(url_for('routes.index'))

@auth_bp.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        email = request.form.get('email')
        user = User.query.filter_by(email=email).first()
        
        if user:
            reset_token = str(uuid.uuid4())
            reset_url = request.host_url.rstrip('/') + f"/reset-password/{reset_token}"
            print("\n" + "="*50)
            print("🔐 PASSWORD RESET REQUESTED 🔐")
            print(f"User: {user.email}")
            print(f"Reset Link: {reset_url}")
            print("="*50 + "\n")
            
        flash('If an account matches that email, a password reset link has been generated.', 'info')
        return redirect(url_for('auth.login'))
        
    return render_template('forgot_password.html')