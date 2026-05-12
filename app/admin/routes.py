from flask import Blueprint, abort, flash, redirect, render_template, request, session, url_for

from app.admin.forms import MessageStatusForm, ProfileForm, SettingForm
from app.admin.resources import (
    RESOURCE_CONFIGS,
    build_insert_sql,
    build_update_sql,
    get_resource_config,
)
from app.auth.decorators import current_user_id, current_user_role, login_required
from app.db import execute, query_all, query_one
from app.services.upload_service import UploadError, save_upload

admin_bp = Blueprint("admin", __name__, url_prefix="/admin")
dashboard_bp = Blueprint("dashboard", __name__, url_prefix="/dashboard")


def current_area() -> str:
    return request.blueprint or "dashboard"


def scoped_user_id() -> int:
    user_id = current_user_id()
    if not user_id:
        abort(403)
    return user_id


def ensure_area_allowed() -> None:
    if current_area() == "admin" and current_user_role() != "admin":
        abort(403)


def is_admin_area() -> bool:
    return current_area() == "admin" and current_user_role() == "admin"


def scoped_where(owner_column: str = "user_id") -> tuple[str, tuple]:
    if is_admin_area():
        return "", ()
    return f" WHERE {owner_column} = %s", (scoped_user_id(),)


def endpoint(name: str) -> str:
    return f"{current_area()}.{name}"


def dashboard_counts() -> dict:
    where, params = scoped_where()
    return {
        "skills": query_one(f"SELECT COUNT(*) AS total FROM skills{where}", params)["total"],
        "projects": query_one(f"SELECT COUNT(*) AS total FROM projects{where}", params)["total"],
        "messages": query_one(
            f"SELECT COUNT(*) AS total FROM messages"
            f"{'' if is_admin_area() else ' WHERE target_user_id = %s'}",
            () if is_admin_area() else (scoped_user_id(),),
        )["total"],
        "unread_messages": query_one(
            "SELECT COUNT(*) AS total FROM messages WHERE status = 'unread'"
            + ("" if is_admin_area() else " AND target_user_id = %s"),
            () if is_admin_area() else (scoped_user_id(),),
        )["total"],
    }


def form_values(form, columns: tuple[str, ...]) -> list:
    values = []
    for column in columns:
        value = getattr(form, column).data
        if isinstance(value, bool):
            value = 1 if value else 0
        values.append(value)
    return values


def has_upload(file) -> bool:
    return bool(file and getattr(file, "filename", "").strip())


def record_upload(upload: dict) -> None:
    execute(
        """
        INSERT INTO uploads (
            original_filename, saved_filename, file_path, mime_type,
            file_size, upload_purpose, user_id
        )
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        """,
        (
            upload["original_filename"],
            upload["saved_filename"],
            upload["file_path"],
            upload["mime_type"],
            upload["file_size"],
            upload["upload_purpose"],
            scoped_user_id(),
        ),
    )


@admin_bp.route("")
@dashboard_bp.route("")
@login_required
def dashboard():
    ensure_area_allowed()
    if is_admin_area():
        recent_messages = query_all("SELECT * FROM messages ORDER BY created_at DESC LIMIT 5")
    else:
        recent_messages = query_all(
            "SELECT * FROM messages WHERE target_user_id = %s ORDER BY created_at DESC LIMIT 5",
            (scoped_user_id(),),
        )
    return render_template(
        "admin/dashboard.html",
        counts=dashboard_counts(),
        recent_messages=recent_messages,
    )


@admin_bp.route("/<resource>")
@dashboard_bp.route("/<resource>")
@login_required
def resource_list(resource):
    ensure_area_allowed()
    try:
        config = get_resource_config(resource)
    except KeyError:
        abort(404)
    where, params = scoped_where(config.owner_column)
    rows = query_all(
        f"SELECT * FROM {config.table}{where} ORDER BY sort_order ASC, id DESC",
        params,
    )
    return render_template("admin/resource_list.html", config=config, rows=rows)


