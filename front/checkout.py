import json
import requests
import datetime
from front import front_bp
from flask import render_template, request, make_response, redirect, url_for, session, flash
from product import get_product_by_id

@front_bp.get('/checkout')
def checkout():
    if not session.get('user'):
        flash('Please sign in to complete your checkout and purchase.', 'danger')
        return redirect(url_for('login'))

    cart_list = request.cookies.get('cart_list')
    cart_list = json.loads(cart_list) if cart_list else []

    # map product data to get price, title, etc.
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

    # total price
    total = 0
    for item in cart_list:
        total += float(item['qty']) * float(item['price'])
    return render_template('front/checkout.html', cart_list=cart_list, total=total)


@front_bp.post('/checkout')
def do_checkout():
    if not session.get('user'):
        flash('Please sign in to complete your checkout and purchase.', 'danger')
        return redirect(url_for('login'))

    # Read posted user info
    order_info = {
        'first_name': request.form.get('first_name', '').strip(),
        'last_name': request.form.get('last_name', '').strip(),
        'address': request.form.get('address', '').strip(),
        'phone': request.form.get('phone', '').strip(),
        'email': request.form.get('email', '').strip(),
        'payment': request.form.get('payment', '').strip(),
    }

    # Capture cart snapshot before clearing cookie
    cart_list = request.cookies.get('cart_list')
    cart_before = json.loads(cart_list) if cart_list else []

    for item in cart_before:
        product = get_product_by_id(item['id'])
        if product:
            item.update({
                'title': product['title'],
                'price': product['price'],
                'image': product['image'],
            })

    subtotal = sum(item['price'] * item['qty'] for item in cart_before)
    shipping = 0
    total = subtotal + shipping
    order_id = datetime.datetime.utcnow().strftime('%Y%m%d%H%M%S')

    message = (
        f"🛒 <b>NEW ORDER RECEIVED</b>\n"
        f"━━━━━━━━━━━━━━━\n"
        f"🆔 <b>Order ID:</b> #{order_id}\n"
        f"👤 <b>Customer:</b> {order_info['first_name']} {order_info['last_name']}\n"
        f"📞 <b>Phone:</b> {order_info['phone']}\n"
        f"📧 <b>Email:</b> {order_info['email']}\n"
        f"📍 <b>Address:</b> {order_info['address']}\n"
        f"💳 <b>Payment:</b> {order_info['payment']}\n"
        f"\n🛍 <b>ORDER ITEMS</b>\n"
        f"━━━━━━━━━━━━━━━\n"
    )

    for item in cart_before:
        title = item.get('title', 'Product')
        qty = item.get('qty', 1)
        price = item.get('price', 0)
        line_total = qty * price

        message += (
            f"▪️ <b>{title}</b>\n"
            f"   Qty: {qty}\n"
            f"   Price: ${price:.2f}\n"
            f"   Total: ${line_total:.2f}\n\n"
        )

    message += (
        f"━━━━━━━━━━━━━━━\n"
        f"💰 <b>Subtotal:</b> ${subtotal:.2f}\n"
        f"🚚 <b>Shipping:</b> Free\n"
        f"💵 <b>Grand Total:</b> ${total:.2f}\n"
        f"━━━━━━━━━━━━━━━\n"
    )

    # Send to Telegram
    bot_token = "8646767525:AAEVn34nmKkBGtek86sROl0wKhaJ4SgquOE"
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    payload = {
        'text': message,
        'parse_mode': 'HTML',
        'chat_id': '@RACTZ_STORE',
        'disable_web_page_preview': False,
        'disable_notification': False,
        'reply_to_message_id': None,
    }
    headers = {
        'accept': 'application/json',
        'User-Agent': 'Telegram Bot SDK - (https://github.com/irazasyed/telegram-bot-sdk)',
        'content-type': 'application/json',
    }
    try:
        response_tg = requests.post(url, json=payload, headers=headers, timeout=10)
        print(f"✅ Telegram sent: {response_tg.status_code}")
        print(f"Response: {response_tg.text}")
    except Exception as e:
        print(f"❌ Telegram error: {e}")
        print(f"URL: {url}")
        print(f"Payload: {payload}")

    # Store order info in session and redirect to payment
    session['order_info'] = order_info
    session['order_id'] = order_id
    session['cart_items'] = cart_before
    session['order_total'] = total

    response = make_response(redirect(url_for('payment')))
    # Clear the cart cookie
    response.delete_cookie('cart_list', path='/')
    return response
