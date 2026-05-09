# Resume Site Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a responsive Flask + MySQL personal resume website with a public resume homepage and a custom Bootstrap administrator backend.

**Architecture:** Use a modular Flask application with blueprints for public pages, authentication, and administration. Use PyMySQL with explicit parameterized SQL, Jinja2 server-side rendering, Bootstrap 5, and `.env` driven configuration for a separate MySQL server.

**Tech Stack:** Python 3, Flask, PyMySQL, Flask-WTF, Flask-Limiter, Werkzeug, Bootstrap 5, jQuery, MySQL 8.0, Gunicorn, Nginx, systemd, pytest.

---

## File Responsibility Map

- `requirements.txt`: Python package dependencies for app runtime and tests.
- `.gitignore`: Ignore virtualenvs, caches, uploads, local env files, and generated artifacts.
- `.env.example`: Document required deployment and local environment variables.
- `run.py`: Local Flask entry point.
- `pytest.ini`: Pytest defaults.
- `app/__init__.py`: Flask application factory, extension setup, blueprint registration, CLI registration.
- `app/config.py`: Environment-backed configuration classes.
- `app/db.py`: PyMySQL connection lifecycle, query helpers, transaction helpers, and SQL file execution helpers.
- `app/cli.py`: `flask init-db` and `flask seed-db`.
- `app/extensions.py`: Shared Flask extension instances for CSRF and rate limiting.
- `app/auth/forms.py`: Administrator login form.
- `app/auth/routes.py`: Login and logout routes.
- `app/auth/decorators.py`: `login_required` route decorator.
- `app/public/forms.py`: Visitor message form.
- `app/public/routes.py`: Public resume homepage and message submission.
- `app/admin/forms.py`: Administrator forms for profile, content resources, messages, settings, and uploads.
- `app/admin/resources.py`: Resource metadata for shared CRUD modules.
- `app/admin/routes.py`: Dashboard, profile, shared CRUD, messages, settings, and upload-backed admin routes.
- `app/services/upload_service.py`: File validation, UUID filename generation, storage, and upload metadata.
- `app/templates/base.html`: Public base template.
- `app/templates/public/index.html`: Public resume homepage template.
- `app/templates/auth/login.html`: Login template.
- `app/templates/admin/layout.html`: Admin shell template.
- `app/templates/admin/dashboard.html`: Admin dashboard template.
- `app/templates/admin/resource_list.html`: Shared admin list template.
- `app/templates/admin/resource_form.html`: Shared admin form template.
- `app/templates/admin/profile.html`: Profile edit template.
- `app/templates/admin/messages.html`: Message management template.
- `app/templates/admin/message_detail.html`: Message detail template.
- `app/templates/admin/settings.html`: Settings template.
- `app/static/css/main.css`: Public and admin styling layered on Bootstrap.
- `app/static/js/main.js`: Navbar collapse behavior, upload preview, delete confirmation, flash fade, back-to-top.
- `app/static/uploads/.gitkeep`: Keep upload directory in git without committing uploaded files.
- `database/schema.sql`: MySQL 8.0 table schema.
- `database/seed.sql`: Default site settings and starter profile content.
- `deployment/gunicorn.conf.py`: Gunicorn production config.
- `deployment/nginx.conf.example`: Nginx reverse proxy and static/uploads config.
- `deployment/resume-site.service.example`: systemd unit example.
- `tests/conftest.py`: Shared pytest fixtures.
- `tests/test_app_factory.py`: App factory tests.
- `tests/test_db.py`: Database helper tests.
- `tests/test_cli.py`: Database CLI tests.
- `tests/test_auth.py`: Authentication tests.
- `tests/test_public.py`: Homepage and message tests.
- `tests/test_admin_resources.py`: Admin resource configuration and CRUD helper tests.
- `tests/test_upload_service.py`: Upload validation and storage tests.
- `README.md`: Local setup, database initialization, deployment, and admin usage.

## Task 1: Project Skeleton and App Factory

**Files:**

- Create: `requirements.txt`
- Create: `.gitignore`
- Create: `.env.example`
- Create: `run.py`
- Create: `pytest.ini`
- Create: `app/__init__.py`
- Create: `app/config.py`
- Create: `app/extensions.py`
- Create: `tests/conftest.py`
- Create: `tests/test_app_factory.py`

- [ ] **Step 1: Write the failing app factory test**

Create `tests/test_app_factory.py`:

```python
from pathlib import Path

from app import create_app


def test_create_app_uses_testing_config():
    app = create_app("testing")

    assert app.config["TESTING"] is True
    assert app.config["MYSQL_HOST"] == "localhost"
    assert app.config["MYSQL_PORT"] == 3306
    assert Path(app.config["UPLOAD_FOLDER"]).name == "uploads"


def test_create_app_registers_core_extensions():
    app = create_app("testing")

    assert "csrf" in app.extensions
    assert "limiter" in app.extensions
```

- [ ] **Step 2: Run the test and verify it fails**

Run:

```bash
pytest tests/test_app_factory.py -v
```

Expected: `ModuleNotFoundError: No module named 'app'`.

- [ ] **Step 3: Create the minimal dependencies and configuration files**

Create `requirements.txt`:

```text
Flask==3.0.3
PyMySQL==1.1.1
Werkzeug==3.0.3
Flask-WTF==1.2.1
Flask-Limiter==3.7.0
python-dotenv==1.0.1
email-validator==2.2.0
gunicorn==22.0.0
pytest==8.2.2
```

Create `.gitignore`:

```gitignore
.env
.venv/
venv/
__pycache__/
*.py[cod]
.pytest_cache/
.coverage
htmlcov/
instance/
app/static/uploads/*
!app/static/uploads/.gitkeep
*.log
```

Create `.env.example`:

```dotenv
FLASK_ENV=production
FLASK_DEBUG=0
SECRET_KEY=replace-with-a-long-random-secret

MYSQL_HOST=127.0.0.1
MYSQL_PORT=3306
MYSQL_USER=resume_user
MYSQL_PASSWORD=replace-with-database-password
MYSQL_DATABASE=resume_site
MYSQL_CHARSET=utf8mb4

ADMIN_USERNAME=admin
ADMIN_PASSWORD=replace-with-initial-admin-password
ADMIN_EMAIL=admin@example.com
ADMIN_DISPLAY_NAME=Administrator

SESSION_COOKIE_SECURE=1
MAX_IMAGE_UPLOAD_MB=2
MAX_PDF_UPLOAD_MB=5
```

Create `pytest.ini`:

```ini
[pytest]
testpaths = tests
pythonpath = .
```

Create `run.py`:

```python
from app import create_app

app = create_app()

if __name__ == "__main__":
    app.run()
```

Create `app/extensions.py`:

```python
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_wtf import CSRFProtect

csrf = CSRFProtect()
limiter = Limiter(key_func=get_remote_address)
```

Create `app/config.py`:

```python
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent


def _bool_env(name: str, default: bool = False) -> bool:
    value = os.getenv(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


class BaseConfig:
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-change-me")
    MYSQL_HOST = os.getenv("MYSQL_HOST", "localhost")
    MYSQL_PORT = int(os.getenv("MYSQL_PORT", "3306"))
    MYSQL_USER = os.getenv("MYSQL_USER", "root")
    MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD", "")
    MYSQL_DATABASE = os.getenv("MYSQL_DATABASE", "resume_site")
    MYSQL_CHARSET = os.getenv("MYSQL_CHARSET", "utf8mb4")
    UPLOAD_FOLDER = str(BASE_DIR / "app" / "static" / "uploads")
    MAX_IMAGE_UPLOAD_MB = int(os.getenv("MAX_IMAGE_UPLOAD_MB", "2"))
    MAX_PDF_UPLOAD_MB = int(os.getenv("MAX_PDF_UPLOAD_MB", "5"))
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SECURE = _bool_env("SESSION_COOKIE_SECURE", False)
    WTF_CSRF_ENABLED = True
    RATELIMIT_ENABLED = True


class DevelopmentConfig(BaseConfig):
    DEBUG = True


class TestingConfig(BaseConfig):
    TESTING = True
    WTF_CSRF_ENABLED = False
    RATELIMIT_ENABLED = False
    SECRET_KEY = "testing-secret"


class ProductionConfig(BaseConfig):
    DEBUG = False


CONFIG_MAP = {
    "development": DevelopmentConfig,
    "testing": TestingConfig,
    "production": ProductionConfig,
}
```

Create `app/__init__.py`:

```python
import os
from pathlib import Path

from dotenv import load_dotenv
from flask import Flask

from app.config import CONFIG_MAP
from app.extensions import csrf, limiter


def create_app(config_name: str | None = None) -> Flask:
    load_dotenv()
    selected_config = config_name or os.getenv("FLASK_ENV", "development")

    app = Flask(__name__)
    app.config.from_object(CONFIG_MAP.get(selected_config, CONFIG_MAP["development"]))

    Path(app.config["UPLOAD_FOLDER"]).mkdir(parents=True, exist_ok=True)

    csrf.init_app(app)
    limiter.init_app(app)

    return app
```

Create `tests/conftest.py`:

```python
import pytest

from app import create_app


@pytest.fixture()
def app():
    return create_app("testing")


@pytest.fixture()
def client(app):
    return app.test_client()
```

Create `app/static/uploads/.gitkeep` as an empty file.

- [ ] **Step 4: Run the app factory tests and verify they pass**

Run:

```bash
pytest tests/test_app_factory.py -v
```

Expected: `2 passed`.

- [ ] **Step 5: Commit**

Run:

```bash
git add requirements.txt .gitignore .env.example run.py pytest.ini app tests
git commit -m "feat: add Flask app skeleton"
```

Expected: commit succeeds.

## Task 2: Database Helper Layer

**Files:**

- Modify: `app/__init__.py`
- Create: `app/db.py`
- Create: `tests/test_db.py`

- [ ] **Step 1: Write failing tests for pure database helper behavior**

Create `tests/test_db.py`:

```python
from app.db import build_connection_kwargs, split_sql_script


def test_build_connection_kwargs_uses_app_config(app):
    kwargs = build_connection_kwargs(app.config)

    assert kwargs["host"] == "localhost"
    assert kwargs["port"] == 3306
    assert kwargs["charset"] == "utf8mb4"
    assert kwargs["cursorclass"].__name__ == "DictCursor"


def test_split_sql_script_ignores_empty_statements_and_line_comments():
    script = """
    -- first table
    CREATE TABLE one (id INT);

    -- second table
    CREATE TABLE two (id INT);
    """

    assert split_sql_script(script) == [
        "CREATE TABLE one (id INT)",
        "CREATE TABLE two (id INT)",
    ]
```

