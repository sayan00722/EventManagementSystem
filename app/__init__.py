import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path
from urllib.parse import urlparse

from flask import Flask, redirect, render_template, request, session, url_for
import pymysql
from sqlalchemy import text

from app.config import Config
from app.extensions import bcrypt, csrf, db, migrate


def _configure_logging(app: Flask) -> None:
    log_dir = Path(app.root_path).parent / "logs"
    log_dir.mkdir(parents=True, exist_ok=True)
    log_file = log_dir / "event_management.log"

    handler = RotatingFileHandler(log_file, maxBytes=1024 * 1024, backupCount=3)
    handler.setFormatter(
        logging.Formatter("%(asctime)s [%(levelname)s] %(name)s %(message)s")
    )

    app.logger.setLevel(logging.INFO)
    app.logger.addHandler(handler)


def _ensure_database_exists(app: Flask) -> None:
    db_url = app.config.get("SQLALCHEMY_DATABASE_URI", "")
    if not db_url.startswith("mysql+pymysql://"):
        return

    parsed = urlparse(db_url.replace("mysql+pymysql://", "mysql://", 1))
    db_name = (parsed.path or "").lstrip("/")
    if not db_name:
        return

    connection = None
    try:
        connection = pymysql.connect(
            host=parsed.hostname,
            port=parsed.port or 3306,
            user=parsed.username,
            password=parsed.password,
            charset="utf8mb4",
            autocommit=True,
        )
        with connection.cursor() as cursor:
            cursor.execute(f"CREATE DATABASE IF NOT EXISTS `{db_name}` CHARACTER SET utf8mb4")
        app.logger.info("Database ensured: %s", db_name)
    except Exception:
        app.logger.exception("Failed to ensure database exists")
    finally:
        if connection:
            connection.close()


def create_app() -> Flask:
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    migrate.init_app(app, db)
    bcrypt.init_app(app)
    csrf.init_app(app)

    _configure_logging(app)
    _ensure_database_exists(app)

    from app.routes.admin_routes import admin_bp
    from app.routes.auth_routes import auth_bp
    from app.routes.user_routes import user_bp
    from app.routes.vendor_routes import vendor_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(user_bp)
    app.register_blueprint(vendor_bp)

    @app.get("/")
    def index():
        return redirect(url_for("auth.login_selector"))

    @app.errorhandler(400)
    def handle_400(error):
        return render_template("errors/error.html", code=400, message="Bad request."), 400

    @app.errorhandler(403)
    def handle_403(error):
        return render_template("errors/error.html", code=403, message="Access denied."), 403

    @app.errorhandler(404)
    def handle_404(error):
        return render_template("errors/error.html", code=404, message="Page not found."), 404

    @app.errorhandler(500)
    def handle_500(error):
        role = session.get("role")
        if role == "admin":
            safe_target = url_for("admin.dashboard")
        elif role == "vendor":
            safe_target = url_for("vendor.dashboard")
        elif role == "user":
            safe_target = url_for("user.dashboard")
        else:
            safe_target = url_for("auth.login_selector")

        app.logger.exception("Unhandled server error on %s", request.path)
        return (
            render_template(
                "errors/error.html",
                code=500,
                message="Unexpected error. You can safely continue.",
                safe_target=safe_target,
            ),
            500,
        )

    with app.app_context():
        from app.models import models  # noqa: F401

        try:
            db.create_all()
            exists_result = db.session.execute(
                text(
                    """
                    SELECT COUNT(*)
                    FROM information_schema.COLUMNS
                    WHERE TABLE_SCHEMA = DATABASE()
                      AND TABLE_NAME = 'vendors'
                      AND COLUMN_NAME = 'sell_items'
                    """
                )
            )
            if (exists_result.scalar() or 0) == 0:
                db.session.execute(text("ALTER TABLE vendors ADD COLUMN sell_items VARCHAR(500) NULL"))
                db.session.commit()
        except Exception:
            app.logger.exception("Database initialization failed; app started in safe mode")

    return app
