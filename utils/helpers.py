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
class SessionManager:
    def __init__(self):
        self.sessions: Dict[str, Dict[str, Any]] = {}
        self.session_timeout = timedelta(hours=2)
    def create_session(self, user_id: str) -> str:
        session_id = f"{user_id}_{int(time.time())}"
        self.sessions[session_id] = {
            'user_id': user_id,
            'created_at': datetime.now(),
            'last_activity': datetime.now(),
            'conversation_history': [],
            'context': {}
        }
        return session_id
    def get_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        if session_id not in self.sessions:
            return None
        session = self.sessions[session_id]
        if datetime.now() - session['last_activity'] > self.session_timeout:
            del self.sessions[session_id]
            return None
        return session
    def update_session(self, session_id: str, **updates):
        if session_id in self.sessions:
            self.sessions[session_id].update(updates)
            self.sessions[session_id]['last_activity'] = datetime.now()
    def add_to_conversation_history(self, session_id: str, user_query: str, bot_response: str):
        if session_id in self.sessions:
            history_item = {
                'timestamp': datetime.now().isoformat(),
                'user_query': user_query,
                'bot_response': bot_response
            }
            self.sessions[session_id]['conversation_history'].append(history_item)
            if len(self.sessions[session_id]['conversation_history']) > 20:
                self.sessions[session_id]['conversation_history'] = \
                    self.sessions[session_id]['conversation_history'][-20:]
    def cleanup_expired_sessions(self):
        now = datetime.now()
        expired_sessions = []
        for session_id, session in self.sessions.items():
            if now - session['last_activity'] > self.session_timeout:
                expired_sessions.append(session_id)
        for session_id in expired_sessions:
            del self.sessions[session_id]
def calculate_similarity_score(query_entities: Dict[str, List[str]], 
                             restaurant: Restaurant) -> float:
    total_score = 0.0
    total_weight = 0.0
    weights = {
        'lokasi': 0.3,
        'jenis_makanan': 0.25,
        'menu': 0.2,
        'preferensi': 0.15,
        'fitur': 0.1
    }
    if 'lokasi' in query_entities:
        location_score = 0.0
        if restaurant.entitas_lokasi:
            for location in query_entities['lokasi']:
                if location.lower() in restaurant.entitas_lokasi.lower():
                    location_score = 1.0
                    break
        total_score += location_score * weights['lokasi']
        total_weight += weights['lokasi']
    if 'jenis_makanan' in query_entities:
        cuisine_score = 0.0
        restaurant_cuisines = [c.lower() for c in restaurant.entitas_jenis_makanan]
        query_cuisines = [c.lower() for c in query_entities['jenis_makanan']]
        matches = sum(1 for cuisine in query_cuisines if cuisine in restaurant_cuisines)
        if query_cuisines:
            cuisine_score = matches / len(query_cuisines)
        total_score += cuisine_score * weights['jenis_makanan']
        total_weight += weights['jenis_makanan']
    if 'menu' in query_entities:
        menu_score = 0.0
        restaurant_menus = [m.lower() for m in restaurant.entitas_menu]
        query_menus = [m.lower() for m in query_entities['menu']]
        matches = sum(1 for menu in query_menus if menu in restaurant_menus)
        if query_menus:
            menu_score = matches / len(query_menus)
        total_score += menu_score * weights['menu']
        total_weight += weights['menu']
    if 'preferensi' in query_entities:
        pref_score = 0.0
        restaurant_prefs = [p.lower() for p in restaurant.entitas_preferensi]
        query_prefs = [p.lower() for p in query_entities['preferensi']]
        matches = sum(1 for pref in query_prefs if pref in restaurant_prefs)
        if query_prefs:
            pref_score = matches / len(query_prefs)
        total_score += pref_score * weights['preferensi']
        total_weight += weights['preferensi']
    if 'fitur' in query_entities:
        feature_score = 0.0
        restaurant_features = [f.lower() for f in restaurant.entitas_features]
        query_features = [f.lower() for f in query_entities['fitur']]
        matches = sum(1 for feature in query_features if feature in restaurant_features)
        if query_features:
            feature_score = matches / len(query_features)
        total_score += feature_score * weights['fitur']
        total_weight += weights['fitur']
    if total_weight > 0:
        return total_score / total_weight
    else:
        return 0.0