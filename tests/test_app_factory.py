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