import os
from pathlib import Path

import click
from flask import current_app
from werkzeug.security import generate_password_hash

from app.db import execute, execute_script, query_one

BASE_DIR = Path(__file__).resolve().parent.parent


def load_sql_file(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def register_cli(app) -> None:
    @app.cli.command("init-db")
    def init_db_command() -> None:
        script = load_sql_file(BASE_DIR / "database" / "schema.sql")
        executed = execute_script(script)
        click.echo(f"Initialized database with {executed} statements.")

    @app.cli.command("seed-db")
    def seed_db_command() -> None:
        username = os.getenv("ADMIN_USERNAME", "admin")
        password = os.getenv("ADMIN_PASSWORD")
        email = os.getenv("ADMIN_EMAIL", "admin@example.com")
        display_name = os.getenv("ADMIN_DISPLAY_NAME", "Administrator")
        demo_username = os.getenv("DEFAULT_USER_USERNAME", "demo")
        demo_password = os.getenv("DEFAULT_USER_PASSWORD", password)
        demo_email = os.getenv("DEFAULT_USER_EMAIL", "demo@example.com")
        demo_display_name = os.getenv("DEFAULT_USER_DISPLAY_NAME", "演示用户")
        if not password:
            raise click.ClickException(
                "ADMIN_PASSWORD is required before running flask seed-db."
            )

        script = load_sql_file(BASE_DIR / "database" / "seed.sql")
        executed = execute_script(script)

        admin_id = upsert_user(username, email, display_name, password, "super_admin")
        demo_user_id = upsert_user(
            demo_username, demo_email, demo_display_name, demo_password, "user"
        )
        seed_default_profile(demo_user_id, demo_display_name, demo_email)
        current_app.logger.info("Seeded administrator '%s'.", username)
        click.echo(
            f"Seeded database with {executed} SQL statements, administrator "
            f"'{username}' (id={admin_id}) and default user "
            f"'{demo_username}' (id={demo_user_id})."
        )


def upsert_user(
    username: str, email: str, display_name: str, password: str, role: str
) -> int:
    password_hash = generate_password_hash(password)
    execute(
        """
        INSERT INTO users (
            username, email, password_hash, display_name, role, is_active
        ) VALUES (
            %s, %s, %s, %s, %s, 1
        )
        ON DUPLICATE KEY UPDATE
            email = VALUES(email),
            password_hash = VALUES(password_hash),
            display_name = VALUES(display_name),
            role = VALUES(role),
            is_active = VALUES(is_active),
            updated_at = CURRENT_TIMESTAMP
        """,
        (username, email, password_hash, display_name, role),
    )
    user = query_one("SELECT id FROM users WHERE username = %s LIMIT 1", (username,))
    if not user:
        raise click.ClickException(f"用户 {username} 初始化失败。")
    return int(user["id"])


def seed_default_profile(user_id: int, display_name: str, email: str) -> None:
    execute(
        """
        INSERT INTO profile (
            user_id, name, title, city, email, summary, job_status, is_active
        ) VALUES (
            %s, %s, '软件工程师', '上海', %s,
            '这里填写一段适合展示在公开简历页的个人简介。',
            '正在寻找合适的机会', 1
        )
        ON DUPLICATE KEY UPDATE
            name = VALUES(name),
            title = VALUES(title),
            city = VALUES(city),
            email = VALUES(email),
            summary = VALUES(summary),
            job_status = VALUES(job_status),
            is_active = VALUES(is_active),
            updated_at = CURRENT_TIMESTAMP
        """,
        (user_id, display_name, email),
    )
