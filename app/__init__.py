from flask import Flask

from .auth import auth_bp
from .db import init_db
from .pages import pages_bp
from .protected import protected_bp


def create_app() -> Flask:
    app = Flask(__name__)
    app.config.from_object("app.config.Config")

    init_db(app.config["DATABASE_PATH"])

    app.register_blueprint(auth_bp, url_prefix="/api/auth")
    app.register_blueprint(protected_bp, url_prefix="/api")
    app.register_blueprint(pages_bp)

    return app
