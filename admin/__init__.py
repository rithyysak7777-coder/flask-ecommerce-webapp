from flask import Blueprint

# Register blueprint (admin)
admin_bp = Blueprint('admin_bp', __name__, template_folder='templates')

from . import auth
from . import dashboard
from . import user
