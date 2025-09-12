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
        "threshold": 0.1
    }
}
RECOMMENDATION_CONFIG = {
    "default_top_n": 5,
    "max_recommendations": 10,
    "min_similarity_score": 0.3,
    "enable_learning": True
}
ENTITY_BONUS_WEIGHTS = {
    "jenis_makanan": 0.4,
    "lokasi": 0.5,
    "cuisine": 0.3,
    "preferences": 0.2,
    "features": 0.2
}
ENTITY_FIELD_MAPPING = {
    "jenis_makanan": ["cuisines", "entitas_jenis_makanan", "name", "about"],
    "lokasi": ["entitas_lokasi", "address", "name"],
    "cuisine": ["cuisines", "entitas_jenis_makanan"],
    "preferences": ["preferences", "entitas_preferensi", "about"],
    "features": ["features", "entitas_features"]
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
    "jenis_makanan": [
        "western", "asian", "italian", "italy", "italia", "japanese", "jepang", 
        "indonesian", "indonesia", "korean", "korea", "european", "eropa", 
        "chinese", "cina", "thai", "mexican", "meksiko", "indian", "mediterranean",
        "pizza", "sushi", "seafood", "steak", "barbecue", "barbeku", "grill", 
        "iga", "coffee", "kopi", "pasta", "burger", "salad", "curry", "noodles",
        "soup", "ramen", "tacos", "sandwich", "bar", "cafe", "fast food", 
        "international", "fusion", "healthy", "pub", "contemporary", "caucasian",
        "polynesian", "hawaiian", "southwestern", "mediterranean", "spanish", 
        "catalan", "central asian", "romana", "lazio", "central-italian", "dining bars"
    ],
    "lokasi": [
        "kuta", "senggigi", "gili trawangan", "gili t", "gili", "mataram", 
        "lombok", "pemenang", "gili indah", "gili air", "gili meno", "sunset boulevard",
        "kelapa road", "jalan bambu", "jl. bintang laut", "jl. raya kuta", 
        "jalan raya kuta", "jl. mawun sikara", "gili islands", "west nusa tenggara",
        "north lombok regency", "kardia resort", "kuta lombok"
    ],
    "cuisine": [
        "bar", "barbecue", "asian", "contemporary", "healthy", "indonesian", 
        "caucasian", "mexican", "southwestern", "polynesian", "hawaiian", "italian", 
        "pizza", "mediterranean", "european", "romana", "lazio", "central-italian",
        "cafe", "international", "fusion", "street food", "dining bars", "spanish",
        "catalan", "central asian", "pub", "fast food"
    ],
    "preferences": [
        "santai", "pesta", "keluarga", "romantis", "pemandangan", "matahari terbenam", 
        "murah", "mewah", "populer", "live music", "tepi pantai", "instagramable", 
        "free wifi", "outdoor", "indoor", "rooftop", "beachfront", "vegetarian", "vegan",
        "delicious food", "great atmosphere", "amazing food", "beautiful restaurant",
        "dinner spot", "lunch and dinner", "great stay", "perfect spot", "amazing place",
        "cool vibe", "good vibes", "great drinks", "fresh ingredients", "signature cocktails",
        "fresh food", "super friendly staff", "quick service", "beautiful sunset",
        "sea view", "fire show", "every night", "during our stay"
    ],
    "features": [
        "wifi", "reservasi", "delivery", "takeaway", "parking", "credit card",
        "outdoor seating", "live music", "happy hour", "buffet", "halal",
        "accepts credit cards", "free wifi", "full bar", "reservations", "seating",
        "serves alcohol", "table service", "digital payments", "mastercard", 
        "parking available", "street parking", "visa", "wheelchair accessible",
        "wine and beer", "takeout", "cash only", "family style", "free off-street parking",
        "gift cards available", "highchairs available", "sports bars"
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
    "port": 8000,
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