from pathlib import Path

import pytest

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


def test_create_app_applies_env_values_at_runtime(monkeypatch):
    monkeypatch.setenv("MYSQL_HOST", "db.internal")
    monkeypatch.setenv("SECRET_KEY", "runtime-secret")
    monkeypatch.setenv("SESSION_COOKIE_SECURE", "1")
    monkeypatch.setenv("RATELIMIT_STORAGE_URI", "memory://")

    app = create_app("development")

    assert app.config["MYSQL_HOST"] == "db.internal"
    assert app.config["SECRET_KEY"] == "runtime-secret"
    assert app.config["SESSION_COOKIE_SECURE"] is True
    assert app.config["RATELIMIT_STORAGE_URI"] == "memory://"


@pytest.mark.parametrize("secret_key", [None, "", "   ", "dev-secret-change-me"])
def test_create_app_production_rejects_missing_or_default_secret_key(
    monkeypatch, secret_key
):
    if secret_key is None:
        monkeypatch.delenv("SECRET_KEY", raising=False)
    else:
        monkeypatch.setenv("SECRET_KEY", secret_key)

    with pytest.raises(RuntimeError, match="SECRET_KEY"):
        create_app("production")


def test_create_app_production_forces_secure_session_cookie(monkeypatch):
    monkeypatch.setenv("SECRET_KEY", "valid-production-secret")
    monkeypatch.setenv("SESSION_COOKIE_SECURE", "0")

    app = create_app("production")

    assert app.config["SESSION_COOKIE_SECURE"] is True
