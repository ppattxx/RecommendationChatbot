"""
Recommendation Controller – handles request/response for recommendation endpoints.
Uses: DTO validation, @handle_errors decorator, DI via container.
"""
from datetime import datetime, timedelta
from collections import Counter
from flask import request, jsonify, current_app

from backend.app.extensions import db
from backend.app.models.database import ChatHistory
from backend.app.utils.dto import RecommendationQueryDTO
from backend.app.utils.serializers import serialize_restaurant_from_object
from backend.app.utils.error_handlers import handle_errors, ServiceUnavailableError
from backend.app.utils.logger import get_logger

logger = get_logger("recommendation_controller")


# ─── Shared helpers ───────────────────────────────────────────────

def _get_engine():
    """Get recommendation engine from DI container."""
    engine = current_app.container.recommendation_engine
    if engine is None:
        raise ServiceUnavailableError("Recommendation system unavailable")
    return engine


def _extract_user_preferences(session_id=None, device_token=None):
    """Extract aggregated user preferences from ALL chat history."""
    query = ChatHistory.query
    if session_id:
        query = query.filter_by(session_id=session_id)
    elif device_token:
        query = query.filter_by(device_token=device_token)
    else:
        return None

    chat_history = query.order_by(ChatHistory.timestamp.desc()).all()
    if not chat_history:
        return None

    cuisines, locations, moods, prices = [], [], [], []
    for chat in chat_history:
        if chat.extracted_cuisine:
            cuisines.extend([c.strip() for c in chat.extracted_cuisine.split(',')])
        if chat.extracted_location:
            locations.extend([l.strip() for l in chat.extracted_location.split(',')])
        if chat.extracted_mood:
            moods.extend([m.strip() for m in chat.extracted_mood.split(',')])
        if chat.extracted_price:
            prices.extend([p.strip() for p in chat.extracted_price.split(',')])

    return {
        'preferred_cuisines': dict(Counter(cuisines).most_common(10)),
        'preferred_locations': dict(Counter(locations).most_common(10)),
        'preferred_moods': dict(Counter(moods).most_common(5)),
        'price_preferences': dict(Counter(prices).most_common(3)),
        'total_conversations': len(chat_history),
    }


def _build_query_from_preferences(user_preferences):
    """Build a search query string from user preferences."""
    parts = []
    if user_preferences.get('preferred_cuisines'):
        parts.extend(list(user_preferences['preferred_cuisines'].keys())[:3])
    if user_preferences.get('preferred_locations'):
        parts.extend(list(user_preferences['preferred_locations'].keys())[:2])
    return ' '.join(parts)


def _serialize_recommendation(rec):
    """Convert a Recommendation object to API-response dict."""
    rest = rec.restaurant
    about_text = ''
    if isinstance(rest.about, str):
        about_text = rest.about[:200] + '...' if len(rest.about) > 200 else rest.about
    location = 'Lombok'
    if isinstance(rest.address, str) and rest.address:
        location = rest.address.split(',')[-1].strip()

    return {
        'id': rest.id,
        'name': str(rest.name) if rest.name else 'Unknown',
        'location': location,
        'rating': rest.rating,
        'review_count': getattr(rest, 'review_count', 0),
        'price_range': str(rest.price_range) if rest.price_range else '$$',
        'cuisine': ', '.join(rest.cuisines[:3]) if rest.cuisines else 'Restaurant',
        'image_url': rest.images[0] if rest.images else '',
        'description': about_text,
        'similarity_score': round(rec.similarity_score, 4),
        'matching_features': rec.matching_features,
        'explanation': rec.explanation,
        'address': str(rest.address) if isinstance(rest.address, str) else ''
    }


