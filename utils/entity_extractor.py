import pandas as pd
import re
from typing import Dict, List, Set, Tuple
from pathlib import Path
from utils.entity_builder import EntityBuilder
from utils.logger import get_logger

logger = get_logger("entity_extractor")


class EntityExtractor:
    """
    Advanced entity extractor yang mengekstrak entitas dari user query
    Menggunakan pattern matching dan fuzzy matching dari dataset
    """

    def __init__(self, data_path: str = None):
        if data_path is None:
            base_dir = Path(__file__).parent.parent
            data_path = base_dir / "data" / "restaurants_entitas.csv"

        self.data_path = data_path
        self.df = None
        self.entity_builder = EntityBuilder(data_path=str(data_path))
        self.entity_patterns = None
        
        self._load_data()
        self._build_patterns()

    def _load_data(self):
        """Load dataset dari CSV"""
        try:
            self.df = pd.read_csv(self.data_path)
            logger.info(f"Loaded data from {self.data_path}")
        except Exception as e:
            logger.error(f"Error loading data: {e}")
            self.df = None

    def _build_patterns(self):
        """Build entity patterns dari dataset"""
        try:
            self.entity_patterns = self.entity_builder.build_all_patterns()
            logger.info("Built entity patterns successfully")
        except Exception as e:
            logger.error(f"Error building patterns: {e}")
            self.entity_patterns = {}

    def _parse_list_field(self, value) -> List[str]:
        """Helper untuk parse list field dari CSV"""
        if pd.isna(value):
            return []
        if isinstance(value, list):
            return value
        if isinstance(value, str):
            try:
                import ast
                return ast.literal_eval(value)
            except:
                return [value]
        return []

    def extract_entities(self, query: str) -> Dict[str, List[str]]:
        """
        Extract semua entitas dari query
        
        Returns:
            Dict dengan keys: cuisine, location, menu, mood, features, price_range
        """
        query_lower = query.lower()
        entities = {
            'cuisine': [],
            'location': [],
            'menu': [],
            'mood': [],
            'features': [],
            'price_range': []
        }
        
        if not self.entity_patterns:
            return entities

        try:
            # Extract cuisine/jenis makanan
            entities['cuisine'] = self._extract_cuisine(query_lower)
            
            # Extract lokasi
            entities['location'] = self._extract_location(query_lower)
            
            # Extract menu items
            entities['menu'] = self._extract_menu_items(query_lower)
            
            # Extract mood/preferensi
            entities['mood'] = self._extract_mood(query_lower)
            
            # Extract features
            entities['features'] = self._extract_features(query_lower)
            
            # Extract price range
            entities['price_range'] = self._extract_price_range(query_lower)
            
            logger.info(f"Extracted entities from query '{query}': {entities}")
            return entities
            
        except Exception as e:
            logger.error(f"Error extracting entities: {e}")
            return entities

    def _extract_cuisine(self, query_lower: str) -> List[str]:
        """Extract jenis makanan/cuisine dari query"""
        cuisines = []
        cuisine_patterns = self.entity_patterns.get('cuisines', {}).get('all_cuisines', [])
        
        # Sorted by length (longest first) untuk match yang lebih akurat
        for cuisine in sorted(cuisine_patterns, key=len, reverse=True):
            if self._match_entity(cuisine, query_lower):
                if cuisine not in cuisines:
                    cuisines.append(cuisine)
        
        return cuisines

    def _extract_location(self, query_lower: str) -> List[str]:
        """Extract lokasi dari query"""
        locations = []
        location_patterns = self.entity_patterns.get('locations', {}).get('all_locations', [])
        
        for location in sorted(location_patterns, key=len, reverse=True):
            if self._match_entity(location, query_lower):
                if location not in locations:
                    locations.append(location)
        
        return locations

    def _extract_menu_items(self, query_lower: str) -> List[str]:
        """Extract menu items dari query"""
        menu_items = []
        menu_patterns = self.entity_patterns.get('menu_items', {}).get('all_menu_items', [])
        
        for menu in sorted(menu_patterns, key=len, reverse=True):
            if self._match_entity(menu, query_lower):
                if menu not in menu_items:
                    menu_items.append(menu)
        
        return menu_items

    def _extract_mood(self, query_lower: str) -> List[str]:
        """Extract mood/preferensi dari query"""
        moods = []
        mood_patterns = self.entity_patterns.get('preferences', {}).get('all_preferences', [])
        
        for mood in sorted(mood_patterns, key=len, reverse=True):
            # Skip jika sudah ada sebagai cuisine atau menu
            if self._match_entity(mood, query_lower):
                if mood not in moods:
                    moods.append(mood)
        
        return moods

    def _extract_features(self, query_lower: str) -> List[str]:
        """Extract fitur restoran dari query"""
        features = []
        feature_patterns = self.entity_patterns.get('features', {}).get('all_features', [])
        
        for feature in sorted(feature_patterns, key=len, reverse=True):
            if self._match_entity(feature, query_lower):
                if feature not in features:
                    features.append(feature)
        
        return features

    def _extract_price_range(self, query_lower: str) -> List[str]:
        """Extract price range dari query"""
        price_ranges = []
        
        price_keywords = {
            'murah': ['murah', 'terjangkau', 'budgert', 'hemat', 'murah meriah'],
            'sedang': ['sedang', 'medium', 'standar'],
            'mahal': ['mahal', 'mewah', 'premium', 'exclusive', 'fine dining']
        }
        
        for price_level, keywords in price_keywords.items():
            for keyword in keywords:
                if re.search(r'\b' + re.escape(keyword) + r'\b', query_lower):
                    if price_level not in price_ranges:
                        price_ranges.append(price_level)
                    break
        
        return price_ranges

    def _match_entity(self, entity: str, query: str, fuzzy: bool = True) -> bool:
        """
        Match entity dengan query menggunakan word boundary
        
        Args:
            entity: Entity string yang dicari
            query: Query string
            fuzzy: Apakah menggunakan fuzzy matching
            
        Returns:
            True jika entity ditemukan di query
        """
        # Normalized match dengan word boundary
        pattern = r'\b' + re.escape(entity) + r'\b'
        return bool(re.search(pattern, query))

    def extract_intent(self, query: str) -> str:
        """
        Extract intent dari query
        
        Returns:
            Intent type: 'restaurant_search', 'restaurant_details', dst
        """
        query_lower = query.lower()
        
        # Detail/info intent
        if any(word in query_lower for word in ['detail', 'info', 'tentang', 'apa', 'siapa', 'bagaimana']):
            return 'restaurant_details'
        
        # Search intent
        return 'restaurant_search'

    def get_search_context(self, query: str, entities: Dict[str, List[str]] = None) -> Dict:
        """
        Get search context yang lengkap dari query dan entities
        
        Returns:
            Dict dengan context untuk recommendation engine
        """
        if entities is None:
            entities = self.extract_entities(query)
        
        context = {
            'query': query,
            'entities': entities,
            'intent': self.extract_intent(query),
            'has_location': bool(entities.get('location')),
            'has_cuisine': bool(entities.get('cuisine')),
            'has_menu': bool(entities.get('menu')),
            'has_mood': bool(entities.get('mood')),
            'has_price': bool(entities.get('price_range')),
            'primary_entity_type': self._get_primary_entity_type(entities)
        }
        
        return context

    def _get_primary_entity_type(self, entities: Dict[str, List[str]]) -> str:
        """Tentukan primary entity type dari entities yang diekstrak"""
        if entities.get('location'):
            return 'location'
        elif entities.get('cuisine'):
            return 'cuisine'
        elif entities.get('menu'):
            return 'menu'
        elif entities.get('mood'):
            return 'mood'
        else:
            return 'generic'

    def validate_entities(self, entities: Dict[str, List[str]]) -> bool:
        """Check apakah entities valid"""
        return any(
            entities.get(key) 
            for key in ['cuisine', 'location', 'menu', 'mood', 'price_range']
        )

    def get_entity_summary(self, entities: Dict[str, List[str]]) -> str:
        """Get human-readable summary dari entities"""
        summary_parts = []
        
        if entities.get('cuisine'):
            summary_parts.append(f"Jenis: {', '.join(entities['cuisine'])}")
        
        if entities.get('location'):
            summary_parts.append(f"Lokasi: {', '.join(entities['location'])}")
        
        if entities.get('menu'):
            summary_parts.append(f"Menu: {', '.join(entities['menu'])}")
        
        if entities.get('mood'):
            summary_parts.append(f"Suasana: {', '.join(entities['mood'])}")
        
        if entities.get('price_range'):
            summary_parts.append(f"Harga: {', '.join(entities['price_range'])}")
        
        return " | ".join(summary_parts) if summary_parts else "Tidak ada entitas terdeteksi"


