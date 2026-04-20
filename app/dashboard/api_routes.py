from flask import Blueprint, jsonify

api_blueprint = Blueprint("api", __name__)


@api_blueprint.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok"})


@api_blueprint.route("/status", methods=["GET"])
def status():
    return jsonify(
        {
            "system": "Industrial Safety Monitoring",
            "state": "running",
        }
    )