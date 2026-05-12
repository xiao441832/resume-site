from collections import defaultdict
from urllib.parse import urlparse

from flask import Blueprint, abort, flash, redirect, render_template, request, url_for

from app.db import execute, query_all, query_one
from app.extensions import limiter
from app.public.forms import MessageForm

public_bp = Blueprint("public", __name__)
SAFE_LINK_SCHEMES = {"http", "https", "mailto"}


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


@public_bp.app_template_global()
def static_upload_url(path: str | None) -> str:
    cleaned = (path or "").strip().replace("\\", "/").lstrip("/")
    parsed = urlparse(cleaned)
    if not cleaned or parsed.scheme or cleaned.startswith("//"):
        return ""
    if cleaned.startswith("static/"):
        cleaned = cleaned.removeprefix("static/")
    return url_for("static", filename=cleaned)


@public_bp.app_template_global()
def safe_public_url(url: str | None) -> str:
    value = (url or "").strip()
    parsed = urlparse(value)
    if parsed.scheme.lower() in SAFE_LINK_SCHEMES and parsed.netloc:
        return value
    return ""


def load_public_resumes(keyword: str = "") -> list[dict]:
    keyword = keyword.strip()
    params: list[str] = []
    search_sql = ""
    if keyword:
        like = f"%{keyword}%"
        search_sql = """
            AND (
                u.username LIKE %s OR u.display_name LIKE %s OR p.name LIKE %s
                OR p.title LIKE %s OR p.city LIKE %s OR p.summary LIKE %s
            )
        """
        params.extend([like, like, like, like, like, like])

    return query_all(
        f"""
        SELECT u.username, u.display_name, p.name, p.title, p.city,
               p.summary, p.avatar_path
        FROM users AS u
        INNER JOIN profile AS p ON p.user_id = u.id
        WHERE u.is_active = 1
          AND u.role = 'user'
          AND u.can_publish = 1
          AND p.is_active = 1
          AND p.is_public_blocked = 0
          {search_sql}
        ORDER BY u.created_at DESC, u.id DESC
        """,
        tuple(params),
    )


def find_public_user(username: str) -> dict | None:
    return query_one(
        """
        SELECT u.id, u.username, u.display_name
        FROM users AS u
        INNER JOIN profile AS p ON p.user_id = u.id
        WHERE u.username = %s
          AND u.is_active = 1
          AND u.role = 'user'
          AND u.can_publish = 1
          AND p.is_active = 1
          AND p.is_public_blocked = 0
        LIMIT 1
        """,
        (username,),
    )


def load_user_resume_data(username: str) -> dict | None:
    owner = find_public_user(username)
    if not owner:
        return None

    user_id = owner["id"]
    profile = query_one(
        """
        SELECT name, title, city, email, phone, wechat, github_url, website_url,
               avatar_path, resume_file_path, summary, job_status
        FROM profile
        WHERE user_id = %s AND is_active = 1
        LIMIT 1
        """,
        (user_id,),
    )
    if not profile:
        return None

    skills = query_all(
        """
        SELECT name, category, proficiency, icon, color
        FROM skills
        WHERE user_id = %s AND is_active = 1
        ORDER BY sort_order ASC, id ASC
        """,
        (user_id,),
    )
    experiences = query_all(
        """
        SELECT company, position, location, start_date, end_date, is_current, description
        FROM experiences
        WHERE user_id = %s AND is_active = 1
        ORDER BY sort_order ASC, start_date DESC, id ASC
        """,
        (user_id,),
    )
    projects = query_all(
        """
        SELECT name, role, tech_stack, project_url, source_url, cover_image_path,
               start_date, end_date, summary, highlights
        FROM projects
        WHERE user_id = %s AND is_active = 1
        ORDER BY sort_order ASC, start_date DESC, id ASC
        """,
        (user_id,),
    )
    education = query_all(
        """
        SELECT school, major, degree, location, start_date, end_date, description
        FROM education
        WHERE user_id = %s AND is_active = 1
        ORDER BY sort_order ASC, start_date DESC, id ASC
        """,
        (user_id,),
    )
    certificates = query_all(
        """
        SELECT name, issuer, issue_date, certificate_url, image_path, description
        FROM certificates
        WHERE user_id = %s AND is_active = 1
        ORDER BY sort_order ASC, issue_date DESC, id ASC
        """,
        (user_id,),
    )

    return {
        "owner": owner,
        "profile": profile,
        "skills_by_category": group_skills(skills),
        "experiences": experiences,
        "projects": projects,
        "education": education,
        "certificates": certificates,
        "settings": get_settings(),
    }


@public_bp.route("/")
def index():
    keyword = request.args.get("q", "").strip()
    settings = get_settings()
    resumes = load_public_resumes(keyword)
    return render_template(
        "public/index.html",
        settings=settings,
        resumes=resumes,
        keyword=keyword,
    )


@public_bp.route("/u/<username>")
def user_resume(username):
    data = load_user_resume_data(username)
    if not data:
        abort(404)
    return render_template("public/resume.html", form=MessageForm(), **data)


@public_bp.route("/messages", methods=["GET", "POST"])
def legacy_messages():
    flash("请先进入某位用户的公开简历页后再提交留言。", "warning")
    return redirect(url_for("public.index") + "#public-resumes")


@public_bp.route("/u/<username>/messages", methods=["POST"])
@limiter.limit("3 per minute")
def submit_message(username):
    user = find_public_user(username)
    if not user:
        abort(404)

    if not messages_enabled():
        flash("留言功能暂未开放。", "warning")
        return redirect(url_for("public.user_resume", username=username) + "#contact")

    form = MessageForm()
    if not form.validate_on_submit():
        flash("请检查留言内容后再提交。", "danger")
        return redirect(url_for("public.user_resume", username=username) + "#contact")

    forwarded_for = request.headers.get("X-Forwarded-For", "")
    ip_address = forwarded_for.split(",", 1)[0].strip() or request.remote_addr
    user_agent = (request.headers.get("User-Agent") or "")[:512]
    phone = form.phone.data.strip() if form.phone.data else None

    execute(
        """
        INSERT INTO messages (
            target_user_id, name, email, phone, content, ip_address, user_agent
        )
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        """,
        (
            user["id"],
            form.name.data.strip(),
            form.email.data.strip(),
            phone,
            form.content.data.strip(),
            ip_address,
            user_agent,
        ),
    )
    flash("留言已提交，对方会尽快回复。", "success")
    return redirect(url_for("public.user_resume", username=username) + "#contact")
