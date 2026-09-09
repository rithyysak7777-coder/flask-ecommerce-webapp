from flask import Flask, url_for
from config import Config
from extensions import db, migrate
import models
import helpers

from front import front_bp
from admin import admin_bp
from api import api_bp

# Flask application factory / configuration
app = Flask(__name__)
app.config.from_object(Config)

# Initialize database and migrations
db.init_app(app)
migrate.init_app(app, db)

# Fallback handler so templates calling url_for('user'), url_for('cart'), etc. resolve correctly across blueprints without recursion
def url_fallback(error, endpoint, values):
    if '.' in endpoint:
        raise error
    for bp_name in ['simple_page', 'admin_bp', 'api_bp']:
        full_endpoint = f"{bp_name}.{endpoint}"
        if full_endpoint in app.view_functions:
            return url_for(full_endpoint, **values)
    raise error

app.url_build_error_handlers.append(url_fallback)

# Register Blueprints
app.register_blueprint(front_bp, url_prefix='/')
app.register_blueprint(admin_bp, url_prefix='/admin')
app.register_blueprint(api_bp, url_prefix='/api')

if __name__ == '__main__':
    app.run(debug=True)
