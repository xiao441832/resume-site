from functools import wraps

from flask import abort, flash, redirect, session, url_for


def current_user_id() -> int | None:
    user_id = session.get("user_id") or session.get("admin_user_id")
    return int(user_id) if user_id else None


def current_user_role() -> str:
    return session.get("role") or ("admin" if session.get("admin_user_id") else "")


def is_super_admin() -> bool:
    return current_user_role() == "super_admin"


def login_required(view):
    @wraps(view)
    def wrapped_view(*args, **kwargs):
        if not current_user_id():
            flash("请先登录。", "warning")
            return redirect(url_for("auth.login"))
        return view(*args, **kwargs)

    return wrapped_view


def admin_required(view):
    @wraps(view)
    def wrapped_view(*args, **kwargs):
        if not current_user_id():
            flash("请先登录。", "warning")
            return redirect(url_for("auth.login"))
        if not is_super_admin():
            abort(403)
        return view(*args, **kwargs)

    return wrapped_view


def super_admin_required(view):
    @wraps(view)
    def wrapped_view(*args, **kwargs):
        if not current_user_id():
            flash("请先登录。", "warning")
            return redirect(url_for("auth.login"))
        if not is_super_admin():
            abort(403)
        return view(*args, **kwargs)

    return wrapped_view
