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
    RATELIMIT_STORAGE_URI = os.getenv("RATELIMIT_STORAGE_URI", "memory://")


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


def apply_env_config(app) -> None:
    app.config.update(
        SECRET_KEY=os.getenv("SECRET_KEY", app.config["SECRET_KEY"]),
        MYSQL_HOST=os.getenv("MYSQL_HOST", app.config["MYSQL_HOST"]),
        MYSQL_PORT=int(os.getenv("MYSQL_PORT", str(app.config["MYSQL_PORT"]))),
        MYSQL_USER=os.getenv("MYSQL_USER", app.config["MYSQL_USER"]),
        MYSQL_PASSWORD=os.getenv("MYSQL_PASSWORD", app.config["MYSQL_PASSWORD"]),
        MYSQL_DATABASE=os.getenv("MYSQL_DATABASE", app.config["MYSQL_DATABASE"]),
        MYSQL_CHARSET=os.getenv("MYSQL_CHARSET", app.config["MYSQL_CHARSET"]),
        MAX_IMAGE_UPLOAD_MB=int(
            os.getenv("MAX_IMAGE_UPLOAD_MB", str(app.config["MAX_IMAGE_UPLOAD_MB"]))
        ),
        MAX_PDF_UPLOAD_MB=int(
            os.getenv("MAX_PDF_UPLOAD_MB", str(app.config["MAX_PDF_UPLOAD_MB"]))
        ),
        SESSION_COOKIE_SECURE=_bool_env(
            "SESSION_COOKIE_SECURE", app.config["SESSION_COOKIE_SECURE"]
        ),
        RATELIMIT_STORAGE_URI=os.getenv(
            "RATELIMIT_STORAGE_URI", app.config["RATELIMIT_STORAGE_URI"]
        ),
    )


def validate_production_config(app) -> None:
    secret_key = str(app.config.get("SECRET_KEY") or "").strip()
    if not secret_key or secret_key == "dev-secret-change-me":
        raise RuntimeError("SECRET_KEY must be set to a secure value in production.")
    app.config["SESSION_COOKIE_SECURE"] = True
