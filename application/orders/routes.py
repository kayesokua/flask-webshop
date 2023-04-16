import os, stripe, pytz
from sqlalchemy import and_
from flask import Blueprint, flash, redirect, render_template, url_for, session, request
from flask_login import login_required, current_user
from application.extensions.db import db
from application.extensions.cache import cache
from application.extensions.limiter import limiter
from application.extensions.twilio import generate_custom_code, send_checkout_verification
from application.models import Product, Orders, OrderLine, Prices, DeliveryAddress
from application.orders.forms import CheckoutForm, VerifyOrderForm
from datetime import timedelta, datetime

bp = Blueprint("orders", __name__)

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

@bp.route('/cart/add/<uuid:id>')
@login_required
def cart_add_item(id):
    if 'cart' in session:
        cart = session['cart']
        item_exists = False
        for item in cart:
            if item['id'] == str(id):
                item['quantity'] += 1
                item_exists = True
                break
        if not item_exists:
            cart.append({'id': str(id), 'quantity': 1})
        session['cart'] = cart
    else:
        session['cart'] = [{'id': str(id), 'quantity': 1}]
    session.modified = True
    cart_items = [{'id': item['id'], 'quantity': item['quantity']} for item in session['cart']]
    print("testing cart items..")
    print(cart_items)
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
@login_required
def checkout():
    form = CheckoutForm()
    products, grand_total, shipping_fee, total_payment = handle_cart()
    if form.validate_on_submit():
        selected_address_id = form.selected_address.data
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
            success_url=f"{domain_url}/orders/{order_id}/payment",
            cancel_url=f"{domain_url}/orders/{order_id}/payment",
        )

        order = Orders.query.filter_by(id=order_id).first()
        order.stripe_payment_id = stripe_session.id
        order.stripe_payment_url = stripe_session.url
        db.session.commit()

        send_checkout_verification(mobile=current_user.mobile, order=order)

        return redirect(f"/orders/{order_id}")
    return render_template('orders/checkout.html', form=form, products=products, grand_total=grand_total, shipping_fee=shipping_fee, total_payment=total_payment)

@bp.route("/orders/<uuid:id>/payment")
def payment_successful(id):
    order = Orders.query.filter_by(id=id).first()
    stripe.api_key = os.environ.get('STRIPE_SECRET_KEY_DEV')
    session = stripe.checkout.Session.retrieve(order.stripe_payment_id)
    if session.payment_status == "paid":
        order.payment_status = "paid"
        db.session.commit()
        flash('Payment complete')
    else:
        flash('Your payment was unsuccessful. Please try again.')
    return redirect(url_for('accounts.settings'))

@bp.route("/orders/<uuid:id>", methods=['GET', 'POST'])
def order_detail(id):
    order = Orders.query.filter_by(id=id).first()
    order_lines = OrderLine.query.filter_by(order_id=id).all()
    address = DeliveryAddress.query.filter_by(id=order.address_id).first()
    expiry_time = order.time_created + timedelta(hours=12)
    remaining_time = expiry_time - datetime.now(pytz.utc)
    form = VerifyOrderForm()
    for order_line in order_lines:
        product = Product.query.filter_by(id=order_line.product_id).first()
        order_line.product = product

    if request.method=='POST' and form.validate_on_submit():
        if form.verification_token.data == order.checkout_verification_code:
            order.is_purchase_verified = True
            db.session.commit()
        else:
            order.checkout_verification_attemps += 1
            db.session.commit()
            flash('Your verification code is invalid. Please try again.')

        if order.checkout_verification_attemps > 4:
            order.delivery_status = "cancelled"
            order.payment_status = "cancelled"
            order.is_expired = True
            db.session.commit()

    return render_template('orders/detail.html',
                           order=order,
                           order_lines=order_lines,
                           title="Order Detail",
                           address=address,
                           remaining_time=remaining_time,
                           form=form)

@bp.route("/orders/<uuid:id>/cancel")
def cancel_order(id):
    order = Orders.query.filter_by(id=id).first()
    order.delivery_status = "cancelled"
    order.payment_status = "cancelled"
    order.time_updated = datetime.now(pytz.utc)
    db.session.commit()
    flash('Your order has been cancelled successfully.')
    if order.delivery_status == "cancelled":
        orderlines = OrderLine.query.filter_by(order_id=id).all()
        for orderline in orderlines:
            product = Product.query.filter_by(id=orderline.product_id).first()
            product.stock += orderline.quantity
            db.session.commit()
    return redirect(url_for('accounts.settings'))