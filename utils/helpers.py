import time
import random
from typing import List, Dict, Any, Optional, Callable
from functools import wraps
from datetime import datetime, timedelta
from models.data_models import Restaurant, Recommendation
from config.settings import CHATBOT_CONFIG
def timing_decorator(func: Callable) -> Callable:
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        execution_time = end_time - start_time
        func_name = func.__name__
        try:
            from utils.logger import get_logger
            logger = get_logger()
            logger.log_performance(func_name, execution_time)
        except:
            pass
        return result
    return wrapper
def retry_decorator(max_retries: int = 3, delay: float = 1.0):
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    if attempt == max_retries - 1:
                        raise e
                    time.sleep(delay * (2 ** attempt))
            return None
        return wrapper
    return decorator
class ResponseGenerator:
    def __init__(self):
        self.greeting_messages = CHATBOT_CONFIG['greeting_messages']
        self.fallback_messages = CHATBOT_CONFIG['fallback_messages']
    def generate_greeting(self) -> str:
        return random.choice(self.greeting_messages)
    def generate_recommendation_response(self, recommendations: List[Recommendation]) -> str:
        if not recommendations:
            return random.choice(self.fallback_messages)
        response_parts = []
        if len(recommendations) == 1:
            response_parts.append("Saya menemukan tempat yang cocok untuk Anda:")
        else:
            response_parts.append(f"Saya menemukan {len(recommendations)} tempat yang mungkin Anda suka:")
        for i, rec in enumerate(recommendations[:5], 1):
            restaurant = rec.restaurant
            score = rec.similarity_score
            restaurant_info = f"\n{i}. **{restaurant.name}** (Rating: {restaurant.rating}/5.0, Kecocokan: {score:.2f})"
            if restaurant.about:
                about_snippet = restaurant.about.split('.')[0][:100] + "..."
                restaurant_info += f"\n   {about_snippet}"
            if restaurant.cuisines:
                cuisines_str = ", ".join(restaurant.cuisines[:3])
                restaurant_info += f"\n   Jenis masakan: {cuisines_str}"
            if restaurant.price_range:
                restaurant_info += f"\n   Harga: {restaurant.price_range}"
            if restaurant.preferences:
                prefs = ", ".join(restaurant.preferences[:3])
                restaurant_info += f"\n   Keunggulan: {prefs}"
            response_parts.append(restaurant_info)
        response_parts.append("\nApakah ada yang menarik? Atau ingin saya carikan dengan kriteria yang berbeda?")
        return "\n".join(response_parts)
    def generate_fallback_response(self, user_query: str) -> str:
        fallback_msg = random.choice(self.fallback_messages)
        suggestions = [
            "Coba sebutkan jenis masakan yang Anda inginkan (contoh: 'pizza', 'sushi', 'seafood')",
            "Sebutkan lokasi yang Anda inginkan (contoh: 'Kuta', 'Gili Trawangan', 'Senggigi')",
            "Ceritakan suasana yang Anda cari (contoh: 'romantis', 'santai', 'tepi pantai')",
            "Sebutkan anggaran Anda (contoh: 'murah', 'menengah', 'mewah')"
        ]
        suggestion = random.choice(suggestions)
        return f"{fallback_msg}\n\nTips: {suggestion}"
    def generate_error_response(self) -> str:
        return "Maaf, terjadi kesalahan saat memproses permintaan Anda. Silakan coba lagi."
    def generate_goodbye_response(self) -> str:
        goodbyes = [
            "Terima kasih sudah menggunakan layanan kami! Selamat menikmati makanan!",
            "Sampai jumpa! Semoga Anda menemukan tempat makan yang sempurna!",
            "Selamat makan! Jangan lupa kembali lagi jika butuh rekomendasi lainnya!"
        ]
        return random.choice(goodbyes)
