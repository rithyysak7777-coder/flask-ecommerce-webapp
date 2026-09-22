from flask import Flask
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

# Register Blueprints
app.register_blueprint(front_bp, url_prefix='/')
app.register_blueprint(admin_bp, url_prefix='/admin')
app.register_blueprint(api_bp, url_prefix='/api')

# Shorthand url_for fallback
helpers.register_url_fallbacks(app)

if __name__ == '__main__':
    app.run(debug=True)
