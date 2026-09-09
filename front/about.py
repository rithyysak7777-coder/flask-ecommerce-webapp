from front import front_bp
from flask import render_template

@front_bp.get('/about')
def about():
    return render_template('front/about.html')