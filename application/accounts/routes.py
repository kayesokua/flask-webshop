from flask import Blueprint, flash, redirect, render_template, request, url_for, session
from flask_login import LoginManager, login_required, logout_user, current_user, login_user
from application import db, cache, limiter
from application.models.accounts import User, DeliveryAddress
from application.models.products import Product
from application.models.orders import Orders, OrderLine
from application.extensions.twilio import send_verification, check_verification_token
from .forms import LoginForm, RegisterForm, DeliveryForm, ChangePasswordForm, ChangeMobileForm, VerifyMobileForm
from datetime import datetime
import pytz
import bcrypt
from os import environ


login_manager = LoginManager()

bp = Blueprint("accounts", __name__, url_prefix="/accounts")
tz = pytz.timezone('UTC')

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)

@login_manager.unauthorized_handler
def unauthorized():
    flash("You must be logged in to view that page.")
    return redirect(url_for("accounts.login"))

@bp.route("/register", methods=["GET", "POST"])
def register():
    form=RegisterForm()
    if current_user.is_authenticated:
        return redirect(url_for("accounts.settings"))
    else:
        if request.method=='POST' and form.validate_on_submit():
            return redirect(url_for('accounts.login'))
        else:
            return render_template('accounts/register.html', form=form)

@bp.route("/login", methods=["GET", "POST"])
def login():
    form=LoginForm()
    if current_user.is_authenticated:
        return redirect(url_for('accounts.settings'))
    else:
        if request.method=='POST' and form.validate_on_submit():
            return redirect(url_for('accounts.settings'))
        else:
            return render_template('accounts/login.html', form=form)

@bp.route("/logout")
@login_required
def logout():
    session.clear()
    logout_user()
    return redirect(url_for('products.index'))

@bp.route("/settings")
@login_required
def settings():
    products = Product.query.filter_by(admin_id=current_user.id).all()
    total_products = Product.query.filter_by(admin_id=current_user.id).count()
    total_orders = Orders.query.filter_by(buyer_id=current_user.id).count()
    addresses = DeliveryAddress.query.filter_by(user_id=current_user.id).limit(5).all()
    orders = Orders.query.filter_by(buyer_id=current_user.id).filter(Orders.payment_status != 'cancelled').order_by(Orders.time_created.desc()).limit(5).all()
    days_before_pass_change = 90 - (datetime.now(tz=tz) - current_user.last_password_change).days

    return render_template("accounts/settings.html",
                           title="My Account",
                           addresses=addresses,
                           orders=orders,
                           products=products,
                           total_orders=total_orders,
                           total_products=total_products,
                           days_before_pass_change=days_before_pass_change)


@bp.route("/change-password", methods=["GET", "POST"])
@login_required
def change_password():
    form = ChangePasswordForm()
    if request.method == 'POST':
        if form.validate_on_submit(current_user=current_user):
            current_user.salt = bcrypt.gensalt()
            current_user.hashed_password = bcrypt.hashpw(form.new_password.data.encode('utf-8'), current_user.salt)
            current_user.last_password_change = datetime.utcnow()
            db.session.add(current_user)
            db.session.commit()
            flash('Password changed successfully.', 'success')
            return redirect(url_for('accounts.settings'))
        else:
            flash("Password change failed. Please try again.", "danger")
    return render_template('accounts/settings/password_form.html', form=form, title="Change Password")

@bp.route("/change-mobile", methods=["GET", "POST"])
@login_required
def change_mobile():
    form = ChangeMobileForm()
    if request.method == 'POST' and form.validate_on_submit():
        new_mobile = f"+{form.country_code.data}{form.mobile_code.data}"
        if new_mobile != current_user.mobile:
            current_user.mobile = new_mobile
            current_user.is_mobile_verified = False
            db.session.commit()
            send_verification(new_mobile, current_user)
            flash("Verification code sent to new mobile number")
            return redirect(url_for('accounts.verify_mobile'))
        else:
            flash("Mobile number already in use. Try a different number")
            return redirect(url_for('accounts.settings'))
    return render_template('accounts/settings/mobile_form.html', form=form, title="Update Mobile")

