from demo_impl.shared.models.devices import VrcT70Device

from flask import jsonify

from loguru import logger

from ..api_blueprint import api_blueprint


@api_blueprint.route("/devices_list")
def devices_list():
    from demo_impl.webui import db

    logger.info("loading devices list")
    devices = db.session.query(VrcT70Device).all()

    res = {
        "devices": [
            {
                "device_id": item.device_id,
                "device_name": item.device_name

            } for item in devices
        ]
    }
    return jsonify(res)
