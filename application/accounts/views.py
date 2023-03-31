from flask import Blueprint, flash, g, redirect, render_template, request, session, url_for
from werkzeug.security import generate_password_hash, check_password_hash
from application import db
from application.models import User
from flask_login import LoginManager, login_required, login_user, logout_user, current_user

bp = Blueprint("accounts", __name__, url_prefix="/accounts")
login_manager = LoginManager()

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@login_manager.unauthorized_handler
def unauthorized():
    flash("You must be logged in to view that page.")
    return redirect(url_for("accounts.login"))

@bp.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("accounts.settings"))
    else:
        username = ""

        if request.method == "POST":
            username = request.form["username"]
            password = request.form["password"]
            password2 = request.form["password2"]

            error = None
            user = User.query.filter_by(username=username).first()

            if user is not None:
                error = "Username " + username + " already exists."
            elif password != password2:
                error = "Passwords do not match."

            if error is None:
                # The username and password are valid, so we can insert the user into the database.
                user = User(username=username, password=generate_password_hash(password))
                db.session.add(user)
                db.session.commit()
                login_user(user)
                return redirect(url_for("index"))

            flash(error)

        return render_template("accounts/register.html", username=username)

@bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("index"))
    else:
        if request.method == "POST":
            username = request.form["username"]
            password = request.form["password"]
            user = User.query.filter_by(username=username).first()
            if not user or not check_password_hash(user.password, password):
                flash('Please check your login details and try again.')
                return redirect(url_for('accounts.login')) # if user doesn't exist or password is wrong, reload the page
            login_user(user)
            return redirect(url_for("index"))
        return render_template("accounts/login.html")

@bp.route("/logout")
@login_required
def logout():
    """Clear the current session, including the stored user id."""
    logout_user()
    return redirect(url_for("index"))

@bp.route("/settings")
@login_required
def settings():
    return render_template("accounts/settings.html")

@login_manager.user_loader
def load_user(user_id):
    return db.session.query(User).get(int(user_id))

@login_manager.unauthorized_handler
def unauthorized():
    flash("You must be logged in to view that page.")
    return redirect(url_for("accounts.login"))