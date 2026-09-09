from front import front_bp
from flask import render_template
from product import product as pro

@front_bp.get('/')
def home():
    return render_template('front/home.html', products=pro)