from flask import Blueprint, flash, g, redirect, render_template, request, session, url_for
from flask_login import LoginManager, login_required, login_user, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from application import db, cache, limiter
from application.models.accounts import User, DeliveryAddress
from application.models.products import Product
from application.models.orders import Orders, OrderLine
from .forms import LoginForm, RegisterForm, DeliveryForm

login_manager = LoginManager()

bp = Blueprint("accounts", __name__, url_prefix="/accounts")

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@login_manager.unauthorized_handler
def unauthorized():
    flash("You must be logged in to view that page.")
    return redirect(url_for("accounts.login"))

@bp.route("/register", methods=["GET", "POST"])
@limiter.limit("3 per minute")
@cache.cached(timeout=60, key_prefix='register')
def register():
    form=RegisterForm()
    if current_user.is_authenticated:
        return redirect(url_for("accounts.settings"))
    else:
        if request.method=='POST' and form.validate_on_submit():
            return redirect(url_for('products.index'))
        else:
            return render_template('accounts/register.html', form=form)

@bp.route("/login", methods=["GET", "POST"])
@limiter.limit("5 per 10 minutes")
@cache.cached(timeout=60, key_prefix='login')
def login():
    form =LoginForm()

    if current_user.is_authenticated:
        return redirect(url_for('products.index'))
    else:
        if request.method=='POST' and form.validate_on_submit():
            return redirect(url_for('products.index'))
        else:
            return render_template('accounts/login.html', form=form)

@bp.route("/logout")
@login_required
def logout():
    """Clear the current session, including the stored user id."""
    logout_user()
    return redirect(url_for('products.index'))

@bp.route("/settings")
@login_required
@cache.cached(timeout=60, key_prefix='settings')
def settings():
    products = Product.query.filter_by(admin_id=current_user.id).all()
    total_products = Product.query.filter_by(admin_id=current_user.id).count()
    total_orders = Orders.query.filter_by(buyer_id=current_user.id).count()
    addresses = DeliveryAddress.query.filter_by(user_id=current_user.id).limit(5).all()
    orders = Orders.query.filter_by(buyer_id=current_user.id).order_by(Orders.time_created.desc()).limit(5).all()
    return render_template("accounts/settings.html",
                           title="My Account",
                           addresses=addresses,
                           orders=orders,
                           products=products,
                           total_orders=total_orders,
                           total_products=total_products)

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

@bp.route("/addresses/<int:address_id>/update", methods=["GET", "POST"])
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
        print(address)
        if address:
            if current_user.id == address.user_id:
                db.session.delete(address)
                db.session.commit()
                flash('Address deleted successfully.')
        else:
            flash('Address not found in database.')
    return redirect(url_for('accounts.create_address'))