- [ ] **Step 2: Run the tests and verify they fail**

Run:

```bash
pytest tests/test_db.py -v
```

Expected: `ModuleNotFoundError: No module named 'app.db'`.

- [ ] **Step 3: Implement the database helper**

Create `app/db.py`:

```python
from collections.abc import Iterable
from typing import Any

import pymysql
from flask import current_app, g
from pymysql.cursors import DictCursor


def build_connection_kwargs(config: dict[str, Any]) -> dict[str, Any]:
    return {
        "host": config["MYSQL_HOST"],
        "port": config["MYSQL_PORT"],
        "user": config["MYSQL_USER"],
        "password": config["MYSQL_PASSWORD"],
        "database": config["MYSQL_DATABASE"],
        "charset": config["MYSQL_CHARSET"],
        "cursorclass": DictCursor,
        "autocommit": False,
    }


def get_db():
    if "db" not in g:
        g.db = pymysql.connect(**build_connection_kwargs(current_app.config))
    return g.db


def close_db(error: BaseException | None = None) -> None:
    db = g.pop("db", None)
    if db is not None:
        db.close()


def query_all(sql: str, params: Iterable[Any] | dict[str, Any] | None = None) -> list[dict[str, Any]]:
    with get_db().cursor() as cursor:
        cursor.execute(sql, params)
        return list(cursor.fetchall())


def query_one(sql: str, params: Iterable[Any] | dict[str, Any] | None = None) -> dict[str, Any] | None:
    with get_db().cursor() as cursor:
        cursor.execute(sql, params)
        return cursor.fetchone()


def execute(sql: str, params: Iterable[Any] | dict[str, Any] | None = None) -> int:
    db = get_db()
    with db.cursor() as cursor:
        affected = cursor.execute(sql, params)
    db.commit()
    return affected


def execute_many(sql: str, params: Iterable[Iterable[Any] | dict[str, Any]]) -> int:
    db = get_db()
    with db.cursor() as cursor:
        affected = cursor.executemany(sql, params)
    db.commit()
    return affected


def split_sql_script(script: str) -> list[str]:
    lines: list[str] = []
    for raw_line in script.splitlines():
        line = raw_line.strip()
        if not line or line.startswith("--"):
            continue
        lines.append(raw_line)

    joined = "\n".join(lines)
    return [statement.strip().rstrip(";") for statement in joined.split(";") if statement.strip()]


def execute_script(script: str) -> int:
    db = get_db()
    statements = split_sql_script(script)
    with db.cursor() as cursor:
        for statement in statements:
            cursor.execute(statement)
    db.commit()
    return len(statements)
```

Modify `app/__init__.py`:

```python
import os
from pathlib import Path

from dotenv import load_dotenv
from flask import Flask

from app.config import CONFIG_MAP
from app.extensions import csrf, limiter


def create_app(config_name: str | None = None) -> Flask:
    load_dotenv()
    selected_config = config_name or os.getenv("FLASK_ENV", "development")

    app = Flask(__name__)
    app.config.from_object(CONFIG_MAP.get(selected_config, CONFIG_MAP["development"]))

    Path(app.config["UPLOAD_FOLDER"]).mkdir(parents=True, exist_ok=True)

    csrf.init_app(app)
    limiter.init_app(app)

    from app import db

    app.teardown_appcontext(db.close_db)

    return app
```

- [ ] **Step 4: Run database helper tests**

Run:

```bash
pytest tests/test_db.py tests/test_app_factory.py -v
```

Expected: `4 passed`.

- [ ] **Step 5: Commit**

Run:

```bash
git add app/__init__.py app/db.py tests/test_db.py
git commit -m "feat: add MySQL helper layer"
```

Expected: commit succeeds.

## Task 3: Schema, Seed Data, and Flask CLI

**Files:**

- Modify: `app/__init__.py`
- Create: `app/cli.py`
- Create: `database/schema.sql`
- Create: `database/seed.sql`
- Create: `tests/test_cli.py`

- [ ] **Step 1: Write failing tests for CLI SQL helpers**

Create `tests/test_cli.py`:

```python
from pathlib import Path

from app.cli import load_sql_file


def test_load_sql_file_reads_utf8_text(tmp_path):
    sql_file = tmp_path / "sample.sql"
    sql_file.write_text("SELECT '中文';", encoding="utf-8")

    assert load_sql_file(sql_file) == "SELECT '中文';"
```

- [ ] **Step 2: Run the CLI test and verify it fails**

Run:

```bash
pytest tests/test_cli.py -v
```

Expected: `ModuleNotFoundError: No module named 'app.cli'`.

- [ ] **Step 3: Create SQL schema and CLI commands**

Create `database/schema.sql`:

```sql
CREATE TABLE IF NOT EXISTS admin_users (
  id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
  username VARCHAR(80) NOT NULL,
  password_hash VARCHAR(255) NOT NULL,
  display_name VARCHAR(120) NOT NULL,
  email VARCHAR(255) NULL,
  is_active TINYINT(1) NOT NULL DEFAULT 1,
  last_login_at DATETIME NULL,
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (id),
  UNIQUE KEY uq_admin_users_username (username)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS profile (
  id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
  name VARCHAR(120) NOT NULL,
  title VARCHAR(160) NOT NULL,
  city VARCHAR(120) NULL,
  email VARCHAR(255) NULL,
  phone VARCHAR(80) NULL,
  wechat VARCHAR(120) NULL,
  github_url VARCHAR(255) NULL,
  website_url VARCHAR(255) NULL,
  avatar_path VARCHAR(255) NULL,
  resume_file_path VARCHAR(255) NULL,
  summary TEXT NULL,
  job_status VARCHAR(160) NULL,
  is_active TINYINT(1) NOT NULL DEFAULT 1,
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (id),
  KEY idx_profile_active (is_active)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS skills (
  id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
  name VARCHAR(120) NOT NULL,
  category VARCHAR(120) NOT NULL,
  proficiency TINYINT UNSIGNED NOT NULL DEFAULT 80,
  icon VARCHAR(120) NULL,
  color VARCHAR(40) NULL,
  sort_order INT NOT NULL DEFAULT 0,
  is_active TINYINT(1) NOT NULL DEFAULT 1,
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (id),
  KEY idx_skills_public_order (is_active, sort_order, id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS experiences (
  id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
  company VARCHAR(180) NOT NULL,
  position VARCHAR(180) NOT NULL,
  location VARCHAR(120) NULL,
  start_date DATE NULL,
  end_date DATE NULL,
  is_current TINYINT(1) NOT NULL DEFAULT 0,
  description TEXT NULL,
  sort_order INT NOT NULL DEFAULT 0,
  is_active TINYINT(1) NOT NULL DEFAULT 1,
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (id),
  KEY idx_experiences_public_order (is_active, sort_order, start_date)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS projects (
  id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
  name VARCHAR(180) NOT NULL,
  role VARCHAR(160) NULL,
  tech_stack VARCHAR(255) NULL,
  project_url VARCHAR(255) NULL,
  source_url VARCHAR(255) NULL,
  cover_image_path VARCHAR(255) NULL,
  start_date DATE NULL,
  end_date DATE NULL,
  summary TEXT NULL,
  highlights TEXT NULL,
  sort_order INT NOT NULL DEFAULT 0,
  is_active TINYINT(1) NOT NULL DEFAULT 1,
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (id),
  KEY idx_projects_public_order (is_active, sort_order, start_date)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS education (
  id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
  school VARCHAR(180) NOT NULL,
  major VARCHAR(180) NULL,
  degree VARCHAR(120) NULL,
  location VARCHAR(120) NULL,
  start_date DATE NULL,
  end_date DATE NULL,
  description TEXT NULL,
  sort_order INT NOT NULL DEFAULT 0,
  is_active TINYINT(1) NOT NULL DEFAULT 1,
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (id),
  KEY idx_education_public_order (is_active, sort_order, start_date)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS certificates (
  id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
  name VARCHAR(180) NOT NULL,
  issuer VARCHAR(180) NULL,
  issue_date DATE NULL,
  certificate_url VARCHAR(255) NULL,
  image_path VARCHAR(255) NULL,
  description TEXT NULL,
  sort_order INT NOT NULL DEFAULT 0,
  is_active TINYINT(1) NOT NULL DEFAULT 1,
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (id),
  KEY idx_certificates_public_order (is_active, sort_order, issue_date)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS messages (
  id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
  name VARCHAR(120) NOT NULL,
  email VARCHAR(255) NOT NULL,
  phone VARCHAR(80) NULL,
  content TEXT NOT NULL,
  ip_address VARCHAR(64) NULL,
  user_agent VARCHAR(512) NULL,
  status ENUM('unread','read','handled','spam') NOT NULL DEFAULT 'unread',
  admin_note TEXT NULL,
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (id),
  KEY idx_messages_status_created (status, created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS uploads (
  id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
  original_filename VARCHAR(255) NOT NULL,
  saved_filename VARCHAR(255) NOT NULL,
  file_path VARCHAR(255) NOT NULL,
  mime_type VARCHAR(120) NOT NULL,
  file_size BIGINT UNSIGNED NOT NULL,
  upload_purpose VARCHAR(80) NOT NULL,
  uploader_id BIGINT UNSIGNED NULL,
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (id),
  KEY idx_uploads_purpose_created (upload_purpose, created_at),
  CONSTRAINT fk_uploads_admin_user FOREIGN KEY (uploader_id) REFERENCES admin_users(id) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS site_settings (
  id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
  setting_key VARCHAR(120) NOT NULL,
  setting_value TEXT NULL,
  setting_type VARCHAR(40) NOT NULL DEFAULT 'string',
  description VARCHAR(255) NULL,
  updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (id),
  UNIQUE KEY uq_site_settings_key (setting_key)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
```

Create `database/seed.sql`:

