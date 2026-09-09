from admin import admin_bp
from flask import render_template, request, redirect, url_for, session, flash
from extensions import db
from werkzeug.security import check_password_hash
from sqlalchemy import text
from functools import wraps

def login_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if not session.get("is_login"):
            return redirect(url_for("admin_login", next=request.path))
        return view(*args, **kwargs)

    return wrapped

@admin_bp.get('/login')
def admin_login():
    if session.get('is_login'):
        return redirect(url_for('dashboard'))
    module = 'login'
    return render_template('admin/login.html', module=module)

@admin_bp.post('/login')
def do_admin_login():
    module = 'login'
    form = request.form
    username = (form.get('username') or '').strip()
    password = form.get('password') or ''

    sql = text("SELECT * FROM user WHERE username = :username")
    result = db.session.execute(sql, {"username": username}).fetchone()

    if result:
        user = dict(result._mapping)
        stored_password = user.get('password', '')

        # Check hashed password or plain-text password fallback
        password_valid = False
        try:
            if check_password_hash(stored_password, password):
                password_valid = True
        except Exception:
            pass

        if not password_valid and stored_password == password:
            password_valid = True

        if password_valid:
            session.clear()
            session.permanent = True  # Save session cookie for 1 day
            session['is_login'] = True
            session['user_id'] = user.get('id')
            session['profile'] = user.get('profile')
            session['username'] = user.get('username')
            session['email'] = user.get('email')
            session['role'] = user.get('role', 'Admin')
            session['joined_date'] = user.get('joined_date') or 'Nov. 2023'
            flash('Signed in successfully.', 'success')
            return redirect(url_for('dashboard'))

    flash('Invalid username or password.', 'danger')
    return render_template('admin/login.html', module=module)

@admin_bp.before_request
def ensure_admin_joined_date():
    if session.get('is_login') and session.get('user_id'):
        sql = text("SELECT joined_date FROM user WHERE id = :user_id")
        result = db.session.execute(sql, {"user_id": session.get('user_id')}).fetchone()
        if result and result[0]:
            session['joined_date'] = result[0]
        elif not session.get('joined_date'):
            session['joined_date'] = 'Aug. 2026'