class TextFormatter:
    @staticmethod
    def format_restaurant_name(name: str) -> str:
        return name.title() if name else "Unknown Restaurant"
    @staticmethod
    def format_rating(rating: float) -> str:
        stars = "*" * int(rating)
        return f"{rating}/5.0 {stars}"
    @staticmethod
    def format_price_range(price_range: str) -> str:
        if not price_range:
            return "Harga tidak tersedia"
        price_map = {
            "$": "Murah",
            "$$": "Menengah", 
            "$$$": "Mahal",
            "$$$$": "Sangat Mahal",
            "$$-$$$": "Menengah ke Mahal"
        }
        return price_map.get(price_range, price_range)
    @staticmethod
    def format_list_items(items: List[str], max_items: int = 3) -> str:
        if not items:
            return "Tidak tersedia"
        if len(items) <= max_items:
            return ", ".join(items)
        else:
            shown_items = items[:max_items]
            remaining = len(items) - max_items
            return f"{', '.join(shown_items)} dan {remaining} lainnya"
    @staticmethod
    def truncate_text(text: str, max_length: int = 100) -> str:
        if not text or len(text) <= max_length:
            return text
        return text[:max_length].rsplit(' ', 1)[0] + "..."

def _fuzzy_location_match(query_location: str, restaurant_location: str) -> bool:
    """Fuzzy matching for location to handle variations like 'gili t' vs 'gili trawangan'"""
    # Exact match
    if query_location in restaurant_location:
        return True
    
    # Common abbreviations
    location_abbreviations = {
        'gili t': 'gili trawangan',
        'gili trawangan': 'gili trawangan',
        'kuta': 'kuta',
        'kuta lombok': 'kuta',
        'senggigi': 'senggigi',
        'mataram': 'mataram',
        'gili air': 'gili air',
        'gili meno': 'gili meno',
        'pemenang': 'pemenang',
    }
    
    # Check if abbreviation matches
    normalized_query = location_abbreviations.get(query_location, query_location)
    if normalized_query in restaurant_location:
        return True
    
    # Partial match for multi-word locations
    query_words = query_location.split()
    if len(query_words) > 1:
        # If all words in query appear in restaurant location
        return all(word in restaurant_location for word in query_words)
    
    return False