```sql
INSERT INTO site_settings (setting_key, setting_value, setting_type, description)
VALUES
  ('site_title', '个人简历网站', 'string', '浏览器标题和导航栏站点名'),
  ('seo_description', '个人简历、项目经历、技能与联系方式', 'string', '页面 SEO 描述'),
  ('icp_text', '', 'string', 'ICP备案展示文本'),
  ('messages_enabled', '1', 'boolean', '是否开放前台留言表单')
ON DUPLICATE KEY UPDATE
  setting_value = VALUES(setting_value),
  setting_type = VALUES(setting_type),
  description = VALUES(description);

INSERT INTO profile (id, name, title, city, email, summary, job_status, is_active)
VALUES (
  1,
  '你的姓名',
  'Python 后端开发工程师',
  '中国',
  'name@example.com',
  '这里展示个人简介，可在后台修改。',
  '正在寻找合适机会',
  1
)
ON DUPLICATE KEY UPDATE
  name = VALUES(name),
  title = VALUES(title),
  city = VALUES(city),
  email = VALUES(email),
  summary = VALUES(summary),
  job_status = VALUES(job_status),
  is_active = VALUES(is_active);
```

Create `app/cli.py`:

```python
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
        schema_path = BASE_DIR / "database" / "schema.sql"
        executed = execute_script(load_sql_file(schema_path))
        click.echo(f"Initialized database with {executed} statements.")

    @app.cli.command("seed-db")
    def seed_db_command() -> None:
        seed_path = BASE_DIR / "database" / "seed.sql"
        executed = execute_script(load_sql_file(seed_path))

        username = os.getenv("ADMIN_USERNAME", "admin")
        password = os.getenv("ADMIN_PASSWORD")
        email = os.getenv("ADMIN_EMAIL", "admin@example.com")
        display_name = os.getenv("ADMIN_DISPLAY_NAME", "Administrator")

        if not password:
            raise click.ClickException("ADMIN_PASSWORD is required before running flask seed-db.")

        execute(
            """
            INSERT INTO admin_users (username, password_hash, display_name, email, is_active)
            VALUES (%s, %s, %s, %s, 1)
            ON DUPLICATE KEY UPDATE
              password_hash = VALUES(password_hash),
              display_name = VALUES(display_name),
              email = VALUES(email),
              is_active = 1
            """,
            (username, generate_password_hash(password), display_name, email),
        )
        current_app.logger.info("Seeded administrator account %s", username)
        click.echo(f"Seeded database with {executed} SQL statements and administrator '{username}'.")
```

Modify `app/__init__.py`:

```python
import os
from pathlib import Path

from dotenv import load_dotenv
from flask import Flask

from app.config import CONFIG_MAP
from app.extensions import csrf, limiter


def create_app(config_name: str | None = None) -> Flask:
    load_dotenv()
    selected_config = config_name or os.getenv("FLASK_ENV", "development")

    app = Flask(__name__)
    app.config.from_object(CONFIG_MAP.get(selected_config, CONFIG_MAP["development"]))

    Path(app.config["UPLOAD_FOLDER"]).mkdir(parents=True, exist_ok=True)

    csrf.init_app(app)
    limiter.init_app(app)

    from app import cli, db

    app.teardown_appcontext(db.close_db)
    cli.register_cli(app)

    return app
```

- [ ] **Step 4: Run CLI and prior tests**

Run:

```bash
pytest tests/test_cli.py tests/test_db.py tests/test_app_factory.py -v
```

Expected: `5 passed`.

- [ ] **Step 5: Commit**

Run:

```bash
git add app/__init__.py app/cli.py database tests/test_cli.py
git commit -m "feat: add database schema and CLI"
```

Expected: commit succeeds.

## Task 4: Authentication Routes

**Files:**

- Modify: `app/__init__.py`
- Create: `app/auth/__init__.py`
- Create: `app/auth/decorators.py`
- Create: `app/auth/forms.py`
- Create: `app/auth/routes.py`
- Create: `app/templates/auth/login.html`
- Create: `tests/test_auth.py`

- [ ] **Step 1: Write failing authentication tests**

Create `tests/test_auth.py`:

```python
from werkzeug.security import generate_password_hash


def test_login_page_renders(client):
    response = client.get("/admin/login")

    assert response.status_code == 200
    assert "管理员登录" in response.get_data(as_text=True)


def test_login_success_sets_session(client, monkeypatch):
    monkeypatch.setattr(
        "app.auth.routes.find_admin_by_username",
        lambda username: {
            "id": 7,
            "username": username,
            "password_hash": generate_password_hash("secret123"),
            "display_name": "Admin",
            "is_active": 1,
        },
    )
    monkeypatch.setattr("app.auth.routes.mark_last_login", lambda admin_id: None)

    response = client.post(
        "/admin/login",
        data={"username": "admin", "password": "secret123"},
        follow_redirects=False,
    )

    assert response.status_code == 302
    with client.session_transaction() as session:
        assert session["admin_user_id"] == 7
        assert session["admin_username"] == "admin"


def test_login_rejects_wrong_password(client, monkeypatch):
    monkeypatch.setattr(
        "app.auth.routes.find_admin_by_username",
        lambda username: {
            "id": 7,
            "username": username,
            "password_hash": generate_password_hash("secret123"),
            "display_name": "Admin",
            "is_active": 1,
        },
    )

    response = client.post(
        "/admin/login",
        data={"username": "admin", "password": "bad-password"},
        follow_redirects=True,
    )

    assert response.status_code == 200
    assert "用户名或密码错误" in response.get_data(as_text=True)
```

- [ ] **Step 2: Run authentication tests and verify they fail**

Run:

```bash
pytest tests/test_auth.py -v
```

Expected: the first test returns `404 NOT FOUND` for `/admin/login`.

- [ ] **Step 3: Implement auth blueprint, form, and template**

Create `app/auth/__init__.py`:

```python
```

Create `app/auth/forms.py`:

```python
from flask_wtf import FlaskForm
from wtforms import PasswordField, StringField, SubmitField
from wtforms.validators import DataRequired, Length


class LoginForm(FlaskForm):
    username = StringField("用户名", validators=[DataRequired(), Length(max=80)])
    password = PasswordField("密码", validators=[DataRequired(), Length(min=6, max=128)])
    submit = SubmitField("登录")
```

Create `app/auth/decorators.py`:

```python
from functools import wraps

from flask import flash, redirect, session, url_for


def login_required(view):
    @wraps(view)
    def wrapped_view(*args, **kwargs):
        if not session.get("admin_user_id"):
            flash("请先登录后台。", "warning")
            return redirect(url_for("auth.login"))
        return view(*args, **kwargs)

    return wrapped_view
```

Create `app/auth/routes.py`:

```python
from flask import Blueprint, flash, redirect, render_template, request, session, url_for
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
        password_ok = bool(admin) and check_password_hash(admin["password_hash"], form.password.data)
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
```

Create `app/templates/auth/login.html`:

```html
<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>管理员登录</title>
  <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css" rel="stylesheet">
</head>
<body class="bg-light">
  <main class="container min-vh-100 d-flex align-items-center justify-content-center">
    <div class="card shadow-sm border-0" style="max-width: 420px; width: 100%;">
      <div class="card-body p-4">
        <h1 class="h4 mb-4 text-center">管理员登录</h1>
        {% with messages = get_flashed_messages(with_categories=true) %}
          {% for category, message in messages %}
            <div class="alert alert-{{ category }}">{{ message }}</div>
          {% endfor %}
        {% endwith %}
        <form method="post">
          {{ form.hidden_tag() }}
          <div class="mb-3">
            {{ form.username.label(class="form-label") }}
            {{ form.username(class="form-control", autocomplete="username") }}
          </div>
          <div class="mb-3">
            {{ form.password.label(class="form-label") }}
            {{ form.password(class="form-control", autocomplete="current-password") }}
          </div>
          {{ form.submit(class="btn btn-primary w-100") }}
        </form>
      </div>
    </div>
  </main>
</body>
</html>
```

Modify `app/__init__.py`:

```python
import os
from pathlib import Path

from dotenv import load_dotenv
from flask import Flask

from app.config import CONFIG_MAP
from app.extensions import csrf, limiter


def create_app(config_name: str | None = None) -> Flask:
    load_dotenv()
    selected_config = config_name or os.getenv("FLASK_ENV", "development")

    app = Flask(__name__)
    app.config.from_object(CONFIG_MAP.get(selected_config, CONFIG_MAP["development"]))

    Path(app.config["UPLOAD_FOLDER"]).mkdir(parents=True, exist_ok=True)

    csrf.init_app(app)
    limiter.init_app(app)

    from app import cli, db
    from app.auth.routes import auth_bp

    app.teardown_appcontext(db.close_db)
    cli.register_cli(app)
    app.register_blueprint(auth_bp)

    return app
```

Add a temporary admin dashboard route in `app/__init__.py` until Task 6 replaces it:

```python
    @app.route("/admin")
    def temporary_admin_dashboard():
        return "Admin dashboard"
```

- [ ] **Step 4: Run authentication tests**

Run:

```bash
pytest tests/test_auth.py -v
```

Expected: `3 passed`.

- [ ] **Step 5: Commit**

Run:

```bash
git add app tests/test_auth.py
git commit -m "feat: add administrator authentication"
```

Expected: commit succeeds.

## Task 5: Public Homepage and Message Submission

**Files:**

- Modify: `app/__init__.py`
- Create: `app/public/__init__.py`
- Create: `app/public/forms.py`
- Create: `app/public/routes.py`
- Create: `app/templates/base.html`
- Create: `app/templates/public/index.html`
- Create: `app/static/css/main.css`
- Create: `app/static/js/main.js`
- Create: `tests/test_public.py`

- [ ] **Step 1: Write failing public route tests**

Create `tests/test_public.py`:

```python
def test_homepage_renders_resume_data(client, monkeypatch):
    monkeypatch.setattr(
        "app.public.routes.load_homepage_data",
        lambda: {
            "profile": {"name": "张三", "title": "Python 工程师", "summary": "热爱后端开发"},
            "skills_by_category": {"后端": [{"name": "Flask", "proficiency": 90}]},
            "experiences": [],
            "projects": [{"name": "简历网站", "tech_stack": "Flask, MySQL", "summary": "个人简历管理"}],
            "education": [],
            "certificates": [],
            "settings": {"site_title": "张三的简历", "messages_enabled": "1", "icp_text": ""},
        },
    )

    response = client.get("/")

    html = response.get_data(as_text=True)
    assert response.status_code == 200
    assert "张三" in html
    assert "Flask" in html
    assert "简历网站" in html


def test_message_submission_inserts_message(client, monkeypatch):
    monkeypatch.setattr("app.public.routes.messages_enabled", lambda: True)
    inserted = {}

    def fake_execute(sql, params):
        inserted["params"] = params
        return 1

    monkeypatch.setattr("app.public.routes.execute", fake_execute)

    response = client.post(
        "/messages",
        data={
            "name": "访客",
            "email": "visitor@example.com",
            "phone": "13800138000",
            "content": "你好，我想了解更多。",
        },
        follow_redirects=False,
    )

    assert response.status_code == 302
    assert inserted["params"][0] == "访客"
    assert inserted["params"][1] == "visitor@example.com"
```

