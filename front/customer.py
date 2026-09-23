from datetime import datetime
from front import front_bp
from flask import render_template, request, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash, check_password_hash
from extensions import db
from models.user import User
from memory_store import load_users, save_users

@front_bp.get('/account')
def account():
    user = session.get('user')
    if not user:
        return redirect(url_for('login'))
    users = load_users()
    user_data = users.get(user['email'], {})
    if not user_data:
        # Fallback if session contains stale user
        session.pop('user', None)
        return redirect(url_for('login'))
    user_data['email'] = user['email']
    orders = user_data.get('orders', [])
    return render_template('front/account.html', user=user_data, orders=orders)

@front_bp.get('/reset-password')
def reset_password():
    return render_template('front/reset_password.html')

@front_bp.post('/handle-reset-password')
def handle_reset_password():
    email = request.form.get('email', '').strip()
    users = load_users()
    db_user = User.query.filter_by(email=email).first()
    if email in users or db_user:
        flash('Password reset link has been sent to your email.', 'success')
    else:
        flash('Email address not found.', 'danger')
    return redirect(url_for('reset_password'))

@front_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')

        # Check database User first
        db_user = User.query.filter_by(email=email).first()
        users = load_users()
        user_data = users.get(email)

        password_valid = False
        user_name = 'User'

        if db_user:
            user_name = db_user.username or 'User'
            try:
                if check_password_hash(db_user.password, password):
                    password_valid = True
            except Exception:
                pass
            if not password_valid and db_user.password == password:
                password_valid = True

        if not password_valid and user_data:
            user_name = user_data.get('name', 'User')
            stored_pwd = user_data.get('password', '')
            try:
                if check_password_hash(stored_pwd, password):
                    password_valid = True
            except Exception:
                pass
            if not password_valid and stored_pwd == password:
                password_valid = True

        if password_valid:
            session['user'] = {
                'email': email,
                'name': user_name
            }
            # Ensure users.json has this user for account order tracking
            if email not in users:
                users[email] = {'name': user_name, 'password': password, 'orders': []}
                save_users(users)

            flash('Logged in successfully.', 'success')
            return redirect(url_for('account'))
        else:
            flash('Invalid email address or password.', 'danger')
            return render_template('front/login.html')
    return render_template('front/login.html')

@front_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')

        if not name or not email or not password:
            flash('Please fill in all required fields.', 'danger')
            return render_template('front/register.html')

        users = load_users()
        existing_db_user = User.query.filter_by(email=email).first()

        if email in users or existing_db_user:
            flash('Email address is already registered.', 'danger')
            return render_template('front/register.html')

        # 1. Create User in SQLite Database so they show in Admin Dashboard & User Management
        hashed_password = generate_password_hash(password)
        joined_date = datetime.now().strftime('%b. %Y')
        new_user = User(
            username=name,
            email=email,
            password=hashed_password,
            role='User',
            status='Active',
            profile='default.png',
            joined_date=joined_date
        )
        try:
            db.session.add(new_user)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            print(f"Error saving user to database: {e}")

        # 2. Also keep data/users.json in sync for customer orders and account views
        users[email] = {
            'name': name,
            'password': password,
            'orders': []
        }
        save_users(users)

        session['user'] = {
            'email': email,
            'name': name
        }
        flash('Account created successfully.', 'success')
        return redirect(url_for('account'))
    return render_template('front/register.html')

@front_bp.get('/logout')
def logout():
    session.pop('user', None)
    flash('You have been logged out.', 'info')
    return redirect(url_for('home'))