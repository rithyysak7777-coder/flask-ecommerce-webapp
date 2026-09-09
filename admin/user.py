import os
from datetime import datetime
from admin import admin_bp
from flask import render_template, request, redirect, url_for, flash, send_from_directory, session
from .auth import login_required
from extensions import db
from sqlalchemy import text
from sqlalchemy.exc import IntegrityError
from werkzeug.security import generate_password_hash
from werkzeug.utils import secure_filename
from models import User
from helpers import allowed, process_user_profile_image, delete_user_photos, UPLOAD_DIR

@admin_bp.get('/user')
@login_required
def user():
    # Get Data this path
    module = 'user'
    sql = text("SELECT * FROM user")
    result = db.session.execute(sql)
    rows = [dict(row._mapping) for row in result]

    return render_template('admin/user/user.html', module=module, users=rows)

@admin_bp.get('/user/add')
@login_required
def add_user():
    module = 'user'
    return render_template('admin/user/add.html', module=module)

@admin_bp.post('/user/add')
@login_required
def do_add_user():
    module = 'user'
    form = request.form
    name = (form.get('name') or form.get('username') or '').strip()
    email = (form.get('email') or '').strip()
    password_raw = form.get('password') or ''
    confirm_password = form.get('confirm_password') or ''
    role = form.get('role', 'User')

    # Validation: Check required fields
    if not name or not email or not password_raw:
        flash('Please fill in all required fields.', 'danger')
        return render_template('admin/user/add.html', module=module)

    # Validation: Check password confirmation
    if confirm_password and password_raw != confirm_password:
        flash('Passwords do not match.', 'danger')
        return render_template('admin/user/add.html', module=module)

    # Validation: Check if email already exists
    existing_user = User.query.filter_by(email=email).first()
    if existing_user:
        flash('Email address is already registered. Please choose a different email.', 'danger')
        return render_template('admin/user/add.html', module=module)

    password = generate_password_hash(password_raw)
    joined_date = datetime.now().strftime('%b. %Y')
    u = User(
        username=name,
        email=email,
        password=password,
        role=role,
        profile='default.png',
        status='Active',
        joined_date=joined_date
    )

    try:
        db.session.add(u)
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        flash('Email address is already registered. Please choose a different email.', 'danger')
        return render_template('admin/user/add.html', module=module)
    except Exception as e:
        db.session.rollback()
        flash(f'Error creating user: {e}', 'danger')
        return render_template('admin/user/add.html', module=module)

    # Process image upload if provided
    file = request.files.get("image")
    if file and file.filename and allowed(file.filename):
        filename, err = process_user_profile_image(file, u.id, name)
        if err:
            flash(err, 'danger')
        elif filename:
            u.profile = filename
            try:
                db.session.commit()
            except Exception:
                db.session.rollback()

    flash('User created successfully.', 'success')
    return redirect(url_for('admin_bp.user'))

@admin_bp.get('/user/confirm-delete/<int:user_id>')
@login_required
def conform_delete(user_id):
    module = 'user'
    sql = text("SELECT * FROM user WHERE id = :user_id")
    result = db.session.execute(sql, {"user_id": user_id}).fetchone()
    user_data = None
    if result:
        user_data = dict(result._mapping)
    else:
        return redirect(url_for('admin_bp.user'))
    return render_template('admin/user/comfirm_delete.html', module=module, user=user_data)

