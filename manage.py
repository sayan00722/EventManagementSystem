import argparse
import os
import subprocess
import sys
from pathlib import Path

from app import create_app
from app.extensions import db
from app.models.models import User, Vendor
from app.services.auth_service import create_user

ROOT = Path(__file__).resolve().parent


def create_admin_command(args) -> int:
    app = create_app()
    with app.app_context():
        user, error = create_user(args.name, args.email, args.password, "admin")
        if error:
            print(f"[ERROR] {error}")
            return 1

        print(f"[OK] Admin created: {user.email} (id={user.id})")
        return 0


def init_db_command(_args) -> int:
    app = create_app()
    with app.app_context():
        db.create_all()
    print("[OK] Database tables initialized.")
    return 0


def seed_demo_command(_args) -> int:
    app = create_app()
    with app.app_context():
        demo = [
            ("Admin", "admin@event.com", "Admin@123", "admin"),
            ("Vendor A", "vendor@event.com", "Vendor@123", "vendor"),
            ("User A", "user@event.com", "User@1234", "user"),
        ]

        created = 0
        for name, email, password, role in demo:
            if User.query.filter_by(email=email, role=role).first():
                continue
            user, error = create_user(name, email, password, role)
            if error:
                print(f"[WARN] {email}: {error}")
                continue
            created += 1

            if role == "vendor" and not Vendor.query.filter_by(user_id=user.id).first():
                vendor = Vendor(
                    user_id=user.id,
                    name=name,
                    category="Catering",
                    contact="9876543210",
                )
                db.session.add(vendor)
                db.session.commit()

    print(f"[OK] Seed complete. New accounts created: {created}")
    return 0


def apply_sql_command(args) -> int:
    schema = (ROOT / "sql" / "schema.sql").as_posix()
    seed = (ROOT / "sql" / "seed.sql").as_posix()

    base = [
        "mysql",
        "-h",
        args.db_host,
        "-P",
        str(args.db_port),
        "-u",
        args.db_user,
        f"-p{args.db_secret}",
    ]

    schema_cmd = base + ["-e", f"source {schema};"]
    seed_cmd = base + ["-e", f"source {seed};"]

    try:
        subprocess.run(schema_cmd, check=True)
        subprocess.run(seed_cmd, check=True)
    except subprocess.CalledProcessError as exc:
        print(f"[ERROR] SQL apply failed: {exc}")
        return 1

    print("[OK] Schema and seed applied.")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Event Management CLI")
    sub = parser.add_subparsers(dest="command", required=True)

    create_admin = sub.add_parser("create-admin", help="Create admin account")
    create_admin.add_argument("--name", required=True)
    create_admin.add_argument("--email", required=True)
    create_admin.add_argument("--password", required=True)
    create_admin.set_defaults(func=create_admin_command)

    init_db = sub.add_parser("init-db", help="Create DB tables via SQLAlchemy")
    init_db.set_defaults(func=init_db_command)

    seed_demo = sub.add_parser("seed-demo", help="Seed demo users")
    seed_demo.set_defaults(func=seed_demo_command)

    apply_sql = sub.add_parser("apply-sql", help="Run schema.sql and seed.sql using mysql client")
    apply_sql.add_argument("--db-user", required=True)
    apply_sql.add_argument("--db-secret", required=True)
    apply_sql.add_argument("--db-host", default="localhost")
    apply_sql.add_argument("--db-port", type=int, default=3306)
    apply_sql.set_defaults(func=apply_sql_command)

    args = parser.parse_args()

    os.environ.setdefault("FLASK_APP", "run.py")
    os.environ.setdefault("FLASK_ENV", "development")
    os.environ.setdefault("SECRET_KEY", "sayan_secret_event_2026")

    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