@bp.route("/verify-mobile", methods=["GET", "POST"])
@login_required
def verify_mobile():
    form = VerifyMobileForm()
    if current_user.is_mobile_verified:
        flash("Mobile number already verified", "success")
        return redirect(url_for('accounts.settings'))
    else:
        if request.method == 'POST' and form.validate_on_submit(current_user=current_user):
            if check_verification_token(form.verification_token.data, current_user=current_user):
                flash("Mobile number verified successfully", "success")
                return redirect(url_for('accounts.settings'))
            else:
                flash("Please try again.", "danger")
    return render_template('accounts/settings/mobile_verify_form.html', form=form, title="Verify Mobile")

@login_manager.user_loader
def load_user(user_id):
    return db.session.query(User).get(int(user_id))

@login_manager.unauthorized_handler
def unauthorized():
    flash("You must be logged in to view that page.")
    return redirect(url_for('accounts.login'))

@bp.route("/addresses/new", methods=["GET", "POST"])
@login_required
def create_address():
    form = DeliveryForm()
    addresses = DeliveryAddress.query.filter_by(user_id=current_user.id).all()
    if request.method=='POST' and form.validate_on_submit():
        new_address = DeliveryAddress(
            first_name=form.first_name.data,
            last_name=form.last_name.data,
            email=form.email.data,
            delivery_house_nr=form.delivery_house_nr.data,
            delivery_street=form.delivery_street.data,
            delivery_additional=form.delivery_additional.data,
            delivery_state=form.delivery_state.data,
            delivery_postal=form.delivery_postal.data,
            delivery_country=form.delivery_country.data,
            instructions=form.instructions.data,
            user_id=current_user.id,
            is_valid=False
        )
        db.session.add(new_address)
        db.session.commit()
        flash('Address added successfully.')
        return redirect(url_for('accounts.create_address'))
    else:
        return render_template('accounts/delivery/form.html', title="New Address", addresses=addresses, form=form)

@bp.route("/addresses/<uuid:address_id>/update", methods=["GET", "POST"])
@login_required
def update_address(address_id):
    addresses = DeliveryAddress.query.filter_by(user_id=current_user.id).all()
    address = DeliveryAddress.query.filter_by(id=address_id).first()

    if current_user.id != address.user_id:
        flash("You do not have permission to edit that address.")
        return redirect(url_for('accounts.settings'))

    form = DeliveryForm()

    if request.method=='POST' and form.validate_on_submit():
        address.first_name=form.first_name.data
        address.last_name=form.last_name.data
        address.email=form.email.data
        address.delivery_house_nr=form.delivery_house_nr.data
        address.delivery_street=form.delivery_street.data
        address.delivery_additional=form.delivery_additional.data
        address.delivery_state=form.delivery_state.data
        address.delivery_postal=form.delivery_postal.data
        address.delivery_country=form.delivery_country.data
        address.instructions=form.instructions.data
        db.session.commit()
        flash('Address updated successfully.')
        return redirect(url_for('accounts.settings'))
    else:
        form.first_name.data = address.first_name
        form.last_name.data = address.last_name
        form.email.data = address.email
        form.delivery_house_nr.data = address.delivery_house_nr
        form.delivery_street.data = address.delivery_street
        form.delivery_additional.data = address.delivery_additional
        form.delivery_state.data = address.delivery_state
        form.delivery_postal.data = address.delivery_postal
        form.delivery_country.data = address.delivery_country
        form.instructions.data = address.instructions
        return render_template('accounts/delivery/form.html', title="Update Address", addresses=addresses, address_id=address.id,form=form)

@bp.route('/addresses/delete', methods=['POST'])
@login_required
def delete_address():
    address_id = request.form.get('address_id')
    if address_id:
        address = DeliveryAddress.query.filter_by(id=address_id).first()
        if address:
            if current_user.id == address.user_id:
                db.session.delete(address)
                db.session.commit()
                flash('Address deleted successfully.')
        else:
            flash('Address not found in database.')
    return redirect(url_for('accounts.create_address'))

@bp.route('/orders')
@login_required
def orders_history():
    orders_history = Orders.query.filter_by(buyer_id=current_user.id).all()
    return render_template('accounts/orders-history.html', title="Orders History", orders_history=orders_history)