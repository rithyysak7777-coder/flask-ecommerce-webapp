from flask import Blueprint

# Register blueprint (api)
api_bp = Blueprint('api_bp', __name__)

from . import user
from . import product
