"""
Centralized error handling for the Flask application.
Provides:
  - Custom exception hierarchy (APIError, NotFoundError, ValidationError, etc.)
  - @handle_errors decorator for controllers
  - Flask error handler registration
  - Consistent JSON error response format with request_id correlation
"""
import functools
import traceback
import uuid as _uuid

from flask import jsonify, request, g
from backend.app.utils.logger import get_logger

logger = get_logger("error_handler")


# ─── Exception Hierarchy ─────────────────────────────────────────

class APIError(Exception):
    """Base API error class."""
    def __init__(self, message, status_code=400, payload=None):
        super().__init__()
        self.message = message
        self.status_code = status_code
        self.payload = payload

    def to_dict(self):
        rv = dict(self.payload or ())
        rv['success'] = False
        rv['error'] = self.message
        rv['request_id'] = getattr(g, 'request_id', None)
        return rv


class NotFoundError(APIError):
    def __init__(self, message="Resource not found"):
        super().__init__(message, status_code=404)


class ValidationError(APIError):
    def __init__(self, message="Invalid request", field=None):
        payload = {'field': field} if field else None
        super().__init__(message, status_code=422, payload=payload)


class ServiceUnavailableError(APIError):
    def __init__(self, message="Service temporarily unavailable"):
        super().__init__(message, status_code=503)


# ─── Controller Decorator ────────────────────────────────────────

def handle_errors(fn):
    """Decorator that wraps a controller function with consistent error handling.

    Catches:
      - DTOValidationError → 422
      - APIError subclasses → their status_code
      - Unhandled exceptions → 500 with logged traceback
    """
    @functools.wraps(fn)
    def wrapper(*args, **kwargs):
        try:
            return fn(*args, **kwargs)
        except APIError:
            raise  # let Flask errorhandler handle it
        except Exception as e:
            # Check if it's a DTO validation error
            from backend.app.utils.dto import DTOValidationError
            if isinstance(e, DTOValidationError):
                raise ValidationError(
                    message=e.message,
                    field=getattr(e, 'field_name', None)
                )

            # Unhandled exception → 500
            request_id = getattr(g, 'request_id', 'unknown')
            logger.error(
                f"Unhandled error in {fn.__name__} "
                f"[request_id={request_id}]: {e}\n"
                f"{traceback.format_exc()}"
            )
            return jsonify({
                'success': False,
                'error': 'Internal server error',
                'request_id': request_id,
            }), 500

    return wrapper


# ─── Flask Error Handler Registration ─────────────────────────────

def register_error_handlers(app):
    """Register centralized error handlers on the Flask app."""

    @app.errorhandler(APIError)
    def handle_api_error(error):
        response = jsonify(error.to_dict())
        response.status_code = error.status_code
        logger.warning(
            f"API Error ({error.status_code}): {error.message} "
            f"[request_id={getattr(g, 'request_id', None)}]"
        )
        return response

    @app.errorhandler(404)
    def handle_not_found(error):
        return jsonify({
            'success': False,
            'error': 'Endpoint tidak ditemukan',
            'request_id': getattr(g, 'request_id', None),
        }), 404

    @app.errorhandler(405)
    def handle_method_not_allowed(error):
        return jsonify({
            'success': False,
            'error': f'Method {request.method} tidak diizinkan untuk {request.path}',
            'request_id': getattr(g, 'request_id', None),
        }), 405

    @app.errorhandler(500)
    def handle_internal_error(error):
        request_id = getattr(g, 'request_id', None)
        logger.error(f"Internal Server Error [request_id={request_id}]: {error}")
        return jsonify({
            'success': False,
            'error': 'Internal server error',
            'request_id': request_id,
        }), 500
