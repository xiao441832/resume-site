from flask import Blueprint, flash, redirect, render_template, session, url_for
from werkzeug.security import check_password_hash, generate_password_hash

from app.auth.forms import LoginForm, RegisterForm
from app.db import execute, query_one
from app.extensions import limiter

auth_bp = Blueprint("auth", __name__)


def find_user_by_login(login_name: str):
    return query_one(
        """
        SELECT id, username, email, password_hash, display_name, role, is_active
        FROM users
        WHERE username = %s OR email = %s
        LIMIT 1
        """,
        (login_name, login_name),
    )


def find_user_by_username(username: str):
    return query_one(
        "SELECT id, username FROM users WHERE username = %s LIMIT 1",
        (username,),
    )


def find_user_by_email(email: str):
    return query_one(
        "SELECT id, email FROM users WHERE email = %s LIMIT 1",
        (email,),
    )


def mark_last_login(user_id: int) -> None:
    execute("UPDATE users SET last_login_at = NOW() WHERE id = %s", (user_id,))


def create_normal_user(
    username: str, email: str, display_name: str, password: str
) -> None:
    execute(
        """
        INSERT INTO users (
            username, email, password_hash, display_name, role, is_active
        )
        VALUES (%s, %s, %s, %s, %s, 1)
        """,
        (username, email, generate_password_hash(password), display_name, "user"),
    )


def set_login_session(user: dict) -> None:
    session.clear()
    session["user_id"] = user["id"]
    session["username"] = user["username"]
    session["display_name"] = user["display_name"]
    session["role"] = user["role"]

    # 兼容旧后台模板和测试，后续后台重构完成后可以移除这些键。
    if user["role"] == "super_admin":
        session["admin_user_id"] = user["id"]
        session["admin_username"] = user["username"]
        session["admin_display_name"] = user["display_name"]


@auth_bp.route("/auth/register", methods=["GET", "POST"])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        username = form.username.data.strip()
        email = form.email.data.strip().lower()
        display_name = form.display_name.data.strip()

        if find_user_by_username(username):
            flash("用户名已存在，请更换后再注册。", "danger")
            return render_template("auth/register.html", form=form)
        if find_user_by_email(email):
            flash("邮箱已被注册，请更换后再注册。", "danger")
            return render_template("auth/register.html", form=form)

        create_normal_user(username, email, display_name, form.password.data)
        flash("注册成功，请登录。", "success")
        return redirect(url_for("auth.login"))

    return render_template("auth/register.html", form=form)


@auth_bp.route("/auth/login", methods=["GET", "POST"])
@limiter.limit("5 per minute")
def login():
    form = LoginForm()
    if form.validate_on_submit():
        login_name = form.username.data.strip()
        user = find_user_by_login(login_name)
        password_ok = bool(user) and check_password_hash(
            user["password_hash"], form.password.data
        )

        if password_ok and int(user["is_active"]) != 1:
            flash("账号已被禁用，请联系管理员。", "danger")
            return render_template("auth/login.html", form=form)

        if password_ok:
            set_login_session(user)
            mark_last_login(user["id"])
            flash("登录成功。", "success")
            if user["role"] == "super_admin":
                return redirect(url_for("admin.dashboard"))
            return redirect("/dashboard")

        flash("用户名或密码错误。", "danger")

    return render_template("auth/login.html", form=form)


@auth_bp.route("/admin/login")
def legacy_admin_login():
    return redirect(url_for("auth.login"))


@auth_bp.route("/auth/logout", methods=["POST"])
def logout():
    session.clear()
    flash("已退出登录。", "success")
    return redirect(url_for("auth.login"))
