import stripe
from flask import Blueprint, flash, g, redirect, render_template, request, url_for, session, jsonify
from werkzeug.exceptions import abort
from collections import defaultdict
from application.auth import login_required
from application.db import get_db
import re
from collections import defaultdict
import os

from dotenv import load_dotenv
load_dotenv()

stripe_keys = {
    "secret_key": os.environ["STRIPE_SECRET_KEY"],
    "publishable_key": os.environ["STRIPE_PUBLISHABLE_KEY"],
    "endpoint_secret": os.environ["STRIPE_ENDPOINT_SECRET"]
}

bp = Blueprint("store", __name__)


@bp.route("/config")
def get_publishable_key():
    stripe_config = {"publicKey": stripe_keys["publishable_key"]}
    return jsonify(stripe_config)


@bp.route("/")
def index():
    db = get_db()
    products = db.execute("SELECT * FROM product").fetchall()
    return render_template("products/index.html", products=products)


def get_product_by_admin(id, check_admin=True):
    product = get_db().execute(
        "SELECT p.*"
        " FROM product p JOIN user u ON p.admin_id = u.id"
        " WHERE p.id = ?",
        (id,)
    ).fetchone()
    if not product:
        abort(404, f"Product id {id} doesn't exist.")
    if check_admin and product["admin_id"] != g.user["id"]:
        abort(403)
    return product


def get_product_by_id(id):
    product = get_db().execute(
        "SELECT p.*"
        " FROM product p JOIN user u ON p.admin_id = u.id"
        " WHERE p.id = ?",
        (id,)
    ).fetchone()
    if not product:
        abort(404, f"Product id {id} doesn't exist.")
    return product


def handle_cart():
    products = []
    grand_total = 0
    shipping_fee = 0
    index = 0
    total_charge = 0
    counts = defaultdict(int)
    for item in session.get('cart', []):
        counts[int(item['id'])] += item['quantity']

    for product_id, qty in counts.items():
        product = get_product_by_id(id=product_id)
        qty_total_price = qty * product['price']
        grand_total += qty_total_price
        products.append(
            {
                'id': product['id'],
                'name': product['name'],
                'price':  product['price'],
                'qty':  qty,
                'qty_total_price': qty_total_price,
                'image': product['image'],
                'index': index
            }
        )
        index += 1
    if grand_total < 99:
        shipping_fee = 15
    total_charge = grand_total + shipping_fee
    return products, grand_total, shipping_fee, total_charge


@bp.route("/add", methods=("GET", "POST"))
@login_required
def add_product():
    if request.method == "POST":
        name = request.form["name"]
        price = request.form["price"]
        stock = request.form["stock"]
        description = request.form["description"]
        image = request.form["image"]

        error = None

        if not name:
            error = 'Name is required.'
        elif not float(price) or float(price) < 0:
            error = 'Price must be a positive number.'
        elif not stock or int(stock) < 0:
            error = 'Stock must be a positive integer.'
        elif not image:
            error = 'Image is required.'
        elif not re.match(r'^https://', image):
            error = 'Image URL must start with "https://'

        if error is not None:
            flash(error)
        else:
            db = get_db()
            try:
                db.execute("INSERT INTO product (name, price, stock, description, image, admin_id) VALUES (?,?,?,?,?,?)",
                           (name, price, stock, description, image, g.user["id"]))
                db.commit()
            except Exception as e:
                flash(f'An error occurred: {e}')
                return redirect(url_for("store.index"))

            return redirect(url_for('store.index'))

    return render_template("products/create.html")


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
    product = get_product_by_admin(id, check_admin=True)

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
        elif not re.match(r'^https://.*\.(jpg|jpeg|png)$', image):
            error = 'Image URL must start with "https://" and end with ".jpg", ".jpeg", or ".png".'

        if error is not None:
            flash(error)
        else:
            db = get_db()
            try:
                db.execute('UPDATE product SET name = ?, price = ?, stock = ?, description = ?, image = ? WHERE id = ?',
                           (name, price, stock, description, image, id))
                db.commit()
            except Exception as e:
                flash(f'An error occurred: {e}')
                return redirect(url_for('store.index'))

            return redirect(url_for('store.index'))

    return render_template('products/update.html', product=product)


@bp.route("/<int:id>/delete", methods=("POST",))
@login_required
def delete(id):
    get_product_by_admin(id)
    db = get_db()
    db.execute("DELETE FROM product WHERE id = ?", (id,))
    db.commit()
    return redirect(url_for("store.index"))