def calculate_boosted_score(base_score: float, query_entities: Dict[str, List[str]], 
                           restaurant: Restaurant) -> float:
    """Apply advanced boosting for entity matches with multi-tier weighting"""
    from config.settings import SYNONYM_MAP
    boost_factor = 1.0
    location_matched = False
    cuisine_matched = False
    preference_matched = False
    menu_matched = False
    
    # Tier 0: Location matching (HIGHEST PRIORITY)
    if 'location' in query_entities and query_entities['location']:
        for loc in query_entities['location']:
            loc_lower = loc.lower()
            # Check extracted location field first
            if isinstance(restaurant.location, str) and _fuzzy_location_match(loc_lower, restaurant.location.lower()):
                boost_factor *= 2.0  # Highest boost for location match
                location_matched = True
                break
            # Fallback to address field
            elif isinstance(restaurant.address, str) and _fuzzy_location_match(loc_lower, restaurant.address.lower()):
                boost_factor *= 1.8
                location_matched = True
                break
    
    # Tier 1: About field matching (general search)
    if 'about' in query_entities and query_entities['about']:
        if isinstance(restaurant.about, str):
            restaurant_about_lower = restaurant.about.lower()
            for term in query_entities['about']:
                if term.lower() in restaurant_about_lower:
                    boost_factor *= 1.5
                    break
    
    # Tier 2: Cuisine matching with advanced synonym expansion
    if 'cuisine' in query_entities and query_entities['cuisine']:
        # Safely handle cuisines - ensure it's a list
        if isinstance(restaurant.cuisines, list):
            restaurant_cuisines = [c.lower() for c in restaurant.cuisines]
        else:
            restaurant_cuisines = []
        # Safely handle name and about fields
        rest_name = restaurant.name.lower() if isinstance(restaurant.name, str) else ''
        rest_about = restaurant.about.lower() if isinstance(restaurant.about, str) else ''
        restaurant_text = ' '.join(restaurant_cuisines + [rest_name, rest_about])
            
        for cuisine in query_entities['cuisine']:
            cuisine_lower = cuisine.lower()
            
            # Direct match in name or cuisines (strongest)
            if isinstance(restaurant.name, str) and cuisine_lower in restaurant.name.lower():
                boost_factor *= 1.9
                cuisine_matched = True
                break
            elif any(cuisine_lower in rest_cuisine for rest_cuisine in restaurant_cuisines):
                boost_factor *= 1.7
                cuisine_matched = True
                break
                
            # Check comprehensive SYNONYM_MAP
            if cuisine_lower in SYNONYM_MAP:
                synonyms = SYNONYM_MAP[cuisine_lower]
                best_syn_boost = 1.0
                rest_name_lower = restaurant.name.lower() if isinstance(restaurant.name, str) else ''
                for syn in synonyms:
                    if syn in rest_name_lower:
                        best_syn_boost = max(best_syn_boost, 1.6)
                        cuisine_matched = True
                    elif syn in ' '.join(restaurant_cuisines):
                        best_syn_boost = max(best_syn_boost, 1.5)
                        cuisine_matched = True
                    elif syn in restaurant_text:
                        best_syn_boost = max(best_syn_boost, 1.3)
                        cuisine_matched = True
                if cuisine_matched:
                    boost_factor *= best_syn_boost
                    break
    
    # Tier 3: Preferences matching
    if 'preferences' in query_entities and query_entities['preferences']:
        # Safely handle preferences - ensure it's a list
        if isinstance(restaurant.preferences, list):
            restaurant_prefs = [p.lower() for p in restaurant.preferences]
        else:
            restaurant_prefs = []
        rest_about = restaurant.about.lower() if isinstance(restaurant.about, str) else ''
        restaurant_text = ' '.join(restaurant_prefs + [rest_about])
        for pref in query_entities['preferences']:
            pref_lower = pref.lower()
            if pref_lower in restaurant_text:
                boost_factor *= 1.25
                preference_matched = True
                break
            # Check preference synonyms
            if pref_lower in SYNONYM_MAP:
                for syn in SYNONYM_MAP[pref_lower]:
                    if syn in restaurant_text:
                        boost_factor *= 1.2
                        preference_matched = True
                        break
                if preference_matched:
                    break
    
    # Tier 4: Features matching
    if 'features' in query_entities and query_entities['features']:
        # Safely handle features - ensure it's a list
        if isinstance(restaurant.features, list):
            restaurant_features = [f.lower() for f in restaurant.features]
        else:
            restaurant_features = []
        for feat in query_entities['features']:
            if any(feat.lower() in f for f in restaurant_features):
                boost_factor *= 1.2
                break
    
    # Combination bonuses (multiplicative for strong signals)
    if location_matched and cuisine_matched:
        boost_factor *= 1.4  # Strong combo bonus
    if cuisine_matched and preference_matched:
        boost_factor *= 1.25  # Cuisine + ambiance bonus
    
    # Rating boost (quality signal)
    if restaurant.rating >= 4.8:
        boost_factor *= 1.2
    elif restaurant.rating >= 4.5:
        boost_factor *= 1.15
    elif restaurant.rating >= 4.0:
        boost_factor *= 1.08
    
    return min(base_score * boost_factor, 1.0)

