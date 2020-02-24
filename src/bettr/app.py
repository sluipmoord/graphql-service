import logging
import os

from flask import Flask


def create_app(config=None):
    import_name = __name__.split(".")[0]
    app = Flask(import_name)
    app.config.from_object(import_name + ".settings")
    envvar = import_name.upper() + "_SETTINGS"
    if envvar in os.environ:
        app.config.from_envvar(envvar)
    if config:
        app.config.from_pyfile(config)

    level = getattr(logging, app.config["LOGGER_LEVEL"].upper())
    app.logger.setLevel(level)

    from .database import db, migrate

    db.init_app(app)
    migrate.init_app(app, db)

    from .cli import cognito_cli

    app.cli.add_command(cognito_cli)

    from .views import api

    app.register_blueprint(api)
    app.logger.info(f"Flask app '{app.name}' created successfully.")

    return app
