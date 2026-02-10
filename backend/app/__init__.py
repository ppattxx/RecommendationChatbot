"""Flask application factory."""
from flask import Flask
from flask_cors import CORS
from backend.app.extensions import db
from backend.app.container import ServiceContainer
from backend.app.utils.error_handlers import register_error_handlers
from backend.app.utils.logger import get_logger, setup_request_logging
from backend.config.settings import DATABASE_CONFIG

logger = get_logger("app")


def create_app():
    """Create and configure the Flask application."""
    app = Flask(__name__)

    # ─── Configuration ────────────────────────────────────────
    app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{DATABASE_CONFIG['sqlite']['path']}"
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SQLALCHEMY_ECHO'] = DATABASE_CONFIG['sqlite'].get('echo', False)

    # ─── Extensions ───────────────────────────────────────────
    db.init_app(app)
    CORS(app)

    # ─── Dependency Injection Container ───────────────────────
    ServiceContainer.init_app(app)

    # ─── Request Logging Middleware ───────────────────────────
    setup_request_logging(app)

    # ─── Blueprints ───────────────────────────────────────────
    from backend.app.routes.chat_routes import chat_bp
    from backend.app.routes.recommendation_routes import recommendations_bp
    from backend.app.routes.preference_routes import preferences_bp

    app.register_blueprint(chat_bp, url_prefix='/api/chat')
    app.register_blueprint(recommendations_bp, url_prefix='/api')
    app.register_blueprint(preferences_bp, url_prefix='/api')

    # ─── Health Check ─────────────────────────────────────────
    @app.route('/api/health', methods=['GET'])
    def health_check():
        """Simple health check endpoint."""
        return {'success': True, 'status': 'healthy', 'service': 'chatbot-api'}, 200

    # ─── Error handlers ──────────────────────────────────────
    register_error_handlers(app)

    # ─── Create DB tables ─────────────────────────────────────
    with app.app_context():
        from backend.app.models import database  # noqa: ensure models are imported
        db.create_all()

    logger.info("Flask app created successfully")
    return app
