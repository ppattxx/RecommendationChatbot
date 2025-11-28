"""
Backend routes package
"""
from .chat_routes import chat_bp
from .preferences_routes import preferences_bp

__all__ = ['chat_bp', 'preferences_bp']
