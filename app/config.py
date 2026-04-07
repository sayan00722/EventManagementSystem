import os


class Config:
    _raw_db_url = os.getenv(
        "DATABASE_URL",
        "mysql+pymysql://root:sayan1234@localhost:3306/event_management",
    )
    if _raw_db_url.startswith("mysql://"):
        _raw_db_url = _raw_db_url.replace("mysql://", "mysql+pymysql://", 1)

    SECRET_KEY = os.getenv("SECRET_KEY", "sayan_secret_event_2026")
    SQLALCHEMY_DATABASE_URI = _raw_db_url
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    _mysql_ssl_enabled = os.getenv("MYSQL_SSL", "false").strip().lower() in {"1", "true", "yes", "on"}
    _mysql_ssl_ca = os.getenv("MYSQL_SSL_CA", "").strip()
    if _mysql_ssl_enabled and SQLALCHEMY_DATABASE_URI.startswith("mysql+pymysql://"):
        if _mysql_ssl_ca:
            SQLALCHEMY_ENGINE_OPTIONS = {"connect_args": {"ssl": {"ca": _mysql_ssl_ca}}}
        else:
            SQLALCHEMY_ENGINE_OPTIONS = {"connect_args": {"ssl": {}}}

    DEBUG = os.getenv("FLASK_ENV", "development") == "development"

    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"
    SESSION_COOKIE_SECURE = False

    WTF_CSRF_TIME_LIMIT = None
    MAX_CONTENT_LENGTH = 8 * 1024 * 1024