def _serialize_restaurant_obj(rest_obj, default_score=None):
    """Serialize a Restaurant object with optional default score."""
    about_text = ''
    if isinstance(rest_obj.about, str):
        about_text = rest_obj.about[:200] + '...' if len(rest_obj.about) > 200 else rest_obj.about
    location = 'Lombok'
    if isinstance(rest_obj.address, str) and rest_obj.address:
        location = rest_obj.address.split(',')[-1].strip()

    return {
        'id': rest_obj.id,
        'name': str(rest_obj.name) if rest_obj.name else 'Unknown',
        'location': location,
        'rating': rest_obj.rating,
        'review_count': getattr(rest_obj, 'review_count', 0),
        'price_range': str(rest_obj.price_range) if rest_obj.price_range else '$$',
        'cuisine': ', '.join(rest_obj.cuisines[:3]) if rest_obj.cuisines else 'Restaurant',
        'image_url': rest_obj.images[0] if rest_obj.images else '',
        'description': about_text,
        'similarity_score': default_score if default_score is not None else 0.5 + (rest_obj.rating / 10.0),
        'matching_features': ['popular', 'highly rated'],
        'explanation': f'Restoran populer dengan rating {rest_obj.rating}/5.0',
        'address': str(rest_obj.address) if isinstance(rest_obj.address, str) else ''
    }


def _apply_personalization_scoring(restaurants, user_preferences):
    """Apply personalization scoring to restaurant dicts."""
    scored = []
    for restaurant in restaurants:
        score = 0
        matching = []

        if user_preferences.get('preferred_cuisines'):
            for cuisine, count in user_preferences['preferred_cuisines'].items():
                if cuisine.lower() in restaurant.get('cuisine', '').lower():
                    score += count * 3
                    matching.append(f"Cuisine: {cuisine} ({count}x)")
        if user_preferences.get('preferred_locations'):
            for loc, count in user_preferences['preferred_locations'].items():
                if loc.lower() in restaurant.get('location', '').lower():
                    score += count * 2
                    matching.append(f"Location: {loc} ({count}x)")
        if user_preferences.get('price_preferences'):
            for price, count in user_preferences['price_preferences'].items():
                if price.lower() in restaurant.get('price_range', '').lower():
                    score += count * 1.5
        score += restaurant.get('rating', 0) * 0.5
        if len(matching) > 1:
            score += len(matching) * 0.5

        restaurant['personalization_score'] = round(score, 2)
        restaurant['matching_features'] = matching[:3]
        scored.append(restaurant)

    scored.sort(key=lambda x: (x.get('personalization_score', 0), x.get('rating', 0)), reverse=True)
    return scored


# ─── Controller functions ─────────────────────────────────────────

