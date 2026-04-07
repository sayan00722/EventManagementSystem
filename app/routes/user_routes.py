from datetime import timedelta
from decimal import Decimal

from flask import Blueprint, flash, redirect, render_template, request, session, url_for
from sqlalchemy.orm import joinedload

from app.extensions import db
from app.models.models import Cart, GuestList, Membership, Order, OrderItem, Product, ProductRequest, Transaction, Vendor
from app.services.guards import login_required, role_required

user_bp = Blueprint("user", __name__, url_prefix="/user")


@user_bp.get("/dashboard")
@login_required
@role_required("user")
def dashboard():
    return render_template("user/dashboard.html")


@user_bp.get("/vendors")
@login_required
@role_required("user")
def vendors():
    category = request.args.get("category", "Catering")
    items = Vendor.query.filter_by(category=category).all()
    return render_template("user/vendors.html", vendors=items, category=category)


@user_bp.post("/cart/add/<int:product_id>")
@login_required
@role_required("user")
def add_to_cart(product_id):
    product = Product.query.get_or_404(product_id)
    user_id = session["user_id"]
    quantity = request.form.get("quantity", type=int) or 1
    if quantity < 1:
        quantity = 1

    row = Cart.query.filter_by(user_id=user_id, product_id=product.id).first()
    if row:
        row.quantity += quantity
    else:
        row = Cart(user_id=user_id, product_id=product.id, quantity=quantity)
        db.session.add(row)

    db.session.commit()
    flash("Added to cart.", "success")
    next_category = product.vendor.category if product.vendor else "Catering"
    return redirect(url_for("user.vendors", category=next_category))


@user_bp.route("/cart", methods=["GET", "POST"])
@login_required
@role_required("user")
def cart():
    user_id = session["user_id"]

    if request.method == "POST":
        action = request.form.get("action")

        if action == "update":
            cart_id = request.form.get("cart_id", type=int)
            quantity = request.form.get("quantity", type=int)
            row = Cart.query.filter_by(id=cart_id, user_id=user_id).first()
            if row and quantity and quantity > 0:
                row.quantity = quantity
                db.session.commit()
                flash("Quantity updated.", "success")

        elif action == "remove":
            cart_id = request.form.get("cart_id", type=int)
            row = Cart.query.filter_by(id=cart_id, user_id=user_id).first()
            if row:
                db.session.delete(row)
                db.session.commit()
                flash("Item removed.", "success")

        elif action == "clear":
            Cart.query.filter_by(user_id=user_id).delete()
            db.session.commit()
            flash("Cart cleared.", "success")

        return redirect(url_for("user.cart"))

    items = (
        Cart.query.options(joinedload(Cart.product))
        .filter_by(user_id=user_id)
        .order_by(Cart.id.desc())
        .all()
    )
    grand_total = sum((Decimal(item.quantity) * Decimal(item.product.price) for item in items), Decimal("0.00"))

    return render_template("user/cart.html", items=items, grand_total=grand_total)


@user_bp.route("/request-item", methods=["GET", "POST"])
@login_required
@role_required("user")
def request_item():
    if request.method == "POST":
        vendor_id = request.form.get("vendor_id", type=int)
        item_name = request.form.get("item_name", "").strip()
        note = request.form.get("note", "").strip()

        if not vendor_id or not item_name:
            flash("Vendor and item name are required.", "danger")
            return redirect(url_for("user.request_item"))

        req = ProductRequest(
            vendor_id=vendor_id,
            requested_by=session["user_id"],
            item_name=item_name,
            note=note,
        )
        db.session.add(req)
        db.session.commit()
        flash("Request submitted.", "success")
        return redirect(url_for("user.request_item"))

    vendors = Vendor.query.order_by(Vendor.name.asc()).all()
    return render_template("user/request_item.html", vendors=vendors)


@user_bp.route("/guest-list", methods=["GET", "POST"])
@login_required
@role_required("user")
def guest_list():
    user_id = session["user_id"]
    if request.method == "POST":
        action = request.form.get("action", "add")
        if action == "add":
            guest = GuestList(
                user_id=user_id,
                name=request.form.get("name", "").strip(),
                email=request.form.get("email", "").strip(),
                address=request.form.get("address", "").strip(),
            )
            if not guest.name:
                flash("Guest name is required.", "danger")
            else:
                db.session.add(guest)
                db.session.commit()
                flash("Guest added.", "success")

        elif action == "update":
            guest_id = request.form.get("guest_id", type=int)
            guest = GuestList.query.filter_by(id=guest_id, user_id=user_id).first()
            if guest:
                guest.name = request.form.get("name", guest.name)
                guest.email = request.form.get("email", guest.email)
                guest.address = request.form.get("address", guest.address)
                db.session.commit()
                flash("Guest updated.", "success")

        elif action == "delete":
            guest_id = request.form.get("guest_id", type=int)
            guest = GuestList.query.filter_by(id=guest_id, user_id=user_id).first()
            if guest:
                db.session.delete(guest)
                db.session.commit()
                flash("Guest deleted.", "success")

        return redirect(url_for("user.guest_list"))

    guests = GuestList.query.filter_by(user_id=user_id).order_by(GuestList.id.desc()).all()
    return render_template("user/guest_list.html", guests=guests)


