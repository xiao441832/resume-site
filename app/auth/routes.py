from flask import Blueprint, flash, redirect, render_template, session, url_for
from werkzeug.security import check_password_hash

from app.auth.forms import LoginForm
from app.db import execute, query_one
from app.extensions import limiter

auth_bp = Blueprint("auth", __name__, url_prefix="/admin")


def find_admin_by_username(username: str):
    return query_one(
        """
        SELECT id, username, password_hash, display_name, is_active
        FROM admin_users
        WHERE username = %s
        LIMIT 1
        """,
        (username,),
    )


def mark_last_login(admin_id: int) -> None:
    execute("UPDATE admin_users SET last_login_at = NOW() WHERE id = %s", (admin_id,))


@auth_bp.route("/login", methods=["GET", "POST"])
@limiter.limit("5 per minute")
def login():
    form = LoginForm()
    if form.validate_on_submit():
        admin = find_admin_by_username(form.username.data.strip())
        password_ok = bool(admin) and check_password_hash(
            admin["password_hash"], form.password.data
        )
        active_ok = bool(admin) and int(admin["is_active"]) == 1

        if password_ok and active_ok:
            session.clear()
            session["admin_user_id"] = admin["id"]
            session["admin_username"] = admin["username"]
            session["admin_display_name"] = admin["display_name"]
            mark_last_login(admin["id"])
            flash("登录成功。", "success")
            return redirect("/admin")

        flash("用户名或密码错误。", "danger")

    return render_template("auth/login.html", form=form)


@auth_bp.route("/logout", methods=["POST"])
def logout():
    session.clear()
    flash("已退出登录。", "success")
    return redirect(url_for("auth.login"))