@bp.route('/cart/add/<id>')
@login_required
def cart_add_item(id):
    id = int(id)
    if 'cart' in session:
        cart = session['cart']
        item_exists = False
        for item in cart:
            if item['id'] == id:
                item['quantity'] += 1
                item_exists = True
                break
        if not item_exists:
            cart.append({'id': id, 'quantity': 1})
        session['cart'] = cart
    else:
        session['cart'] = [{'id': id, 'quantity': 1}]
    session.modified = True
    print(session['cart'])
    return redirect(url_for('index'))


@bp.route('/cart/delete/<index>')
@login_required
def cart_remove_item(index):
    index = int(index)
    session['cart'] = [item for i, item in enumerate(
        session.get('cart', [])) if i != index]
    session.modified = True
    return redirect("/cart")


@bp.route("/cart")
@login_required
def cart():
    products, grand_total, shipping_fee, total_payment = handle_cart()
    return render_template('products/cart.html', products=products, grand_total=grand_total, shipping_fee=shipping_fee, total_payment=total_payment)


@bp.route('/checkout', methods=['GET', 'POST'])
@login_required
def checkout():
    products, grand_total, shipping_fee, total_payment = handle_cart()
    error = None
    stripe_public_key = os.environ.get('STRIPE_PUBLISHABLE_KEY')
    if request.method == 'POST':
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        email = request.form['email']
        delivery_house_nr = request.form['delivery_house_nr']
        delivery_street = request.form['delivery_street']
        delivery_additional = request.form['delivery_additional']
        delivery_state = request.form['delivery_state']
        delivery_postal = request.form['delivery_postal']
        delivery_country = request.form['delivery_country']
        instructions = request.form['instructions']
        delivery_status = 'CHECKOUT'
        stripe_payment_id = 'None'

        if error is None:
            db = get_db()
            db.execute(
                "INSERT INTO orders (buyer_id, shipping_fee, grand_total, first_name, last_name, email, delivery_house_nr, delivery_street, delivery_additional,delivery_state,delivery_postal,delivery_country,instructions, delivery_status, stripe_payment_id) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)", (
                    g.user["id"], shipping_fee, grand_total, first_name, last_name, email, delivery_house_nr, delivery_street, delivery_additional, delivery_state, delivery_postal, delivery_country, instructions, status, stripe_payment_id,),
            )
            db.commit()

            # If orders successfully saves, add cart session to order lines using the same Order ID
            order_id = db.lastrowid
            for item in session['cart']:
                db.execute(
                    "INSERT INTO orderlines (order_id, product_id, quantity) VALUES (?,?,?)", (
                        order_id, item['id'], item['quantity']),
                )
                db.commit()

        # Connect to Stripe api for payment
        return redirect(url_for("store.payment"))

    return render_template('products/checkout.html', products=products, grand_total=grand_total, shipping_fee=shipping_fee, total_payment=total_payment, stripe_public_key=stripe_public_key)


stripe.api_key = stripe_keys["secret_key"]

@bp.route("/create-checkout-session", methods=["GET", "POST"])
def create_checkout_session():
    domain_url = "https://127.0.0.1:8000/"
    stripe.api_key = stripe_keys["secret_key"]
    products, grand_total, shipping_fee, total_charge = handle_cart()

    line_items = []
    for product in products:
        line_items.append({
            "name": product['name'],
            "quantity": product['qty'],
            "currency": "eur",
            "amount": round(product['price'] * 100),
        })
    if shipping_fee > 0:
        line_items.append({
            "name": "Shipping Fee",
            "quantity": 1,
            "currency": "eur",
            "amount": round(shipping_fee * 100),
        })

    try:
        checkout_session = stripe.checkout.Session.create(
            success_url=domain_url + "success?session_id={CHECKOUT_SESSION_ID}",
            cancel_url=domain_url + f"checkout?session_id={{CHECKOUT_SESSION_ID}}",
            payment_method_types=["card"],
            mode="payment",
            line_items=line_items
        )
        return jsonify({"sessionId": checkout_session["id"]})
    except Exception as e:
        return jsonify(error=str(e)), 403


@bp.route("/webhook", methods=['POST'])
def stripe_webhook():
    payload = request.get_data(as_text=True)
    sig_header = request.headers.get('Stripe-Signature')

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, stripe_keys["endpoint_secret"]
        )

    except ValueError as e:
        # Invalid payload
        return 'Invalid payload', 400
    except stripe.error.SignatureVerificationError as e:
        # Invalid signature
        return 'Invalid signature', 400

    # Handle the checkout.session.completed event
    if event['type'] == 'checkout.session.completed':
        session = event['data']['object']

        # Fulfill the purchase...
        handle_checkout_session(session)

    return 'Success', 200


def handle_checkout_session(session):
    print("Payment was successful.")
    # TODO: run some custom code here


@bp.route("/success")
def success():
    return render_template("products/payments.html")
