from collections import defaultdict

from flask import Blueprint, flash, redirect, render_template, request, url_for

from app.db import execute, query_all, query_one
from app.extensions import limiter
from app.public.forms import MessageForm

public_bp = Blueprint("public", __name__)


def get_settings() -> dict[str, str]:
    rows = query_all("SELECT setting_key, setting_value FROM site_settings")
    return {row["setting_key"]: row.get("setting_value") or "" for row in rows}


def messages_enabled() -> bool:
    return get_settings().get("messages_enabled", "1") == "1"


def group_skills(skills: list[dict]) -> dict[str, list[dict]]:
    grouped = defaultdict(list)
    for skill in skills:
        grouped[skill.get("category") or "其他"].append(skill)
    return dict(grouped)


def load_homepage_data() -> dict:
    profile = query_one(
        """
        SELECT name, title, city, email, phone, wechat, github_url, website_url,
               avatar_path, resume_file_path, summary, job_status
        FROM profile
        WHERE is_active = 1
        ORDER BY id ASC
        LIMIT 1
        """
    )
    skills = query_all(
        """
        SELECT name, category, proficiency, icon, color
        FROM skills
        WHERE is_active = 1
        ORDER BY sort_order ASC, id ASC
        """
    )
    experiences = query_all(
        """
        SELECT company, position, location, start_date, end_date, is_current, description
        FROM experiences
        WHERE is_active = 1
        ORDER BY sort_order ASC, start_date DESC, id ASC
        """
    )
    projects = query_all(
        """
        SELECT name, role, tech_stack, project_url, source_url, cover_image_path,
               start_date, end_date, summary, highlights
        FROM projects
        WHERE is_active = 1
        ORDER BY sort_order ASC, start_date DESC, id ASC
        """
    )
    education = query_all(
        """
        SELECT school, major, degree, location, start_date, end_date, description
        FROM education
        WHERE is_active = 1
        ORDER BY sort_order ASC, start_date DESC, id ASC
        """
    )
    certificates = query_all(
        """
        SELECT name, issuer, issue_date, certificate_url, image_path, description
        FROM certificates
        WHERE is_active = 1
        ORDER BY sort_order ASC, issue_date DESC, id ASC
        """
    )

    return {
        "profile": profile or {},
        "skills_by_category": group_skills(skills),
        "experiences": experiences,
        "projects": projects,
        "education": education,
        "certificates": certificates,
        "settings": get_settings(),
    }


@public_bp.route("/")
def index():
    data = load_homepage_data()
    return render_template("public/index.html", form=MessageForm(), **data)


@public_bp.route("/messages", methods=["POST"])
@limiter.limit("3 per minute")
def submit_message():
    if not messages_enabled():
        flash("留言功能暂未开放。", "warning")
        return redirect(url_for("public.index") + "#contact")

    form = MessageForm()
    if not form.validate_on_submit():
        flash("请检查留言内容后再提交。", "danger")
        return redirect(url_for("public.index") + "#contact")

    forwarded_for = request.headers.get("X-Forwarded-For", "")
    ip_address = forwarded_for.split(",", 1)[0].strip() or request.remote_addr
    user_agent = (request.headers.get("User-Agent") or "")[:512]
    phone = form.phone.data.strip() if form.phone.data else None

    execute(
        """
        INSERT INTO messages (name, email, phone, content, ip_address, user_agent)
        VALUES (%s, %s, %s, %s, %s, %s)
        """,
        (
            form.name.data.strip(),
            form.email.data.strip(),
            phone,
            form.content.data.strip(),
            ip_address,
            user_agent,
        ),
    )
    flash("留言已提交，我会尽快回复。", "success")
    return redirect(url_for("public.index") + "#contact")
