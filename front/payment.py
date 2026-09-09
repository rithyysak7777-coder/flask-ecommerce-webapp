from front import front_bp
from flask import render_template, redirect, url_for, session

@front_bp.get('/payment')
def payment():
    order_info = session.get('order_info')
    order_id = session.get('order_id')
    cart_items = session.get('cart_items', [])
    order_total = session.get('order_total', 0)

    if not order_info:
        return redirect(url_for('checkout'))

    return render_template(
        'front/payment.html',
        order_info=order_info,
        order_id=order_id,
        cart_items=cart_items,
        order_total=order_total
    )

@front_bp.post('/complete-order')
def complete_order():
    return redirect(url_for('account'))
