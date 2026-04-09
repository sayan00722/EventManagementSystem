from datetime import date, timedelta
from decimal import Decimal

from flask import Blueprint, flash, redirect, render_template, request, session, url_for

from app.extensions import bcrypt, db
from app.models.models import Membership, Order, Product, Transaction, User, Vendor
from app.services.auth_service import create_user, validate_password
from app.services.guards import login_required, role_required

admin_bp = Blueprint("admin", __name__, url_prefix="/admin")


def _normalize_sell_items(raw_value: str) -> str:
    if not raw_value:
        return ""

    seen = set()
    cleaned = []
    for token in [part.strip() for part in raw_value.split(",") if part.strip()]:
        key = token.lower()
        if key in seen:
            continue
        seen.add(key)
        cleaned.append(token)

    return ", ".join(cleaned)


def _normalize_product_key(value: str) -> str:
    # Collapse extra spaces and compare names case-insensitively.
    return " ".join((value or "").strip().split()).lower()


def _sync_vendor_products_from_sell_items(vendor: Vendor) -> int:
    if not vendor or not vendor.sell_items:
        return 0

    requested_items = [" ".join(item.strip().split()) for item in vendor.sell_items.split(",") if item.strip()]
    if not requested_items:
        return 0

    existing_names = {
        _normalize_product_key(product.name)
        for product in Product.query.filter_by(vendor_id=vendor.id).all()
    }

    requested_unique = []
    requested_seen = set()
    for item_name in requested_items:
        key = _normalize_product_key(item_name)
        if not key or key in requested_seen:
            continue
        requested_seen.add(key)
        requested_unique.append(item_name)

    created = 0
    default_image = "https://images.pexels.com/photos/169190/pexels-photo-169190.jpeg"
    for item_name in requested_unique:
        key = _normalize_product_key(item_name)
        if key in existing_names:
            continue

        db.session.add(
            Product(
                vendor_id=vendor.id,
                name=item_name,
                price=Decimal("100.00"),
                image=default_image,
            )
        )
        existing_names.add(key)
        created += 1

    return created


@admin_bp.get("/dashboard")
@login_required
@role_required("admin")
def dashboard():
    return render_template("admin/dashboard.html")


@admin_bp.route("/maintenance/user", methods=["GET", "POST"])
@login_required
@role_required("admin")
def maintain_user():
    if request.method == "POST":
        action = request.form.get("action", "add")
        if action == "add":
            user, err = create_user(
                request.form.get("name", ""),
                request.form.get("email", ""),
                request.form.get("password", ""),
                "user",
            )
            if err:
                flash(err, "danger")
            else:
                flash("User added.", "success")

        elif action == "update":
            user_id = request.form.get("user_id", type=int)
            user = User.query.filter_by(id=user_id, role="user").first()
            if not user:
                flash("User not found.", "danger")
            else:
                name = request.form.get("name", "").strip()
                email = request.form.get("email", "").strip().lower()
                new_password = request.form.get("new_password", "")

                if name:
                    user.name = name

                if email and email != user.email:
                    email_exists = User.query.filter(User.email == email, User.id != user.id).first()
                    if email_exists:
                        flash("Email already in use by another account.", "danger")
                        return redirect(url_for("admin.maintain_user"))
                    user.email = email

                if new_password:
                    if not validate_password(new_password):
                        flash("Password must be 8+ chars with upper, lower, and number.", "danger")
                        return redirect(url_for("admin.maintain_user"))
                    user.password = bcrypt.generate_password_hash(new_password).decode("utf-8")

                db.session.commit()
                flash("User updated.", "success")

        elif action == "delete":
            user_id = request.form.get("user_id", type=int)
            user = User.query.filter_by(id=user_id, role="user").first()
            if not user:
                flash("User not found.", "danger")
            else:
                db.session.delete(user)
                db.session.commit()
                flash("User deleted.", "success")

        return redirect(url_for("admin.maintain_user"))

    users = User.query.filter_by(role="user").order_by(User.id.desc()).all()
    return render_template("admin/maintain_user.html", users=users)