- [ ] **Step 2: Run public tests and verify they fail**

Run:

```bash
pytest tests/test_public.py -v
```

Expected: the homepage test returns `404 NOT FOUND`.

- [ ] **Step 3: Implement public blueprint, form, templates, CSS, and JS**

Create `app/public/__init__.py`:

```python
```

Create `app/public/forms.py`:

```python
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, Email, Length, Optional


class MessageForm(FlaskForm):
    name = StringField("姓名", validators=[DataRequired(), Length(max=120)])
    email = StringField("邮箱", validators=[DataRequired(), Email(), Length(max=255)])
    phone = StringField("手机号", validators=[Optional(), Length(max=80)])
    content = TextAreaField("留言内容", validators=[DataRequired(), Length(min=5, max=2000)])
    submit = SubmitField("提交留言")
```

Create `app/public/routes.py`:

```python
from collections import defaultdict

from flask import Blueprint, flash, redirect, render_template, request, url_for

from app.db import execute, query_all, query_one
from app.extensions import limiter
from app.public.forms import MessageForm

public_bp = Blueprint("public", __name__)


def get_settings() -> dict[str, str]:
    rows = query_all("SELECT setting_key, setting_value FROM site_settings")
    return {row["setting_key"]: row["setting_value"] for row in rows}


def messages_enabled() -> bool:
    return get_settings().get("messages_enabled", "1") == "1"


def group_skills(skills: list[dict]) -> dict[str, list[dict]]:
    grouped = defaultdict(list)
    for skill in skills:
        grouped[skill["category"]].append(skill)
    return dict(grouped)


def load_homepage_data() -> dict:
    skills = query_all(
        "SELECT * FROM skills WHERE is_active = 1 ORDER BY sort_order ASC, id ASC"
    )
    return {
        "profile": query_one("SELECT * FROM profile WHERE is_active = 1 ORDER BY id ASC LIMIT 1"),
        "skills_by_category": group_skills(skills),
        "experiences": query_all(
            "SELECT * FROM experiences WHERE is_active = 1 ORDER BY sort_order ASC, start_date DESC, id DESC"
        ),
        "projects": query_all(
            "SELECT * FROM projects WHERE is_active = 1 ORDER BY sort_order ASC, start_date DESC, id DESC"
        ),
        "education": query_all(
            "SELECT * FROM education WHERE is_active = 1 ORDER BY sort_order ASC, start_date DESC, id DESC"
        ),
        "certificates": query_all(
            "SELECT * FROM certificates WHERE is_active = 1 ORDER BY sort_order ASC, issue_date DESC, id DESC"
        ),
        "settings": get_settings(),
    }


@public_bp.route("/")
def index():
    data = load_homepage_data()
    return render_template("public/index.html", form=MessageForm(), **data)


@public_bp.route("/messages", methods=["POST"])
@limiter.limit("3 per minute")
def create_message():
    form = MessageForm()
    if not messages_enabled():
        flash("留言功能暂未开放。", "warning")
        return redirect(url_for("public.index") + "#contact")

    if form.validate_on_submit():
        execute(
            """
            INSERT INTO messages (name, email, phone, content, ip_address, user_agent)
            VALUES (%s, %s, %s, %s, %s, %s)
            """,
            (
                form.name.data.strip(),
                form.email.data.strip(),
                form.phone.data.strip() if form.phone.data else None,
                form.content.data.strip(),
                request.headers.get("X-Forwarded-For", request.remote_addr),
                request.headers.get("User-Agent", "")[:512],
            ),
        )
        flash("留言提交成功。", "success")
    else:
        flash("请检查留言表单内容。", "danger")

    return redirect(url_for("public.index") + "#contact")
```

Create `app/templates/base.html`:

```html
<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta name="description" content="{{ settings.get('seo_description', '个人简历网站') if settings else '个人简历网站' }}">
  <title>{{ settings.get('site_title', '个人简历网站') if settings else '个人简历网站' }}</title>
  <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css" rel="stylesheet">
  <link href="{{ url_for('static', filename='css/main.css') }}" rel="stylesheet">
</head>
<body>
  {% block body %}{% endblock %}
  <script src="https://code.jquery.com/jquery-3.7.1.min.js"></script>
  <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/js/bootstrap.bundle.min.js"></script>
  <script src="{{ url_for('static', filename='js/main.js') }}"></script>
</body>
</html>
```

Create `app/templates/public/index.html`:

```html
{% extends "base.html" %}

{% block body %}
<nav class="navbar navbar-expand-lg bg-white border-bottom sticky-top">
  <div class="container">
    <a class="navbar-brand fw-semibold" href="#top">{{ profile.name if profile else "个人简历" }}</a>
    <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#mainNav">
      <span class="navbar-toggler-icon"></span>
    </button>
    <div class="collapse navbar-collapse" id="mainNav">
      <ul class="navbar-nav ms-auto">
        <li class="nav-item"><a class="nav-link" href="#skills">技能</a></li>
        <li class="nav-item"><a class="nav-link" href="#experience">经历</a></li>
        <li class="nav-item"><a class="nav-link" href="#projects">项目</a></li>
        <li class="nav-item"><a class="nav-link" href="#education">教育</a></li>
        <li class="nav-item"><a class="nav-link" href="#certificates">证书</a></li>
        <li class="nav-item"><a class="nav-link" href="#contact">联系</a></li>
      </ul>
    </div>
  </div>
</nav>

<main id="top">
  <section class="hero-section">
    <div class="container py-5">
      <div class="row align-items-center g-4">
        <div class="col-md-4 text-center">
          {% if profile and profile.avatar_path %}
            <img class="avatar" src="{{ url_for('static', filename=profile.avatar_path) }}" alt="{{ profile.name }}">
          {% else %}
            <div class="avatar avatar-fallback">{{ profile.name[:1] if profile else "简" }}</div>
          {% endif %}
        </div>
        <div class="col-md-8">
          <p class="text-uppercase text-secondary small mb-2">{{ profile.job_status if profile else "" }}</p>
          <h1 class="display-5 fw-bold">{{ profile.name if profile else "个人简历" }}</h1>
          <p class="lead mb-3">{{ profile.title if profile else "欢迎访问我的简历网站" }}</p>
          <p class="text-secondary">{{ profile.summary if profile else "" }}</p>
          <div class="d-flex flex-wrap gap-2">
            <a class="btn btn-primary" href="#contact">联系我</a>
            {% if profile and profile.resume_file_path %}
              <a class="btn btn-outline-primary" href="{{ url_for('static', filename=profile.resume_file_path) }}">下载简历</a>
            {% endif %}
          </div>
        </div>
      </div>
    </div>
  </section>

  <section id="skills" class="section-band">
    <div class="container">
      <h2 class="section-title">技能</h2>
      <div class="row g-3">
        {% for category, skills in skills_by_category.items() %}
          <div class="col-lg-4">
            <div class="content-card h-100">
              <h3 class="h5">{{ category }}</h3>
              {% for skill in skills %}
                <div class="mb-3">
                  <div class="d-flex justify-content-between">
                    <span>{{ skill.name }}</span>
                    <span>{{ skill.proficiency }}%</span>
                  </div>
                  <div class="progress" role="progressbar" aria-valuenow="{{ skill.proficiency }}" aria-valuemin="0" aria-valuemax="100">
                    <div class="progress-bar" style="width: {{ skill.proficiency }}%"></div>
                  </div>
                </div>
              {% endfor %}
            </div>
          </div>
        {% endfor %}
      </div>
    </div>
  </section>

  <section id="experience" class="section-band bg-soft">
    <div class="container">
      <h2 class="section-title">工作 / 实习经历</h2>
      {% for item in experiences %}
        <article class="timeline-item">
          <h3 class="h5">{{ item.position }} · {{ item.company }}</h3>
          <p class="text-secondary">{{ item.start_date or "" }} - {{ "至今" if item.is_current else (item.end_date or "") }} · {{ item.location or "" }}</p>
          <p>{{ item.description or "" }}</p>
        </article>
      {% endfor %}
    </div>
  </section>

  <section id="projects" class="section-band">
    <div class="container">
      <h2 class="section-title">项目经历</h2>
      <div class="row g-4">
        {% for project in projects %}
          <div class="col-md-6 col-lg-4">
            <article class="content-card h-100">
              {% if project.cover_image_path %}
                <img class="project-cover" src="{{ url_for('static', filename=project.cover_image_path) }}" alt="{{ project.name }}">
              {% endif %}
              <h3 class="h5">{{ project.name }}</h3>
              <p class="text-secondary">{{ project.tech_stack or "" }}</p>
              <p>{{ project.summary or "" }}</p>
              <div class="d-flex gap-2">
                {% if project.project_url %}<a class="btn btn-sm btn-outline-primary" href="{{ project.project_url }}">项目</a>{% endif %}
                {% if project.source_url %}<a class="btn btn-sm btn-outline-secondary" href="{{ project.source_url }}">源码</a>{% endif %}
              </div>
            </article>
          </div>
        {% endfor %}
      </div>
    </div>
  </section>

  <section id="education" class="section-band bg-soft">
    <div class="container">
      <h2 class="section-title">教育经历</h2>
      {% for item in education %}
        <article class="content-card mb-3">
          <h3 class="h5">{{ item.school }}</h3>
          <p class="text-secondary">{{ item.degree or "" }} · {{ item.major or "" }} · {{ item.location or "" }}</p>
          <p>{{ item.description or "" }}</p>
        </article>
      {% endfor %}
    </div>
  </section>

  <section id="certificates" class="section-band">
    <div class="container">
      <h2 class="section-title">证书</h2>
      <div class="row g-3">
        {% for item in certificates %}
          <div class="col-md-6">
            <article class="content-card h-100">
              <h3 class="h5">{{ item.name }}</h3>
              <p class="text-secondary">{{ item.issuer or "" }} · {{ item.issue_date or "" }}</p>
              <p>{{ item.description or "" }}</p>
            </article>
          </div>
        {% endfor %}
      </div>
    </div>
  </section>

  <section id="contact" class="section-band bg-soft">
    <div class="container">
      <h2 class="section-title">联系</h2>
      {% with messages = get_flashed_messages(with_categories=true) %}
        {% for category, message in messages %}
          <div class="alert alert-{{ category }}">{{ message }}</div>
        {% endfor %}
      {% endwith %}
      <form method="post" action="{{ url_for('public.create_message') }}" class="content-card">
        {{ form.hidden_tag() }}
        <div class="row g-3">
          <div class="col-md-4">{{ form.name.label(class="form-label") }}{{ form.name(class="form-control") }}</div>
          <div class="col-md-4">{{ form.email.label(class="form-label") }}{{ form.email(class="form-control") }}</div>
          <div class="col-md-4">{{ form.phone.label(class="form-label") }}{{ form.phone(class="form-control") }}</div>
          <div class="col-12">{{ form.content.label(class="form-label") }}{{ form.content(class="form-control", rows=5) }}</div>
          <div class="col-12">{{ form.submit(class="btn btn-primary") }}</div>
        </div>
      </form>
    </div>
  </section>
</main>

<footer class="py-4 border-top">
  <div class="container text-secondary small d-flex flex-wrap justify-content-between gap-2">
    <span>&copy; {{ profile.name if profile else "个人简历" }}</span>
    <span>{{ settings.get('icp_text', '') }}</span>
  </div>
</footer>

<button id="backToTop" class="btn btn-primary back-to-top" type="button">↑</button>
{% endblock %}
```

