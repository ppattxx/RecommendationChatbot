"""
Serializers for converting domain objects to API response dicts
Eliminates 5x duplicate Restaurant→dict conversion code
"""
import pandas as pd


def serialize_restaurant_from_object(rest_obj):
    """Convert a Restaurant dataclass object to API response dict"""
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
        'opening_hours': rest_obj.hours.get('monday', 'Contact for hours') if rest_obj.hours else 'Contact for hours',
        'popular_dishes': [],
        'category': _determine_category(rest_obj.cuisines or []),
        'personalization_score': 0,
        'url': '',
        'address': str(rest_obj.address) if isinstance(rest_obj.address, str) else ''
    }


def serialize_recommendation(rec):
    """Convert a Recommendation object (with similarity score) to API response dict"""
    rest = rec.restaurant
    base = serialize_restaurant_from_object(rest)
    base.update({
        'similarity_score': round(rec.similarity_score, 4),
        'matching_features': rec.matching_features,
        'explanation': rec.explanation
    })
    return base


def serialize_restaurant_from_row(row):
    """Convert a pandas DataFrame row to API response dict"""
    cuisines = _parse_list_field(row.get('cuisines'))
    cuisine_str = ', '.join(cuisines[:3]) if cuisines else 'Restaurant'

    popular_dishes = _parse_list_field(row.get('preferences'))[:5]

    about = row.get('about', '')
    description = ''
    if pd.notna(about) and isinstance(about, str):
        description = about[:200] + '...' if len(about) > 200 else about

    return {
        'id': int(row['id']),
        'name': str(row['name']) if pd.notna(row['name']) else 'Unknown',
        'location': _extract_location(row.get('address')),
        'rating': float(row['rating']) if pd.notna(row['rating']) else 4.0,
        'price_range': str(row['price_range']) if pd.notna(row.get('price_range')) else '$$',
        'cuisine': cuisine_str,
        'image_url': str(row['img1_url']) if pd.notna(row.get('img1_url')) else '',
        'description': description,
        'opening_hours': _get_opening_hours(row),
        'popular_dishes': popular_dishes,
        'category': _determine_category(cuisines),
        'personalization_score': 0,
        'url': str(row['url']) if pd.notna(row.get('url')) else '',
        'address': str(row['address']) if pd.notna(row.get('address')) else '',
        'konten_stemmed': str(row['konten_stemmed']) if pd.notna(row.get('konten_stemmed')) else ''
    }


def serialize_chat_record(record):
    """Convert a ChatHistory DB record to API response dict"""
    return {
        'id': record.id,
        'user_message': record.user_message,
        'bot_response': record.bot_response,
        'timestamp': record.timestamp.isoformat(),
        'extracted_entities': {
            'cuisine': record.extracted_cuisine,
            'location': record.extracted_location,
            'mood': record.extracted_mood,
            'price': record.extracted_price
        }
    }


# --- Private helpers ---

def _parse_list_field(value):
    """Safely parse a string representation of a list"""
    if pd.isna(value) if hasattr(pd, 'isna') else value is None:
        return []
    try:
        return eval(value) if isinstance(value, str) else []
    except Exception:
        return []


def _determine_category(cuisines):
    """Determine restaurant category from cuisines list"""
    cuisines_lower = [c.lower() for c in cuisines] if cuisines else []
    if any(c in cuisines_lower for c in ['italian', 'pizza', 'pasta']):
        return 'italian'
    elif any(c in cuisines_lower for c in ['mexican', 'tacos']):
        return 'mexican'
    elif any(c in cuisines_lower for c in ['asian', 'indonesian', 'chinese', 'japanese', 'thai']):
        return 'asian'
    elif any(c in cuisines_lower for c in ['bar', 'cafe', 'coffee']):
        return 'cafe'
    elif any(c in cuisines_lower for c in ['healthy', 'vegetarian', 'vegan']):
        return 'healthy'
    else:
        return 'international'


def _extract_location(address):
    """Extract location name from address string"""
    if pd.isna(address) if hasattr(pd, 'isna') else address is None:
        return 'Lombok'
    address = str(address)
    location_map = {
        'Gili Trawangan': ['Gili Trawangan', 'Gili T'],
        'Gili Air': ['Gili Air'],
        'Gili Meno': ['Gili Meno'],
        'Kuta, Lombok': ['Kuta'],
        'Senggigi': ['Senggigi'],
        'Mataram': ['Mataram']
    }
    for location, keywords in location_map.items():
        if any(kw in address for kw in keywords):
            return location
    return 'Lombok'


def _get_opening_hours(row):
    """Get opening hours from row data"""
    if pd.notna(row.get('monday_hours')):
        return row['monday_hours']
    elif pd.notna(row.get('sunday_hours')):
        return row['sunday_hours']
    return 'Contact for hours'
