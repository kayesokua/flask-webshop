from flask import Flask, render_template, redirect, url_for, request, session, flash, abort
from flask_login import LoginManager
from config import DevelopmentConfig, ProductionConfig, TestingConfig
from application.extensions.db import db, migrate
from application.products.routes import index

from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

def create_app():
    app = Flask(__name__)
    app.config.from_object('config.DevelopmentConfig')
    db.init_app(app)

    with app.app_context():
        from application.models import User, Product, OrderLine, Orders, DeliveryAddress, Prices
        db.create_all()
        migrate.init_app(app, db, compare_type=True)

    from application.accounts.routes import bp as accounts
    from application.products.routes import bp as products
    from application.orders.routes import bp as orders

    app.register_blueprint(accounts)
    app.register_blueprint(products)
    app.register_blueprint(orders)
    app.add_url_rule("/", endpoint='products.index')

    login_manager = LoginManager()
    login_manager.login_view = 'accounts.login'
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    @app.errorhandler(401)
    def unauthorized_page(error):
        return render_template("errors/401.html"), 401

    @app.errorhandler(404)
    def page_not_found(error):
        return render_template("errors/404.html"), 404

    @app.errorhandler(500)
    def server_error_page(error):
        return render_template("errors/500.html"), 500

    limiter = Limiter(
    get_remote_address,
        app=app,
        default_limits=["200 per day", "50 per hour"],
        storage_uri="memory://",
    )

    return app