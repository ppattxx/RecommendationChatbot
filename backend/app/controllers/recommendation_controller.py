"""
Recommendation Controller – handles request/response for recommendation endpoints.
Uses: DTO validation, @handle_errors decorator, DI via container.
"""
from datetime import datetime, timedelta, timezone
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


def _get_chatbot_service():
    """Get chatbot service from DI container."""
    chatbot = current_app.container.chatbot_service
    if chatbot is None:
        raise ServiceUnavailableError("Chatbot system unavailable")
    return chatbot


def _extract_user_preferences(session_id=None, device_token=None):
    """Extract weighted user preferences from chat history.

    Uses both frequency and recency so card recommendations represent
    accumulated user behavior while still adapting to recent intent.
    """
    query = ChatHistory.query
    # Personalization is user-centric: prefer device token (cross-session history)
    # and fallback to session when device token is unavailable.
    if device_token:
        query = query.filter_by(device_token=device_token)
    elif session_id:
        query = query.filter_by(session_id=session_id)
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

    now = datetime.now(timezone.utc)
    for idx, chat in enumerate(chat_history):
        # Recency weight: newer interactions contribute more.
        base_weight = max(0.35, 1.0 - (idx * 0.015))

        # Light time decay to avoid overfitting old history.
        chat_ts = chat.timestamp or now
        if chat_ts.tzinfo is None:
            chat_ts = chat_ts.replace(tzinfo=timezone.utc)
        else:
            chat_ts = chat_ts.astimezone(timezone.utc)
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


def _has_meaningful_preferences(user_prefs):
    """Return True only when there is substantial preference signal.

    Initial state (device token baru): Chatbot & Web SAMA
    After history builds: Web personalizes based on accumulated preferences
    """
    if not user_prefs:
        return False

    has_entity_signal = any([
        bool(user_prefs.get('preferred_cuisines')),
        bool(user_prefs.get('preferred_locations')),
        bool(user_prefs.get('preferred_moods')),
        bool(user_prefs.get('price_preferences')),
    ])

    # Require at least 3 conversations before personalization kicks in
    # This ensures fresh device tokens show identical chatbot & web results
    enough_history = user_prefs.get('total_conversations', 0) >= 3
    return has_entity_signal and enough_history


def _extract_recent_query_context(session_id=None, device_token=None, limit=8):
    """Extract recent query context so card ranking follows latest chat intent."""
    query = ChatHistory.query
    # Keep recent-intent local to active conversation when available.
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

    # Blend latest intent with historical profile signal (frequency-based),
    # but avoid noisy duplication.
    if latest_message:
        latest_lower = latest_message.lower()
        profile_tokens = []

        if user_preferences:
            top_cuisines = list((user_preferences.get('preferred_cuisines') or {}).keys())[:2]
            top_locations = list((user_preferences.get('preferred_locations') or {}).keys())[:1]
            top_moods = list((user_preferences.get('preferred_moods') or {}).keys())[:1]
            for token in [*top_cuisines, *top_locations, *top_moods]:
                t = str(token).strip().lower()
                if t and t not in latest_lower:
                    profile_tokens.append(t)

        if profile_tokens:
            return f"{latest_message} {' '.join(profile_tokens[:2])}".strip()
        return latest_message

    return profile_query


def _build_personalization_insights(user_preferences=None, recent_context=None):
    """Build compact personalization insights for UI/chat explainability."""
    user_preferences = user_preferences or {}
    recent_context = recent_context or {}

    pref_cuisines = list((user_preferences.get('preferred_cuisines') or {}).keys())[:3]
    pref_locations = list((user_preferences.get('preferred_locations') or {}).keys())[:3]
    pref_moods = list((user_preferences.get('preferred_moods') or {}).keys())[:2]
    pref_prices = list((user_preferences.get('price_preferences') or {}).keys())[:2]

    recent_cuisines = list(recent_context.get('recent_cuisines') or [])[:3]
    recent_locations = list(recent_context.get('recent_locations') or [])[:2]
    recent_moods = list(recent_context.get('recent_moods') or [])[:2]

    profile_strength = 0
    if pref_cuisines:
        profile_strength += 1
    if pref_locations:
        profile_strength += 1
    if pref_moods:
        profile_strength += 1
    if pref_prices:
        profile_strength += 1

    return {
        'profile_strength': profile_strength,
        'total_conversations': int(user_preferences.get('total_conversations', 0) or 0),
        'top_preferences': {
            'cuisines': pref_cuisines,
            'locations': pref_locations,
            'moods': pref_moods,
            'prices': pref_prices,
        },
        'recent_intent': {
            'latest_message': str(recent_context.get('latest_message', '') or ''),
            'cuisines': recent_cuisines,
            'locations': recent_locations,
            'moods': recent_moods,
        }
    }


