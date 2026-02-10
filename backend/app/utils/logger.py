"""
Logging with request context and correlation IDs.
Provides:
  - ChatbotLogger: thin wrapper around stdlib logging
  - RequestContextFilter: injects request_id, endpoint, method
  - setup_request_logging(): before/after_request hooks
  - get_logger(): factory function
"""
import logging
import logging.config
import uuid
import time
from pathlib import Path
from typing import Optional
from datetime import datetime

from backend.config.settings import LOGGING_CONFIG, LOGS_DIR


# ─── Request Context Filter ──────────────────────────────────────

class RequestContextFilter(logging.Filter):
    """Inject Flask request context into every log record."""

    def filter(self, record):
        try:
            from flask import g, request as flask_request
            record.request_id = getattr(g, 'request_id', '-')
            record.endpoint = getattr(flask_request, 'endpoint', '-') or '-'
            record.method = getattr(flask_request, 'method', '-')
        except RuntimeError:
            # Outside of request context
            record.request_id = '-'
            record.endpoint = '-'
            record.method = '-'
        return True


# ─── Structured Formatter ────────────────────────────────────────

LOG_FORMAT = (
    '%(asctime)s | %(levelname)-8s | %(name)-20s '
    '| req=%(request_id)s | %(method)s %(endpoint)s '
    '| %(message)s'
)


# ─── Logger Class ────────────────────────────────────────────────

class ChatbotLogger:
    """Thin wrapper around stdlib logging with structured helpers."""

    def __init__(self, name: str = "chatbot", log_file: Optional[str] = None):
        self.name = name
        self.log_file = log_file or str(LOGS_DIR / f"{name}.log")
        self._setup_logger()

    def _setup_logger(self):
        LOGS_DIR.mkdir(exist_ok=True)
        try:
            config = LOGGING_CONFIG.copy()
            config['handlers']['file']['filename'] = self.log_file
            logging.config.dictConfig(config)
        except Exception:
            logging.basicConfig(level=logging.INFO, format=LOG_FORMAT)

        self.logger = logging.getLogger(self.name)

        # Add request-context filter if not already added
        if not any(isinstance(f, RequestContextFilter) for f in self.logger.filters):
            self.logger.addFilter(RequestContextFilter())

    # ─── Core logging methods ─────────────────────────────────

    def info(self, message: str, **kwargs):
        self.logger.info(message, extra=kwargs, stacklevel=2)

    def debug(self, message: str, **kwargs):
        self.logger.debug(message, extra=kwargs, stacklevel=2)

    def warning(self, message: str, **kwargs):
        self.logger.warning(message, extra=kwargs, stacklevel=2)

    def error(self, message: str, **kwargs):
        self.logger.error(message, extra=kwargs, stacklevel=2)

    def critical(self, message: str, **kwargs):
        self.logger.critical(message, extra=kwargs, stacklevel=2)

    # ─── Domain-specific logging helpers ─────────────────────

    def log_user_query(self, session_id: str, query: str, device_token: str = ""):
        self.info(
            f"User query | session={session_id} | "
            f"device={device_token} | query={query[:80]}"
        )

    def log_recommendation(self, query: str, count: int, avg_score: float):
        self.info(
            f"Recommendations generated | query={query[:50]} | "
            f"count={count} | avg_score={avg_score:.4f}"
        )

    def log_error(self, error_type: str, error_message: str, **context):
        self.error(
            f"{error_type}: {error_message} | context={context}"
        )

    def log_performance(self, operation: str, duration: float, **metrics):
        self.debug(
            f"Perf | {operation} | {duration:.3f}s | {metrics}"
        )


# ─── Singleton Cache ─────────────────────────────────────────────

_logger_cache: dict = {}
_default_logger = None


def get_logger(name: str = "chatbot") -> ChatbotLogger:
    """Get or create a named logger instance."""
    global _default_logger
    if name == "chatbot":
        if _default_logger is None:
            _default_logger = ChatbotLogger()
        return _default_logger
    if name not in _logger_cache:
        _logger_cache[name] = ChatbotLogger(name)
    return _logger_cache[name]


# ─── Flask Request Middleware ─────────────────────────────────────

def setup_request_logging(app):
    """Register before/after_request hooks for request-scoped logging."""

    @app.before_request
    def _before_request():
        from flask import g, request
        g.request_id = request.headers.get('X-Request-ID', uuid.uuid4().hex[:12])
        g.request_start = time.time()

    @app.after_request
    def _after_request(response):
        from flask import g, request
        duration = time.time() - getattr(g, 'request_start', time.time())
        status = response.status_code

        # Skip noisy health checks
        if request.path == '/api/health':
            return response

        level = 'info'
        if status >= 500:
            level = 'error'
        elif status >= 400:
            level = 'warning'

        log_fn = getattr(get_logger("http"), level)
        log_fn(
            f"{request.method} {request.path} → {status} "
            f"({duration:.3f}s)"
        )

        # Add request_id to response headers
        response.headers['X-Request-ID'] = getattr(g, 'request_id', '')
        return response