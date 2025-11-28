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
    Analisis history chat user dan return statistik preferensi
    
    Query Parameters:
    - device_token (optional): Filter by device token
    - session_id (optional): Filter by session
    - limit (optional): Limit number of records (default: 100)
    
    Response:
    {
        "success": true,
        "data": {
            "total_conversations": 50,
            "preferred_cuisines": [
                {"name": "pizza", "count": 15, "percentage": 30},
                {"name": "seafood", "count": 10, "percentage": 20}
            ],
            "preferred_locations": [...],
            "preferred_moods": [...],
            "price_preferences": {...},
            "activity_timeline": [...],
            "top_searches": [...]
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
        
        # Get records
        records = query.order_by(ChatHistory.timestamp.desc()).limit(limit).all()
        
        if not records:
            return jsonify({
                'success': True,
                'data': {
                    'total_conversations': 0,
                    'message': 'Belum ada riwayat percakapan'
                }
            }), 200
        
        # Analisis data
        analysis = _analyze_preferences(records)
        
        logger.info(f"Preferences analyzed for {len(records)} records")
        
        return jsonify({
            'success': True,
            'data': analysis
        }), 200
        
    except Exception as e:
        logger.error(f"Error analyzing preferences: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


def _analyze_preferences(records):
    """Analyze chat history records and extract preferences"""
    
    # Counters untuk berbagai kategori
    cuisines = []
    locations = []
    moods = []
    prices = []
    
    # Collect data dari records
    for record in records:
        if record.extracted_cuisine:
            cuisines.extend([c.strip() for c in record.extracted_cuisine.split(',')])
        
        if record.extracted_location:
            locations.extend([l.strip() for l in record.extracted_location.split(',')])
        
        if record.extracted_mood:
            moods.extend([m.strip() for m in record.extracted_mood.split(',')])
        
        if record.extracted_price:
            prices.extend([p.strip() for p in record.extracted_price.split(',')])
    
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
            'name': cuisine,
            'count': count,
            'percentage': round((count / total_conversations) * 100, 1)
        })
    
    # Format preferred locations
    preferred_locations = []
    for location, count in location_counter.most_common(10):
        preferred_locations.append({
            'name': location,
            'count': count,
            'percentage': round((count / total_conversations) * 100, 1)
        })
    
    # Format preferred moods
    preferred_moods = []
    for mood, count in mood_counter.most_common(10):
        preferred_moods.append({
            'name': mood,
            'count': count,
            'percentage': round((count / total_conversations) * 100, 1)
        })
    
    # Price preferences
    price_preferences = {}
    for price, count in price_counter.items():
        price_preferences[price] = {
            'count': count,
            'percentage': round((count / total_conversations) * 100, 1)
        }
    
    # Activity timeline (last 7 days)
    from datetime import datetime, timedelta
    today = datetime.utcnow().date()
    activity_timeline = []
    
    for i in range(6, -1, -1):
        date = today - timedelta(days=i)
        count = sum(1 for r in records if r.timestamp.date() == date)
        activity_timeline.append({
            'date': date.isoformat(),
            'count': count
        })
    
    # Top searches (user messages)
    top_searches = []
    for record in records[:10]:  # Get last 10 searches
        top_searches.append({
            'query': record.user_message,
            'timestamp': record.timestamp.isoformat()
        })
    
    # Return comprehensive analysis
    return {
        'total_conversations': total_conversations,
        'preferred_cuisines': preferred_cuisines,
        'preferred_locations': preferred_locations,
        'preferred_moods': preferred_moods,
        'price_preferences': price_preferences,
        'activity_timeline': activity_timeline,
        'top_searches': top_searches,
        'summary': {
            'most_searched_cuisine': preferred_cuisines[0]['name'] if preferred_cuisines else None,
            'most_visited_location': preferred_locations[0]['name'] if preferred_locations else None,
            'favorite_mood': preferred_moods[0]['name'] if preferred_moods else None
        }
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