@user_bp.route("/checkout", methods=["GET", "POST"])
@login_required
@role_required("user")
def checkout():
    user_id = session["user_id"]
    cart_items = (
        Cart.query.options(joinedload(Cart.product))
        .filter_by(user_id=user_id)
        .order_by(Cart.id.desc())
        .all()
    )
    grand_total = sum((Decimal(item.quantity) * Decimal(item.product.price) for item in cart_items), Decimal("0.00"))

    if request.method == "POST":
        payment_method = request.form.get("payment_method", "Cash")
        customer_name = request.form.get("customer_name", "").strip()
        customer_number = request.form.get("customer_number", "").strip()
        customer_email = request.form.get("customer_email", "").strip()
        customer_address = request.form.get("customer_address", "").strip()
        customer_state = request.form.get("customer_state", "").strip()
        customer_city = request.form.get("customer_city", "").strip()
        customer_pincode = request.form.get("customer_pincode", "").strip()

        required_fields = [
            customer_name,
            customer_number,
            customer_email,
            customer_address,
            customer_state,
            customer_city,
            customer_pincode,
        ]

        if not all(required_fields):
            flash("All checkout fields are required.", "danger")
            return redirect(url_for("user.checkout"))

        if payment_method not in {"Cash", "UPI"}:
            flash("Invalid payment method.", "danger")
            return redirect(url_for("user.checkout"))

        if not cart_items:
            flash("Cart is empty.", "warning")
            return redirect(url_for("user.cart"))

        order = Order(
            user_id=user_id,
            total=grand_total,
            customer_name=customer_name,
            customer_number=customer_number,
            customer_email=customer_email,
            customer_address=customer_address,
            customer_state=customer_state,
            customer_city=customer_city,
            customer_pincode=customer_pincode,
            status="Received",
        )
        db.session.add(order)
        db.session.flush()

        for item in cart_items:
            db.session.add(
                OrderItem(order_id=order.id, product_id=item.product_id, quantity=item.quantity)
            )

        db.session.add(Transaction(order_id=order.id, payment_method=payment_method, status="Completed"))

        Cart.query.filter_by(user_id=user_id).delete()
        db.session.commit()

        return redirect(url_for("user.success", order_id=order.id))

    return render_template("user/checkout.html", grand_total=grand_total)


@user_bp.get("/success/<int:order_id>")
@login_required
@role_required("user")
def success(order_id):
    order = Order.query.filter_by(id=order_id, user_id=session["user_id"]).first_or_404()
    txn = Transaction.query.filter_by(order_id=order.id).first()
    return render_template("user/success.html", order=order, txn=txn)


@user_bp.get("/order-status")
@login_required
@role_required("user")
def order_status():
    items = Order.query.filter_by(user_id=session["user_id"]).order_by(Order.id.desc()).all()
    return render_template("user/order_status.html", items=items)


@user_bp.get("/reports")
@login_required
@role_required("user")
def reports():
    user_id = session["user_id"]
    orders = Order.query.filter_by(user_id=user_id).all()
    total_orders = len(orders)
    total_spend = sum((Decimal(order.total) for order in orders), Decimal("0.00"))

    status_count = {
        "Received": 0,
        "Ready for Shipping": 0,
        "Out for Delivery": 0,
    }
    for order in orders:
        if order.status in status_count:
            status_count[order.status] += 1

    return render_template(
        "user/reports.html",
        total_orders=total_orders,
        total_spend=total_spend,
        status_count=status_count,
    )


@user_bp.get("/transactions")
@login_required
@role_required("user")
def transactions():
    items = (
        Transaction.query.join(Order, Transaction.order_id == Order.id)
        .filter(Order.user_id == session["user_id"])
        .order_by(Transaction.id.desc())
        .all()
    )
    return render_template("user/transactions.html", items=items)


@user_bp.route("/membership", methods=["GET", "POST"])
@login_required
@role_required("user")
def membership():
    user_id = session["user_id"]
    durations = {"6 months": 180, "1 year": 365, "2 years": 730}
    current = (
        Membership.query.filter_by(user_id=user_id)
        .order_by(Membership.end_date.desc(), Membership.id.desc())
        .first()
    )

    if request.method == "POST":
        action = request.form.get("action", "update")
        if not current:
            flash("Membership not found for your account.", "danger")
            return redirect(url_for("user.membership"))

        if action == "update":
            extension = request.form.get("duration", "6 months")
            extra_days = durations.get(extension, 180)
            current.duration = extension
            current.end_date = current.end_date + timedelta(days=extra_days)
            db.session.commit()
            flash("Membership extended successfully.", "success")

        elif action == "revoke":
            db.session.delete(current)
            db.session.commit()
            flash("Membership canceled successfully.", "success")

        return redirect(url_for("user.membership"))

    return render_template("user/membership.html", membership=current)
