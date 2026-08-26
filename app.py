from flask import Flask, render_template, request, make_response, redirect, url_for, jsonify, session, flash, request , session
from product import get_product_by_id, get_product_by_category ,product as pr
from memory_store import load_users, save_users
import json
import datetime
import requests
from werkzeug.security import check_password_hash, generate_password_hash
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from sqlalchemy import text
from werkzeug.utils import secure_filename
import os
from datetime import timedelta
from functools import wraps

# confix to connect with database
app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///mydb.sqlite3"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

app.config["SECRET_KEY"] = "change-this"
app.config["PERMANENT_SESSION_LIFETIME"] = timedelta(minutes=1440)  # session TTL

# for profile upload
UPLOAD_DIR = os.path.join("static", "images")
os.makedirs(UPLOAD_DIR, exist_ok=True)

ALLOWED_EXT = {"png", "jpg", "jpeg", "gif"}
# function to check
def allowed(name):
    return "." in name and name.rsplit(".", 1)[-1].lower() in ALLOWED_EXT

# generate custom image filename: createddate_module_action_username.ext
def generate_image_filename(original_filename, module, action, username):
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    clean_username = secure_filename(username or 'user').replace(' ', '_') or 'user'
    ext = original_filename.rsplit('.', 1)[-1].lower() if '.' in original_filename else 'png'
    return f"{timestamp}_{module}_{action}_{clean_username}.{ext}"

# Create for instance , db and migrate
db = SQLAlchemy(app)
migrate = Migrate(app, db)
# Create Model ( Table )
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    profile = db.Column(db.String(255), nullable=False, default='/static/images/default.png')
    username = db.Column(db.String(80), nullable=False)
    password = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(120), nullable=False, unique=True)
    role = db.Column(db.String(80), nullable=False)
    status = db.Column(db.String(80), nullable=False, default='Active')



def login_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if not session.get("is_login"):
            return redirect(url_for("admin_login", next=request.path))
        return view(*args, **kwargs)

    return wrapped

app.secret_key = 'ractz-demo-secret-key'
@app.route('/')
@app.get('/home')
def home():
    return render_template('front/home.html', products= pr )

@app.get('/products')
def products():
    active_category = request.args.get('category', 'all')
    categories = sorted({item['category'] for item in pr})

    if active_category != 'all':
        filtered_products = get_product_by_category(active_category)
    else:
        filtered_products = pr

    return render_template(
        'front/products.html',
        products=filtered_products,
        categories=categories,
        active_category=active_category
    )

@app.get('/products/<int:product_id>')
@app.get('/product/<int:product_id>')
def product_detail(product_id):
    product = get_product_by_id(product_id)
    if not product:
        return render_template('front/product_detail.html', product=None, similar_products=[])

    similar_products = [
        item for item in get_product_by_category(product['category'])
        if item['id'] != product_id
    ]
    return render_template(
        'front/product_detail.html',
        product=product,
        similar_products=similar_products
    )

@app.get('/cart')
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
            
    # assert False , cart_list
 ## make response
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
        response = make_response(redirect(url_for('cart'))) # for response
    else:
        response = make_response(render_template('front/cart.html',cart_list=cart_list)) # for response
#   set cookie
#   return response
    cookie_cart_list = [{'id': item['id'], 'qty': item['qty']} for item in cart_list]
    if cookie_cart_list:
        response.set_cookie(
            'cart_list',
            json.dumps(cookie_cart_list),
            max_age=60 * 60 * 24 * 7,
            path='/',
            samesite='Lax'
        ) # for set
    else:
        response.delete_cookie('cart_list', path='/')
    return response



@app.get('/about')
def about():
    
    return render_template('front/about.html')


@app.get('/contact')
def contact():
    return render_template('front/contact.html')


@app.get('/sale')
def sale():
    return render_template('front/products.html',)

@app.get('/search')
def search():
    return render_template('front/search.html', products=pr)

@app.get('/checkout')
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
@app.post('/checkout')
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



