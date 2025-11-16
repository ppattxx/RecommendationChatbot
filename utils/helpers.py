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

def calculate_similarity_score(query_entities: Dict[str, List[str]], 
                             restaurant: Restaurant) -> float:
    total_score = 0.0
    total_weight = 0.0
    
    weights = {
        'lokasi': 0.25,
        'jenis_makanan': 0.35,
        'cuisine': 0.35,
        'menu': 0.15,
        'preferensi': 0.15,
        'preferences': 0.15,
        'fitur': 0.1
    }
    
    if 'lokasi' in query_entities and query_entities['lokasi']:
        location_score = 0.0
        if restaurant.entitas_lokasi:
            for location in query_entities['lokasi']:
                if location.lower() in restaurant.entitas_lokasi.lower():
                    location_score = 1.0
                    break
        total_score += location_score * weights['lokasi']
        total_weight += weights['lokasi']
    
    cuisine_keys = ['jenis_makanan', 'cuisine']
    for key in cuisine_keys:
        if key in query_entities and query_entities[key]:
            cuisine_score = 0.0
            restaurant_cuisines = [c.lower() for c in restaurant.entitas_jenis_makanan]
            query_cuisines = [c.lower() for c in query_entities[key]]
            
            matches = 0
            for query_cuisine in query_cuisines:
                for restaurant_cuisine in restaurant_cuisines:
                    if query_cuisine == restaurant_cuisine or \
                       query_cuisine in restaurant_cuisine or \
                       restaurant_cuisine in query_cuisine:
                        matches += 1
                        break
            
            if query_cuisines:
                cuisine_score = min(matches / len(query_cuisines), 1.0)
            
            total_score += cuisine_score * weights[key]
            total_weight += weights[key]
    
    if 'menu' in query_entities and query_entities['menu']:
        menu_score = 0.0
        restaurant_menus = [m.lower() for m in restaurant.entitas_menu]
        query_menus = [m.lower() for m in query_entities['menu']]
        matches = sum(1 for menu in query_menus if any(menu in rest_menu or rest_menu in menu for rest_menu in restaurant_menus))
        if query_menus:
            menu_score = min(matches / len(query_menus), 1.0)
        total_score += menu_score * weights['menu']
        total_weight += weights['menu']
    
    pref_keys = ['preferensi', 'preferences']
    for key in pref_keys:
        if key in query_entities and query_entities[key]:
            pref_score = 0.0
            restaurant_prefs = [p.lower() for p in restaurant.entitas_preferensi]
            query_prefs = [p.lower() for p in query_entities[key]]
            matches = sum(1 for pref in query_prefs if any(pref in rest_pref or rest_pref in pref for rest_pref in restaurant_prefs))
            if query_prefs:
                pref_score = min(matches / len(query_prefs), 1.0)
            total_score += pref_score * weights[key]
            total_weight += weights[key]
    
    if 'fitur' in query_entities and query_entities['fitur']:
        feature_score = 0.0
        restaurant_features = [f.lower() for f in restaurant.entitas_features]
        query_features = [f.lower() for f in query_entities['fitur']]
        matches = sum(1 for feature in query_features if any(feature in rest_feat or rest_feat in feature for rest_feat in restaurant_features))
        if query_features:
            feature_score = min(matches / len(query_features), 1.0)
        total_score += feature_score * weights['fitur']
        total_weight += weights['fitur']
    
    if total_weight > 0:
        final_score = total_score / total_weight
        return min(final_score, 1.0)
    else:
        return 0.0