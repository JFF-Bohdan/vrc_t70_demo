from flask import Flask


app = Flask(__name__)
__version__ = "0.1.1"

from .routes import *  # noqa
