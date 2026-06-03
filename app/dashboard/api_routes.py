import logging
import os
from flask import Blueprint, jsonify, request
from app.core.config_loader import load_config
from app.database.db_manager import DBManager

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
config = load_config(os.path.join(ROOT_DIR, "config.yaml"))
logger = logging.getLogger("dashboard")
db = DBManager(config, logger)

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


@api_blueprint.route("/current", methods=["GET"])
def current():
    latest_event = db.get_latest_event()
    if latest_event is None:
        return jsonify({"message": "no_data"}), 204
    return jsonify(latest_event)


@api_blueprint.route("/events", methods=["GET"])
def events():
    limit = request.args.get("limit", default=50, type=int)
    return jsonify(db.get_recent_events(limit))