Create `app/static/css/main.css`:

```css
:root {
  --resume-primary: #2563eb;
  --resume-ink: #172033;
  --resume-muted: #64748b;
  --resume-soft: #f4f7fb;
}

body {
  color: var(--resume-ink);
}

.hero-section {
  background: linear-gradient(135deg, #eef6ff 0%, #ffffff 55%, #f8fbf2 100%);
}

.section-band {
  padding: 4rem 0;
}

.bg-soft {
  background: var(--resume-soft);
}

.section-title {
  font-size: 1.75rem;
  font-weight: 700;
  margin-bottom: 1.5rem;
}

.content-card {
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  background: #fff;
  padding: 1.25rem;
}

.avatar {
  width: min(240px, 70vw);
  aspect-ratio: 1;
  border-radius: 50%;
  object-fit: cover;
  box-shadow: 0 1rem 2rem rgb(15 23 42 / 12%);
}

.avatar-fallback {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  background: var(--resume-primary);
  color: #fff;
  font-size: 4rem;
  font-weight: 700;
}

.timeline-item {
  border-left: 3px solid var(--resume-primary);
  padding: 0.25rem 0 1.25rem 1rem;
}

.project-cover {
  width: 100%;
  aspect-ratio: 16 / 9;
  object-fit: cover;
  border-radius: 6px;
  margin-bottom: 1rem;
}

.back-to-top {
  position: fixed;
  right: 1rem;
  bottom: 1rem;
  display: none;
  z-index: 1030;
}
```

Create `app/static/js/main.js`:

```javascript
$(function () {
  const $backToTop = $("#backToTop");

  $(window).on("scroll", function () {
    $backToTop.toggle($(this).scrollTop() > 300);
  });

  $backToTop.on("click", function () {
    $("html, body").animate({ scrollTop: 0 }, 200);
  });

  $(".navbar-nav .nav-link").on("click", function () {
    const nav = $("#mainNav");
    if (nav.hasClass("show")) {
      bootstrap.Collapse.getOrCreateInstance(nav[0]).hide();
    }
  });

  $("[data-confirm]").on("click", function (event) {
    if (!window.confirm($(this).data("confirm"))) {
      event.preventDefault();
    }
  });

  $("[data-preview-target]").on("change", function () {
    const file = this.files && this.files[0];
    const target = $($(this).data("preview-target"));
    if (!file || !target.length) {
      return;
    }
    target.attr("src", URL.createObjectURL(file)).removeClass("d-none");
  });
});
```

Modify `app/__init__.py` to register the public blueprint:

```python
    from app.public.routes import public_bp

    app.register_blueprint(public_bp)
```

- [ ] **Step 4: Run public tests and existing tests**

Run:

```bash
pytest tests/test_public.py tests/test_auth.py tests/test_db.py tests/test_cli.py tests/test_app_factory.py -v
```

Expected: `10 passed`.

- [ ] **Step 5: Commit**

Run:

```bash
git add app tests/test_public.py
git commit -m "feat: add public resume homepage"
```

Expected: commit succeeds.

## Task 6: Upload Service

**Files:**

- Create: `app/services/__init__.py`
- Create: `app/services/upload_service.py`
- Create: `tests/test_upload_service.py`

- [ ] **Step 1: Write failing upload service tests**

Create `tests/test_upload_service.py`:

```python
from io import BytesIO

import pytest
from werkzeug.datastructures import FileStorage

from app.services.upload_service import UploadError, save_upload


def make_file(filename, content_type, content=b"file-content"):
    return FileStorage(stream=BytesIO(content), filename=filename, content_type=content_type)


def test_save_upload_accepts_image(app, tmp_path):
    app.config["UPLOAD_FOLDER"] = str(tmp_path)

    with app.app_context():
        result = save_upload(make_file("avatar.png", "image/png"), "avatar")

    assert result["original_filename"] == "avatar.png"
    assert result["saved_filename"].endswith(".png")
    assert result["file_path"].startswith("uploads/")
    assert (tmp_path / result["saved_filename"]).exists()


def test_save_upload_rejects_disallowed_extension(app, tmp_path):
    app.config["UPLOAD_FOLDER"] = str(tmp_path)

    with app.app_context():
        with pytest.raises(UploadError, match="不支持的文件类型"):
            save_upload(make_file("shell.exe", "application/octet-stream"), "avatar")


def test_save_upload_rejects_large_pdf(app, tmp_path):
    app.config["UPLOAD_FOLDER"] = str(tmp_path)
    app.config["MAX_PDF_UPLOAD_MB"] = 1

    with app.app_context():
        with pytest.raises(UploadError, match="文件大小超过限制"):
            save_upload(make_file("resume.pdf", "application/pdf", b"x" * (1024 * 1024 + 1)), "resume")
```

- [ ] **Step 2: Run upload service tests and verify they fail**

Run:

```bash
pytest tests/test_upload_service.py -v
```

Expected: `ModuleNotFoundError: No module named 'app.services'`.

- [ ] **Step 3: Implement upload service**

Create `app/services/__init__.py`:

```python
```

Create `app/services/upload_service.py`:

```python
from pathlib import Path
from uuid import uuid4

from flask import current_app
from werkzeug.datastructures import FileStorage
from werkzeug.utils import secure_filename

IMAGE_EXTENSIONS = {"jpg", "jpeg", "png", "webp", "gif"}
PDF_EXTENSIONS = {"pdf"}
IMAGE_PURPOSES = {"avatar", "project_cover", "certificate_image"}
PDF_PURPOSES = {"resume"}


class UploadError(ValueError):
    pass


def extension_for(filename: str) -> str:
    safe_name = secure_filename(filename or "")
    if "." not in safe_name:
        return ""
    return safe_name.rsplit(".", 1)[1].lower()


def max_size_for(purpose: str) -> int:
    if purpose in PDF_PURPOSES:
        return current_app.config["MAX_PDF_UPLOAD_MB"] * 1024 * 1024
    return current_app.config["MAX_IMAGE_UPLOAD_MB"] * 1024 * 1024


def allowed_extensions_for(purpose: str) -> set[str]:
    if purpose in PDF_PURPOSES:
        return PDF_EXTENSIONS
    if purpose in IMAGE_PURPOSES:
        return IMAGE_EXTENSIONS
    raise UploadError("未知的上传用途。")


def save_upload(file: FileStorage, purpose: str) -> dict:
    ext = extension_for(file.filename)
    if ext not in allowed_extensions_for(purpose):
        raise UploadError("不支持的文件类型。")

    file.stream.seek(0, 2)
    size = file.stream.tell()
    file.stream.seek(0)

    if size > max_size_for(purpose):
        raise UploadError("文件大小超过限制。")

    upload_dir = Path(current_app.config["UPLOAD_FOLDER"])
    upload_dir.mkdir(parents=True, exist_ok=True)
    saved_filename = f"{uuid4().hex}.{ext}"
    saved_path = upload_dir / saved_filename
    file.save(saved_path)

    return {
        "original_filename": file.filename,
        "saved_filename": saved_filename,
        "file_path": f"uploads/{saved_filename}",
        "mime_type": file.content_type or "application/octet-stream",
        "file_size": size,
        "upload_purpose": purpose,
    }
```

- [ ] **Step 4: Run upload tests**

Run:

```bash
pytest tests/test_upload_service.py -v
```

Expected: `3 passed`.

- [ ] **Step 5: Commit**

Run:

```bash
git add app/services tests/test_upload_service.py
git commit -m "feat: add upload validation service"
```

Expected: commit succeeds.

## Task 7: Administrator Resource Registry and Dashboard

**Files:**

- Modify: `app/__init__.py`
- Create: `app/admin/__init__.py`
- Create: `app/admin/forms.py`
- Create: `app/admin/resources.py`
- Create: `app/admin/routes.py`
- Create: `app/templates/admin/layout.html`
- Create: `app/templates/admin/dashboard.html`
- Create: `tests/test_admin_resources.py`

- [ ] **Step 1: Write failing admin resource tests**

Create `tests/test_admin_resources.py`:

```python
from app.admin.resources import RESOURCE_CONFIGS, build_insert_sql, build_update_sql


def test_resource_registry_contains_resume_modules():
    assert set(RESOURCE_CONFIGS) == {
        "skills",
        "experiences",
        "projects",
        "education",
        "certificates",
    }


def test_build_insert_sql_uses_config_columns():
    config = RESOURCE_CONFIGS["skills"]

    sql = build_insert_sql(config)

    assert sql == (
        "INSERT INTO skills (name, category, proficiency, icon, color, sort_order, is_active) "
        "VALUES (%s, %s, %s, %s, %s, %s, %s)"
    )


def test_build_update_sql_excludes_id_and_timestamps():
    config = RESOURCE_CONFIGS["skills"]

    sql = build_update_sql(config)

    assert sql == (
        "UPDATE skills SET name = %s, category = %s, proficiency = %s, icon = %s, "
        "color = %s, sort_order = %s, is_active = %s WHERE id = %s"
    )
```

- [ ] **Step 2: Run admin resource tests and verify they fail**

