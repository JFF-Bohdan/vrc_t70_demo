from flask import Flask

from .api_blueprint.api_blueprint import api_blueprint


app = Flask(__name__)
app.register_blueprint(api_blueprint, url_prefix='/api/v1')
