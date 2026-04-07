from functools import wraps

from flask import flash, redirect, request, session, url_for


ROLE_LOGIN_ROUTE = {
    "admin": "auth.admin_login",
    "vendor": "auth.vendor_login",
    "user": "auth.user_login",
}

ROLE_HOME_ROUTE = {
    "admin": "admin.dashboard",
    "vendor": "vendor.dashboard",
    "user": "user.dashboard",
}


def _safe_login_redirect(role=None):
    role_to_use = role or session.get("role")
    endpoint = ROLE_LOGIN_ROUTE.get(role_to_use, "auth.login_selector")
    return redirect(url_for(endpoint))


def _infer_role_from_path(path: str):
    if path.startswith("/admin"):
        return "admin"
    if path.startswith("/vendor"):
        return "vendor"
    if path.startswith("/user"):
        return "user"
    return None


def login_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if "user_id" not in session:
            flash("Please login to continue.", "warning")
            return _safe_login_redirect(_infer_role_from_path(request.path))
        return view(*args, **kwargs)

    return wrapped


def role_required(required_role):
    def decorator(view):
        @wraps(view)
        def wrapped(*args, **kwargs):
            if "user_id" not in session:
                return _safe_login_redirect(required_role)

            role = session.get("role")
            if role != required_role:
                flash("Unauthorized route for your role.", "danger")
                home_endpoint = ROLE_HOME_ROUTE.get(role)
                if home_endpoint:
                    return redirect(url_for(home_endpoint))
                return _safe_login_redirect()

            return view(*args, **kwargs)

        return wrapped

    return decorator


def route_on_error_for_role(role):
    endpoint = ROLE_LOGIN_ROUTE.get(role, "auth.login_selector")
    return redirect(url_for(endpoint))


def current_user_role():
    return session.get("role")


def current_user_id():
    return session.get("user_id")
