from flask import Blueprint, abort, flash, redirect, render_template, request, url_for

from app.admin.forms import (
    AccountStatusForm,
    MessageStatusForm,
    ProfileForm,
    PublishStatusForm,
    ResumeBlockForm,
    SettingForm,
)
from app.admin.resources import (
    RESOURCE_CONFIGS,
    build_insert_sql,
    build_update_sql,
    get_resource_config,
)
from app.auth.decorators import (
    current_user_id,
    is_super_admin,
    login_required,
    super_admin_required,
)
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
    if current_area() == "admin" and not is_super_admin():
        abort(403)


def is_admin_area() -> bool:
    return current_area() == "admin" and is_super_admin()


def scoped_where(owner_column: str = "user_id") -> tuple[str, tuple]:
    if is_admin_area():
        return "", ()
    return f" WHERE {owner_column} = %s", (scoped_user_id(),)


def endpoint(name: str) -> str:
    return f"{current_area()}.{name}"


def dashboard_counts() -> dict:
    if is_admin_area():
        return {
            "users": query_one(
                "SELECT COUNT(*) AS total FROM users WHERE role = 'user'"
            )["total"],
            "active_users": query_one(
                """
                SELECT COUNT(*) AS total
                FROM users
                WHERE role = 'user' AND is_active = 1
                """
            )["total"],
            "banned_users": query_one(
                """
                SELECT COUNT(*) AS total
                FROM users
                WHERE role = 'user' AND is_active = 0
                """
            )["total"],
            "public_resumes": query_one(
                """
                SELECT COUNT(*) AS total
                FROM profile AS p
                INNER JOIN users AS u ON u.id = p.user_id
                WHERE u.role = 'user'
                  AND u.is_active = 1
                  AND u.can_publish = 1
                  AND p.is_active = 1
                  AND p.is_public_blocked = 0
                """
            )["total"],
            "blocked_resumes": query_one(
                """
                SELECT COUNT(*) AS total
                FROM profile AS p
                INNER JOIN users AS u ON u.id = p.user_id
                WHERE u.role = 'user' AND p.is_public_blocked = 1
                """
            )["total"],
            "messages": query_one("SELECT COUNT(*) AS total FROM messages")["total"],
            "unread_messages": query_one(
                "SELECT COUNT(*) AS total FROM messages WHERE status = 'unread'"
            )["total"],
        }

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


def managed_user_or_404(user_id: int) -> dict:
    user = query_one(
        """
        SELECT id, username, email, display_name, role, is_active, can_publish,
               ban_reason, publish_ban_reason, last_login_at, created_at
        FROM users
        WHERE id = %s
        LIMIT 1
        """,
        (user_id,),
    )
    if not user:
        abort(404)
    if user.get("role") == "super_admin":
        abort(403)
    return user


def user_profile_status(user_id: int) -> dict:
    return query_one(
        """
        SELECT id, name, title, is_active, is_public_blocked, public_block_reason
        FROM profile
        WHERE user_id = %s
        LIMIT 1
        """,
        (user_id,),
    ) or {}


def clean_reason(value: str | None) -> str | None:
    reason = (value or "").strip()
    return reason or None


