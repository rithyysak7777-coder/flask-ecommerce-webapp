from admin import admin_bp
from flask import render_template
from .auth import login_required
from models.user import User

@admin_bp.get('/dashboard')
@login_required
def dashboard():
    module = 'dashboard'
    customer_count = User.query.filter(User.role != 'Admin').count()
    total_users = User.query.count()
    return render_template(
        'admin/dashboard/dashboard.html',
        module=module,
        customer_count=customer_count,
        total_users=total_users
    )

