import os, stripe
from flask import Blueprint, flash, redirect, render_template, request, url_for, session
from application import db
from application.extensions.limiter import limiter
from application.extensions.cache import cache
from application.models import Product, Prices
from flask_login import login_required, current_user
from .forms import ProductForm

bp = Blueprint("products", __name__, url_prefix="/products")

@bp.route("/")
def index():
    products = Product.query.all()
    return render_template("products/index.html", products=products)

def create_stripe_product(new_product):
    stripe.api_key = os.environ.get('STRIPE_SECRET_KEY_DEV')
    stripe_product = stripe.Product.create(name=new_product.name, description=new_product.description)
    stripe_product_id = stripe_product.id
    return stripe_product_id

def create_stripe_price(stripe_product_id, new_price):
    stripe.api_key = os.environ.get('STRIPE_SECRET_KEY_DEV')
    stripe_price = stripe.Price.create(
            unit_amount=int(new_price.price) * 100,
            currency="eur",
            product=stripe_product_id,
        )
    return stripe_price.id

@bp.route("/add", methods=("GET", "POST"))
@limiter.limit("1 per minute")
@cache.cached(timeout=60, key_prefix='add_product')
@login_required
def create_product():
    form = ProductForm()
    if current_user.is_admin == False:
        flash("You are not authorized to add products.")
        return redirect(url_for('products.index'))

    if form.validate_on_submit():
        new_product = Product(
            name=form.name.data,
            price=form.price.data,
            stock=form.stock.data,
            image=form.image.data,
            description=form.description.data,
            admin_id=current_user.id
        )

        db.session.add(new_product)
        db.session.commit()

        new_price = Prices(
            product_id=new_product.id,
            price=form.price.data
        )

        db.session.add(new_price)
        db.session.commit()

        new_product.price_id = new_price.id
        db.session.commit()

        stripe_product_id = create_stripe_product(new_product)
        stripe_price_id = create_stripe_price(stripe_product_id, new_price)

        new_product.stripe_product_ref = stripe_product_id
        new_price.stripe_price_id = stripe_price_id
        db.session.commit()

        flash('Product added successfully.')
        return redirect(url_for('products.index'))
    else:
        return render_template('products/form.html', title="Add Product", form=form)

@bp.route('/<int:id>/', methods=('GET', 'POST'))
@cache.cached(timeout=60, key_prefix='read_product')
@login_required
def read_product(id):
    product = Product.query.filter_by(id=id).first_or_404()
    recommendations = Product.query.filter(Product.id != id).limit(3).all()
    quantity = 0

    if request.method == 'POST':
        quantity = int(request.form['quantity'])
        if 'cart' in session:
            cart = session['cart']
            item_exists = False
            for item in cart:
                if item['id'] == id:
                    item['quantity'] += quantity
                    item_exists = True
                    break
            if not item_exists:
                cart.append({'id': id, 'quantity': quantity})
            session['cart'] = cart
        else:
            session['cart'] = [{'id': id, 'quantity': quantity}]
        session.modified = True
    return render_template('products/detail.html', product=product, recommendations=recommendations)

@bp.route('/<int:id>/update', methods=['GET', 'POST'])
@limiter.limit("1 per minute")
@cache.cached(timeout=60, key_prefix='update_product')
@login_required
def update_product(id):
    product = Product.query.filter_by(id=id).first_or_404()

    if not current_user.is_admin or current_user.id != product.admin_id:
        flash("You are not authorized to update products.")
        return redirect(url_for('products.index'))

    form = ProductForm(product=product)

    if form.validate_on_submit():
        product.name = form.name.data
        product.price = form.price.data
        product.stock = form.stock.data
        product.image = form.image.data
        product.description = form.description.data

        db.session.commit()

        flash('Product updated successfully.')
        return redirect(url_for('products.index', id=product.id))

    form.name.data = product.name
    form.price.data = product.price
    form.stock.data = product.stock
    form.image.data = product.image
    form.description.data = product.description

    return render_template('products/form.html', title='Update Product', form=form, product=product)

@bp.route('/delete', methods=['POST'])
@limiter.limit("1 per minute")
@cache.cached(timeout=60, key_prefix='delete_product')
@login_required
def delete_product():

    product_id = request.form.get('product_id')

    product = Product.query.filter_by(id=product_id).first_or_404()
    if not current_user.is_admin or current_user.id != product.admin_id:
        flash("You are not authorized to delete products.")
        return redirect(url_for('products.index'))

    if not product:
        flash('Product not found')
        return redirect(url_for('products.index'))

    try:
        db.session.delete(product)
        db.session.commit()
        flash('Product deleted successfully')

    except Exception as e:
        db.session.rollback()
        flash(f'An error occurred while deleting the product: {e}')

    return redirect(url_for('products.index'))