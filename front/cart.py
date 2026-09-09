import json
from front import front_bp
from flask import render_template, request, make_response, redirect, url_for, jsonify, session, flash
from product import get_product_by_id

@front_bp.get('/cart')
def cart():
    if not session.get('user'):
        flash('Please sign in to add products to your cart and complete your purchase.', 'danger')
        return redirect(url_for('login'))

    product_id = request.args.get('product_id')
    action = request.args.get('action', 'add')
    cart_list = request.cookies.get('cart_list')
    try:
        cart_list = json.loads(cart_list) if cart_list else []
    except json.JSONDecodeError:
        cart_list = []

    # clean old cookie data and merge same product into one row
    clean_cart = []
    for item in cart_list:
        item_id = str(item.get('id'))
        item_qty = max(int(item.get('qty', item.get('quantity', 1))), 1)

        duplicate_item = next((cart_item for cart_item in clean_cart if cart_item['id'] == item_id), None)
        if duplicate_item:
            duplicate_item['qty'] += item_qty
        else:
            clean_cart.append({'id': item_id, 'qty': item_qty})

    cart_list = clean_cart

    if product_id:
        product_id = str(product_id)
        if action == 'remove':
            cart_list = [item for item in cart_list if item['id'] != product_id]
        else:
            duplicate_product_ids = [item['id'] for item in cart_list]
            if product_id in duplicate_product_ids:
                for item in cart_list:
                    if item['id'] == product_id and action == 'minus':
                        item['qty'] = max(item['qty'] - 1, 1)
                    elif item['id'] == product_id:
                        item['qty'] += 1
            elif action != 'minus':
                cart_list.append({"id": product_id, "qty": 1})

    # map product data every time, after add or refresh
    mapped_cart_list = []
    for item in cart_list:
        product = get_product_by_id(item['id'])
        if product:
            item['image'] = product['image']
            item['title'] = product['title']
            item['price'] = product['price']
            item['category'] = product['category']
            item['description'] = product['description']
            mapped_cart_list.append(item)

    cart_list = mapped_cart_list

    # calculate totals
    subtotal = sum(item['price'] * item['qty'] for item in cart_list)
    discount = subtotal * 0.10
    shipping = 0 if subtotal >= 150 or subtotal == 0 else 12
    estimated_tax = (subtotal - discount) * 0.07
    total = subtotal - discount + shipping + estimated_tax
    item_count = sum(item['qty'] for item in cart_list)

    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        response = make_response(jsonify({
            'cart_empty': len(cart_list) == 0,
            'item_count': item_count,
            'subtotal': subtotal,
            'discount': discount,
            'shipping': shipping,
            'estimated_tax': estimated_tax,
            'total': total,
            'items': [
                {
                    'id': item['id'],
                    'qty': item['qty'],
                    'price': item['price'],
                    'line_total': item['price'] * item['qty']
                }
                for item in cart_list
            ]
        }))
    elif product_id:
        response = make_response(redirect(url_for('cart')))
    else:
        response = make_response(render_template('front/cart.html', cart_list=cart_list))

    cookie_cart_list = [{'id': item['id'], 'qty': item['qty']} for item in cart_list]
    if cookie_cart_list:
        response.set_cookie(
            'cart_list',
            json.dumps(cookie_cart_list),
            max_age=60 * 60 * 24 * 7,
            path='/',
            samesite='Lax'
        )
    else:
        response.delete_cookie('cart_list', path='/')
    return response