def _is_query_specific(explicit_query):
    """Return True when query contains enough concrete entities to prefer query-first ranking."""
    query = (explicit_query or '').strip()
    if not query:
        return False

    try:
        chatbot = _get_chatbot_service()
        _, entities = chatbot._extract_intent_and_entities(query)
        entity_count = 0
        for value in entities.values():
            if isinstance(value, list):
                entity_count += len(value)
        return entity_count >= 2
    except Exception:
        # Be conservative: keep current behavior if entity extraction is unavailable.
        return False


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
        'img1_url': rest.images[0] if rest.images else '',
        'img2_url': rest.images[1] if rest.images and len(rest.images) > 1 else '',
        'img3_url': rest.images[2] if rest.images and len(rest.images) > 2 else '',
        'description': about_text,
        'similarity_score': round(rec.similarity_score, 4),
        'raw_similarity_score': round(
            rec.raw_similarity_score if rec.raw_similarity_score is not None else rec.similarity_score,
            4
        ),
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
        'img1_url': rest_obj.images[0] if rest_obj.images else '',
        'img2_url': rest_obj.images[1] if rest_obj.images and len(rest_obj.images) > 1 else '',
        'img3_url': rest_obj.images[2] if rest_obj.images and len(rest_obj.images) > 2 else '',
        'description': about_text,
        'similarity_score': default_score if default_score is not None else 0.5 + (rest_obj.rating / 10.0),
        'matching_features': ['popular', 'highly rated'],
        'explanation': f'Restoran populer dengan rating {rest_obj.rating}/5.0',
        'address': str(rest_obj.address) if isinstance(rest_obj.address, str) else ''
    }


def _serialize_chatbot_ranked_row(rec):
    """Serialize chatbot-ranked row dict into API-response shape."""
    row = rec.get('restaurant', {})
    cuisines_raw = row.get('cuisines', '')
    cuisine_text = str(cuisines_raw)
    about_text = str(row.get('about', '') or '')
    if len(about_text) > 200:
        about_text = about_text[:200] + '...'

    def _to_int(v, default=0):
        try:
            return int(v)
        except Exception:
            return default

    def _to_float(v, default=0.0):
        try:
            return float(v)
        except Exception:
            return default

    image_url = ''
    for image_key in ['img1_url', 'image_url', 'image', 'img']:
        raw_img = row.get(image_key)
        if raw_img is not None:
            img_val = str(raw_img).strip()
            if img_val and img_val.lower() != 'nan':
                image_url = img_val
                break

    return {
        'id': _to_int(row.get('id', 0), 0),
        'name': str(row.get('name', 'Unknown')),
        'location': str(row.get('location', 'Lombok')),
        'rating': _to_float(row.get('rating', 0), 0.0),
        'review_count': _to_int(row.get('reviews_count', 0), 0),
        'price_range': str(row.get('price_range', '$$')),
        'cuisine': cuisine_text,
        'image_url': image_url,
        'img1_url': image_url,
        'img2_url': str(row.get('img2_url', '') or ''),
        'img3_url': str(row.get('img3_url', '') or ''),
        'description': about_text,
        'similarity_score': float(rec.get('similarity', rec.get('total_score', 0))),
        'raw_similarity_score': float(rec.get('raw_similarity', rec.get('similarity', rec.get('total_score', 0)))),
        'matching_features': [],
        'explanation': 'Ranked by chatbot recommendation pipeline',
        'address': str(row.get('address', '') or ''),
    }


