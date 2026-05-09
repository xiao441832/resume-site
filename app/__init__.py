import os
from pathlib import Path

from dotenv import load_dotenv
from flask import Flask

from app.config import CONFIG_MAP, apply_env_config, validate_production_config
from app.extensions import csrf, limiter


def create_app(config_name: str | None = None) -> Flask:
    load_dotenv()
    selected_config = config_name or os.getenv("FLASK_ENV", "development")

    app = Flask(__name__)
    app.config.from_object(CONFIG_MAP.get(selected_config, CONFIG_MAP["development"]))
    apply_env_config(app)
    if selected_config == "production":
        validate_production_config(app)

    Path(app.config["UPLOAD_FOLDER"]).mkdir(parents=True, exist_ok=True)

    csrf.init_app(app)
    limiter.init_app(app)
    app.extensions["limiter"] = limiter

    from app import db

    app.teardown_appcontext(db.close_db)

    return app
