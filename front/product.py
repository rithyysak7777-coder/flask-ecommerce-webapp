from front import front_bp
from flask import render_template, request
from product import get_product_by_id, get_product_by_category, product as pr

@front_bp.get('/products')
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

@front_bp.get('/products/<int:product_id>')
@front_bp.get('/product/<int:product_id>')
def product_detail(product_id):
    product_item = get_product_by_id(product_id)
    if not product_item:
        return render_template('front/product_detail.html', product=None, similar_products=[])

    similar_products = [
        item for item in get_product_by_category(product_item['category'])
        if item['id'] != product_id
    ]
    return render_template(
        'front/product_detail.html',
        product=product_item,
        similar_products=similar_products
    )
