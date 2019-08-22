from flask import Flask
from flask.logging import default_handler
from flask_log_request_id import RequestID, current_request_id
from flask_sqlalchemy import SQLAlchemy

from .api_blueprint.api_blueprint import api_blueprint

db = SQLAlchemy()
# from demo_impl.shared.models.shared import set_base

# set_base(db.Model)


class WrapperForLoguru(object):
    """
    This class is used to config loguru
    """

    def __init__(self, logger, app=None):
        self.logger = logger
        if app is not None:
            self.init_app(app)

    def init_app(self, app):
        """
        This is used to initialize logger with your app object
        """

        if not hasattr(app, "extensions"):
            app.extensions = {}

        app.extensions.setdefault("loguru", {})
        app.extensions["loguru"][self] = self.logger


def create_app(additional_logger, db_connection_uri, root_path=None):
    app = Flask(__name__, root_path=root_path)

    app.logger.removeHandler(default_handler)

    app.config['SQLALCHEMY_DATABASE_URI'] = db_connection_uri
    db.init_app(app)
    RequestID(app)

    log = WrapperForLoguru(additional_logger)
    log.init_app(app)

    app.register_blueprint(api_blueprint, url_prefix='/api/v1')

    return app
