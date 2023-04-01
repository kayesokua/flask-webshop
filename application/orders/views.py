import stripe
from flask import Blueprint, flash, g, redirect, render_template, request, url_for, session, jsonify
from application.extensions.db import db
from collections import defaultdict
from flask_login import login_required, current_user
from collections import defaultdict
import os
from application.models import Product, Orders, OrderLine
from application.orders.forms import OrderStatusForm, CheckoutForm
from application.models.accounts import DeliveryAddress

bp = Blueprint("orders", __name__)

from dotenv import load_dotenv
load_dotenv()

stripe_keys = {
    "secret_key": os.environ["STRIPE_SECRET_KEY"],
    "publishable_key": os.environ["STRIPE_PUBLISHABLE_KEY"],
    "endpoint_secret": os.environ["STRIPE_ENDPOINT_SECRET"]
}

@bp.route("/config")
def get_publishable_key():
    stripe_config = {"publicKey": stripe_keys["publishable_key"]}
    return jsonify(stripe_config)

def handle_cart():
    products = []
    grand_total = 0
    shipping_fee = 0
    index = 0
    total_charge = 0

    for item in session['cart']:
        product = Product.query.filter_by(id=item['id']).first()
        if product is not None:
            qty_total_price = item['quantity'] * product.price
            products.append(
                {
                    'index': index,
                    'id': product.id,
                    'name': product.name,
                    'price':  product.price,
                    'stock': product.stock,
                    'qty':  item['quantity'],
                    'qty_total_price': qty_total_price,
                    'image': product.image,

                }
            )
            index += 1
            grand_total += qty_total_price

    if 50 > grand_total:
        shipping_fee = 5.99

    total_charge = grand_total + shipping_fee
    return products, grand_total, shipping_fee, total_charge

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
    return redirect(url_for('products.index'))

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
    return render_template('orders/cart.html', products=products, grand_total=grand_total, shipping_fee=shipping_fee, total_payment=total_payment)


@bp.route('/cart/checkout', methods=['GET', 'POST'])
@login_required
def checkout():
    form = CheckoutForm()
    products, grand_total, shipping_fee, total_payment = handle_cart()

    if form.validate_on_submit():
        selected_address_id = int(form.selected_address.data)
        new_order = Orders(
            address_id=selected_address_id,
            buyer_id=current_user.id,
            shipping_fee=shipping_fee,
            grand_total=total_payment)

        db.session.add(new_order)
        db.session.commit()

        for product in products:
            print(product)
            order_line = OrderLine(order_id=new_order.id, product_id=product['id'], quantity=product['qty'], total_price=product['qty_total_price'])
            db.session.add(order_line)
            db.session.commit()

        product_update_stock = Product.query.filter_by(id=product['id']).first()
        product_update_stock.stock =  product_update_stock.stock - product['qty']
        db.session.commit()

        session['cart'].pop()

        flash('Your order has been created successfully.')
        return redirect(url_for('accounts.settings'))

    return render_template('orders/checkout.html', products=products, grand_total=grand_total, shipping_fee=shipping_fee, total_payment=total_payment, form=form)

stripe.api_key = stripe_keys["secret_key"]

@bp.route("/cart/create-checkout-session", methods=["GET", "POST"])
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
        return 'Invalid payload', 400
    except stripe.error.SignatureVerificationError as e:
        return 'Invalid signature', 400

    if event['type'] == 'checkout.session.completed':
        session = event['data']['object']
        handle_checkout_session(session)

    return 'Success', 200

def handle_checkout_session(session):
    print("Payment was successful.")

@bp.route("/success")
def success():
    return render_template("products/payments.html")