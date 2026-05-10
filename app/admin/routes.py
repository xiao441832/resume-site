from flask import Blueprint, abort, flash, redirect, render_template, url_for

from app.admin.resources import (
    RESOURCE_CONFIGS,
    build_insert_sql,
    build_update_sql,
    get_resource_config,
)
from app.auth.decorators import login_required
from app.db import execute, query_all, query_one

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