Run:

```bash
pytest tests/test_admin_resources.py -v
```

Expected: `ModuleNotFoundError: No module named 'app.admin'`.

- [ ] **Step 3: Implement admin forms, resource config, dashboard route, and layout**

Create `app/admin/__init__.py`:

```python
```

Create `app/admin/forms.py`:

```python
from flask_wtf import FlaskForm
from wtforms import BooleanField, DateField, IntegerField, StringField, SubmitField, TextAreaField, URLField
from wtforms.validators import DataRequired, Length, NumberRange, Optional


class SkillForm(FlaskForm):
    name = StringField("技能名称", validators=[DataRequired(), Length(max=120)])
    category = StringField("分类", validators=[DataRequired(), Length(max=120)])
    proficiency = IntegerField("熟练度", validators=[DataRequired(), NumberRange(min=0, max=100)])
    icon = StringField("图标", validators=[Optional(), Length(max=120)])
    color = StringField("颜色", validators=[Optional(), Length(max=40)])
    sort_order = IntegerField("排序", default=0)
    is_active = BooleanField("前台展示", default=True)
    submit = SubmitField("保存")


class ExperienceForm(FlaskForm):
    company = StringField("公司", validators=[DataRequired(), Length(max=180)])
    position = StringField("职位", validators=[DataRequired(), Length(max=180)])
    location = StringField("地点", validators=[Optional(), Length(max=120)])
    start_date = DateField("开始日期", validators=[Optional()])
    end_date = DateField("结束日期", validators=[Optional()])
    is_current = BooleanField("至今")
    description = TextAreaField("描述", validators=[Optional()])
    sort_order = IntegerField("排序", default=0)
    is_active = BooleanField("前台展示", default=True)
    submit = SubmitField("保存")


class ProjectForm(FlaskForm):
    name = StringField("项目名称", validators=[DataRequired(), Length(max=180)])
    role = StringField("角色", validators=[Optional(), Length(max=160)])
    tech_stack = StringField("技术栈", validators=[Optional(), Length(max=255)])
    project_url = URLField("项目链接", validators=[Optional(), Length(max=255)])
    source_url = URLField("源码链接", validators=[Optional(), Length(max=255)])
    cover_image_path = StringField("封面路径", validators=[Optional(), Length(max=255)])
    start_date = DateField("开始日期", validators=[Optional()])
    end_date = DateField("结束日期", validators=[Optional()])
    summary = TextAreaField("简介", validators=[Optional()])
    highlights = TextAreaField("亮点", validators=[Optional()])
    sort_order = IntegerField("排序", default=0)
    is_active = BooleanField("前台展示", default=True)
    submit = SubmitField("保存")


class EducationForm(FlaskForm):
    school = StringField("学校", validators=[DataRequired(), Length(max=180)])
    major = StringField("专业", validators=[Optional(), Length(max=180)])
    degree = StringField("学历", validators=[Optional(), Length(max=120)])
    location = StringField("地点", validators=[Optional(), Length(max=120)])
    start_date = DateField("开始日期", validators=[Optional()])
    end_date = DateField("结束日期", validators=[Optional()])
    description = TextAreaField("描述", validators=[Optional()])
    sort_order = IntegerField("排序", default=0)
    is_active = BooleanField("前台展示", default=True)
    submit = SubmitField("保存")


class CertificateForm(FlaskForm):
    name = StringField("证书名称", validators=[DataRequired(), Length(max=180)])
    issuer = StringField("颁发机构", validators=[Optional(), Length(max=180)])
    issue_date = DateField("颁发日期", validators=[Optional()])
    certificate_url = URLField("证书链接", validators=[Optional(), Length(max=255)])
    image_path = StringField("图片路径", validators=[Optional(), Length(max=255)])
    description = TextAreaField("描述", validators=[Optional()])
    sort_order = IntegerField("排序", default=0)
    is_active = BooleanField("前台展示", default=True)
    submit = SubmitField("保存")
```

Create `app/admin/resources.py`:

```python
from dataclasses import dataclass
from typing import Type

from flask_wtf import FlaskForm

from app.admin.forms import CertificateForm, EducationForm, ExperienceForm, ProjectForm, SkillForm


@dataclass(frozen=True)
class ResourceConfig:
    key: str
    table: str
    title: str
    form_class: Type[FlaskForm]
    columns: tuple[str, ...]
    list_columns: tuple[str, ...]


RESOURCE_CONFIGS = {
    "skills": ResourceConfig(
        key="skills",
        table="skills",
        title="技能",
        form_class=SkillForm,
        columns=("name", "category", "proficiency", "icon", "color", "sort_order", "is_active"),
        list_columns=("name", "category", "proficiency", "sort_order", "is_active"),
    ),
    "experiences": ResourceConfig(
        key="experiences",
        table="experiences",
        title="工作 / 实习经历",
        form_class=ExperienceForm,
        columns=("company", "position", "location", "start_date", "end_date", "is_current", "description", "sort_order", "is_active"),
        list_columns=("company", "position", "location", "sort_order", "is_active"),
    ),
    "projects": ResourceConfig(
        key="projects",
        table="projects",
        title="项目经历",
        form_class=ProjectForm,
        columns=("name", "role", "tech_stack", "project_url", "source_url", "cover_image_path", "start_date", "end_date", "summary", "highlights", "sort_order", "is_active"),
        list_columns=("name", "role", "tech_stack", "sort_order", "is_active"),
    ),
    "education": ResourceConfig(
        key="education",
        table="education",
        title="教育经历",
        form_class=EducationForm,
        columns=("school", "major", "degree", "location", "start_date", "end_date", "description", "sort_order", "is_active"),
        list_columns=("school", "major", "degree", "sort_order", "is_active"),
    ),
    "certificates": ResourceConfig(
        key="certificates",
        table="certificates",
        title="证书",
        form_class=CertificateForm,
        columns=("name", "issuer", "issue_date", "certificate_url", "image_path", "description", "sort_order", "is_active"),
        list_columns=("name", "issuer", "issue_date", "sort_order", "is_active"),
    ),
}


def get_resource_config(key: str) -> ResourceConfig:
    if key not in RESOURCE_CONFIGS:
        raise KeyError(key)
    return RESOURCE_CONFIGS[key]


def build_insert_sql(config: ResourceConfig) -> str:
    columns = ", ".join(config.columns)
    value_slots = ", ".join(["%s"] * len(config.columns))
    return f"INSERT INTO {config.table} ({columns}) VALUES ({value_slots})"


def build_update_sql(config: ResourceConfig) -> str:
    assignments = ", ".join(f"{column} = %s" for column in config.columns)
    return f"UPDATE {config.table} SET {assignments} WHERE id = %s"
```

Create `app/admin/routes.py`:

```python
from flask import Blueprint, abort, flash, redirect, render_template, request, url_for

from app.auth.decorators import login_required
from app.db import execute, query_all, query_one
from app.admin.resources import RESOURCE_CONFIGS, build_insert_sql, build_update_sql, get_resource_config

admin_bp = Blueprint("admin", __name__, url_prefix="/admin")


def dashboard_counts() -> dict:
    return {
        "skills": query_one("SELECT COUNT(*) AS total FROM skills")["total"],
        "projects": query_one("SELECT COUNT(*) AS total FROM projects")["total"],
        "messages": query_one("SELECT COUNT(*) AS total FROM messages")["total"],
        "unread_messages": query_one("SELECT COUNT(*) AS total FROM messages WHERE status = 'unread'")["total"],
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
    return render_template("admin/dashboard.html", counts=dashboard_counts(), recent_messages=recent_messages)


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
```

Create `app/templates/admin/layout.html`:

```html
<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{% block title %}后台管理{% endblock %}</title>
  <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css" rel="stylesheet">
  <link href="{{ url_for('static', filename='css/main.css') }}" rel="stylesheet">
</head>
<body class="bg-light">
  <nav class="navbar navbar-expand-lg bg-white border-bottom">
    <div class="container-fluid">
      <a class="navbar-brand" href="{{ url_for('admin.dashboard') }}">后台管理</a>
      <form method="post" action="{{ url_for('auth.logout') }}">
        <button class="btn btn-outline-secondary btn-sm" type="submit">退出</button>
      </form>
    </div>
  </nav>
  <div class="container-fluid">
    <div class="row">
      <aside class="col-lg-2 bg-white border-end min-vh-100 p-3">
        <div class="list-group list-group-flush">
          <a class="list-group-item list-group-item-action" href="{{ url_for('admin.dashboard') }}">仪表盘</a>
          <a class="list-group-item list-group-item-action" href="{{ url_for('admin.profile') }}">个人信息</a>
          {% for key, item in resource_configs.items() %}
            <a class="list-group-item list-group-item-action" href="{{ url_for('admin.resource_list', resource=key) }}">{{ item.title }}</a>
          {% endfor %}
          <a class="list-group-item list-group-item-action" href="{{ url_for('admin.messages') }}">留言</a>
          <a class="list-group-item list-group-item-action" href="{{ url_for('admin.settings') }}">站点设置</a>
        </div>
      </aside>
      <main class="col-lg-10 p-4">
        {% with messages = get_flashed_messages(with_categories=true) %}
          {% for category, message in messages %}
            <div class="alert alert-{{ category }}">{{ message }}</div>
          {% endfor %}
        {% endwith %}
        {% block content %}{% endblock %}
      </main>
    </div>
  </div>
  <script src="https://code.jquery.com/jquery-3.7.1.min.js"></script>
  <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/js/bootstrap.bundle.min.js"></script>
  <script src="{{ url_for('static', filename='js/main.js') }}"></script>
</body>
</html>
```

Create `app/templates/admin/dashboard.html`:

```html
{% extends "admin/layout.html" %}
{% block title %}仪表盘{% endblock %}
{% block content %}
<h1 class="h3 mb-4">仪表盘</h1>
<div class="row g-3 mb-4">
  <div class="col-md-3"><div class="content-card"><div class="text-secondary">技能</div><div class="fs-3 fw-bold">{{ counts.skills }}</div></div></div>
  <div class="col-md-3"><div class="content-card"><div class="text-secondary">项目</div><div class="fs-3 fw-bold">{{ counts.projects }}</div></div></div>
  <div class="col-md-3"><div class="content-card"><div class="text-secondary">留言</div><div class="fs-3 fw-bold">{{ counts.messages }}</div></div></div>
  <div class="col-md-3"><div class="content-card"><div class="text-secondary">未读</div><div class="fs-3 fw-bold">{{ counts.unread_messages }}</div></div></div>
</div>
<div class="content-card">
  <h2 class="h5">最近留言</h2>
  <div class="table-responsive">
    <table class="table align-middle">
      <thead><tr><th>姓名</th><th>邮箱</th><th>状态</th><th>时间</th></tr></thead>
      <tbody>
        {% for message in recent_messages %}
          <tr><td>{{ message.name }}</td><td>{{ message.email }}</td><td>{{ message.status }}</td><td>{{ message.created_at }}</td></tr>
        {% endfor %}
      </tbody>
    </table>
  </div>
</div>
{% endblock %}
```