@handle_errors
def handle_get_recommendations():
    """Paginated restaurant recommendations."""
    dto = RecommendationQueryDTO.from_request(request)
    engine = _get_engine()

    # Get user prefs
    user_prefs = None
    if dto.session_id or dto.device_token:
        user_prefs = _extract_user_preferences(dto.session_id, dto.device_token)
    is_personalized = bool(user_prefs)

    # Get all restaurants as dicts
    all_recs = [serialize_restaurant_from_object(r) for r in engine.restaurants_objects]

    # Apply personalization
    if user_prefs:
        all_recs = _apply_personalization_scoring(all_recs, user_prefs)

    # Category filter
    if dto.category:
        all_recs = [r for r in all_recs if r.get('category') == dto.category]

    # Paginate
    total = len(all_recs)
    total_pages = max((total + dto.per_page - 1) // dto.per_page, 1)
    page = min(dto.page, total_pages)
    start = (page - 1) * dto.per_page
    paginated = all_recs[start:start + dto.per_page]

    return jsonify({
        'success': True,
        'data': {
            'restaurants': paginated,
            'total': total,
            'page': page,
            'per_page': dto.per_page,
            'total_pages': total_pages,
            'has_next': page < total_pages,
            'has_prev': page > 1,
            'personalized': is_personalized,
            'category': dto.category
        }
    }), 200


@handle_errors
def handle_get_categories():
    """Return available restaurant categories."""
    categories = [
        {"key": "all", "label": "Semua", "count": 8},
        {"key": "local_food", "label": "Makanan Lokal", "count": 3},
        {"key": "beach", "label": "Pantai", "count": 2},
        {"key": "nature", "label": "Alam", "count": 1},
        {"key": "religious", "label": "Wisata Religi", "count": 1},
        {"key": "spicy_food", "label": "Pedas", "count": 1},
    ]
    return jsonify({'success': True, 'data': {'categories': categories}}), 200


@handle_errors
def handle_get_trending():
    """Return trending restaurants."""
    limit = int(request.args.get('limit', 5))
    engine = _get_engine()

    # Sort by rating as proxy for trending
    sorted_recs = sorted(engine.restaurants_objects, key=lambda x: x.rating, reverse=True)
    trending = [_serialize_restaurant_obj(r) for r in sorted_recs[:limit]]

    return jsonify({
        'success': True,
        'data': {
            'restaurants': trending,
            'period': '7_days',
            'based_on': 'popularity and ratings'
        }
    }), 200


@handle_errors
def handle_get_top5():
    """Top-5 recommendations using cosine similarity."""
    dto = RecommendationQueryDTO.from_request(request)
    engine = _get_engine()

    user_prefs = None
    if dto.session_id or dto.device_token:
        user_prefs = _extract_user_preferences(dto.session_id, dto.device_token)

    user_query = dto.query
    if not user_query and user_prefs:
        user_query = _build_query_from_preferences(user_prefs)

    top5 = []
    if user_query:
        recommendations = engine.get_recommendations(user_query, top_n=20)
        top5 = [_serialize_recommendation(rec) for rec in recommendations]
    else:
        sorted_objs = sorted(engine.restaurants_objects,
                             key=lambda x: (x.rating, getattr(x, 'review_count', 0)), reverse=True)
        top5 = [_serialize_restaurant_obj(r) for r in sorted_objs[:20]]

    # Sort and slice
    top5.sort(key=lambda x: (x.get('similarity_score', 0), x.get('rating', 0), x.get('review_count', 0)), reverse=True)
    top5 = top5[:5]

    logger.log_recommendation(query=user_query, count=len(top5),
                              avg_score=sum(r.get('similarity_score', 0) for r in top5) / max(len(top5), 1))

    return jsonify({
        'success': True,
        'data': {
            'restaurants': top5,
            'query': user_query,
            'personalized': bool(user_prefs),
            'algorithm': 'cosine_similarity',
            'tie_breaker': 'rating_and_review_count'
        }
    }), 200


@handle_errors
def handle_get_all_ranked():
    """All restaurants ranked by cosine similarity with pagination."""
    dto = RecommendationQueryDTO.from_request(request, per_page_key='limit')
    engine = _get_engine()

    user_prefs = None
    if dto.session_id or dto.device_token:
        user_prefs = _extract_user_preferences(dto.session_id, dto.device_token)

    user_query = dto.query
    if not user_query and user_prefs:
        user_query = _build_query_from_preferences(user_prefs)

    all_recs = []
    if user_query:
        recommendations = engine.get_recommendations(user_query, top_n=2000)
        all_recs = [_serialize_recommendation(rec) for rec in recommendations]
    else:
        sorted_objs = sorted(engine.restaurants_objects,
                             key=lambda x: (x.rating, getattr(x, 'review_count', 0)), reverse=True)
        all_recs = [_serialize_restaurant_obj(r) for r in sorted_objs]

    # Sort by similarity
    all_recs.sort(key=lambda x: (x.get('similarity_score', 0), x.get('rating', 0), x.get('review_count', 0)), reverse=True)

    # Add rank & top5 flag
    for idx, r in enumerate(all_recs):
        r['rank'] = idx + 1
        r['is_top5'] = idx < 5

    # Paginate
    total = len(all_recs)
    total_pages = max((total + dto.per_page - 1) // dto.per_page, 1)
    start = (dto.page - 1) * dto.per_page
    paginated = all_recs[start:start + dto.per_page]

    return jsonify({
        'success': True,
        'data': {
            'restaurants': paginated,
            'pagination': {
                'current_page': dto.page,
                'total_pages': total_pages,
                'total_items': total,
                'items_per_page': dto.per_page,
                'has_next': dto.page < total_pages,
                'has_prev': dto.page > 1,
            },
            'query': user_query,
            'personalized': bool(user_prefs),
            'algorithm': 'cosine_similarity',
            'tie_breaker': 'rating_and_review_count'
        }
    }), 200