@admin_bp.route("/<resource>/new", methods=["GET", "POST"])
@dashboard_bp.route("/<resource>/new", methods=["GET", "POST"])
@login_required
def resource_create(resource):
    ensure_area_allowed()
    try:
        config = get_resource_config(resource)
    except KeyError:
        abort(404)
    form = config.form_class()
    if form.validate_on_submit():
        execute(
            build_insert_sql(config),
            [scoped_user_id(), *form_values(form, config.columns)],
        )
        flash(f"{config.title}已创建。", "success")
        return redirect(url_for(endpoint("resource_list"), resource=resource))
    return render_template("admin/resource_form.html", config=config, form=form)


@admin_bp.route("/<resource>/<int:item_id>/edit", methods=["GET", "POST"])
@dashboard_bp.route("/<resource>/<int:item_id>/edit", methods=["GET", "POST"])
@login_required
def resource_edit(resource, item_id):
    ensure_area_allowed()
    try:
        config = get_resource_config(resource)
    except KeyError:
        abort(404)
    if is_admin_area():
        item = query_one(f"SELECT * FROM {config.table} WHERE id = %s", (item_id,))
    else:
        item = query_one(
            f"SELECT * FROM {config.table} WHERE id = %s AND {config.owner_column} = %s",
            (item_id, scoped_user_id()),
        )
    if not item:
        abort(404)
    form = config.form_class(data=item)
    if form.validate_on_submit():
        execute(
            build_update_sql(config),
            [*form_values(form, config.columns), item_id, item[config.owner_column]],
        )
        flash(f"{config.title}已保存。", "success")
        return redirect(url_for(endpoint("resource_list"), resource=resource))
    return render_template("admin/resource_form.html", config=config, form=form, item=item)


@admin_bp.route("/<resource>/<int:item_id>/delete", methods=["POST"])
@dashboard_bp.route("/<resource>/<int:item_id>/delete", methods=["POST"])
@login_required
def resource_delete(resource, item_id):
    ensure_area_allowed()
    try:
        config = get_resource_config(resource)
    except KeyError:
        abort(404)
    if is_admin_area():
        execute(f"DELETE FROM {config.table} WHERE id = %s", (item_id,))
    else:
        execute(
            f"DELETE FROM {config.table} WHERE id = %s AND {config.owner_column} = %s",
            (item_id, scoped_user_id()),
        )
    flash(f"{config.title}已删除。", "success")
    return redirect(url_for(endpoint("resource_list"), resource=resource))


@admin_bp.route("/profile", methods=["GET", "POST"])
@dashboard_bp.route("/profile", methods=["GET", "POST"])
@login_required
def profile():
    ensure_area_allowed()
    if is_admin_area():
        item = query_one("SELECT * FROM profile ORDER BY id ASC LIMIT 1") or {}
    else:
        item = query_one(
            "SELECT * FROM profile WHERE user_id = %s LIMIT 1",
            (scoped_user_id(),),
        ) or {}
    form = ProfileForm(data=item)
    if form.validate_on_submit():
        avatar_path = item.get("avatar_path")
        resume_file_path = item.get("resume_file_path")

        if has_upload(form.avatar.data):
            try:
                upload = save_upload(form.avatar.data, "avatar")
            except UploadError as exc:
                flash(str(exc), "danger")
                return render_template("admin/profile.html", form=form, item=item)
            record_upload(upload)
            avatar_path = upload["file_path"]

        if has_upload(form.resume_file.data):
            try:
                upload = save_upload(form.resume_file.data, "resume")
            except UploadError as exc:
                flash(str(exc), "danger")
                return render_template("admin/profile.html", form=form, item=item)
            record_upload(upload)
            resume_file_path = upload["file_path"]

        params = (
            form.name.data,
            form.title.data,
            form.city.data,
            form.email.data,
            form.phone.data,
            form.wechat.data,
            form.github_url.data,
            form.website_url.data,
            avatar_path,
            resume_file_path,
            form.summary.data,
            form.job_status.data,
            1 if form.is_active.data else 0,
        )

        if item.get("id"):
            execute(
                """
                UPDATE profile
                SET name = %s, title = %s, city = %s, email = %s, phone = %s,
                    wechat = %s, github_url = %s, website_url = %s,
                    avatar_path = %s, resume_file_path = %s, summary = %s,
                    job_status = %s, is_active = %s
                WHERE id = %s AND user_id = %s
                """,
                (*params, item["id"], item.get("user_id") or scoped_user_id()),
            )
        else:
            execute(
                """
                INSERT INTO profile (
                    user_id, name, title, city, email, phone, wechat, github_url,
                    website_url, avatar_path, resume_file_path, summary,
                    job_status, is_active
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """,
                (scoped_user_id(), *params),
            )

        flash("个人信息已保存。", "success")
        return redirect(url_for(endpoint("profile")))

    return render_template("admin/profile.html", form=form, item=item)