def calculate_similarity_score(query_entities: Dict[str, List[str]], 
                             restaurant: Restaurant) -> float:
    total_score = 0.0
    total_weight = 0.0
    
    # Optimized weights for 5 entities
    weights = {
        'location': 0.50,  # Location is highest priority for restaurant search
        'cuisine': 0.40,  # Cuisine is second most important
        'about': 0.30,  # General description matching
        'preferences': 0.20,  # Preferences and ambiance
        'features': 0.20  # Facilities
    }
    
    # Location matching (HIGHEST PRIORITY)
    if 'location' in query_entities and query_entities['location']:
        location_score = 0.0
        query_locations = [l.lower() for l in query_entities['location']]
        
        for query_loc in query_locations:
            # Check extracted location field
            if isinstance(restaurant.location, str) and _fuzzy_location_match(query_loc, restaurant.location.lower()):
                location_score = 1.0
                break
            # Check full address
            elif isinstance(restaurant.address, str) and _fuzzy_location_match(query_loc, restaurant.address.lower()):
                location_score = 0.9
                break
        
        total_score += location_score * weights['location']
        total_weight += weights['location']
    
    # About field matching
    if 'about' in query_entities and query_entities['about']:
        about_score = 0.0
        if isinstance(restaurant.about, str):
            restaurant_about_lower = restaurant.about.lower()
            matches = sum(1 for term in query_entities['about'] if term.lower() in restaurant_about_lower)
            if query_entities['about']:
                about_score = min(matches / len(query_entities['about']), 1.0)
        total_score += about_score * weights['about']
        total_weight += weights['about']
    
    # Cuisine matching
    if 'cuisine' in query_entities and query_entities['cuisine']:
        cuisine_score = 0.0
        # Safely handle cuisines - ensure it's a list
        if isinstance(restaurant.cuisines, list):
            restaurant_cuisines = [c.lower() for c in restaurant.cuisines]
        else:
            restaurant_cuisines = []
        query_cuisines = [c.lower() for c in query_entities['cuisine']]
        
        matches = 0
        from config.settings import SYNONYM_MAP
        for query_cuisine in query_cuisines:
            # Check direct match
            for restaurant_cuisine in restaurant_cuisines:
                if query_cuisine == restaurant_cuisine or \
                   query_cuisine in restaurant_cuisine or \
                   restaurant_cuisine in query_cuisine:
                    matches += 1
                    break
            else:
                # Check synonym match if no direct match
                if query_cuisine in SYNONYM_MAP:
                    synonyms = SYNONYM_MAP[query_cuisine]
                    for synonym in synonyms:
                        if any(synonym in restaurant_cuisine for restaurant_cuisine in restaurant_cuisines):
                            matches += 0.8  # Slightly lower score for synonym match
                            break
        
        if query_cuisines:
            cuisine_score = min(matches / len(query_cuisines), 1.0)
        
        total_score += cuisine_score * weights['cuisine']
        total_weight += weights['cuisine']
    
    # Preferences matching
    if 'preferences' in query_entities and query_entities['preferences']:
        pref_score = 0.0
        # Safely handle preferences - ensure it's a list
        if isinstance(restaurant.preferences, list):
            restaurant_prefs = [p.lower() for p in restaurant.preferences]
        else:
            restaurant_prefs = []
        query_prefs = [p.lower() for p in query_entities['preferences']]
        matches = sum(1 for pref in query_prefs if any(pref in rest_pref or rest_pref in pref for rest_pref in restaurant_prefs))
        if query_prefs:
            pref_score = min(matches / len(query_prefs), 1.0)
        total_score += pref_score * weights['preferences']
        total_weight += weights['preferences']
    
    # Features matching
    if 'features' in query_entities and query_entities['features']:
        feature_score = 0.0
        # Safely handle features - ensure it's a list
        if isinstance(restaurant.features, list):
            restaurant_features = [f.lower() for f in restaurant.features]
        else:
            restaurant_features = []
        query_features = [f.lower() for f in query_entities['features']]
        matches = sum(1 for feature in query_features if any(feature in rest_feat or rest_feat in feature for rest_feat in restaurant_features))
        if query_features:
            feature_score = min(matches / len(query_features), 1.0)
        total_score += feature_score * weights['features']
        total_weight += weights['features']
    
    if total_weight > 0:
        final_score = total_score / total_weight
        return min(final_score, 1.0)
    else:
        return 0.0