class EntityMatcher:
    """Helper class untuk matching entities dengan restaurants"""
    
    def __init__(self, df: pd.DataFrame):
        self.df = df

    def find_matching_restaurants(
        self, 
        entities: Dict[str, List[str]], 
        match_threshold: float = 0.5
    ) -> List[int]:
        """
        Find restaurants yang match dengan entities
        
        Args:
            entities: Dict dari entities yang diekstrak
            match_threshold: Minimum score untuk dianggap match
            
        Returns:
            List dari restaurant IDs yang match
        """
        if self.df is None or self.df.empty:
            return []
        
        matching_indices = []
        
        for idx, row in self.df.iterrows():
            match_score = self._calculate_match_score(row, entities)
            
            if match_score >= match_threshold:
                matching_indices.append(idx)
        
        return matching_indices

    def _calculate_match_score(self, row: pd.Series, entities: Dict[str, List[str]]) -> float:
        """Calculate match score antara restaurant dengan entities"""
        score = 0.0
        total_weight = 0.0
        
        # Cuisine matching
        if entities.get('cuisine'):
            total_weight += 1.0
            row_cuisines = self._parse_list_field(row.get('entitas_jenis_makanan', ''))
            row_cuisines_lower = [c.lower() for c in row_cuisines]
            
            matches = sum(1 for e in entities['cuisine'] if e.lower() in row_cuisines_lower)
            score += (matches / len(entities['cuisine'])) if entities['cuisine'] else 0
        
        # Location matching
        if entities.get('location'):
            total_weight += 1.0
            row_location = str(row.get('entitas_lokasi', '')).lower()
            
            matches = sum(1 for e in entities['location'] if e.lower() in row_location)
            score += (matches / len(entities['location'])) if entities['location'] else 0
        
        # Menu matching
        if entities.get('menu'):
            total_weight += 0.8
            row_menu = self._parse_list_field(row.get('entitas_menu', ''))
            row_menu_lower = [m.lower() for m in row_menu]
            
            matches = sum(1 for e in entities['menu'] if e.lower() in row_menu_lower)
            score += (matches / len(entities['menu'])) * 0.8 if entities['menu'] else 0
        
        # Mood/Preference matching
        if entities.get('mood'):
            total_weight += 0.6
            row_mood = self._parse_list_field(row.get('entitas_preferensi', ''))
            row_mood_lower = [m.lower() for m in row_mood]
            
            matches = sum(1 for e in entities['mood'] if e.lower() in row_mood_lower)
            score += (matches / len(entities['mood'])) * 0.6 if entities['mood'] else 0
        
        # Price range matching
        if entities.get('price_range'):
            total_weight += 0.5
            row_price = str(row.get('price_range', '')).lower()
            
            for price in entities['price_range']:
                if price.lower() in row_price:
                    score += 0.5
                    break
        
        # Normalize score
        if total_weight > 0:
            return score / total_weight
        
        return 0.0

    def _parse_list_field(self, value) -> List[str]:
        """Helper untuk parse list field"""
        if pd.isna(value):
            return []
        if isinstance(value, list):
            return value
        if isinstance(value, str):
            try:
                import ast
                return ast.literal_eval(value)
            except:
                return [value]
        return []


if __name__ == "__main__":
    extractor = EntityExtractor()
    
    # Test queries
    test_queries = [
        "Cari pizza di Kuta",
        "Sushi murah di Senggigi",
        "Restoran romantic dengan seafood",
        "Makanan sehat di Lombok",
        "Tempat makan keluarga yang nyaman"
    ]
    
    for query in test_queries:
        print(f"\nQuery: {query}")
        entities = extractor.extract_entities(query)
        context = extractor.get_search_context(query, entities)
        print(f"Entities: {extractor.get_entity_summary(entities)}")
        print(f"Context: {context}")
