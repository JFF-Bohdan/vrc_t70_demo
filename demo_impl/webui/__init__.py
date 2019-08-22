from flask import Flask
from flask.logging import default_handler

from .api_blueprint.api_blueprint import api_blueprint


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


def create_app(additional_logger):
    app = Flask(__name__)

    app.logger.removeHandler(default_handler)

    log = WrapperForLoguru(additional_logger)
    log.init_app(app)

    app.register_blueprint(api_blueprint, url_prefix='/api/v1')

    return app
