from decimal import Decimal

from flask import Blueprint, flash, redirect, render_template, request, session, url_for
from sqlalchemy import select

from app.extensions import db
from app.models.models import Order, OrderItem, Product, ProductRequest, Transaction, Vendor
from app.services.guards import login_required, role_required

vendor_bp = Blueprint("vendor", __name__, url_prefix="/vendor")


def _current_vendor():
    return Vendor.query.filter_by(user_id=session.get("user_id")).first()


@vendor_bp.get("/dashboard")
@login_required
@role_required("vendor")
def dashboard():
    return render_template("vendor/dashboard.html")


@vendor_bp.route("/items", methods=["GET", "POST"])
@login_required
@role_required("vendor")
def items():
    vendor = _current_vendor()
    if not vendor:
        flash("Vendor profile missing. Contact admin.", "danger")
        return redirect(url_for("vendor.dashboard"))

    if request.method == "POST":
        name = request.form.get("name", "").strip()
        price = request.form.get("price", "0")
        image = request.form.get("image", "")

        try:
            price_num = Decimal(price)
            if price_num < 0:
                raise ValueError("negative")
        except Exception:
            flash("Price must be a valid positive number.", "danger")
            return redirect(url_for("vendor.items"))

        if not name:
            flash("Product name is required.", "danger")
            return redirect(url_for("vendor.items"))

        product = Product(vendor_id=vendor.id, name=name, price=price_num, image=image)
        db.session.add(product)
        db.session.commit()
        flash("Product added.", "success")
        return redirect(url_for("vendor.items"))

    products = Product.query.filter_by(vendor_id=vendor.id).order_by(Product.id.desc()).all()
    return render_template("vendor/items.html", products=products)


@vendor_bp.post("/items/<int:product_id>/update")
@login_required
@role_required("vendor")
def update_item(product_id):
    vendor = _current_vendor()
    product = Product.query.filter_by(id=product_id, vendor_id=vendor.id).first_or_404()

    name = request.form.get("name", product.name).strip()
    price = request.form.get("price", str(product.price))

    try:
        product.price = Decimal(price)
    except Exception:
        flash("Invalid price value.", "danger")
        return redirect(url_for("vendor.items"))

    product.name = name or product.name
    product.image = request.form.get("image", product.image)
    db.session.commit()
    flash("Product updated.", "success")
    return redirect(url_for("vendor.items"))


@vendor_bp.post("/items/<int:product_id>/delete")
@login_required
@role_required("vendor")
def delete_item(product_id):
    vendor = _current_vendor()
    product = Product.query.filter_by(id=product_id, vendor_id=vendor.id).first_or_404()
    db.session.delete(product)
    db.session.commit()
    flash("Product deleted.", "success")
    return redirect(url_for("vendor.items"))


@vendor_bp.get("/requests")
@login_required
@role_required("vendor")
def requests_view():
    vendor = _current_vendor()
    requests = ProductRequest.query.filter_by(vendor_id=vendor.id).order_by(ProductRequest.id.desc()).all()
    return render_template("vendor/requests.html", requests=requests)


@vendor_bp.get("/transactions")
@login_required
@role_required("vendor")
def transactions():
    vendor = _current_vendor()
    order_id_subquery = (
        db.session.query(OrderItem.order_id)
        .join(Product, Product.id == OrderItem.product_id)
        .filter(Product.vendor_id == vendor.id)
        .distinct()
        .subquery()
    )

    order_items = (
        db.session.query(Order, Transaction)
        .join(Transaction, Transaction.order_id == Order.id)
        .filter(Order.id.in_(select(order_id_subquery.c.order_id)))
        .order_by(Order.id.desc())
        .all()
    )

    return render_template("vendor/transactions.html", order_items=order_items)


@vendor_bp.route("/status", methods=["GET", "POST"])
@login_required
@role_required("vendor")
def status_update():
    vendor = _current_vendor()
    if not vendor:
        flash("Vendor profile missing. Contact admin.", "danger")
        return redirect(url_for("vendor.dashboard"))

    order_id_subquery = (
        db.session.query(OrderItem.order_id)
        .join(Product, Product.id == OrderItem.product_id)
        .filter(Product.vendor_id == vendor.id)
        .distinct()
        .subquery()
    )

    vendor_orders = (
        Order.query.filter(Order.id.in_(select(order_id_subquery.c.order_id)))
        .order_by(Order.id.desc())
        .all()
    )

    if request.method == "POST":
        order_id = request.form.get("order_id", type=int)
        status = request.form.get("status", "Received")
        order = (
            Order.query.filter(Order.id == order_id)
            .filter(Order.id.in_(select(order_id_subquery.c.order_id)))
            .first()
        )
        if not order:
            flash("Order not found.", "danger")
        elif status not in {"Received", "Ready for Shipping", "Out for Delivery"}:
            flash("Invalid status.", "danger")
        else:
            order.status = status
            db.session.commit()
            flash("Status updated.", "success")

        return redirect(url_for("vendor.status_update"))

    return render_template("vendor/status.html", orders=vendor_orders)
