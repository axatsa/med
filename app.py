import os
from flask import Flask, jsonify, send_from_directory
from flask_cors import CORS
from config import Config
from models.database import db
from routes.predict import predict_bp
from routes.patients import patients_bp
from routes.report import report_bp


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Ensure data directory exists
    os.makedirs(os.path.join(os.path.dirname(__file__), "data"), exist_ok=True)

    CORS(app, resources={r"/api/*": {"origins": "*"}})
    db.init_app(app)

    with app.app_context():
        db.create_all()

    app.register_blueprint(predict_bp, url_prefix="/api")
    app.register_blueprint(patients_bp, url_prefix="/api")
    app.register_blueprint(report_bp, url_prefix="/api")

    frontend_dir = os.path.join(os.path.dirname(__file__), "frontend")

    @app.get("/")
    def index():
        return send_from_directory(frontend_dir, "index.html")

    @app.get("/frontend/<path:filename>")
    def frontend_static(filename):
        return send_from_directory(frontend_dir, filename)

    @app.get("/api")
    def api_index():
        return jsonify({
            "project": "PE Predictor API",
            "version": "1.0.0",
            "status": "running",
            "endpoints": {
                "POST /api/predict": "Calculate preeclampsia risk",
                "GET  /api/patients": "List all patients",
                "GET  /api/patients/:id": "Get patient by ID",
                "DELETE /api/patients/:id": "Delete patient",
                "GET  /api/stats": "Risk level statistics",
                "GET  /api/report/:patient_id": "Download PDF report",
                "GET  /api/health": "Health check",
            }
        })

    @app.get("/api/health")
    def health():
        return jsonify({"status": "ok", "version": "1.0.0"})

    @app.errorhandler(404)
    def not_found(e):
        return jsonify({"success": False, "error": "Not found"}), 404

    @app.errorhandler(500)
    def server_error(e):
        return jsonify({"success": False, "error": "Internal server error"}), 500

    return app


if __name__ == "__main__":
    application = create_app()
    port = int(os.environ.get("PORT", 8000))
    application.run(debug=True, host="0.0.0.0", port=port)
