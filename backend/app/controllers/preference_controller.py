"""
Preference Controller – handles user preference analysis endpoints.
Uses: DTO validation, @handle_errors decorator.
"""
from datetime import datetime, timedelta
from collections import Counter
from flask import request, jsonify
from sqlalchemy import func

from backend.app.extensions import db
from backend.app.models.database import ChatHistory
from backend.app.utils.dto import PreferenceQueryDTO
from backend.app.utils.error_handlers import handle_errors
from backend.app.utils.logger import get_logger

logger = get_logger("preference_controller")


@handle_errors
def handle_get_user_preferences():
    """Analyze chat history and return preference statistics."""
    dto = PreferenceQueryDTO.from_request(request)

    query = ChatHistory.query
    if dto.device_token:
        query = query.filter_by(device_token=dto.device_token)
    if dto.session_id:
        query = query.filter_by(session_id=dto.session_id)

    records = query.order_by(ChatHistory.timestamp.asc()).limit(dto.limit).all()

    if not records:
        return jsonify({
            'success': True,
            'data': {
                'session_info': {
                    'device_token': dto.device_token,
                    'session_id': dto.session_id,
                    'total_conversations': 0
                },
                'all_conversations': [],
                'preferences_analysis': None,
                'message': 'Belum ada riwayat percakapan'
            }
        }), 200

    # Format conversations
    conversations = [{
        'conversation_number': idx,
        'timestamp': r.timestamp.isoformat(),
        'user_query': r.user_message,
        'bot_response': r.bot_response,
        'extracted_entities': {
            'cuisine': r.extracted_cuisine,
            'location': r.extracted_location,
            'mood': r.extracted_mood,
            'price': r.extracted_price
        }
    } for idx, r in enumerate(records, 1)]

    analysis = _analyze_preferences(records)

    session_info = {
        'device_token': dto.device_token,
        'session_id': dto.session_id,
        'total_conversations': len(records),
        'first_conversation_timestamp': records[0].timestamp.isoformat(),
        'last_conversation_timestamp': records[-1].timestamp.isoformat(),
        'session_duration_minutes': round(
            (records[-1].timestamp - records[0].timestamp).total_seconds() / 60, 2
        ) if len(records) > 1 else 0
    }

    return jsonify({
        'success': True,
        'data': {
            'generated_at': datetime.utcnow().isoformat(),
            'session_info': session_info,
            'all_conversations': conversations,
            'preferences_analysis': analysis
        }
    }), 200


@handle_errors
def handle_get_preferences_summary():
    """Quick aggregate summary of all user preferences."""
    total_conversations = db.session.query(func.count(ChatHistory.id)).scalar()
    total_sessions = db.session.query(func.count(func.distinct(ChatHistory.session_id))).scalar()

    top_cuisine = _get_top_value(ChatHistory.extracted_cuisine)
    top_location = _get_top_value(ChatHistory.extracted_location)

    return jsonify({
        'success': True,
        'data': {
            'total_sessions': total_sessions,
            'total_conversations': total_conversations,
            'top_cuisine': top_cuisine,
            'top_location': top_location,
            'avg_messages_per_session': round(total_conversations / total_sessions, 1) if total_sessions else 0
        }
    }), 200


# ─── Internal helpers ─────────────────────────────────────────────

def _get_top_value(column):
    """Return the most common non-null value for a column."""
    result = (db.session.query(column, func.count(column))
              .filter(column.isnot(None))
              .group_by(column)
              .order_by(func.count(column).desc())
              .first())
    return result[0] if result else None


def _analyze_preferences(records):
    """Analyze records and return structured preference data."""
    cuisines, locations, moods, prices = [], [], [], []

    for r in records:
        if r.extracted_cuisine:
            cuisines.extend([c.strip() for c in r.extracted_cuisine.split(',') if c.strip()])
        if r.extracted_location:
            locations.extend([l.strip() for l in r.extracted_location.split(',') if l.strip()])
        if r.extracted_mood:
            moods.extend([m.strip() for m in r.extracted_mood.split(',') if m.strip()])
        if r.extracted_price:
            prices.extend([p.strip() for p in r.extracted_price.split(',') if p.strip()])

    total = len(records)
    cuisine_c = Counter(cuisines)
    location_c = Counter(locations)
    mood_c = Counter(moods)
    price_c = Counter(prices)

    def _format(counter, key_name, max_items=10):
        return [{key_name: k, 'mention_count': v,
                 'frequency_percentage': round((v / total) * 100, 1)}
                for k, v in counter.most_common(max_items)]

    # Activity timeline (last 7 days)
    today = datetime.utcnow().date()
    timeline = [{'date': (today - timedelta(days=i)).isoformat(),
                 'conversations_count': sum(1 for r in records if r.timestamp.date() == today - timedelta(days=i))}
                for i in range(6, -1, -1)]

    preferred_cuisines = _format(cuisine_c, 'cuisine_name')
    preferred_locations = _format(location_c, 'location_name')
    preferred_moods = _format(mood_c, 'mood_type')
    price_prefs = _format(price_c, 'price_range')

    return {
        'statistics': {
            'total_conversations': total,
            'unique_cuisines_mentioned': len(cuisine_c),
            'unique_locations_mentioned': len(location_c),
            'unique_moods_mentioned': len(mood_c),
            'unique_price_ranges_mentioned': len(price_c)
        },
        'top_preferences': {
            'cuisines': preferred_cuisines,
            'locations': preferred_locations,
            'moods': preferred_moods,
            'price_ranges': price_prefs
        },
        'activity_timeline': timeline,
        'summary': {
            'most_mentioned_cuisine': preferred_cuisines[0]['cuisine_name'] if preferred_cuisines else None,
            'most_mentioned_location': preferred_locations[0]['location_name'] if preferred_locations else None,
            'most_common_mood': preferred_moods[0]['mood_type'] if preferred_moods else None,
            'most_common_price_range': price_prefs[0]['price_range'] if price_prefs else None,
        }
    }
