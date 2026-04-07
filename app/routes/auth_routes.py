from flask import Blueprint, flash, redirect, render_template, request, session, url_for

from app.extensions import db
from app.models.models import User, Vendor
from app.services.auth_service import authenticate_user, create_user

auth_bp = Blueprint("auth", __name__)


def _perform_login(user):
    session.clear()
    session["user_id"] = user.id
    session["role"] = user.role
    session["name"] = user.name


def _redirect_for_role(role: str):
    if role == "admin":
        return redirect(url_for("admin.dashboard"))
    if role == "vendor":
        return redirect(url_for("vendor.dashboard"))
    return redirect(url_for("user.dashboard"))


@auth_bp.get("/login")
def login_selector():
    if session.get("role"):
        return _redirect_for_role(session["role"])
    return render_template("auth/login_selector.html")


@auth_bp.route("/login/admin", methods=["GET", "POST"])
def admin_login():
    if request.method == "POST":
        try:
            email = request.form.get("email", "")
            password = request.form.get("password", "")
            user = authenticate_user(email, password, "admin")
            if not user:
                flash("Invalid admin credentials.", "danger")
                return render_template("auth/admin_login.html"), 401

            _perform_login(user)
            flash("Admin login successful.", "success")
            return redirect(url_for("admin.dashboard"))
        except Exception:
            flash("Admin login failed due to server error.", "danger")
            return render_template("auth/admin_login.html"), 500

    return render_template("auth/admin_login.html")


@auth_bp.route("/login/user", methods=["GET", "POST"])
def user_login():
    if request.method == "POST":
        try:
            email = request.form.get("email", "")
            password = request.form.get("password", "")
            user = authenticate_user(email, password, "user")
            if not user:
                flash("Invalid user credentials.", "danger")
                return render_template("auth/user_login.html"), 401

            _perform_login(user)
            flash("User login successful.", "success")
            return redirect(url_for("user.dashboard"))
        except Exception:
            flash("User login failed due to server error.", "danger")
            return render_template("auth/user_login.html"), 500

    return render_template("auth/user_login.html")


@auth_bp.route("/login/vendor", methods=["GET", "POST"])
def vendor_login():
    if request.method == "POST":
        try:
            email = request.form.get("email", "")
            password = request.form.get("password", "")
            user = authenticate_user(email, password, "vendor")
            if not user:
                flash("Invalid vendor credentials.", "danger")
                return render_template("auth/vendor_login.html"), 401

            _perform_login(user)
            flash("Vendor login successful.", "success")
            return redirect(url_for("vendor.dashboard"))
        except Exception:
            flash("Vendor login failed due to server error.", "danger")
            return render_template("auth/vendor_login.html"), 500

    return render_template("auth/vendor_login.html")


@auth_bp.route("/signup/<role>", methods=["GET", "POST"])
def signup(role):
    if role not in {"admin", "user", "vendor"}:
        return redirect(url_for("auth.login_selector"))

    if request.method == "POST":
        name = request.form.get("name", "")
        email = request.form.get("email", "")
        password = request.form.get("password", "")
        category = request.form.get("category", "Catering")
        contact = request.form.get("contact", "")

        user, err = create_user(name=name, email=email, password=password, role=role)
        if err:
            flash(err, "danger")
            return render_template("auth/signup.html", role=role), 400

        if role == "vendor":
            vendor = Vendor(user_id=user.id, name=name, category=category, contact=contact or email)
            db.session.add(vendor)
            db.session.commit()

        flash("Account created. Please login.", "success")
        if role == "admin":
            return redirect(url_for("auth.admin_login"))
        if role == "vendor":
            return redirect(url_for("auth.vendor_login"))
        return redirect(url_for("auth.user_login"))

    return render_template("auth/signup.html", role=role)


@auth_bp.post("/logout")
def logout():
    role = session.get("role")
    session.clear()
    flash("Logged out successfully.", "success")

    if role == "admin":
        return redirect(url_for("auth.admin_login"))
    if role == "vendor":
        return redirect(url_for("auth.vendor_login"))
    if role == "user":
        return redirect(url_for("auth.user_login"))
    return redirect(url_for("auth.login_selector"))


@auth_bp.cli.command("seed")
def seed_command():
    from app.extensions import bcrypt

    if User.query.count() > 0:
        return

    demo = [
        ("Admin", "admin@event.com", "Admin@123", "admin"),
        ("Vendor A", "vendor@event.com", "Vendor@123", "vendor"),
        ("User A", "user@event.com", "User@1234", "user"),
    ]

    for name, email, password, role in demo:
        hashed = bcrypt.generate_password_hash(password).decode("utf-8")
        db.session.add(User(name=name, email=email, password=hashed, role=role))

    db.session.commit()

    vendor_user = User.query.filter_by(email="vendor@event.com", role="vendor").first()
    if vendor_user:
        db.session.add(
            Vendor(
                user_id=vendor_user.id,
                name="Vendor A",
                category="Catering",
                contact="9876543210",
            )
        )
        db.session.commit()
