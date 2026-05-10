from flask import Blueprint, abort, flash, redirect, render_template, session, url_for

from app.admin.forms import MessageStatusForm, ProfileForm, SettingForm
from app.admin.resources import (
    RESOURCE_CONFIGS,
    build_insert_sql,
    build_update_sql,
    get_resource_config,
)
from app.auth.decorators import login_required
from app.db import execute, query_all, query_one
from app.services.upload_service import UploadError, save_upload

admin_bp = Blueprint("admin", __name__, url_prefix="/admin")


def dashboard_counts() -> dict:
    return {
        "skills": query_one("SELECT COUNT(*) AS total FROM skills")["total"],
        "projects": query_one("SELECT COUNT(*) AS total FROM projects")["total"],
        "messages": query_one("SELECT COUNT(*) AS total FROM messages")["total"],
        "unread_messages": query_one(
            "SELECT COUNT(*) AS total FROM messages WHERE status = 'unread'"
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
            file_size, upload_purpose, uploader_id
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
            session.get("admin_user_id"),
        ),
    )


@admin_bp.route("")
@login_required
def dashboard():
    recent_messages = query_all("SELECT * FROM messages ORDER BY created_at DESC LIMIT 5")
    return render_template(
        "admin/dashboard.html",
        counts=dashboard_counts(),
        recent_messages=recent_messages,
    )


@admin_bp.route("/<resource>")
@login_required
def resource_list(resource):
    try:
        config = get_resource_config(resource)
    except KeyError:
        abort(404)
    rows = query_all(f"SELECT * FROM {config.table} ORDER BY sort_order ASC, id DESC")
    return render_template("admin/resource_list.html", config=config, rows=rows)


@admin_bp.route("/<resource>/new", methods=["GET", "POST"])
@login_required
def resource_create(resource):
    try:
        config = get_resource_config(resource)
    except KeyError:
        abort(404)
    form = config.form_class()
    if form.validate_on_submit():
        execute(build_insert_sql(config), form_values(form, config.columns))
        flash(f"{config.title}已创建。", "success")
        return redirect(url_for("admin.resource_list", resource=resource))
    return render_template("admin/resource_form.html", config=config, form=form)


@admin_bp.route("/<resource>/<int:item_id>/edit", methods=["GET", "POST"])
@login_required
def resource_edit(resource, item_id):
    try:
        config = get_resource_config(resource)
    except KeyError:
        abort(404)
    item = query_one(f"SELECT * FROM {config.table} WHERE id = %s", (item_id,))
    if not item:
        abort(404)
    form = config.form_class(data=item)
    if form.validate_on_submit():
        execute(build_update_sql(config), [*form_values(form, config.columns), item_id])
        flash(f"{config.title}已保存。", "success")
        return redirect(url_for("admin.resource_list", resource=resource))
    return render_template("admin/resource_form.html", config=config, form=form, item=item)


@admin_bp.route("/<resource>/<int:item_id>/delete", methods=["POST"])
@login_required
def resource_delete(resource, item_id):
    try:
        config = get_resource_config(resource)
    except KeyError:
        abort(404)
    execute(f"DELETE FROM {config.table} WHERE id = %s", (item_id,))
    flash(f"{config.title}已删除。", "success")
    return redirect(url_for("admin.resource_list", resource=resource))


@admin_bp.route("/profile", methods=["GET", "POST"])
@login_required
def profile():
    item = query_one("SELECT * FROM profile ORDER BY id ASC LIMIT 1") or {}
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
                WHERE id = %s
                """,
                (*params, item["id"]),
            )
        else:
            execute(
                """
                INSERT INTO profile (
                    name, title, city, email, phone, wechat, github_url,
                    website_url, avatar_path, resume_file_path, summary,
                    job_status, is_active
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """,
                params,
            )

        flash("个人信息已保存。", "success")
        return redirect(url_for("admin.profile"))

    return render_template("admin/profile.html", form=form, item=item)


@admin_bp.route("/messages")
@login_required
def messages():
    rows = query_all("SELECT * FROM messages ORDER BY created_at DESC")
    return render_template("admin/messages.html", rows=rows)


@admin_bp.route("/messages/<int:message_id>", methods=["GET", "POST"])
@login_required
def message_detail(message_id):
    item = query_one("SELECT * FROM messages WHERE id = %s", (message_id,))
    if not item:
        abort(404)

    form = MessageStatusForm(data=item)
    if form.validate_on_submit():
        execute(
            "UPDATE messages SET status = %s, admin_note = %s WHERE id = %s",
            (form.status.data, form.admin_note.data, message_id),
        )
        flash("留言状态已更新。", "success")
        return redirect(url_for("admin.messages"))

    return render_template("admin/message_detail.html", item=item, form=form)


@admin_bp.route("/messages/<int:message_id>/delete", methods=["POST"])
@login_required
def message_delete(message_id):
    execute("DELETE FROM messages WHERE id = %s", (message_id,))
    flash("留言已删除。", "success")
    return redirect(url_for("admin.messages"))


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
