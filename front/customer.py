from front import front_bp
from flask import render_template, request, redirect, url_for, session, flash
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
    if email in users:
        flash('Password reset link has been sent to your email.', 'success')
    else:
        flash('Email address not found.', 'danger')
    return redirect(url_for('reset_password'))

@front_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')
        users = load_users()
        user_data = users.get(email)
        if user_data and user_data.get('password') == password:
            session['user'] = {
                'email': email,
                'name': user_data.get('name', 'User')
            }
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
        users = load_users()
        if email in users:
            flash('Email address is already registered.', 'danger')
            return render_template('front/register.html')
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