def _apply_personalization_scoring(restaurants, user_preferences, recent_context=None):
    """Apply personalization scoring to restaurant dicts with STRONG personalization bias."""
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

        # STRONG cuisine preference multiplier (10x vs 3x)
        if user_preferences.get('preferred_cuisines'):
            for cuisine, count in user_preferences['preferred_cuisines'].items():
                if cuisine.lower() in cuisine_text:
                    score += count * 10  # INCREASED from 3 to 10
                    matching.append(f"Cuisine: {cuisine} ({count}x)")
                    matched_any_signal = True
        
        # STRONG location preference multiplier (8x vs 2x)
        if user_preferences.get('preferred_locations'):
            for loc, count in user_preferences['preferred_locations'].items():
                if loc.lower() in location_text:
                    score += count * 8  # INCREASED from 2 to 8
                    matching.append(f"Location: {loc} ({count}x)")
                    matched_any_signal = True
        
        # Strong mood preference multiplier (6x vs 1.5x)
        if user_preferences.get('preferred_moods'):
            for mood, count in user_preferences['preferred_moods'].items():
                if mood.lower() in text_blob:
                    score += count * 6  # INCREASED from 1.5 to 6
                    matching.append(f"Mood: {mood} ({count}x)")
                    matched_any_signal = True
        
        # Strong price preference multiplier (5x vs 1.5x)
        if user_preferences.get('price_preferences'):
            for price, count in user_preferences['price_preferences'].items():
                if price.lower() in restaurant.get('price_range', '').lower():
                    score += count * 5  # INCREASED from 1.5 to 5
                    matching.append(f"Price: {price} ({count}x)")
                    matched_any_signal = True

        # Rating bonus: only matter when preferences matched
        if matched_any_signal:
            score += restaurant.get('rating', 0) * 0.3  # INCREASED from 0.15 to 0.3
        else:
            # Penalty for non-matching restaurants when user has preferences
            score -= restaurant.get('rating', 0) * 0.1

        # Bonus for multiple matching features  
        if len(matching) > 1:
            score += len(matching) * 2  # INCREASED from 0.5 to 2

        # STRONG recent intent boost (much higher priority)
        for cuisine in recent_cuisines:
            if cuisine and cuisine in cuisine_text:
                score += 10  # INCREASED from 2.4 to 10
                matched_recent_intent = True
                break
        for loc in recent_locations:
            if loc and loc in location_text:
                score += 8  # INCREASED from 2.0 to 8
                matched_recent_intent = True
                break
        for mood in recent_moods:
            if mood and mood in text_blob:
                score += 6  # INCREASED from 1.2 to 6
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
    is_personalized = _has_meaningful_preferences(user_prefs)

    # Get all restaurants as dicts
    all_recs = [serialize_restaurant_from_object(r) for r in engine.restaurants_objects]

    # Apply personalization
    if is_personalized:
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
    """Top-5 recommendations: query-driven when no history, personalization-driven when history exists."""
    dto = RecommendationQueryDTO.from_request(request)
    engine = _get_engine()

    user_prefs = None
    if dto.session_id or dto.device_token:
        user_prefs = _extract_user_preferences(dto.session_id, dto.device_token)
    is_personalized = _has_meaningful_preferences(user_prefs)
    recent_context = _extract_recent_query_context(dto.session_id, dto.device_token)
    personalization_insights = _build_personalization_insights(
        user_preferences=user_prefs if user_prefs else None,
        recent_context=recent_context,
    )

    explicit_query = (dto.query or '').strip()
    
    top5 = []
    
    # Step 1: Get base recommendations
    if not is_personalized and explicit_query:
        # NO HISTORY: Use exact same ranking as chatbot for consistency
        chatbot_svc = _get_chatbot_service()
        _, entities = chatbot_svc._extract_intent_and_entities(explicit_query)
        recommendations = chatbot_svc.get_ranked_recommendations(
            query=explicit_query,
            entities=entities,
            session_id=dto.session_id,
            device_token=dto.device_token,
            top_n=20,
            update_preferences=False
        )
        top5 = [_serialize_chatbot_ranked_row(rec) for rec in recommendations]
    elif explicit_query:
        # WITH HISTORY: Use standard engine then personalize
        recommendations = engine.get_recommendations(explicit_query, top_n=20)
        top5 = [_serialize_recommendation(rec) for rec in recommendations]
    else:
        # No query provided
        sorted_objs = sorted(engine.restaurants_objects,
                             key=lambda x: (x.rating, getattr(x, 'review_count', 0)), reverse=True)
        top5 = [_serialize_restaurant_obj(r) for r in sorted_objs[:20]]
    
    # Step 2: Apply web personalization when query is generic/ambiguous.
    # For specific queries, keep query-first ranking so web matches script/chat intent.
    apply_personalization = is_personalized and (not explicit_query or not _is_query_specific(explicit_query))
    if apply_personalization:
        top5 = _apply_personalization_scoring(top5, user_prefs, recent_context=recent_context)
        top5.sort(
            key=lambda x: (
                x.get('has_recent_intent_match', False),
                x.get('has_preference_match', False),
                x.get('personalization_score', 0),
                x.get('similarity_score', 0) if explicit_query else 0,
                x.get('rating', 0),
                x.get('review_count', 0)
            ),
            reverse=True
        )
        algorithm = 'personalization_enhanced'
    else:
        # No personalization - return in chatbot ranking order (already sorted from engine)
        # DON'T re-sort - maintain engine's order for consistency with chatbot
        algorithm = 'query_similarity' if explicit_query else 'popularity'
    
    top5 = top5[:5]

    logger.log_recommendation(query=explicit_query, count=len(top5),
                              avg_score=sum(r.get('similarity_score', 0) for r in top5) / max(len(top5), 1))

    return jsonify({
        'success': True,
        'data': {
            'restaurants': top5,
            'query': explicit_query,
            'personalized': is_personalized,
            'personalization_insights': personalization_insights,
            'algorithm': algorithm,
            'tie_breaker': 'personalization_score' if apply_personalization else 'rating_and_review_count'
        }
    }), 200


