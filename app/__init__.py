import os
from pathlib import Path

from dotenv import load_dotenv
from flask import Flask, flash, redirect, url_for
from flask_wtf.csrf import CSRFError

from app.config import CONFIG_MAP, apply_env_config, validate_production_config
from app.extensions import csrf, limiter


def create_app(config_name: str | None = None) -> Flask:
    selected_config = config_name or os.getenv("FLASK_ENV", "development")
    if config_name is None:
        load_dotenv()
        selected_config = os.getenv("FLASK_ENV", selected_config)

    app = Flask(__name__)
    app.config.from_object(CONFIG_MAP.get(selected_config, CONFIG_MAP["development"]))
    if selected_config != "testing":
        apply_env_config(app)
    if selected_config == "production":
        validate_production_config(app)

    Path(app.config["UPLOAD_FOLDER"]).mkdir(parents=True, exist_ok=True)

    csrf.init_app(app)
    limiter.init_app(app)
    app.extensions["limiter"] = limiter

    from app import cli, db

    app.teardown_appcontext(db.close_db)
    cli.register_cli(app)

    from app.admin.routes import admin_bp
    from app.auth.routes import auth_bp
    from app.public.routes import public_bp

    app.register_blueprint(public_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(admin_bp)

    @app.errorhandler(CSRFError)
    def handle_csrf_error(error):
        flash("页面安全校验已过期，请刷新页面后重新提交。", "warning")
        return redirect(url_for("public.index") + "#contact")

    @app.context_processor
    def inject_admin_resources():
        from app.admin.resources import RESOURCE_CONFIGS

        return {"resource_configs": RESOURCE_CONFIGS}

    return app
