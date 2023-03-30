from flask import Flask, render_template
from config import Config
from application.extensions.db import db, migrate

def create_app(config_class=Config):

    app = Flask(__name__)
    app.config.from_object(config_class)
    db.init_app(app)

    with app.app_context():
        from application.models import User, Product, Orders, OrderLine
        db.create_all()
        migrate.init_app(app, db, compare_type=True)

    from application.accounts.views import bp as auth
    from application.products.views import bp as products
    from application.orders.views import bp as orders

    app.register_blueprint(auth)
    app.register_blueprint(products)
    app.register_blueprint(orders)
    app.add_url_rule("/", endpoint="index")

    @app.errorhandler(401)
    def unauthorized_page(error):
        return render_template("errors/401.html"), 401

    @app.errorhandler(404)
    def page_not_found(error):
        return render_template("errors/404.html"), 404

    @app.errorhandler(500)
    def server_error_page(error):
        return render_template("errors/500.html"), 500

    return app
