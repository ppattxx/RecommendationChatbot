import os
from pathlib import Path
from typing import Dict, List, Any
BASE_DIR = Path(__file__).parent.parent
DATA_DIR = BASE_DIR / "data"
MODELS_DIR = BASE_DIR / "models"
LOGS_DIR = BASE_DIR / "logs"
RESTAURANTS_CSV = DATA_DIR / "restaurants.csv"
RESTAURANTS_PROCESSED_CSV = DATA_DIR / "restaurants_processed.csv"
RESTAURANTS_ENTITAS_CSV = DATA_DIR / "restaurants_entitas.csv"
MODEL_CONFIG = {
    "tfidf": {
        "max_features": 5000,
        "min_df": 1,
        "max_df": 0.95,
        "stop_words": None,
        "ngram_range": (1, 2)
    },
    "similarity": {
        "metric": "cosine",
        "threshold": 0.003  # Balanced threshold
    },
    "use_synonym_expansion": True  # Enable synonym expansion for better matching
}
RECOMMENDATION_CONFIG = {
    "default_top_n": 5,
    "max_recommendations": 10,
    "min_similarity_score": 0.01,  # Optimized for best balance between precision and recall
    "enable_learning": True
}
ENTITY_BONUS_WEIGHTS = {
    "location": 0.5,  # Highest weight - location is crucial
    "cuisine": 0.4,
    "about": 0.3,
    "preferences": 0.2,
    "features": 0.2
}