@handle_errors
def handle_get_all_ranked():
    """All restaurants ranked by query + personalization preferences (web-specific ranking)."""
    dto = RecommendationQueryDTO.from_request(request, per_page_key='limit')
    engine = _get_engine()

    user_prefs = None
    if dto.session_id or dto.device_token:
        user_prefs = _extract_user_preferences(dto.session_id, dto.device_token)
    is_personalized = _has_meaningful_preferences(user_prefs)
    recent_context = _extract_recent_query_context(dto.session_id, dto.device_token)
    personalization_insights = _build_personalization_insights(
        user_preferences=user_prefs if user_prefs else None,
        recent_context=recent_context,
    )

    explicit_query = (dto.query or '').strip()

    all_recs = []
    
    # Step 1: Get base recommendations (query-based if query provided, popularity otherwise)
    if not is_personalized and explicit_query:
        # NO HISTORY: Use exact same ranking as chatbot for consistency
        chatbot_svc = _get_chatbot_service()
        _, entities = chatbot_svc._extract_intent_and_entities(explicit_query)
        recommendations = chatbot_svc.get_ranked_recommendations(
            query=explicit_query,
            entities=entities,
            session_id=dto.session_id,
            device_token=dto.device_token,
            top_n=2000,
            update_preferences=False
        )
        all_recs = [_serialize_chatbot_ranked_row(rec) for rec in recommendations]
    elif explicit_query:
        # WITH HISTORY: Use standard engine then personalize
        recommendations = engine.get_recommendations(explicit_query, top_n=2000)
        all_recs = [_serialize_recommendation(rec) for rec in recommendations]
    else:
        sorted_objs = sorted(engine.restaurants_objects,
                             key=lambda x: (x.rating, getattr(x, 'review_count', 0)), reverse=True)
        all_recs = [_serialize_restaurant_obj(r) for r in sorted_objs]

    # Step 2: Apply web-specific personalization only for generic/ambiguous queries.
    apply_personalization = is_personalized and (not explicit_query or not _is_query_specific(explicit_query))
    if apply_personalization:
        all_recs = _apply_personalization_scoring(all_recs, user_prefs, recent_context=recent_context)
        # Sort by personalization scores primarily
        all_recs.sort(
            key=lambda x: (
                x.get('has_recent_intent_match', False),
                x.get('has_preference_match', False),
                x.get('personalization_score', 0),
                x.get('similarity_score', 0) if explicit_query else 0,
                x.get('rating', 0),
                x.get('review_count', 0)
            ),
            reverse=True
        )
    # else: NO re-sorting - maintain engine order for consistency with chatbot

    # Add rank & top5 flag (not pinned to chatbot top-5 in web mode)
    for idx, r in enumerate(all_recs):
        r['rank'] = idx + 1

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
            'query': explicit_query,
            'personalized': is_personalized,
            'personalization_insights': personalization_insights,
            'algorithm': 'personalization_discovery' if apply_personalization else 'query_similarity',
            'tie_breaker': 'personalization_score' if apply_personalization else 'rating_and_review_count'
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
