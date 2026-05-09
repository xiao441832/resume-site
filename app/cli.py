import os
from pathlib import Path

import click
from flask import current_app
from werkzeug.security import generate_password_hash

from app.db import execute, execute_script

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
        if not password:
            raise click.ClickException(
                "ADMIN_PASSWORD is required before running flask seed-db."
            )

        script = load_sql_file(BASE_DIR / "database" / "seed.sql")
        executed = execute_script(script)

        password_hash = generate_password_hash(password)
        execute(
            """
            INSERT INTO admin_users (
                username, password_hash, display_name, email, is_active
            ) VALUES (
                %s, %s, %s, %s, 1
            )
            ON DUPLICATE KEY UPDATE
                password_hash = VALUES(password_hash),
                display_name = VALUES(display_name),
                email = VALUES(email),
                is_active = VALUES(is_active),
                updated_at = CURRENT_TIMESTAMP
            """,
            (username, password_hash, display_name, email),
        )
        current_app.logger.info("Seeded administrator '%s'.", username)
        click.echo(
            f"Seeded database with {executed} SQL statements and administrator "
            f"'{username}'."
        )
