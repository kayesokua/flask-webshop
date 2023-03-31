import stripe
from flask import Blueprint, flash, g, redirect, render_template, request, url_for, session, jsonify
from werkzeug.exceptions import abort
from application import db
from collections import defaultdict
from application.accounts.views import login_required
import re
from collections import defaultdict
import os
from application.models import User, Product, Orders, OrderLine

from dotenv import load_dotenv
load_dotenv()

bp = Blueprint("products", __name__)

stripe_keys = {
    "secret_key": os.environ["STRIPE_SECRET_KEY"],
    "publishable_key": os.environ["STRIPE_PUBLISHABLE_KEY"],
    "endpoint_secret": os.environ["STRIPE_ENDPOINT_SECRET"]
}

@bp.route("/")
def index():
    products = Product.query.all()
    return render_template("products/index.html", products=products)

def get_product_by_admin(id, check_admin=True):
    product = Product.query.filter_by(id=id).join(User).filter_by(id=User.id).first()
    if not product:
        abort(404, f"Product id {id} doesn't exist.")
    if check_admin and product.admin_id != g.user.id:
        abort(403)
    return product

def get_product_by_id(id):
    product = Product.query.filter_by(id=id).first()
    if not product:
        abort(404, f"Product id {id} doesn't exist.")
    return product


@bp.route('/product/<int:id>/', methods=('GET', 'POST'))
@login_required
def read(id):
    product = get_product_by_id(id)
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

    return render_template('products/detail.html', product=product)


@bp.route('/<int:id>/update', methods=['GET', 'POST'])
@login_required
def update(id):
    product = Product.query.filter_by(id=id).first_or_404()
    if product.admin_id != g.user.id:
        abort(403)

    if request.method == 'POST':
        name = request.form['name']
        price = float(request.form['price'])
        stock = int(request.form['stock'])
        description = request.form['description']
        image = request.form['image']
        error = None


        if not name:
            error = 'Name is required.'
        elif not price or price < 0:
            error = 'Price must be a positive number.'
        elif not stock or stock < 0:
            error = 'Stock must be a positive integer.'
        elif not image:
            error = 'Image is required.'
        elif not re.match(r'^https://', image):
            error = 'Image URL must start with "https://"'

        print("error: ", error)
        if error is not None:
            flash(error)
        else:
            try:
                product.name = name
                product.price = price
                product.stock = stock
                product.description = description
                product.image = image
                db.session.commit()
                print("product updated")
                print(db.session.commit())
            except Exception as e:
                flash(f'An error occurred: {e}')
                return redirect(url_for('store.index'))

            flash('Product updated successfully.')
            return redirect(url_for('store.index', id=product.id))

    return render_template('products/update.html', product=product)

@bp.route('/<int:id>/delete', methods=['POST'])
@login_required
def delete(id):
    product = get_product_by_admin(id)
    if not product:
        flash('Product not found')
        return redirect(url_for('store.index'))

    try:
        db.session.delete(product)
        db.session.commit()
        flash('Product deleted successfully')
    except Exception as e:
        db.session.rollback()
        flash(f'An error occurred while deleting the product: {e}')

    return redirect(url_for('store.index'))
