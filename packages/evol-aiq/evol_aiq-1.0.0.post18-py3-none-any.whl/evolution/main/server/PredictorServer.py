from flask import Flask, request, jsonify
import logging
from evolution.main.server.controllers.ControllerFactory import create_prediction_bp
from evolution.main.server.services.PredictionService import PredictionService


class PredictorServer:
    logger = logging.getLogger(__name__)
    prediction_service: PredictionService = None
    app: Flask = None
    config: dict = None

    def __init__(self, config: dict):
        self.app = Flask(__name__)
        self.config = config

        #services
        prediction_service = PredictionService(config)

        self.app.register_blueprint(create_prediction_bp(prediction_service, "1"))

        # --- Register Auth Filter ---
        self._register_auth_filter()

    def _register_auth_filter(self):
        """Global authentication filter using before_request"""

        @self.app.before_request
        def auth_filter():
            # Allow health or public routes without auth if needed
            if request.endpoint in ['health_check']:
                return None

            try:
                data = request.get_json(silent=True) or {}
            except Exception:
                return jsonify({"error": "Invalid JSON"}), 400

            username = data.get("username")
            password = data.get("password")
            

            # Basic authentication check (replace with your real logic)
            if username != self.config['app_sever']["auth_username"] or password != self.config['app_sever']["auth_password"]:
                return jsonify({"error": "Unauthorized"}), 401
            return None

    def run(self):
        self.app.run(port=self.config['port'])

    def get_app(self) -> Flask:
        return self.app
