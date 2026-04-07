from datetime import datetime

from sqlalchemy import CheckConstraint, Enum, ForeignKey, Index, UniqueConstraint
from sqlalchemy.orm import relationship

from app.extensions import db


class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(190), nullable=False, unique=True, index=True)
    password = db.Column(db.String(255), nullable=False)
    role = db.Column(Enum("admin", "vendor", "user", name="user_roles"), nullable=False)

    memberships = relationship("Membership", back_populates="user", cascade="all, delete")
    cart_items = relationship("Cart", back_populates="user", cascade="all, delete")
    orders = relationship("Order", back_populates="user", cascade="all, delete")
    guest_items = relationship("GuestList", back_populates="user", cascade="all, delete")


class Vendor(db.Model):
    __tablename__ = "vendors"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, ForeignKey("users.id", ondelete="CASCADE"), unique=True)
    name = db.Column(db.String(120), nullable=False)
    category = db.Column(
        Enum("Catering", "Florist", "Decoration", "Lighting", name="vendor_categories"),
        nullable=False,
        index=True,
    )
    contact = db.Column(db.String(120), nullable=False)
    sell_items = db.Column(db.String(500), nullable=True)

    user = relationship("User")
    products = relationship("Product", back_populates="vendor", cascade="all, delete")
    requests = relationship("ProductRequest", back_populates="vendor", cascade="all, delete")


class Product(db.Model):
    __tablename__ = "products"

    id = db.Column(db.Integer, primary_key=True)
    vendor_id = db.Column(db.Integer, ForeignKey("vendors.id", ondelete="CASCADE"), nullable=False)
    name = db.Column(db.String(120), nullable=False)
    price = db.Column(db.Numeric(10, 2), nullable=False)
    image = db.Column(db.String(300), nullable=True)

    vendor = relationship("Vendor", back_populates="products")

    __table_args__ = (
        CheckConstraint("price >= 0", name="ck_products_price_positive"),
        Index("ix_products_vendor", "vendor_id"),
    )


class Cart(db.Model):
    __tablename__ = "cart"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    product_id = db.Column(db.Integer, ForeignKey("products.id", ondelete="CASCADE"), nullable=False)
    quantity = db.Column(db.Integer, nullable=False, default=1)

    user = relationship("User", back_populates="cart_items")
    product = relationship("Product")

    __table_args__ = (
        CheckConstraint("quantity > 0", name="ck_cart_qty_positive"),
        UniqueConstraint("user_id", "product_id", name="uq_cart_user_product"),
        Index("ix_cart_user", "user_id"),
    )


class Order(db.Model):
    __tablename__ = "orders"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    total = db.Column(db.Numeric(10, 2), nullable=False)
    customer_name = db.Column(db.String(120), nullable=False)
    customer_number = db.Column(db.String(25), nullable=False)
    customer_email = db.Column(db.String(190), nullable=False)
    customer_address = db.Column(db.String(220), nullable=False)
    customer_state = db.Column(db.String(120), nullable=False)
    customer_city = db.Column(db.String(120), nullable=False)
    customer_pincode = db.Column(db.String(20), nullable=False)
    status = db.Column(
        Enum("Received", "Ready for Shipping", "Out for Delivery", name="order_status"),
        nullable=False,
        default="Received",
    )
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    user = relationship("User", back_populates="orders")
    items = relationship("OrderItem", back_populates="order", cascade="all, delete")
    transaction = relationship("Transaction", back_populates="order", uselist=False)

    __table_args__ = (
        CheckConstraint("total >= 0", name="ck_orders_total_positive"),
        Index("ix_orders_user", "user_id"),
        Index("ix_orders_status", "status"),
    )


class OrderItem(db.Model):
    __tablename__ = "order_items"

    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, ForeignKey("orders.id", ondelete="CASCADE"), nullable=False)
    product_id = db.Column(db.Integer, ForeignKey("products.id", ondelete="RESTRICT"), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)

    order = relationship("Order", back_populates="items")
    product = relationship("Product")

    __table_args__ = (
        CheckConstraint("quantity > 0", name="ck_order_items_qty_positive"),
        Index("ix_order_items_order", "order_id"),
    )


class Membership(db.Model):
    __tablename__ = "membership"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    duration = db.Column(Enum("6 months", "1 year", "2 years", name="membership_duration"), nullable=False)
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)

    user = relationship("User", back_populates="memberships")

    __table_args__ = (Index("ix_membership_user", "user_id"),)


class Transaction(db.Model):
    __tablename__ = "transactions"

    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, ForeignKey("orders.id", ondelete="CASCADE"), nullable=False, unique=True)
    payment_method = db.Column(Enum("Cash", "UPI", name="payment_methods"), nullable=False)
    status = db.Column(db.String(50), nullable=False, default="Completed")

    order = relationship("Order", back_populates="transaction")

    __table_args__ = (Index("ix_transactions_order", "order_id"),)


class GuestList(db.Model):
    __tablename__ = "guest_list"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(190), nullable=True)
    address = db.Column(db.String(200), nullable=True)

    user = relationship("User", back_populates="guest_items")

    __table_args__ = (Index("ix_guest_user", "user_id"),)


class ProductRequest(db.Model):
    __tablename__ = "product_requests"

    id = db.Column(db.Integer, primary_key=True)
    vendor_id = db.Column(db.Integer, ForeignKey("vendors.id", ondelete="CASCADE"), nullable=False)
    requested_by = db.Column(db.Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    item_name = db.Column(db.String(120), nullable=False)
    note = db.Column(db.String(300), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    vendor = relationship("Vendor", back_populates="requests")
    requester = relationship("User")

    __table_args__ = (Index("ix_requests_vendor", "vendor_id"),)
