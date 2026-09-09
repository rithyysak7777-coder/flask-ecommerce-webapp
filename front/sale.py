from front import front_bp
from flask import render_template, request
from product import product as pr

@front_bp.get('/sale')
def sale():
    categories = sorted({item['category'] for item in pr})
    return render_template('front/products.html', products=pr, categories=categories, active_category='all')

@front_bp.get('/search')
def search():
    query = request.args.get('q', '').strip()
    if query:
        query_lower = query.lower()
        filtered = [
            item for item in pr
            if query_lower in item.get('title', '').lower()
            or query_lower in item.get('category', '').lower()
            or query_lower in item.get('description', '').lower()
        ]
    else:
        filtered = pr

    return render_template('front/search.html', products=filtered, query=query)
