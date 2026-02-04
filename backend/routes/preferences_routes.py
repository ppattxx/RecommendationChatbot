"""
API Routes untuk User Preferences Analysis
Endpoint: GET /api/user-preferences
"""
import sys
from pathlib import Path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from flask import Blueprint, request, jsonify
from sqlalchemy import func
from backend.models.database import db, ChatHistory
from collections import Counter
from utils.logger import get_logger

logger = get_logger("preferences_routes")

preferences_bp = Blueprint('preferences', __name__)


@preferences_bp.route('/user-preferences', methods=['GET'])
def get_user_preferences():
    """
    Analisis history chat user dan return statistik preferensi beserta semua query
    
    Query Parameters:
    - device_token (optional): Filter by device token
    - session_id (optional): Filter by session
    - limit (optional): Limit number of records (default: 100)
    
    Response:
    {
        "success": true,
        "data": {
            "session_info": {...},
            "all_conversations": [...],
            "preferences_analysis": {...}
        }
    }
    """
    try:
        # Get query parameters
        device_token = request.args.get('device_token')
        session_id = request.args.get('session_id')
        limit = request.args.get('limit', 100, type=int)
        
        # Build query
        query = ChatHistory.query
        
        if device_token:
            query = query.filter_by(device_token=device_token)
        
        if session_id:
            query = query.filter_by(session_id=session_id)
        
        # Get records ordered by timestamp ascending (oldest first for chronological order)
        records = query.order_by(ChatHistory.timestamp.asc()).limit(limit).all()
        
        if not records:
            return jsonify({
                'success': True,
                'data': {
                    'session_info': {
                        'device_token': device_token,
                        'session_id': session_id,
                        'total_conversations': 0
                    },
                    'all_conversations': [],
                    'preferences_analysis': None,
                    'message': 'Belum ada riwayat percakapan'
                }
            }), 200
        
        # Extract all conversations dengan format yang rapi
        all_conversations = []
        for idx, record in enumerate(records, 1):
            conversation = {
                'conversation_number': idx,
                'timestamp': record.timestamp.isoformat(),
                'user_query': record.user_message,
                'bot_response': record.bot_response,
                'extracted_entities': {
                    'cuisine': record.extracted_cuisine,
                    'location': record.extracted_location,
                    'mood': record.extracted_mood,
                    'price': record.extracted_price
                }
            }
            all_conversations.append(conversation)
        
        # Analisis preferensi
        preferences_analysis = _analyze_preferences(records)
        
        # Session info
        from datetime import datetime
        session_info = {
            'device_token': device_token,
            'session_id': session_id,
            'total_conversations': len(records),
            'first_conversation_timestamp': records[0].timestamp.isoformat(),
            'last_conversation_timestamp': records[-1].timestamp.isoformat(),
            'session_duration_minutes': round((records[-1].timestamp - records[0].timestamp).total_seconds() / 60, 2) if len(records) > 1 else 0
        }
        
        logger.info(f"Preferences analyzed for {len(records)} records")
        
        # Return dengan format yang lebih terstruktur dengan timestamp
        response_data = {
            'generated_at': datetime.utcnow().isoformat(),
            'session_info': session_info,
            'all_conversations': all_conversations,
            'preferences_analysis': preferences_analysis
        }
        
        return jsonify({
            'success': True,
            'data': response_data
        }), 200
        
    except Exception as e:
        logger.error(f"Error analyzing preferences: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


def _analyze_preferences(records):
    """Analyze chat history records and extract preferences with clean formatting"""
    
    # Counters untuk berbagai kategori
    cuisines = []
    locations = []
    moods = []
    prices = []
    
    # Collect data dari records
    for record in records:
        if record.extracted_cuisine:
            cuisines.extend([c.strip() for c in record.extracted_cuisine.split(',') if c.strip()])
        
        if record.extracted_location:
            locations.extend([l.strip() for l in record.extracted_location.split(',') if l.strip()])
        
        if record.extracted_mood:
            moods.extend([m.strip() for m in record.extracted_mood.split(',') if m.strip()])
        
        if record.extracted_price:
            prices.extend([p.strip() for p in record.extracted_price.split(',') if p.strip()])
    
    # Count frequencies
    cuisine_counter = Counter(cuisines)
    location_counter = Counter(locations)
    mood_counter = Counter(moods)
    price_counter = Counter(prices)
    
    total_conversations = len(records)
    
    # Format preferred cuisines
    preferred_cuisines = []
    for cuisine, count in cuisine_counter.most_common(10):
        preferred_cuisines.append({
            'cuisine_name': cuisine,
            'mention_count': count,
            'frequency_percentage': round((count / total_conversations) * 100, 1)
        })
    
    # Format preferred locations
    preferred_locations = []
    for location, count in location_counter.most_common(10):
        preferred_locations.append({
            'location_name': location,
            'mention_count': count,
            'frequency_percentage': round((count / total_conversations) * 100, 1)
        })
    
    # Format preferred moods
    preferred_moods = []
    for mood, count in mood_counter.most_common(10):
        preferred_moods.append({
            'mood_type': mood,
            'mention_count': count,
            'frequency_percentage': round((count / total_conversations) * 100, 1)
        })
    
    # Price preferences dengan format yang lebih rapi
    price_preferences = []
    for price, count in price_counter.most_common():
        price_preferences.append({
            'price_range': price,
            'mention_count': count,
            'frequency_percentage': round((count / total_conversations) * 100, 1)
        })
    
    # Activity timeline (last 7 days)
    from datetime import datetime, timedelta
    today = datetime.utcnow().date()
    activity_timeline = []
    
    for i in range(6, -1, -1):
        date = today - timedelta(days=i)
        count = sum(1 for r in records if r.timestamp.date() == date)
        activity_timeline.append({
            'date': date.isoformat(),
            'conversations_count': count
        })
    
    # Summary statistics
    summary = {
        'total_unique_cuisines': len(cuisine_counter),
        'total_unique_locations': len(location_counter),
        'total_unique_moods': len(mood_counter),
        'most_mentioned_cuisine': preferred_cuisines[0]['cuisine_name'] if preferred_cuisines else None,
        'most_mentioned_location': preferred_locations[0]['location_name'] if preferred_locations else None,
        'most_common_mood': preferred_moods[0]['mood_type'] if preferred_moods else None,
        'most_common_price_range': price_preferences[0]['price_range'] if price_preferences else None
    }
    
    # Return comprehensive analysis dengan struktur yang rapi
    return {
        'statistics': {
            'total_conversations': total_conversations,
            'unique_cuisines_mentioned': len(cuisine_counter),
            'unique_locations_mentioned': len(location_counter),
            'unique_moods_mentioned': len(mood_counter),
            'unique_price_ranges_mentioned': len(price_counter)
        },
        'top_preferences': {
            'cuisines': preferred_cuisines,
            'locations': preferred_locations,
            'moods': preferred_moods,
            'price_ranges': price_preferences
        },
        'activity_timeline': activity_timeline,
        'summary': summary
    }


@preferences_bp.route('/user-preferences/summary', methods=['GET'])
def get_preferences_summary():
    """
    Get quick summary of user preferences
    
    Response:
    {
        "success": true,
        "data": {
            "total_users": 25,
            "total_conversations": 150,
            "top_cuisine": "pizza",
            "top_location": "Kuta"
        }
    }
    """
    try:
        # Get aggregate statistics
        total_conversations = db.session.query(func.count(ChatHistory.id)).scalar()
        total_sessions = db.session.query(func.count(func.distinct(ChatHistory.session_id))).scalar()
        
        # Get most common cuisine
        cuisine_data = db.session.query(
            ChatHistory.extracted_cuisine,
            func.count(ChatHistory.extracted_cuisine)
        ).filter(
            ChatHistory.extracted_cuisine.isnot(None)
        ).group_by(
            ChatHistory.extracted_cuisine
        ).order_by(
            func.count(ChatHistory.extracted_cuisine).desc()
        ).first()
        
        top_cuisine = cuisine_data[0] if cuisine_data else None
        
        # Get most common location
        location_data = db.session.query(
            ChatHistory.extracted_location,
            func.count(ChatHistory.extracted_location)
        ).filter(
            ChatHistory.extracted_location.isnot(None)
        ).group_by(
            ChatHistory.extracted_location
        ).order_by(
            func.count(ChatHistory.extracted_location).desc()
        ).first()
        
        top_location = location_data[0] if location_data else None
        
        return jsonify({
            'success': True,
            'data': {
                'total_sessions': total_sessions,
                'total_conversations': total_conversations,
                'top_cuisine': top_cuisine,
                'top_location': top_location,
                'avg_messages_per_session': round(total_conversations / total_sessions, 1) if total_sessions > 0 else 0
            }
        }), 200
        
    except Exception as e:
        logger.error(f"Error getting preferences summary: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