@app.get('/payment')
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

@app.post('/complete-order')
def complete_order():
    # Order completed, clear session data
    # session.pop('order_info', None)
    # session.pop('order_id', None)
    # session.pop('cart_items', None)
    # session.pop('order_total', None)
    
    return redirect(url_for('account'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')
        users = load_users()
        user_data = users.get(email)
        if user_data and user_data.get('password') == password:
            session['user'] = {
                'email': email,
                'name': user_data.get('name', 'User')
            }
            flash('Logged in successfully.', 'success')
            return redirect(url_for('account'))
        else:
            flash('Invalid email address or password.', 'danger')
            return render_template('front/login.html')
    return render_template('front/login.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')
        users = load_users()
        if email in users:
            flash('Email address is already registered.', 'danger')
            return render_template('front/register.html')
        users[email] = {
            'name': name,
            'password': password,
            'orders': []
        }
        save_users(users)
        session['user'] = {
            'email': email,
            'name': name
        }
        flash('Account created successfully.', 'success')
        return redirect(url_for('account'))
    return render_template('front/register.html')


@app.get('/logout')
def logout():
    session.pop('user', None)
    flash('You have been logged out.', 'info')
    return redirect(url_for('home'))


@app.get('/account')
def account():
    user = session.get('user')
    if not user:
        return redirect(url_for('login'))
    users = load_users()
    user_data = users.get(user['email'], {})
    if not user_data:
        # Fallback if session contains stale user
        session.pop('user', None)
        return redirect(url_for('login'))
    user_data['email'] = user['email']
    orders = user_data.get('orders', [])
    return render_template('front/account.html', user=user_data, orders=orders)


@app.get('/reset-password')
def reset_password():
    return render_template('front/reset_password.html')

@app.post('/handle-reset-password')
def handle_reset_password():
    email = request.form.get('email', '').strip()
    users = load_users()
    if email in users:
        flash('Password reset link has been sent to your email.', 'success')
    else:
        flash('Email address not found.', 'danger')
    return redirect(url_for('reset_password'))



@app.get('/admin/dashboard')
@login_required
def dashboard():
    module = 'dashboard'
    # if not session.get('is_login'):  # if admin not have session should go to login
    #     return redirect(url_for('admin_login'))
    return render_template('admin/dashboard/dashboard.html',module=module)

@app.get('/admin/user')
@login_required
def user():
    # Get Data this path
    module = 'user'
    sql = text("SELECT * FROM user")
    result = db.session.execute(sql)
    rows = [dict(row._mapping) for row in result]

    return render_template('admin/user/user.html', module=module, users=rows)

@app.get('/admin/user/add')
@login_required
def add_user():
    module = 'user'
    return render_template('admin/user/add.html', module=module)

@app.post('/admin/user/add')
@login_required
def do_add_user():
    module = 'user'
    form = request.form
    name = form.get('name') or form.get('username')
    email = form.get('email')

    filename = None
    file = request.files.get("image")
    if file and file.filename and allowed(file.filename):
        filename = generate_image_filename(file.filename, module, 'add', name)
        file.save(os.path.join(UPLOAD_DIR, filename))

    password = generate_password_hash(form.get('password'))
    role = form.get('role', 'User')

    # new object
    u = User(
        username=name,
        email=email,
        password=password,
        role=role,
        profile=filename,
        status='Active'
    )
    db.session.add(u)
    db.session.commit()
    return redirect(url_for('user'))

@app.get('/admin/user/confirm-delete/<int:user_id>')
@login_required
def conform_delete(user_id):
    module = 'user'
    sql = text("SELECT * FROM user WHERE id = :user_id")
    result = db.session.execute(sql, {"user_id": user_id}).fetchone()
    user = None
    if result:
        user = dict(result._mapping)
    else:
        return redirect(url_for('user'))
    return render_template('admin/user/comfirm_delete.html', module=module, user=user)



@app.post('/admin/user/delete')
@login_required # protect this function
def delete_user():
    module = 'user'
    form = request.form
    user_id = form.get('user_id')
    user = User.query.get(user_id)
    if not user:
        return redirect(url_for('user'))

    db.session.delete(user)
    db.session.commit()
    return redirect(url_for('user'))

@app.get('/admin/user/edit/<int:user_id>')
@login_required
def edit_user(user_id):
    module = 'user'
    sql = text("SELECT * FROM user WHERE id = :user_id")
    result = db.session.execute(sql, {"user_id": user_id}).fetchone()
    user = None
    if result:
        user = dict(result._mapping)
    else:
        return redirect(url_for('user'))
    return render_template(
        'admin/user/edit.html',module=module,user=user
    )


@app.post('/admin/user/edit')
@login_required
def do_edit_user():
    module = 'user'
    form = request.form
    user_id = form.get('id') or form.get('user_id')
    user = User.query.get(user_id) if user_id else None
    if not user:
        return redirect(url_for('user'))

    user.username = form.get('name') or form.get('username')
    user.email = form.get('email')
    user.role = form.get('role')

    file = request.files.get("image")
    if file and file.filename and allowed(file.filename):
        filename = generate_image_filename(file.filename, module, 'edit', user.username)
        file.save(os.path.join(UPLOAD_DIR, filename))
        user.profile = filename

    if form.get('password') is not None and form.get('password').strip() != '':
        user.password = generate_password_hash(form.get('password'))

    db.session.commit()
    return redirect(url_for('user'))



@app.get('/admin/user/profile/<int:user_id>')
@login_required
def user_profile(user_id):
    module = 'user'
    sql = text("SELECT * FROM user WHERE id = :user_id")
    result = db.session.execute(sql, {"user_id": user_id}).fetchone()
    user = None
    if result:
        user = dict(result._mapping)  # convert to single dictionary
    else:
        return redirect(url_for('user'))
    return render_template('admin/user/profile.html', module=module, user=user)



@app.get('/admin/login')
def admin_login():
    if session.get('is_login'):
        return redirect(url_for('dashboard'))
    module = 'login'
    return render_template('admin/login.html', module=module)

@app.post('/admin/login')
def do_admin_login():
    module = 'login'
    form = request.form
    username = (form.get('username') or '').strip()
    password = form.get('password') or ''

    sql = text("SELECT * FROM user WHERE username = :username")
    result = db.session.execute(sql, {"username": username}).fetchone()

    if result:
        user = dict(result._mapping)
        stored_password = user.get('password', '')

        # Check hashed password or plain-text password fallback
        password_valid = False
        try:
            if check_password_hash(stored_password, password):
                password_valid = True
        except Exception:
            pass

        if not password_valid and stored_password == password:
            password_valid = True

        if password_valid:
            session.clear()
            session.permanent = True  # Save session cookie for 1 day
            session['is_login'] = True
            session['user_id'] = user.get('id')
            session['profile'] = user.get('profile')
            session['username'] = user.get('username')
            session['email'] = user.get('email')
            flash('Signed in successfully.', 'success')
            return redirect(url_for('dashboard'))

    flash('Invalid username or password.', 'danger')
    return render_template('admin/login.html', module=module)

@app.get('/admin/logout')
def admin_logout():
    session.clear()
    flash('Logged out successfully.', 'info')
    return redirect(url_for('admin_login'))

@app.get('/admin/order')
@login_required
def order():
    module = 'order'
    return render_template('admin/user/user.html', module=module)

@app.get('/admin/product')
@login_required
def product():
    module = 'product'
    return render_template('admin/user/user.html', module=module)



# @app.before_request
# def before_request():
#     # print("Before request")
#     # print("Method:", request.method)
#     # print("Path:", request.path)
#     path = request.path
#     if 'admin' in path:
#         if session.get('is_login'):
#             return redirect(url_for('dashboard'))
#         # assert False, True
#         else:
#             return redirect(url_for('admin_login'))
#
#     return None

if __name__ == '__main__':
    app.run(debug=True)
