from flask import Flask
from app.dashboard.api_routes import api_blueprint


def create_dashboard_app() -> Flask:
    app = Flask(__name__)
    app.register_blueprint(api_blueprint, url_prefix="/api")
    return app


if __name__ == "__main__":
    app = create_dashboard_app()
    app.run(host="0.0.0.0", port=5000, debug=True)