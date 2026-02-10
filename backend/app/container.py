"""
Service Container – simple dependency injection for Flask.
Replaces global mutable singletons with a lazy-loading container
stored on the Flask app instance.

Usage in controllers:
    from flask import current_app
    engine = current_app.container.recommendation_engine
"""
from backend.app.utils.logger import get_logger

logger = get_logger("container")


class ServiceContainer:
    """Lazy-loading service container attached to a Flask app."""

    def __init__(self, app=None):
        self._app = app
        self._chatbot_service = None
        self._recommendation_engine = None

    # ─── Chatbot Service ──────────────────────────────────────

    @property
    def chatbot_service(self):
        if self._chatbot_service is None:
            from backend.app.services.chatbot_engine import ChatbotService
            self._chatbot_service = ChatbotService()
            logger.info("ChatbotService initialized via container")
        return self._chatbot_service

    # ─── Recommendation Engine ────────────────────────────────

    @property
    def recommendation_engine(self):
        if self._recommendation_engine is None:
            from pathlib import Path
            from backend.app.services.recommendation_engine import ContentBasedRecommendationEngine

            csv_path = str(Path(__file__).parent.parent.parent / 'data' / 'restaurants_entitas.csv')
            logger.info(f"Loading recommendation engine from {csv_path}")
            self._recommendation_engine = ContentBasedRecommendationEngine(data_path=csv_path)
            logger.info("ContentBasedRecommendationEngine initialized via container")
        return self._recommendation_engine

    # ─── Registration ─────────────────────────────────────────

    @classmethod
    def init_app(cls, app):
        """Register the container on a Flask app instance."""
        container = cls(app)
        app.container = container
        logger.info("ServiceContainer registered on app")
        return container
