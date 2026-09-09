from front import front_bp
from flask import render_template

@front_bp.get('/contact')
def contact():
    return render_template('front/contact.html')