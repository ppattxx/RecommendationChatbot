"""Thin recommendation routes – URL mapping only, delegates to controllers."""
from flask import Blueprint
from backend.app.controllers.recommendation_controller import (
    handle_get_recommendations,
    handle_get_categories,
    handle_get_trending,
    handle_get_top5,
    handle_get_all_ranked,
)

recommendations_bp = Blueprint('recommendations', __name__)


@recommendations_bp.route('/recommendations', methods=['GET'])
def get_recommendations():
    return handle_get_recommendations()


@recommendations_bp.route('/recommendations/categories', methods=['GET'])
def get_categories():
    return handle_get_categories()


@recommendations_bp.route('/recommendations/trending', methods=['GET'])
def get_trending():
    return handle_get_trending()


@recommendations_bp.route('/recommendations/top5', methods=['GET'])
def get_top5_recommendations():
    return handle_get_top5()


@recommendations_bp.route('/recommendations/all-ranked', methods=['GET'])
def get_all_ranked_recommendations():
    return handle_get_all_ranked()