@admin_bp.post('/user/delete')
@login_required # protect this function
def delete_user():
    form = request.form
    user_id = form.get('user_id') or form.get('id')
    user_obj = User.query.get(user_id)
    if not user_obj:
        return redirect(url_for('admin_bp.user'))

    delete_user_photos(user_obj)
    try:
        db.session.delete(user_obj)
        db.session.commit()
        flash('User and associated photo(s) deleted successfully.', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error deleting user: {e}', 'danger')

    return redirect(url_for('admin_bp.user'))

@admin_bp.get('/user/edit/<int:user_id>')
@login_required
def edit_user(user_id):
    module = 'user'
    sql = text("SELECT * FROM user WHERE id = :user_id")
    result = db.session.execute(sql, {"user_id": user_id}).fetchone()
    user_data = None
    if result:
        user_data = dict(result._mapping)
    else:
        return redirect(url_for('admin_bp.user'))
    return render_template('admin/user/edit.html', module=module, user=user_data)

@admin_bp.post('/user/edit')
@login_required
def do_edit_user():
    module = 'user'
    form = request.form
    user_id = form.get('id') or form.get('user_id')
    user_obj = User.query.get(user_id) if user_id else None
    if not user_obj:
        flash('User not found.', 'danger')
        return redirect(url_for('admin_bp.user'))

    name = (form.get('name') or form.get('username') or '').strip()
    email = (form.get('email') or '').strip()
    role = form.get('role', user_obj.role)

    if not name or not email:
        flash('Name and email cannot be empty.', 'danger')
        return render_template('admin/user/edit.html', module=module, user=user_obj)

    # Validation: Check if email is already taken by another user
    existing_user = User.query.filter(User.email == email, User.id != user_obj.id).first()
    if existing_user:
        flash('Email address is already taken by another user. Please choose a different email.', 'danger')
        return render_template('admin/user/edit.html', module=module, user=user_obj)

    user_obj.username = name
    user_obj.email = email
    user_obj.role = role

    file = request.files.get("image")
    if file and file.filename and allowed(file.filename):
        delete_user_photos(user_obj)
        filename, err = process_user_profile_image(file, user_obj.id, user_obj.username)
        if err:
            flash(err, 'danger')
        elif filename:
            user_obj.profile = filename

    if form.get('password') is not None and form.get('password').strip() != '':
        user_obj.password = generate_password_hash(form.get('password'))

    try:
        db.session.commit()
        if session.get('user_id') == user_obj.id:
            session['username'] = user_obj.username
            session['email'] = user_obj.email
            session['role'] = user_obj.role
            session['profile'] = user_obj.profile
        flash('User updated successfully.', 'success')
    except IntegrityError:
        db.session.rollback()
        flash('Email address is already taken by another user. Please choose a different email.', 'danger')
        return render_template('admin/user/edit.html', module=module, user=user_obj)
    except Exception as e:
        db.session.rollback()
        flash(f'Error updating user: {e}', 'danger')
        return render_template('admin/user/edit.html', module=module, user=user_obj)

    return redirect(url_for('admin_bp.user'))

@admin_bp.get('/profile')
@login_required
def admin_profile():
    user_id = session.get('user_id')
    if not user_id:
        return redirect(url_for('admin_bp.admin_login'))
    return redirect(url_for('admin_bp.user_profile', user_id=user_id))

@admin_bp.get('/user/profile/<int:user_id>')
@login_required
def user_profile(user_id):
    module = 'user'
    sql = text("SELECT * FROM user WHERE id = :user_id")
    result = db.session.execute(sql, {"user_id": user_id}).fetchone()
    user_data = None
    if result:
        user_data = dict(result._mapping)  # convert to single dictionary
    else:
        return redirect(url_for('admin_bp.user'))
    return render_template('admin/user/profile.html', module=module, user=user_data)

@admin_bp.get('/user/photo/<int:user_id>/<string:photo_type>')
def user_photo(user_id, photo_type):
    user_obj = User.query.get(user_id)
    default_filename = 'default.png'

    if not user_obj or not user_obj.profile or user_obj.profile == 'default.png':
        return send_from_directory(UPLOAD_DIR, default_filename)

    clean_username = secure_filename(user_obj.username or 'user').replace(' ', '_') or 'user'

    if photo_type == 'thum':
        thum_filename = f"{user_obj.id}_thum_{clean_username}.jpg"
        if os.path.exists(os.path.join(UPLOAD_DIR, thum_filename)):
            return send_from_directory(UPLOAD_DIR, thum_filename)
        if os.path.exists(os.path.join(UPLOAD_DIR, user_obj.profile)):
            return send_from_directory(UPLOAD_DIR, user_obj.profile)
    else:
        # photo_type == 'org'
        if os.path.exists(os.path.join(UPLOAD_DIR, user_obj.profile)):
            return send_from_directory(UPLOAD_DIR, user_obj.profile)
        org_prefix = f"{user_obj.id}_org_"
        if os.path.exists(UPLOAD_DIR):
            for f in os.listdir(UPLOAD_DIR):
                if f.startswith(org_prefix):
                    return send_from_directory(UPLOAD_DIR, f)

    return send_from_directory(UPLOAD_DIR, default_filename)

@admin_bp.get('/logout')
def admin_logout():
    session.clear()
    flash('Logged out successfully.', 'info')
    return redirect(url_for('admin_bp.admin_login'))

@admin_bp.get('/order')
@login_required
def order():
    module = 'order'
    return render_template('admin/user/user.html', module=module)

@admin_bp.get('/product')
@login_required
def product():
    module = 'product'
    return render_template('admin/user/user.html', module=module)