@admin_bp.route("/maintenance/vendor", methods=["GET", "POST"])
@login_required
@role_required("admin")
def maintain_vendor():
    if request.method == "POST":
        action = request.form.get("action", "add")
        if action == "add":
            name = request.form.get("name", "")
            email = request.form.get("email", "")
            password = request.form.get("password", "")
            contact = request.form.get("contact", "")
            category = request.form.get("category", "Catering")
            sell_items = _normalize_sell_items(request.form.get("sell_items", ""))

            user, err = create_user(name, email, password, "vendor")
            if err:
                flash(err, "danger")
            else:
                vendor = Vendor(
                    user_id=user.id,
                    name=name,
                    category=category,
                    contact=contact or email,
                    sell_items=sell_items,
                )
                db.session.add(vendor)
                db.session.flush()

                new_count = _sync_vendor_products_from_sell_items(vendor)
                db.session.commit()
                if new_count > 0:
                    flash(f"Vendor added. {new_count} product(s) generated from items list.", "success")
                else:
                    flash("Vendor added.", "success")

        elif action == "update":
            vendor_id = request.form.get("vendor_id", type=int)
            vendor = Vendor.query.filter_by(id=vendor_id).first()
            if not vendor:
                flash("Vendor not found.", "danger")
            else:
                name = request.form.get("name", "").strip()
                email = request.form.get("email", "").strip().lower()
                contact = request.form.get("contact", "").strip()
                category = request.form.get("category", vendor.category)
                sell_items = _normalize_sell_items(request.form.get("sell_items", ""))
                new_password = request.form.get("new_password", "")

                if name:
                    vendor.name = name
                if contact:
                    vendor.contact = contact
                vendor.category = category
                vendor.sell_items = sell_items

                linked_user = User.query.filter_by(id=vendor.user_id, role="vendor").first()
                if linked_user and email and email != linked_user.email:
                    email_exists = User.query.filter(User.email == email, User.id != linked_user.id).first()
                    if email_exists:
                        flash("Email already in use by another account.", "danger")
                        return redirect(url_for("admin.maintain_vendor"))
                    linked_user.email = email

                if linked_user and new_password:
                    if not validate_password(new_password):
                        flash("Password must be 8+ chars with upper, lower, and number.", "danger")
                        return redirect(url_for("admin.maintain_vendor"))
                    linked_user.password = bcrypt.generate_password_hash(new_password).decode("utf-8")

                new_count = _sync_vendor_products_from_sell_items(vendor)
                db.session.commit()
                if new_count > 0:
                    flash(f"Vendor updated. {new_count} product(s) generated from items list.", "success")
                else:
                    flash("Vendor updated.", "success")

        elif action == "delete":
            vendor_id = request.form.get("vendor_id", type=int)
            vendor = Vendor.query.filter_by(id=vendor_id).first()
            if not vendor:
                flash("Vendor not found.", "danger")
            else:
                linked_user = User.query.filter_by(id=vendor.user_id, role="vendor").first()
                if linked_user:
                    db.session.delete(linked_user)
                else:
                    db.session.delete(vendor)
                db.session.commit()
                flash("Vendor deleted.", "success")

        return redirect(url_for("admin.maintain_vendor"))

    vendors = Vendor.query.order_by(Vendor.id.desc()).all()
    vendor_users = {
        user.id: user for user in User.query.filter_by(role="vendor").all()
    }
    return render_template("admin/maintain_vendor.html", vendors=vendors, vendor_users=vendor_users)


@admin_bp.route("/membership", methods=["GET", "POST"])
@login_required
@role_required("admin")
def membership():
    durations = {"6 months": 180, "1 year": 365, "2 years": 730}
    membership_to_edit = None

    if request.method == "POST":
        action = request.form.get("action", "add")
        if action == "add":
            user_id = request.form.get("user_id", type=int)
            duration = request.form.get("duration", "6 months")
            start = date.today()
            end = start + timedelta(days=durations.get(duration, 180))

            if not user_id:
                flash("User ID is required.", "danger")
            else:
                record = Membership(
                    user_id=user_id,
                    duration=duration,
                    start_date=start,
                    end_date=end,
                )
                db.session.add(record)
                db.session.commit()
                flash("Membership added.", "success")

        if action == "update":
            membership_id = request.form.get("membership_id", type=int)
            user_id = request.form.get("user_id", type=int)
            extension = request.form.get("duration", "6 months")
            if not membership_id:
                flash("Membership ID is mandatory.", "danger")
            else:
                record = Membership.query.filter_by(id=membership_id).first()
                if not record:
                    flash("Membership not found.", "danger")
                else:
                    extra = timedelta(days=durations.get(extension, 180))
                    record.duration = extension
                    if user_id:
                        record.user_id = user_id
                    record.end_date = record.end_date + extra
                    db.session.commit()
                    flash("Membership updated.", "success")

        if action == "revoke":
            membership_id = request.form.get("membership_id", type=int)
            record = Membership.query.filter_by(id=membership_id).first()
            if not record:
                flash("Membership not found.", "danger")
            else:
                db.session.delete(record)
                db.session.commit()
                flash("Membership revoked.", "success")

        return redirect(url_for("admin.membership"))

    lookup_id = request.args.get("membership_id", type=int)
    if lookup_id:
        membership_to_edit = Membership.query.filter_by(id=lookup_id).first()

    records = Membership.query.order_by(Membership.id.desc()).all()
    users = User.query.filter_by(role="user").order_by(User.id.desc()).all()
    return render_template(
        "admin/membership.html",
        records=records,
        membership_to_edit=membership_to_edit,
        users=users,
    )


@admin_bp.get("/reports")
@login_required
@role_required("admin")
def reports():
    total_orders = Order.query.count()
    completed_txn = Transaction.query.filter_by(status="Completed").count()
    revenue = (
        db.session.query(db.func.coalesce(db.func.sum(Order.total), Decimal("0.00"))).scalar()
        or Decimal("0.00")
    )

    return render_template(
        "admin/reports.html",
        total_orders=total_orders,
        completed_txn=completed_txn,
        revenue=revenue,
    )


@admin_bp.get("/transactions")
@login_required
@role_required("admin")
def transactions():
    items = (
        Transaction.query.join(Order, Transaction.order_id == Order.id)
        .order_by(Transaction.id.desc())
        .all()
    )
    return render_template("admin/transactions.html", items=items)


@admin_bp.post("/order-status/<int:order_id>")
@login_required
@role_required("admin")
def update_order_status(order_id):
    status = request.form.get("status", "Received")
    if status not in {"Received", "Ready for Shipping", "Out for Delivery"}:
        flash("Invalid status.", "danger")
        return redirect(url_for("admin.transactions"))

    order = Order.query.get_or_404(order_id)
    order.status = status
    db.session.commit()
    flash("Order status updated.", "success")
    return redirect(url_for("admin.transactions"))
