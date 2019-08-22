from demo_impl.webui.__version__ import __version__

from flask import jsonify

from loguru import logger

from ..api_blueprint import api_blueprint


@api_blueprint.route("/version")
@api_blueprint.route("/liveness")
def version_endpoint():
    res = {
        "version": __version__,
        "short_name": "VRC-T70 Demo Application",
        "long_name": "Flask based demo application for VRC-T70 Python package (SQLite db used)"
    }

    logger.info("test-2")
    return jsonify(res)
