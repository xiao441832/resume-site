from functools import wraps

from flask import flash, redirect, session, url_for


def login_required(view):
    @wraps(view)
    def wrapped_view(*args, **kwargs):
        if not session.get("admin_user_id"):
            flash("请先登录后台。", "warning")
            return redirect(url_for("auth.login"))
        return view(*args, **kwargs)

    return wrapped_view
