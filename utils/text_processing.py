import re
import string
from typing import List, Set, Dict, Optional
from Sastrawi.Stemmer.StemmerFactory import StemmerFactory
from unidecode import unidecode

from config.settings import ENTITY_KEYWORDS


class TextPreprocessor:
    
    def __init__(self):
        self.stemmer = StemmerFactory().create_stemmer()
        self.stopwords = self._load_stopwords()
    
    def _load_stopwords(self) -> Set[str]:
        stopwords = {
            'yang', 'dan', 'di', 'dari', 'ke', 'untuk', 'pada', 'dengan', 'atau', 'adalah',
            'ini', 'itu', 'akan', 'dapat', 'dapat', 'juga', 'saya', 'anda', 'kita', 'mereka',
            'dia', 'ia', 'nya', 'mu', 'ku', 'se', 'ter', 'ber', 'per', 'an', 'kan', 'lah',
            'kah', 'pun', 'ada', 'tidak', 'bukan', 'belum', 'sudah', 'telah', 'sedang',
            'masih', 'akan', 'hendak', 'ingin', 'mau', 'bisa', 'dapat', 'boleh', 'harus',
            'wajib', 'perlu', 'penting', 'baik', 'bagus', 'jelek', 'buruk', 'besar', 'kecil'
        }
        
        return stopwords
    
    def clean_text(self, text: str) -> str:
        if not text:
            return ""
        
        text = text.lower()
        text = re.sub(r'[^\w\s]', ' ', text)
        text = re.sub(r'\s+', ' ', text)
        text = text.strip()
        
        return text
    
    def normalize_text(self, text: str) -> str:
        return unidecode(text)
    
    def remove_stopwords(self, text: str) -> str:
        words = text.split()
        filtered_words = [word for word in words if word not in self.stopwords]
        return ' '.join(filtered_words)
    
    def stem_text(self, text: str) -> str:
        return self.stemmer.stem(text)
    
    def preprocess(self, text: str, 
                   normalize: bool = True,
                   remove_stopwords: bool = False,
                   apply_stemming: bool = True) -> str:
        if not text:
            return ""
        
        processed_text = self.clean_text(text)
        
        if normalize:
            processed_text = self.normalize_text(processed_text)
        
        if remove_stopwords:
            processed_text = self.remove_stopwords(processed_text)
        
        if apply_stemming:
            processed_text = self.stem_text(processed_text)
        
        return processed_text
    
    def tokenize(self, text: str) -> List[str]:
        if not text:
            return []
        
        clean_text = self.clean_text(text)
        return clean_text.split()
    
    def extract_ngrams(self, text: str, n: int = 2) -> List[str]:
        words = self.tokenize(text)
        if len(words) < n:
            return []
        
        ngrams = []
        for i in range(len(words) - n + 1):
            ngram = ' '.join(words[i:i+n])
            ngrams.append(ngram)
        
        return ngrams


class EntityExtractor:
    
    def __init__(self):
        self.entity_keywords = ENTITY_KEYWORDS
        self.preprocessor = TextPreprocessor()
    
    def extract_entities(self, text: str) -> Dict[str, List[str]]:
        if not text:
            return {}
        
        clean_text = self.preprocessor.normalize_text(text.lower())
        
        entities = {}
        
        for entity_type, keywords in self.entity_keywords.items():
            found_entities = []
            
            for keyword in keywords:
                if keyword in clean_text:
                    found_entities.append(keyword)
                
                elif any(part in clean_text for part in keyword.split()):
                    found_entities.append(keyword)
            
            if found_entities:
                entities[entity_type] = list(set(found_entities))
        
        return entities
    
    def extract_intent(self, text: str) -> Optional[str]:
        clean_text = self.preprocessor.clean_text(text)
        
        intent_patterns = {
            'cari_restoran': [
                'cari', 'carikan', 'rekomendasi', 'rekomendasikan', 'sarankan',
                'mau makan', 'ingin makan', 'pengen makan', 'lapar'
            ],
            'info_restoran': [
                'info', 'informasi', 'detail', 'jam buka', 'alamat', 'harga',
                'menu', 'rating', 'review'
            ],
            'greeting': [
                'hai', 'halo', 'selamat', 'pagi', 'siang', 'sore', 'malam'
            ],
            'goodbye': [
                'terima kasih', 'selesai', 'keluar', 'bye', 'sampai jumpa'
            ]
        }
        
        for intent, patterns in intent_patterns.items():
            if any(pattern in clean_text for pattern in patterns):
                return intent
        
        return 'cari_restoran'
    
    def get_location_entities(self, text: str) -> List[str]:
        entities = self.extract_entities(text)
        return entities.get('lokasi', [])
    
    def get_cuisine_entities(self, text: str) -> List[str]:  
        entities = self.extract_entities(text)
        return entities.get('jenis_makanan', [])
    
    def get_menu_entities(self, text: str) -> List[str]:
        entities = self.extract_entities(text)
        return entities.get('menu', [])
    
    def get_preference_entities(self, text: str) -> List[str]:
        entities = self.extract_entities(text)
        return entities.get('preferensi', [])
