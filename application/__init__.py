from flask import Flask, render_template
from config import Config
from application.extensions.db import db, migrate

def create_app(config_class=Config):

    app = Flask(__name__)
    app.config.from_object(config_class)
    db.init_app(app)

    with app.app_context():
        from application.models import store, auth
        db.create_all()

        migrate.init_app(app, db, compare_type=True)

    from application.views import auth, store
    app.register_blueprint(auth.bp)
    app.register_blueprint(store.bp)
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