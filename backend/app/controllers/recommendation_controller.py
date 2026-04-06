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
    """Extract weighted user preferences from chat history.

    Uses both frequency and recency so card recommendations represent
    accumulated user behavior while still adapting to recent intent.
    """
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

    def _split_values(raw):
        if not raw:
            return []
        return [v.strip().lower() for v in str(raw).split(',') if v and v.strip()]

    cuisine_scores = Counter()
    location_scores = Counter()
    mood_scores = Counter()
    price_scores = Counter()

    now = datetime.utcnow()
    for idx, chat in enumerate(chat_history):
        # Recency weight: newer interactions contribute more.
        base_weight = max(0.35, 1.0 - (idx * 0.015))

        # Light time decay to avoid overfitting old history.
        chat_ts = chat.timestamp or now
        age_days = max((now - chat_ts).total_seconds() / 86400.0, 0.0)
        time_weight = max(0.5, 1.0 / (1.0 + (age_days * 0.05)))

        w = base_weight * time_weight

        for c in _split_values(chat.extracted_cuisine):
            cuisine_scores[c] += w
        for l in _split_values(chat.extracted_location):
            location_scores[l] += w
        for m in _split_values(chat.extracted_mood):
            mood_scores[m] += w
        for p in _split_values(chat.extracted_price):
            price_scores[p] += w

    def _top_items(counter_obj, limit):
        return {k: round(v, 3) for k, v in counter_obj.most_common(limit)}

    return {
        'preferred_cuisines': _top_items(cuisine_scores, 10),
        'preferred_locations': _top_items(location_scores, 10),
        'preferred_moods': _top_items(mood_scores, 5),
        'price_preferences': _top_items(price_scores, 3),
        'total_conversations': len(chat_history),
    }


def _extract_recent_query_context(session_id=None, device_token=None, limit=8):
    """Extract recent query context so card ranking follows latest chat intent."""
    query = ChatHistory.query
    if session_id:
        query = query.filter_by(session_id=session_id)
    elif device_token:
        query = query.filter_by(device_token=device_token)
    else:
        return None

    rows = query.order_by(ChatHistory.timestamp.desc()).limit(limit).all()
    if not rows:
        return None

    def _split_values(raw):
        if not raw:
            return []
        return [v.strip().lower() for v in str(raw).split(',') if v and v.strip()]

    cuisine_scores = Counter()
    location_scores = Counter()
    mood_scores = Counter()

    latest_message = ''
    for idx, row in enumerate(rows):
        if not latest_message and isinstance(row.user_message, str) and row.user_message.strip():
            latest_message = row.user_message.strip()

        w = max(0.45, 1.0 - (idx * 0.12))
        for c in _split_values(row.extracted_cuisine):
            cuisine_scores[c] += w
        for l in _split_values(row.extracted_location):
            location_scores[l] += w
        for m in _split_values(row.extracted_mood):
            mood_scores[m] += w

    return {
        'latest_message': latest_message,
        'recent_cuisines': [k for k, _ in cuisine_scores.most_common(4)],
        'recent_locations': [k for k, _ in location_scores.most_common(4)],
        'recent_moods': [k for k, _ in mood_scores.most_common(3)],
    }


def _build_query_from_preferences(user_preferences):
    """Build a search query string from accumulated preferences."""
    parts = []
    if user_preferences.get('preferred_cuisines'):
        parts.extend(list(user_preferences['preferred_cuisines'].keys())[:2])
    if user_preferences.get('preferred_locations'):
        parts.extend(list(user_preferences['preferred_locations'].keys())[:2])
    if user_preferences.get('preferred_moods'):
        parts.extend(list(user_preferences['preferred_moods'].keys())[:1])
    if user_preferences.get('price_preferences'):
        parts.extend(list(user_preferences['price_preferences'].keys())[:1])
    return ' '.join(parts)


def _build_hybrid_query(explicit_query=None, user_preferences=None, recent_context=None):
    """Build hybrid query: explicit > latest chat context + profile > profile only."""
    if explicit_query and explicit_query.strip():
        return explicit_query.strip()

    profile_query = _build_query_from_preferences(user_preferences) if user_preferences else ''
    latest_message = (recent_context or {}).get('latest_message', '').strip() if recent_context else ''

    if latest_message and profile_query:
        return f"{latest_message} {profile_query}".strip()
    if latest_message:
        return latest_message
    return profile_query


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