SYNONYM_MAP = {
    # Food Types - Comprehensive Coverage
    'pizza': ['pizza', 'italian', 'italia', 'pizzeria', 'margherita', 'pepperoni', 'neapolitan', 'wood fired'],
    'sushi': ['sushi', 'japanese', 'jepang', 'japan', 'sashimi', 'maki', 'roll', 'nigiri', 'tempura', 'teriyaki'],
    'burger': ['burger', 'hamburger', 'american', 'cheeseburger', 'beef burger', 'chicken burger', 'veggie burger'],
    'pasta': ['pasta', 'italian', 'italia', 'spaghetti', 'fettuccine', 'linguine', 'penne', 'carbonara', 'bolognese', 'aglio olio', 'ravioli', 'lasagna'],
    'nasi goreng': ['nasi goreng', 'indonesian', 'indonesia', 'fried rice', 'nasgor', 'nasi', 'rice', 'local food'],
    'seafood': ['seafood', 'ikan', 'udang', 'cumi', 'kerang', 'fish', 'shrimp', 'prawn', 'lobster', 'crab', 'tuna', 'salmon', 'sea food', 'makanan laut', 'catch of the day', 'fresh fish'],
    'chicken': ['chicken', 'ayam', 'poultry', 'wings', 'fried chicken', 'grilled chicken', 'roast chicken', 'chicken satay'],
    'steak': ['steak', 'beef', 'daging', 'meat', 'tenderloin', 'sirloin', 'ribeye', 'wagyu', 'grilled meat', 'bbq meat'],
    'coffee': ['coffee', 'kopi', 'cafe', 'kafe', 'espresso', 'cappuccino', 'latte', 'americano', 'coffeeshop', 'coffee shop', 'barista'],
    'bakery': ['bakery', 'roti', 'bread', 'pastry', 'cake', 'croissant', 'bakehouse', 'patisserie', 'baked goods'],
    
    # Cuisines - Enhanced
    'mexican': ['mexican', 'meksiko', 'taco', 'burrito', 'quesadilla', 'nachos', 'enchilada', 'fajita', 'salsa', 'guacamole', 'southwestern'],
    'chinese': ['chinese', 'cina', 'china', 'dim sum', 'wonton', 'dumplings', 'noodles', 'chow mein', 'canton', 'mandarin'],
    'thai': ['thai', 'thailand', 'pad thai', 'tom yum', 'green curry', 'red curry', 'massaman', 'thai basil'],
    'mediterranean': ['mediterranean', 'mediterania', 'greek', 'yunani', 'turkish', 'turki', 'middle eastern', 'levantine'],
    'indian': ['indian', 'india', 'curry', 'tandoori', 'biryani', 'naan', 'tikka masala', 'vindaloo', 'korma'],
    'vietnamese': ['vietnamese', 'vietnam', 'pho', 'banh mi', 'spring rolls', 'bun', 'nem'],
    'french': ['french', 'prancis', 'france', 'bistro', 'brasserie', 'croissant', 'french cuisine'],
    'spanish': ['spanish', 'spanyol', 'spain', 'tapas', 'paella', 'catalan', 'iberian'],
    'korean': ['korean', 'korea', 'kimchi', 'bulgogi', 'bibimbap', 'korean bbq'],
    'indonesian': ['indonesian', 'indonesia', 'nasi goreng', 'satay', 'rendang', 'gado-gado', 'local', 'traditional'],
    'italian': ['italian', 'italia', 'italy', 'pizza', 'pasta', 'risotto', 'romano', 'lazio', 'central-italian'],
    'asian': ['asian', 'asia', 'oriental', 'pan-asian', 'southeast asian'],
    'european': ['european', 'eropa', 'continental', 'western'],
    'american': ['american', 'burger', 'fast food', 'bbq', 'diner', 'grill'],
    'japanese': ['japanese', 'jepang', 'japan', 'sushi', 'ramen', 'tempura', 'teriyaki', 'izakaya'],
    
    # BBQ & Grilling
    'bbq': ['bbq', 'barbecue', 'grill', 'grilled', 'panggang', 'smoke', 'smoked', 'barbeque', 'charcoal'],
    'grill': ['grill', 'grilled', 'bbq', 'barbecue', 'charcoal', 'wood fire', 'grillhouse'],
    
    # Dietary Preferences
    'vegetarian': ['vegetarian', 'vegetar', 'veggie', 'sayur', 'sayuran', 'vegetables', 'meat-free'],
    'vegan': ['vegan', 'plant based', 'nabati', 'plant-based', 'dairy-free'],
    'halal': ['halal', 'muslim-friendly', 'islamic', 'halal food', 'halal certified'],
    'organic': ['organic', 'healthy', 'natural', 'fresh', 'farm-to-table', 'sustainable'],
    'healthy': ['healthy', 'organic', 'fresh', 'clean eating', 'nutritious', 'wholesome'],
    
    # Meal Times
    'breakfast': ['breakfast', 'sarapan', 'pagi', 'morning', 'brunch', 'early morning'],
    'lunch': ['lunch', 'makan siang', 'siang', 'noon', 'afternoon', 'midday'],
    'dinner': ['dinner', 'makan malam', 'malam', 'evening', 'supper', 'night'],
    'brunch': ['brunch', 'breakfast', 'lunch', 'late breakfast', 'weekend brunch'],
    
    # Desserts
    'dessert': ['dessert', 'ice cream', 'gelato', 'sweet', 'manis', 'cake', 'pudding', 'pastry'],
    'ice cream': ['ice cream', 'gelato', 'frozen yogurt', 'sorbet', 'dessert', 'sweet'],
    
    # Drinks & Bar
    'bar': ['bar', 'pub', 'tavern', 'lounge', 'cocktail', 'drink', 'beer', 'wine', 'cocktail bar', 'sports bar'],
    'cocktail': ['cocktail', 'drink', 'bar', 'mixology', 'cocktail bar', 'signature drinks'],
    'wine': ['wine', 'vino', 'wine bar', 'wine list', 'wine selection'],
    'beer': ['beer', 'craft beer', 'brewery', 'ale', 'lager', 'pub'],
    
    # Price & Value
    'murah': ['murah', 'cheap', 'affordable', 'budget', 'inexpensive', 'economical', 'terjangkau', 'value'],
    'mahal': ['mahal', 'expensive', 'upscale', 'fine dining', 'luxury', 'premium', 'high-end'],
    'fine dining': ['fine dining', 'upscale', 'elegant', 'gourmet', 'haute cuisine', 'luxury dining'],
    
    # Ambiance & Style
    'romantis': ['romantis', 'romantic', 'intimate', 'cozy', 'date', 'couple', 'candlelit', 'date night'],
    'santai': ['santai', 'casual', 'relaxed', 'laid back', 'chill', 'easy going', 'informal'],
    'keluarga': ['keluarga', 'family', 'kids', 'children', 'family-friendly', 'kid-friendly', 'family style'],
    'cozy': ['cozy', 'intimate', 'warm', 'comfortable', 'homey', 'welcoming'],
    'elegant': ['elegant', 'sophisticated', 'classy', 'upscale', 'refined', 'chic'],
    
    # Views & Location Features
    'view': ['view', 'pemandangan', 'scenery', 'vista', 'panorama', 'sea view', 'ocean view', 'sunset view', 'beach view', 'scenic'],
    'sunset': ['sunset', 'matahari terbenam', 'sunset view', 'evening view', 'golden hour'],
    'beach': ['beach', 'pantai', 'beachfront', 'beach front', 'seaside', 'oceanfront', 'waterfront'],
    'beachfront': ['beachfront', 'beach front', 'beach', 'seaside', 'oceanfront', 'on the beach', 'beach side'],
    
    # Seating & Space
    'outdoor': ['outdoor', 'open air', 'terrace', 'patio', 'garden', 'beachfront', 'beach front', 'open-air', 'al fresco', 'outside'],
    'indoor': ['indoor', 'inside', 'air conditioned', 'ac', 'air-conditioned'],
    'terrace': ['terrace', 'outdoor', 'patio', 'rooftop', 'deck', 'balcony'],
    'rooftop': ['rooftop', 'roof', 'top floor', 'terrace', 'sky bar'],
    
    # Features & Amenities
    'wifi': ['wifi', 'wi-fi', 'internet', 'free wifi', 'wireless', 'free wi-fi', 'internet access'],
    'parking': ['parking', 'parkir', 'parking available', 'free parking', 'car park', 'parking space'],
    'music': ['music', 'live music', 'band', 'entertainment', 'acoustic', 'live band', 'live entertainment'],
    'takeaway': ['takeaway', 'take away', 'take-away', 'to go', 'takeout', 'take out'],
    'delivery': ['delivery', 'deliver', 'delivery service', 'online order', 'food delivery'],
    'reservation': ['reservation', 'booking', 'reserve', 'book', 'table booking'],
    
    # Group & Events
    'group': ['group', 'party', 'gathering', 'large group', 'groups', 'group dining'],
    'party': ['party', 'celebration', 'event', 'gathering', 'birthday', 'private dining'],
    
    # Quality & Freshness
    'fresh': ['fresh', 'segar', 'fresh ingredients', 'daily catch', 'freshly made', 'fresh daily'],
    'delicious': ['delicious', 'enak', 'tasty', 'yummy', 'great food', 'amazing food'],
    'authentic': ['authentic', 'traditional', 'original', 'genuine', 'real', 'true'],
    
    # Service Style
    'buffet': ['buffet', 'all you can eat', 'self service', 'unlimited'],
    'fast food': ['fast food', 'quick service', 'quick bite', 'fast casual'],
}
ENTITY_FIELD_MAPPING = {
    "about": ["about", "name"],
    "location": ["entitas_lokasi"], 
    "cuisine": ["cuisines"],
    "preferences": ["preferences"],
    "features": ["features"]
}
CHATBOT_CONFIG = {
    "greeting_messages": [
        "Selamat datang di Chatbot Rekomendasi Restoran!",
        "Saya siap membantu Anda menemukan tempat makan yang pas!",
        "Mari cari restoran yang cocok untuk Anda!"
    ],
    "fallback_messages": [
        "Maaf, saya tidak menemukan restoran yang cocok dengan kriteria Anda.",
        "Coba gunakan kata kunci yang berbeda untuk pencarian yang lebih baik.",
        "Mungkin Anda bisa coba dengan deskripsi yang lebih spesifik?"
    ],
    "exit_keywords": ["keluar", "exit", "quit", "selesai", "bye"],
    "max_conversation_length": 50
}
ENTITY_KEYWORDS = {
    # Location keywords - highest priority (weight 0.5)
    "location": [
        "kuta", "senggigi", "gili trawangan", "gili t", "gili", "mataram", 
        "lombok", "pemenang", "gili indah", "gili air", "gili meno", "sunset boulevard",
        "kelapa road", "jalan bambu", "jl. bintang laut", "jl. raya kuta", 
        "jalan raya kuta", "jl. mawun sikara", "gili islands", "west nusa tenggara",
        "north lombok regency", "kardia resort", "kuta lombok", "di", "dekat", "sekitar"
    ],
    
    # Cuisine keywords - second priority (weight 0.4)
    "cuisine": [
        "western", "asian", "italian", "italy", "italia", "japanese", "jepang", 
        "indonesian", "indonesia", "korean", "korea", "european", "eropa", 
        "chinese", "cina", "thai", "mexican", "meksiko", "indian", "mediterranean",
        "pizza", "sushi", "seafood", "steak", "barbecue", "barbeku", "grill", 
        "iga", "coffee", "kopi", "pasta", "burger", "salad", "curry", "noodles",
        "soup", "ramen", "tacos", "sandwich", "bar", "cafe", "fast food", 
        "international", "fusion", "healthy", "pub", "contemporary", "caucasian",
        "polynesian", "hawaiian", "southwestern", "spanish", 
        "catalan", "central asian", "romana", "lazio", "central-italian", "dining bars",
        "makanan", "makan", "restoran", "restaurant", "tempat makan"
    ],
    
    # About keywords - general descriptors (weight 0.3)
    "about": [
        "enak", "lezat", "nikmat", "sedap", "mantap", "terbaik", "best", "top",
        "recommended", "rekomendasi", "populer", "terkenal", "famous", "hits",
        "baru", "new", "modern", "tradisional", "traditional", "authentic",
        "murah", "terjangkau", "affordable", "mahal", "mewah", "luxury", "premium",
        "bagus", "good", "great", "excellent", "amazing", "wonderful"
    ],
    
    # Preferences keywords - ambiance and atmosphere (weight 0.2)
    "preferences": [
        "santai", "casual", "relaxed", "pesta", "party", "keluarga", "family", 
        "romantis", "romantic", "intimate", "pemandangan", "view", "matahari terbenam", "sunset",
        "live music", "musik", "tepi pantai", "beachfront", "beach", "pantai",
        "instagramable", "aesthetic", "outdoor", "indoor", "rooftop", "terrace",
        "vegetarian", "vegan", "halal", "organic", "healthy",
        "delicious food", "great atmosphere", "amazing food", "beautiful restaurant",
        "dinner spot", "lunch and dinner", "great stay", "perfect spot", "amazing place",
        "cool vibe", "good vibes", "great drinks", "fresh ingredients", "signature cocktails",
        "fresh food", "super friendly staff", "quick service", "beautiful sunset",
        "sea view", "fire show", "cozy", "nyaman", "tenang", "ramai", "crowded"
    ],
    
    # Features keywords - amenities and facilities (weight 0.2)
    "features": [
        "wifi", "wi-fi", "internet", "reservasi", "booking", "delivery", "antar",
        "takeaway", "takeout", "bungkus", "parking", "parkir", "credit card", "kartu kredit",
        "outdoor seating", "tempat duduk luar", "live music", "musik langsung",
        "happy hour", "buffet", "prasmanan", "halal", "accepts credit cards", 
        "free wifi", "full bar", "reservations", "seating", "serves alcohol",
        "table service", "digital payments", "mastercard", "visa", 
        "parking available", "street parking", "wheelchair accessible",
        "wine and beer", "takeout", "cash only", "family style", 
        "free off-street parking", "gift cards available", "highchairs available", 
        "sports bars", "ac", "air conditioner", "smoking area", "non smoking"
    ]
}
LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "detailed": {
            "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            "datefmt": "%Y-%m-%d %H:%M:%S"
        },
        "simple": {
            "format": "%(levelname)s - %(message)s"
        }
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "level": "INFO",
            "formatter": "simple",
            "stream": "ext://sys.stdout"
        },
        "file": {
            "class": "logging.FileHandler",
            "level": "DEBUG",
            "formatter": "detailed",
            "filename": str(LOGS_DIR / "chatbot.log"),
            "mode": "a"
        }
    },
    "loggers": {
        "chatbot": {
            "level": "DEBUG",
            "handlers": ["console", "file"],
            "propagate": False
        }
    }
}
API_CONFIG = {
    "host": "0.0.0.0",
    "port": 5500,
    "debug": True,
    "api_version": "v1"
}
DATABASE_CONFIG = {
    "sqlite": {
        "path": str(BASE_DIR / "chatbot.db"),
        "echo": False
    }
}
def load_env_config() -> Dict[str, Any]:
    from dotenv import load_dotenv
    load_dotenv()
    return {
        "debug": os.getenv("DEBUG", "True").lower() == "true",
        "log_level": os.getenv("LOG_LEVEL", "INFO"),
        "data_update_interval": int(os.getenv("DATA_UPDATE_INTERVAL", "3600")),
        "max_cache_size": int(os.getenv("MAX_CACHE_SIZE", "1000"))
    }