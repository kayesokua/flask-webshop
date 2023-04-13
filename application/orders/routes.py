import os
from sqlalchemy import and_

from flask import Blueprint, flash, g, redirect, render_template, request, url_for, session, jsonify
from flask_login import login_required, current_user

from application.extensions.db import db
from application.models import Product, Orders, OrderLine, Prices
from application.models.accounts import DeliveryAddress
from application.orders.forms import OrderStatusForm, CheckoutForm

from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

import stripe

bp = Blueprint("orders", __name__)
limiter = Limiter(key_func=get_remote_address)

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
    if 'cart' not in session:
        session['cart'] = []
    products, grand_total, shipping_fee, total_payment = handle_cart()
    return render_template('orders/cart.html', products=products, grand_total=grand_total, shipping_fee=shipping_fee, total_payment=total_payment)

@bp.route('/cart/checkout', methods=['GET', 'POST'])
@limiter.limit("1 per minute", key_func=get_remote_address)
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
        session.modified = True

        order_id = new_order.id

        stripe.api_key = os.environ.get('STRIPE_SECRET_KEY_DEV')
        domain_url = os.environ.get('DOMAIN_URL_DEV')

        line_items = (
        db.session.query(
            Prices.stripe_price_id,
            OrderLine.quantity
        )
        .join(
            Product,
            Prices.product_id == Product.id
        )
        .join(
            OrderLine,
            and_(
                OrderLine.product_id == Product.id,
                OrderLine.order_id == order_id
            )
        )
        .all())

        line_items = [{"price": price, "quantity": quantity} for price, quantity in line_items]

        stripe_session = stripe.checkout.Session.create(
            shipping_options=[
                {
                "shipping_rate_data": {
                    "type": "fixed_amount",
                    "fixed_amount": {"amount": 590, "currency": "eur"},
                    "display_name": "Standard Shipping",
                    "delivery_estimate": {
                    "minimum": {"unit": "business_day", "value": 5},
                    "maximum": {"unit": "business_day", "value": 7},
                    },
                },
                },
                {
                "shipping_rate_data": {
                    "type": "fixed_amount",
                    "fixed_amount": {"amount": 990, "currency": "eur"},
                    "display_name": "Next day air",
                    "delivery_estimate": {
                    "minimum": {"unit": "business_day", "value": 1},
                    "maximum": {"unit": "business_day", "value": 1},
                    },
                },
                },],
            mode="payment",
            line_items=line_items,
            success_url=f"{domain_url}/orders/success",
            cancel_url=f"{domain_url}/orders/cancel",
        )

        # Save the session id to the order object
        order = Orders.query.filter_by(id=order_id).first()
        order.stripe_payment_id = stripe_session.id
        db.session.commit()

        stripe_session_id_url = stripe_session.url
        db.session.commit()

        return redirect(stripe_session_id_url, code=303)
    return render_template('orders/checkout.html', form=form, products=products, grand_total=grand_total, shipping_fee=shipping_fee, total_payment=total_payment)

@bp.route("/config")
def get_publishable_key():
    stripe_config = {"publicKey": os.environ.get('STRIPE_PUBLISHABLE_KEY')}
    return jsonify(stripe_config)


@bp.route("/orders/success")
def payment_successful():
    flash('Your order has been created successfully.')
    return redirect(url_for('accounts.settings'))

@bp.route("/orders/cancel")
def payment_unsuccessful():
    flash('Your payment was unsuccessful. Please go to our Acount > Order History > Order to find the unique payment link.')
    return redirect(url_for('accounts.settings'))