Modify `app/__init__.py`:

```python
    from app.admin.routes import admin_bp

    app.register_blueprint(admin_bp)

    @app.context_processor
    def inject_admin_resources():
        from app.admin.resources import RESOURCE_CONFIGS

        return {"resource_configs": RESOURCE_CONFIGS}
```

Remove the temporary admin dashboard route from `app/__init__.py`.

- [ ] **Step 4: Run admin resource tests and existing tests**

Run:

```bash
pytest tests/test_admin_resources.py tests/test_auth.py tests/test_public.py tests/test_upload_service.py tests/test_db.py tests/test_cli.py tests/test_app_factory.py -v
```

Expected: `16 passed`.

- [ ] **Step 5: Commit**

Run:

```bash
git add app tests/test_admin_resources.py
git commit -m "feat: add admin resource framework"
```

Expected: commit succeeds.

## Task 8: Administrator CRUD Templates, Profile, Messages, and Settings

**Files:**

- Modify: `app/admin/forms.py`
- Modify: `app/admin/routes.py`
- Create: `app/templates/admin/resource_list.html`
- Create: `app/templates/admin/resource_form.html`
- Create: `app/templates/admin/profile.html`
- Create: `app/templates/admin/messages.html`
- Create: `app/templates/admin/message_detail.html`
- Create: `app/templates/admin/settings.html`

- [ ] **Step 1: Write failing route smoke tests**

Append to `tests/test_admin_resources.py`:

```python
def login_session(client):
    with client.session_transaction() as session:
        session["admin_user_id"] = 1
        session["admin_username"] = "admin"
        session["admin_display_name"] = "Admin"


def test_profile_page_renders(client, monkeypatch):
    login_session(client)
    monkeypatch.setattr("app.admin.routes.query_one", lambda sql, params=None: {"id": 1, "name": "张三", "title": "工程师"})

    response = client.get("/admin/profile")

    assert response.status_code == 200
    assert "个人信息" in response.get_data(as_text=True)


def test_messages_page_renders(client, monkeypatch):
    login_session(client)
    monkeypatch.setattr("app.admin.routes.query_all", lambda sql, params=None: [])

    response = client.get("/admin/messages")

    assert response.status_code == 200
    assert "留言管理" in response.get_data(as_text=True)
```

- [ ] **Step 2: Run the new admin tests and verify they fail**

Run:

```bash
pytest tests/test_admin_resources.py -v
```

Expected: profile and messages tests return `404 NOT FOUND`.

- [ ] **Step 3: Add admin forms and routes**

Append to `app/admin/forms.py`:

```python
from flask_wtf.file import FileAllowed, FileField
from wtforms import EmailField, SelectField


class ProfileForm(FlaskForm):
    name = StringField("姓名", validators=[DataRequired(), Length(max=120)])
    title = StringField("职位标题", validators=[DataRequired(), Length(max=160)])
    city = StringField("城市", validators=[Optional(), Length(max=120)])
    email = EmailField("邮箱", validators=[Optional(), Length(max=255)])
    phone = StringField("手机号", validators=[Optional(), Length(max=80)])
    wechat = StringField("微信", validators=[Optional(), Length(max=120)])
    github_url = URLField("GitHub", validators=[Optional(), Length(max=255)])
    website_url = URLField("个人网站", validators=[Optional(), Length(max=255)])
    avatar = FileField("头像", validators=[Optional(), FileAllowed(["jpg", "jpeg", "png", "webp", "gif"])])
    resume_file = FileField("简历 PDF", validators=[Optional(), FileAllowed(["pdf"])])
    summary = TextAreaField("个人简介", validators=[Optional()])
    job_status = StringField("求职状态", validators=[Optional(), Length(max=160)])
    is_active = BooleanField("前台展示", default=True)
    submit = SubmitField("保存")


class MessageStatusForm(FlaskForm):
    status = SelectField("状态", choices=[("unread", "未读"), ("read", "已读"), ("handled", "已处理"), ("spam", "垃圾留言")])
    admin_note = TextAreaField("管理员备注", validators=[Optional()])
    submit = SubmitField("保存")


class SettingForm(FlaskForm):
    site_title = StringField("站点标题", validators=[DataRequired(), Length(max=120)])
    seo_description = StringField("SEO 描述", validators=[Optional(), Length(max=255)])
    icp_text = StringField("备案号", validators=[Optional(), Length(max=120)])
    messages_enabled = BooleanField("开放留言", default=True)
    submit = SubmitField("保存")
```

Append to `app/admin/routes.py`:

```python
from app.admin.forms import MessageStatusForm, ProfileForm, SettingForm
from app.services.upload_service import UploadError, save_upload


@admin_bp.route("/profile", methods=["GET", "POST"])
@login_required
def profile():
    item = query_one("SELECT * FROM profile ORDER BY id ASC LIMIT 1") or {}
    form = ProfileForm(data=item)
    if form.validate_on_submit():
        avatar_path = item.get("avatar_path")
        resume_file_path = item.get("resume_file_path")

        if form.avatar.data:
            try:
                upload = save_upload(form.avatar.data, "avatar")
                avatar_path = upload["file_path"]
                execute(
                    """
                    INSERT INTO uploads (original_filename, saved_filename, file_path, mime_type, file_size, upload_purpose, uploader_id)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                    """,
                    (
                        upload["original_filename"],
                        upload["saved_filename"],
                        upload["file_path"],
                        upload["mime_type"],
                        upload["file_size"],
                        upload["upload_purpose"],
                        None,
                    ),
                )
            except UploadError as exc:
                flash(str(exc), "danger")
                return render_template("admin/profile.html", form=form, item=item)

        if form.resume_file.data:
            try:
                upload = save_upload(form.resume_file.data, "resume")
                resume_file_path = upload["file_path"]
            except UploadError as exc:
                flash(str(exc), "danger")
                return render_template("admin/profile.html", form=form, item=item)

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
                SET name = %s, title = %s, city = %s, email = %s, phone = %s, wechat = %s,
                    github_url = %s, website_url = %s, avatar_path = %s, resume_file_path = %s,
                    summary = %s, job_status = %s, is_active = %s
                WHERE id = %s
                """,
                (*params, item["id"]),
            )
        else:
            execute(
                """
                INSERT INTO profile
                (name, title, city, email, phone, wechat, github_url, website_url, avatar_path, resume_file_path, summary, job_status, is_active)
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
    values = {row["setting_key"]: row["setting_value"] for row in rows}
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
                ON DUPLICATE KEY UPDATE setting_value = VALUES(setting_value), setting_type = VALUES(setting_type)
                """,
                (key, value, "boolean" if key == "messages_enabled" else "string"),
            )
        flash("站点设置已保存。", "success")
        return redirect(url_for("admin.settings"))
    return render_template("admin/settings.html", form=form)
```

- [ ] **Step 4: Create admin templates**

Create `app/templates/admin/resource_list.html`:

```html
{% extends "admin/layout.html" %}
{% block title %}{{ config.title }}{% endblock %}
{% block content %}
<div class="d-flex justify-content-between align-items-center mb-3">
  <h1 class="h3">{{ config.title }}</h1>
  <a class="btn btn-primary" href="{{ url_for('admin.resource_create', resource=config.key) }}">新增</a>
</div>
<div class="content-card">
  <div class="table-responsive">
    <table class="table align-middle">
      <thead>
        <tr>
          {% for column in config.list_columns %}<th>{{ column }}</th>{% endfor %}
          <th>操作</th>
        </tr>
      </thead>
      <tbody>
        {% for row in rows %}
          <tr>
            {% for column in config.list_columns %}
              <td>{{ row[column] }}</td>
            {% endfor %}
            <td class="d-flex gap-2">
              <a class="btn btn-sm btn-outline-primary" href="{{ url_for('admin.resource_edit', resource=config.key, item_id=row.id) }}">编辑</a>
              <form method="post" action="{{ url_for('admin.resource_delete', resource=config.key, item_id=row.id) }}">
                <input type="hidden" name="csrf_token" value="{{ csrf_token() }}">
                <button class="btn btn-sm btn-outline-danger" data-confirm="确认删除？" type="submit">删除</button>
              </form>
            </td>
          </tr>
        {% endfor %}
      </tbody>
    </table>
  </div>
</div>
{% endblock %}
```

Create `app/templates/admin/resource_form.html`:

```html
{% extends "admin/layout.html" %}
{% block title %}{{ config.title }}{% endblock %}
{% block content %}
<h1 class="h3 mb-3">{{ config.title }}</h1>
<form method="post" class="content-card">
  {{ form.hidden_tag() }}
  {% for field in form if field.name not in ["csrf_token", "submit"] %}
    <div class="mb-3">
      {{ field.label(class="form-label") }}
      {% if field.type == "BooleanField" %}
        <div class="form-check">{{ field(class="form-check-input") }}</div>
      {% elif field.type == "TextAreaField" %}
        {{ field(class="form-control", rows=5) }}
      {% else %}
        {{ field(class="form-control") }}
      {% endif %}
      {% for error in field.errors %}<div class="text-danger small">{{ error }}</div>{% endfor %}
    </div>
  {% endfor %}
  <div class="d-flex gap-2">
    {{ form.submit(class="btn btn-primary") }}
    <a class="btn btn-outline-secondary" href="{{ url_for('admin.resource_list', resource=config.key) }}">返回</a>
  </div>
</form>
{% endblock %}
```

Create `app/templates/admin/profile.html`:

