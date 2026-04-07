from app import create_app
from app.extensions import db
import os

app = create_app()

# ✅ CREATE TABLES + SEED (FIRST TIME ONLY)
with app.app_context():
    db.create_all()

    # Optional: seed demo data (safe)
    from app.models.models import User
    from app.services.auth_service import create_user

    if not User.query.first():  # only if empty DB
        demo = [
            ("Admin", "admin@event.com", "Admin@123", "admin"),
            ("Vendor A", "vendor@event.com", "Vendor@123", "vendor"),
            ("User A", "user@event.com", "User@1234", "user"),
        ]

        for name, email, password, role in demo:
            create_user(name, email, password, role)

        print("[OK] Demo data seeded")

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)