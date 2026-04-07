import re

from sqlalchemy import func

from app.extensions import bcrypt, db
from app.models.models import User

EMAIL_REGEX = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
PASSWORD_REGEX = re.compile(r"^(?=.*[A-Z])(?=.*[a-z])(?=.*\d).{8,}$")


def validate_email(email: str) -> bool:
    return bool(EMAIL_REGEX.match(email or ""))


def validate_password(password: str) -> bool:
    return bool(PASSWORD_REGEX.match(password or ""))


def create_user(name: str, email: str, password: str, role: str):
    if not name or not email or not password:
        return None, "All fields are required."
    if not validate_email(email):
        return None, "Invalid email format."
    if not validate_password(password):
        return (
            None,
            "Password must be 8+ chars with upper, lower, and number.",
        )

    existing = User.query.filter(func.lower(User.email) == email.lower()).first()
    if existing:
        return None, "Email already exists."

    hashed = bcrypt.generate_password_hash(password).decode("utf-8")
    user = User(name=name.strip(), email=email.strip().lower(), password=hashed, role=role)
    db.session.add(user)
    db.session.commit()
    return user, None


def authenticate_user(email: str, password: str, role: str):
    user = User.query.filter_by(email=(email or "").strip().lower(), role=role).first()
    if not user:
        return None

    if not bcrypt.check_password_hash(user.password, password or ""):
        return None

    return user
