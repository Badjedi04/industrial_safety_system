import os
import sys
from flask import Flask, render_template

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from app.dashboard.api_routes import api_blueprint


def create_dashboard_app() -> Flask:
    app = Flask(
        __name__,
        static_folder="static",
        template_folder="templates",
    )
    app.register_blueprint(api_blueprint, url_prefix="/api")

    @app.route("/")
    def index():
        return render_template("index.html")

    return app


if __name__ == "__main__":
    app = create_dashboard_app()
    app.run(host="0.0.0.0", port=5000, debug=True)