@admin_bp.route("/messages")
@dashboard_bp.route("/messages")
@login_required
def messages():
    ensure_area_allowed()
    if is_admin_area():
        rows = query_all("SELECT * FROM messages ORDER BY created_at DESC")
    else:
        rows = query_all(
            "SELECT * FROM messages WHERE target_user_id = %s ORDER BY created_at DESC",
            (scoped_user_id(),),
        )
    return render_template("admin/messages.html", rows=rows)


@admin_bp.route("/messages/<int:message_id>", methods=["GET", "POST"])
@dashboard_bp.route("/messages/<int:message_id>", methods=["GET", "POST"])
@login_required
def message_detail(message_id):
    ensure_area_allowed()
    if is_admin_area():
        item = query_one("SELECT * FROM messages WHERE id = %s", (message_id,))
    else:
        item = query_one(
            "SELECT * FROM messages WHERE id = %s AND target_user_id = %s",
            (message_id, scoped_user_id()),
        )
    if not item:
        abort(404)

    form = MessageStatusForm(data=item)
    if form.validate_on_submit():
        execute(
            "UPDATE messages SET status = %s, admin_note = %s "
            + ("WHERE id = %s" if is_admin_area() else "WHERE id = %s AND target_user_id = %s"),
            (
                (form.status.data, form.admin_note.data, message_id)
                if is_admin_area()
                else (form.status.data, form.admin_note.data, message_id, scoped_user_id())
            ),
        )
        flash("留言状态已更新。", "success")
        return redirect(url_for(endpoint("messages")))

    return render_template("admin/message_detail.html", item=item, form=form)


@admin_bp.route("/messages/<int:message_id>/delete", methods=["POST"])
@dashboard_bp.route("/messages/<int:message_id>/delete", methods=["POST"])
@login_required
def message_delete(message_id):
    ensure_area_allowed()
    if is_admin_area():
        execute("DELETE FROM messages WHERE id = %s", (message_id,))
    else:
        execute(
            "DELETE FROM messages WHERE id = %s AND target_user_id = %s",
            (message_id, scoped_user_id()),
        )
    flash("留言已删除。", "success")
    return redirect(url_for(endpoint("messages")))


@admin_bp.route("/settings", methods=["GET", "POST"])
@login_required
def settings():
    rows = query_all("SELECT setting_key, setting_value FROM site_settings")
    values = {row["setting_key"]: row.get("setting_value") or "" for row in rows}
    form = SettingForm(
        data={
            "site_title": values.get("site_title", "个人简历网站"),
            "seo_description": values.get("seo_description", ""),
            "icp_text": values.get("icp_text", ""),
            "messages_enabled": values.get("messages_enabled", "1") == "1",
        }
    )

    if form.validate_on_submit():
        pairs = {
            "site_title": form.site_title.data,
            "seo_description": form.seo_description.data,
            "icp_text": form.icp_text.data,
            "messages_enabled": "1" if form.messages_enabled.data else "0",
        }
        for key, value in pairs.items():
            execute(
                """
                INSERT INTO site_settings (setting_key, setting_value, setting_type)
                VALUES (%s, %s, %s)
                ON DUPLICATE KEY UPDATE
                    setting_value = VALUES(setting_value),
                    setting_type = VALUES(setting_type)
                """,
                (key, value, "boolean" if key == "messages_enabled" else "string"),
            )

        flash("站点设置已保存。", "success")
        return redirect(url_for("admin.settings"))

    return render_template("admin/settings.html", form=form)