```html
{% extends "admin/layout.html" %}
{% block title %}个人信息{% endblock %}
{% block content %}
<h1 class="h3 mb-3">个人信息</h1>
<form method="post" enctype="multipart/form-data" class="content-card">
  {{ form.hidden_tag() }}
  <div class="row g-3">
    <div class="col-md-6">{{ form.name.label(class="form-label") }}{{ form.name(class="form-control") }}</div>
    <div class="col-md-6">{{ form.title.label(class="form-label") }}{{ form.title(class="form-control") }}</div>
    <div class="col-md-4">{{ form.city.label(class="form-label") }}{{ form.city(class="form-control") }}</div>
    <div class="col-md-4">{{ form.email.label(class="form-label") }}{{ form.email(class="form-control") }}</div>
    <div class="col-md-4">{{ form.phone.label(class="form-label") }}{{ form.phone(class="form-control") }}</div>
    <div class="col-md-4">{{ form.wechat.label(class="form-label") }}{{ form.wechat(class="form-control") }}</div>
    <div class="col-md-4">{{ form.github_url.label(class="form-label") }}{{ form.github_url(class="form-control") }}</div>
    <div class="col-md-4">{{ form.website_url.label(class="form-label") }}{{ form.website_url(class="form-control") }}</div>
    <div class="col-md-6">
      {{ form.avatar.label(class="form-label") }}
      {{ form.avatar(class="form-control", **{"data-preview-target": "#avatarPreview"}) }}
      {% if item.avatar_path %}
        <img id="avatarPreview" class="avatar mt-3" src="{{ url_for('static', filename=item.avatar_path) }}" alt="头像预览">
      {% else %}
        <img id="avatarPreview" class="avatar mt-3 d-none" alt="头像预览">
      {% endif %}
    </div>
    <div class="col-md-6">{{ form.resume_file.label(class="form-label") }}{{ form.resume_file(class="form-control") }}</div>
    <div class="col-12">{{ form.summary.label(class="form-label") }}{{ form.summary(class="form-control", rows=5) }}</div>
    <div class="col-md-8">{{ form.job_status.label(class="form-label") }}{{ form.job_status(class="form-control") }}</div>
    <div class="col-md-4 d-flex align-items-end">
      <div class="form-check">{{ form.is_active(class="form-check-input") }} {{ form.is_active.label(class="form-check-label") }}</div>
    </div>
    <div class="col-12">{{ form.submit(class="btn btn-primary") }}</div>
  </div>
</form>
{% endblock %}
```

Create `app/templates/admin/messages.html`:

```html
{% extends "admin/layout.html" %}
{% block title %}留言管理{% endblock %}
{% block content %}
<h1 class="h3 mb-3">留言管理</h1>
<div class="content-card">
  <div class="table-responsive">
    <table class="table align-middle">
      <thead><tr><th>姓名</th><th>邮箱</th><th>状态</th><th>时间</th><th>操作</th></tr></thead>
      <tbody>
        {% for row in rows %}
          <tr>
            <td>{{ row.name }}</td>
            <td>{{ row.email }}</td>
            <td><span class="badge text-bg-secondary">{{ row.status }}</span></td>
            <td>{{ row.created_at }}</td>
            <td class="d-flex gap-2">
              <a class="btn btn-sm btn-outline-primary" href="{{ url_for('admin.message_detail', message_id=row.id) }}">查看</a>
              <form method="post" action="{{ url_for('admin.message_delete', message_id=row.id) }}">
                <input type="hidden" name="csrf_token" value="{{ csrf_token() }}">
                <button class="btn btn-sm btn-outline-danger" data-confirm="确认删除留言？" type="submit">删除</button>
              </form>
            </td>
          </tr>
        {% endfor %}
      </tbody>
    </table>
  </div>
</div>
{% endblock %}
```

Create `app/templates/admin/message_detail.html`:

```html
{% extends "admin/layout.html" %}
{% block title %}留言详情{% endblock %}
{% block content %}
<h1 class="h3 mb-3">留言详情</h1>
<div class="row g-3">
  <div class="col-lg-7">
    <div class="content-card">
      <dl class="row mb-0">
        <dt class="col-sm-3">姓名</dt><dd class="col-sm-9">{{ item.name }}</dd>
        <dt class="col-sm-3">邮箱</dt><dd class="col-sm-9">{{ item.email }}</dd>
        <dt class="col-sm-3">手机号</dt><dd class="col-sm-9">{{ item.phone or "" }}</dd>
        <dt class="col-sm-3">IP</dt><dd class="col-sm-9">{{ item.ip_address or "" }}</dd>
        <dt class="col-sm-3">浏览器</dt><dd class="col-sm-9">{{ item.user_agent or "" }}</dd>
        <dt class="col-sm-3">内容</dt><dd class="col-sm-9">{{ item.content }}</dd>
      </dl>
    </div>
  </div>
  <div class="col-lg-5">
    <form method="post" class="content-card">
      {{ form.hidden_tag() }}
      <div class="mb-3">{{ form.status.label(class="form-label") }}{{ form.status(class="form-select") }}</div>
      <div class="mb-3">{{ form.admin_note.label(class="form-label") }}{{ form.admin_note(class="form-control", rows=6) }}</div>
      <div class="d-flex gap-2">
        {{ form.submit(class="btn btn-primary") }}
        <a class="btn btn-outline-secondary" href="{{ url_for('admin.messages') }}">返回</a>
      </div>
    </form>
  </div>
</div>
{% endblock %}
```

Create `app/templates/admin/settings.html`:

```html
{% extends "admin/layout.html" %}
{% block title %}站点设置{% endblock %}
{% block content %}
<h1 class="h3 mb-3">站点设置</h1>
<form method="post" class="content-card">
  {{ form.hidden_tag() }}
  <div class="mb-3">{{ form.site_title.label(class="form-label") }}{{ form.site_title(class="form-control") }}</div>
  <div class="mb-3">{{ form.seo_description.label(class="form-label") }}{{ form.seo_description(class="form-control") }}</div>
  <div class="mb-3">{{ form.icp_text.label(class="form-label") }}{{ form.icp_text(class="form-control") }}</div>
  <div class="form-check mb-3">{{ form.messages_enabled(class="form-check-input") }} {{ form.messages_enabled.label(class="form-check-label") }}</div>
  {{ form.submit(class="btn btn-primary") }}
</form>
{% endblock %}
```

- [ ] **Step 5: Run admin tests**

Run:

```bash
pytest tests/test_admin_resources.py -v
```

Expected: all admin resource tests pass.

- [ ] **Step 6: Commit**

Run:

```bash
git add app tests/test_admin_resources.py
git commit -m "feat: complete admin management pages"
```

Expected: commit succeeds.

## Task 9: Deployment Files and README

**Files:**

- Create: `deployment/gunicorn.conf.py`
- Create: `deployment/nginx.conf.example`
- Create: `deployment/resume-site.service.example`
- Create: `README.md`

- [ ] **Step 1: Create Gunicorn config**

Create `deployment/gunicorn.conf.py`:

```python
bind = "127.0.0.1:8000"
workers = 3
worker_class = "sync"
timeout = 60
accesslog = "-"
errorlog = "-"
loglevel = "info"
```

- [ ] **Step 2: Create Nginx example**

Create `deployment/nginx.conf.example`:

```nginx
server {
    listen 80;
    server_name example.com;

    client_max_body_size 8m;

    location /static/ {
        alias /opt/resume-site/app/static/;
        expires 7d;
        add_header Cache-Control "public";
    }

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

- [ ] **Step 3: Create systemd example**

Create `deployment/resume-site.service.example`:

```ini
[Unit]
Description=Resume Site Gunicorn Service
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=/opt/resume-site
EnvironmentFile=/opt/resume-site/.env
ExecStart=/opt/resume-site/.venv/bin/gunicorn -c deployment/gunicorn.conf.py run:app
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
```

- [ ] **Step 4: Create README**

Create `README.md`:

```markdown
# Resume Site

Flask + MySQL responsive personal resume website with a custom Bootstrap administrator backend.

## Local Setup

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
```

Edit `.env` and set `MYSQL_HOST`, `MYSQL_PORT`, `MYSQL_USER`, `MYSQL_PASSWORD`, `MYSQL_DATABASE`, `SECRET_KEY`, and `ADMIN_PASSWORD`.

## Database Initialization

Manual DMS path:

1. Open Aliyun DMS.
2. Select the existing empty database.
3. Execute `database/schema.sql`.
4. Configure `.env` on the web server.
5. Run `flask seed-db`.

Command-line path:

```bash
flask init-db
flask seed-db
```

## Run Locally

```bash
flask --app run run --debug
```

Public site: `http://127.0.0.1:5000/`

Admin login: `http://127.0.0.1:5000/admin/login`

## Production

Use the files in `deployment/` as examples for Gunicorn, Nginx, and systemd. The web server and MySQL server are separate; configure the RDS host and credentials in `.env`.

## Tests

```bash
pytest -v
```
```

- [ ] **Step 5: Commit**

Run:

```bash
git add deployment README.md
git commit -m "docs: add deployment guide"
```

Expected: commit succeeds.

## Task 10: Full Verification and Browser Check

**Files:**

- Modify files only if verification reveals a specific failure.

- [ ] **Step 1: Run the full test suite**

Run:

```bash
pytest -v
```

Expected: every collected test passes.

- [ ] **Step 2: Run a syntax compile check**

Run:

```bash
python -m compileall app
```

Expected: command exits with code `0`.

- [ ] **Step 3: Start the development server**

Run:

```bash
flask --app run run --debug --port 5000
```

Expected: Flask serves on `http://127.0.0.1:5000`.

- [ ] **Step 4: Verify public page and admin login in a browser**

Open:

```text
http://127.0.0.1:5000/
http://127.0.0.1:5000/admin/login
```

Expected:

- Public page renders without template errors.
- Navbar collapses on mobile width.
- Back-to-top button appears after scrolling.
- Admin login page renders.
- Text does not overlap at desktop width and mobile width.

- [ ] **Step 5: Final status check**

Run:

```bash
git status --short
```

Expected: no uncommitted changes after any final fixes are committed.

## Self-Review Notes

- Spec coverage: tasks cover project skeleton, configuration, database schema, seed data, Flask CLI, authentication, public homepage, message submission, upload validation, admin dashboard, admin CRUD, profile, messages, settings, deployment files, README, tests, and browser verification.
- Database separation: `.env.example`, `app/config.py`, `database/schema.sql`, CLI commands, and README all assume the MySQL server is separate from the web server.
- Security coverage: password hashing, CSRF, rate limits, parameterized SQL, upload type/size checks, UUID filenames, secure session flags, and least-privilege database guidance are covered.
- Remaining implementation risk: Task 8 contains the most surface area because it completes multiple admin screens; run its route tests immediately after implementation before moving to deployment docs.