def current_publish_policy() -> dict:
    if is_admin_area():
        return {"can_publish": 1, "publish_ban_reason": None}
    policy = query_one(
        """
        SELECT can_publish, publish_ban_reason
        FROM users
        WHERE id = %s
        LIMIT 1
        """,
        (scoped_user_id(),),
    ) or {}
    can_publish = policy.get("can_publish")
    if can_publish is None:
        can_publish = 1
    return {
        "can_publish": int(can_publish),
        "publish_ban_reason": policy.get("publish_ban_reason"),
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
        recent_users = query_all(
            """
            SELECT id, username, display_name, email, is_active, can_publish, created_at
            FROM users
            WHERE role = 'user'
            ORDER BY created_at DESC, id DESC
            LIMIT 5
            """
        )
    else:
        recent_messages = query_all(
            "SELECT * FROM messages WHERE target_user_id = %s ORDER BY created_at DESC LIMIT 5",
            (scoped_user_id(),),
        )
        recent_users = []
    return render_template(
        "admin/dashboard.html",
        counts=dashboard_counts(),
        recent_messages=recent_messages,
        recent_users=recent_users,
    )


@admin_bp.route("/users")
@super_admin_required
def users():
    keyword = request.args.get("q", "").strip()
    status = request.args.get("status", "").strip()
    where = ["u.role = 'user'"]
    params: list[str] = []

    if keyword:
        like = f"%{keyword}%"
        where.append(
            "(u.username LIKE %s OR u.email LIKE %s OR u.display_name LIKE %s)"
        )
        params.extend([like, like, like])
    if status == "active":
        where.append("u.is_active = 1")
    elif status == "banned":
        where.append("u.is_active = 0")
    elif status == "publish_banned":
        where.append("u.can_publish = 0")
    elif status == "resume_blocked":
        where.append("COALESCE(p.is_public_blocked, 0) = 1")

    rows = query_all(
        f"""
        SELECT u.id, u.username, u.email, u.display_name, u.is_active,
               u.can_publish, u.created_at, u.last_login_at,
               COALESCE(p.is_public_blocked, 0) AS is_public_blocked,
               p.is_active AS profile_is_active
        FROM users AS u
        LEFT JOIN profile AS p ON p.user_id = u.id
        WHERE {' AND '.join(where)}
        ORDER BY u.created_at DESC, u.id DESC
        """,
        tuple(params),
    )
    return render_template(
        "admin/users.html",
        rows=rows,
        keyword=keyword,
        status=status,
    )


@admin_bp.route("/users/<int:user_id>")
@super_admin_required
def user_detail(user_id):
    user = managed_user_or_404(user_id)
    profile_status = user_profile_status(user_id)
    recent_messages = query_all(
        "SELECT * FROM messages WHERE target_user_id = %s ORDER BY created_at DESC LIMIT 5",
        (user_id,),
    )
    return render_template(
        "admin/user_detail.html",
        user=user,
        profile_status=profile_status,
        recent_messages=recent_messages,
        account_form=AccountStatusForm(
            data={
                "is_active": int(user.get("is_active") or 0) == 1,
                "ban_reason": user.get("ban_reason") or "",
            }
        ),
        publish_form=PublishStatusForm(
            data={
                "can_publish": int(user.get("can_publish") or 0) == 1,
                "publish_ban_reason": user.get("publish_ban_reason") or "",
            }
        ),
        resume_form=ResumeBlockForm(
            data={
                "is_public_blocked": int(
                    profile_status.get("is_public_blocked") or 0
                )
                == 1,
                "public_block_reason": profile_status.get("public_block_reason") or "",
            }
        ),
    )


@admin_bp.route("/users/<int:user_id>/account-status", methods=["POST"])
@super_admin_required
def user_account_status(user_id):
    managed_user_or_404(user_id)
    form = AccountStatusForm()
    if not form.validate_on_submit():
        abort(400)
    is_active = 1 if form.is_active.data else 0
    ban_reason = None if is_active else clean_reason(form.ban_reason.data)
    execute(
        "UPDATE users SET is_active = %s, ban_reason = %s WHERE id = %s",
        (is_active, ban_reason, user_id),
    )
    flash("账号状态已更新。", "success")
    return redirect(url_for("admin.user_detail", user_id=user_id))


@admin_bp.route("/users/<int:user_id>/publish-status", methods=["POST"])
@super_admin_required
def user_publish_status(user_id):
    managed_user_or_404(user_id)
    form = PublishStatusForm()
    if not form.validate_on_submit():
        abort(400)
    can_publish = 1 if form.can_publish.data else 0
    publish_ban_reason = (
        None if can_publish else clean_reason(form.publish_ban_reason.data)
    )
    execute(
        """
        UPDATE users
        SET can_publish = %s, publish_ban_reason = %s
        WHERE id = %s
        """,
        (can_publish, publish_ban_reason, user_id),
    )
    flash("发布权限已更新。", "success")
    return redirect(url_for("admin.user_detail", user_id=user_id))


@admin_bp.route("/users/<int:user_id>/resume-status", methods=["POST"])
@super_admin_required
def user_resume_status(user_id):
    managed_user_or_404(user_id)
    form = ResumeBlockForm()
    if not form.validate_on_submit():
        abort(400)
    is_public_blocked = 1 if form.is_public_blocked.data else 0
    public_block_reason = (
        clean_reason(form.public_block_reason.data) if is_public_blocked else None
    )
    execute(
        """
        UPDATE profile
        SET is_public_blocked = %s, public_block_reason = %s
        WHERE user_id = %s
        """,
        (is_public_blocked, public_block_reason, user_id),
    )
    flash("公开简历状态已更新。", "success")
    return redirect(url_for("admin.user_detail", user_id=user_id))


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
    publish_policy = current_publish_policy()
    form = ProfileForm(data=item)
    if form.validate_on_submit():
        avatar_path = item.get("avatar_path")
        resume_file_path = item.get("resume_file_path")

        if has_upload(form.avatar.data):
            try:
                upload = save_upload(form.avatar.data, "avatar")
            except UploadError as exc:
                flash(str(exc), "danger")
                return render_template(
                    "admin/profile.html",
                    form=form,
                    item=item,
                    publish_policy=publish_policy,
                )
            record_upload(upload)
            avatar_path = upload["file_path"]

        if has_upload(form.resume_file.data):
            try:
                upload = save_upload(form.resume_file.data, "resume")
            except UploadError as exc:
                flash(str(exc), "danger")
                return render_template(
                    "admin/profile.html",
                    form=form,
                    item=item,
                    publish_policy=publish_policy,
                )
            record_upload(upload)
            resume_file_path = upload["file_path"]

        is_active = 1 if form.is_active.data else 0
        if not is_admin_area() and int(publish_policy.get("can_publish") or 0) != 1:
            if is_active:
                flash("当前账号已被禁止发布，不能公开简历。", "warning")
            is_active = 0

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
            is_active,
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

    return render_template(
        "admin/profile.html",
        form=form,
        item=item,
        publish_policy=publish_policy,
    )


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
@super_admin_required
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
