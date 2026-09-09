from extensions import db
from datetime import datetime

# Create Model ( Table )
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    profile = db.Column(db.String(255), nullable=False, default='/static/images/default.png')
    username = db.Column(db.String(80), nullable=False)
    password = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(120), nullable=False, unique=True)
    role = db.Column(db.String(80), nullable=False)
    status = db.Column(db.String(80), nullable=False, default='Active')
    joined_date = db.Column(db.String(80), nullable=True, default=lambda: datetime.now().strftime('%b. %Y'))