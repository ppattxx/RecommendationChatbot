"""Thin preference routes – URL mapping only, delegates to controllers."""
from flask import Blueprint
from backend.app.controllers.preference_controller import (
    handle_get_user_preferences,
    handle_get_preferences_summary,
)

preferences_bp = Blueprint('preferences', __name__)


@preferences_bp.route('/user-preferences', methods=['GET'])
def get_user_preferences():
    return handle_get_user_preferences()


@preferences_bp.route('/user-preferences/summary', methods=['GET'])
def get_preferences_summary():
    return handle_get_preferences_summary()
