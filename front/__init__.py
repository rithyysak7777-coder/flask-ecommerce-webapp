from flask import Blueprint

# Register blueprint
front_bp = Blueprint('simple_page', __name__, template_folder='templates')

# Register submodules
from . import home
from . import product
from . import cart
from . import customer
from . import checkout
from . import about
from . import contact
from . import sale
from . import payment