def _apply_personalization_scoring(restaurants, user_preferences, recent_context=None):
    """Apply personalization scoring to restaurant dicts."""
    scored = []

    recent_cuisines = set((recent_context or {}).get('recent_cuisines', []))
    recent_locations = set((recent_context or {}).get('recent_locations', []))
    recent_moods = set((recent_context or {}).get('recent_moods', []))

    for restaurant in restaurants:
        score = 0
        matching = []
        matched_any_signal = False
        matched_recent_intent = False

        cuisine_text = restaurant.get('cuisine', '').lower()
        location_text = f"{restaurant.get('location', '')} {restaurant.get('address', '')}".lower()
        text_blob = f"{restaurant.get('description', '')} {restaurant.get('cuisine', '')} {restaurant.get('address', '')}".lower()

        if user_preferences.get('preferred_cuisines'):
            for cuisine, count in user_preferences['preferred_cuisines'].items():
                if cuisine.lower() in cuisine_text:
                    score += count * 3
                    matching.append(f"Cuisine: {cuisine} ({count}x)")
                    matched_any_signal = True
        if user_preferences.get('preferred_locations'):
            for loc, count in user_preferences['preferred_locations'].items():
                if loc.lower() in location_text:
                    score += count * 2
                    matching.append(f"Location: {loc} ({count}x)")
                    matched_any_signal = True
        if user_preferences.get('preferred_moods'):
            for mood, count in user_preferences['preferred_moods'].items():
                if mood.lower() in text_blob:
                    score += count * 1.5
                    matching.append(f"Mood: {mood} ({count}x)")
                    matched_any_signal = True
        if user_preferences.get('price_preferences'):
            for price, count in user_preferences['price_preferences'].items():
                if price.lower() in restaurant.get('price_range', '').lower():
                    score += count * 1.5
                    matching.append(f"Price: {price} ({count}x)")
                    matched_any_signal = True

        # Quality bonus should not dominate personalization intent.
        if matched_any_signal:
            score += restaurant.get('rating', 0) * 0.15
        else:
            score += restaurant.get('rating', 0) * 0.02

        if len(matching) > 1:
            score += len(matching) * 0.5

        # Keep cards aligned with the latest chat intent while preserving accumulated profile.
        for cuisine in recent_cuisines:
            if cuisine and cuisine in cuisine_text:
                score += 2.4
                matched_recent_intent = True
                break
        for loc in recent_locations:
            if loc and loc in location_text:
                score += 2.0
                matched_recent_intent = True
                break
        for mood in recent_moods:
            if mood and mood in text_blob:
                score += 1.2
                matched_recent_intent = True
                break

        restaurant['personalization_score'] = round(score, 2)
        restaurant['has_preference_match'] = matched_any_signal
        restaurant['has_recent_intent_match'] = matched_recent_intent
        restaurant['matching_features'] = matching[:3]
        scored.append(restaurant)

    scored.sort(
        key=lambda x: (
            x.get('has_recent_intent_match', False),
            x.get('has_preference_match', False),
            x.get('personalization_score', 0),
            x.get('similarity_score', 0),
            x.get('rating', 0)
        ),
        reverse=True
    )
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
    recent_context = _extract_recent_query_context(dto.session_id, dto.device_token)

    user_query = _build_hybrid_query(
        explicit_query=dto.query,
        user_preferences=user_prefs,
        recent_context=recent_context,
    )

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
    recent_context = _extract_recent_query_context(dto.session_id, dto.device_token)

    user_query = _build_hybrid_query(
        explicit_query=dto.query,
        user_preferences=user_prefs,
        recent_context=recent_context,
    )

    all_recs = []
    if user_query:
        recommendations = engine.get_recommendations(user_query, top_n=2000)
        all_recs = [_serialize_recommendation(rec) for rec in recommendations]
    else:
        sorted_objs = sorted(engine.restaurants_objects,
                             key=lambda x: (x.rating, getattr(x, 'review_count', 0)), reverse=True)
        all_recs = [_serialize_restaurant_obj(r) for r in sorted_objs]

    # Re-rank by accumulated preference profile when available.
    if user_prefs:
        all_recs = _apply_personalization_scoring(all_recs, user_prefs, recent_context=recent_context)

    # Sort by similarity
    all_recs.sort(
        key=lambda x: (
            x.get('has_recent_intent_match', False),
            x.get('has_preference_match', False),
            x.get('personalization_score', 0),
            x.get('similarity_score', 0),
            x.get('rating', 0),
            x.get('review_count', 0)
        ),
        reverse=True
    )

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


@handle_errors
def handle_get_profile_debug():
    """Return personalization profile used for card recommendation ranking."""
    dto = RecommendationQueryDTO.from_request(request)

    # Requires at least one user identifier to inspect profile.
    if not dto.session_id and not dto.device_token:
        return jsonify({
            'success': False,
            'error': {
                'message': 'session_id atau device_token diperlukan untuk profile debug'
            }
        }), 400

    user_prefs = _extract_user_preferences(dto.session_id, dto.device_token)
    recent_context = _extract_recent_query_context(dto.session_id, dto.device_token)
    synthesized_query = _build_hybrid_query(
        explicit_query='',
        user_preferences=user_prefs,
        recent_context=recent_context,
    ) if user_prefs or recent_context else ''

    query = ChatHistory.query
    if dto.session_id:
        query = query.filter_by(session_id=dto.session_id)
    elif dto.device_token:
        query = query.filter_by(device_token=dto.device_token)

    recent_rows = query.order_by(ChatHistory.timestamp.desc()).limit(10).all()

    recent_entities = []
    for row in recent_rows:
        recent_entities.append({
            'timestamp': row.timestamp.isoformat() if row.timestamp else None,
            'user_message': row.user_message,
            'extracted': {
                'cuisine': row.extracted_cuisine,
                'location': row.extracted_location,
                'mood': row.extracted_mood,
                'price': row.extracted_price,
            }
        })

    return jsonify({
        'success': True,
        'data': {
            'identity': {
                'session_id': dto.session_id,
                'device_token': dto.device_token,
            },
            'profile': user_prefs or {
                'preferred_cuisines': {},
                'preferred_locations': {},
                'preferred_moods': {},
                'price_preferences': {},
                'total_conversations': 0,
            },
            'synthesized_query': synthesized_query,
            'recent_context': recent_context or {
                'latest_message': '',
                'recent_cuisines': [],
                'recent_locations': [],
                'recent_moods': [],
            },
            'recent_entities': recent_entities,
            'notes': {
                'weighting': 'frequency + recency decay + latest-intent boost',
                'used_by': '/recommendations/top5 and /recommendations/all-ranked when query is empty'
            }
        }
    }), 200
