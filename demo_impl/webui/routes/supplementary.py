from flask import jsonify

from demo_impl.webui import app, __version__


@app.route('/version')
@app.route('/liveness')
def version_endpoint():
    res = {
        "version": __version__,
        "short_name": "VRC-T70 Demo Application",
        "long_name": "Flask based demo application for VRC-T70 Python package (SQLite db used)"
    }
    return jsonify(res)
