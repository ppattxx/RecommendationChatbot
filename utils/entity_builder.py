import pandas as pd
import ast
from typing import Dict, List, Set
from pathlib import Path

class EntityBuilder:
    
    def __init__(self, data_path: str = None):
        if data_path is None:
            base_dir = Path(__file__).parent.parent
            data_path = base_dir / "data" / "restaurants_entitas.csv"
        
        self.data_path = data_path
        self.df = None
        self.entity_patterns = None
    
    def load_data(self):
        self.df = pd.read_csv(self.data_path)
    
    def _parse_list_field(self, value) -> List[str]:
        if pd.isna(value):
            return []
        if isinstance(value, list):
            return value
        if isinstance(value, str):
            try:
                return ast.literal_eval(value)
            except:
                return []
        return []
    
    def build_cuisine_patterns(self) -> Dict[str, Set[str]]:
        all_cuisines = set()
        
        for cuisines in self.df['cuisines'].dropna():
            cuisine_list = self._parse_list_field(cuisines)
            for cuisine in cuisine_list:
                if cuisine:
                    all_cuisines.add(cuisine.lower().strip())
        
        if 'entitas_jenis_makanan' in self.df.columns:
            for cuisines in self.df['entitas_jenis_makanan'].dropna():
                cuisine_list = self._parse_list_field(cuisines)
                for cuisine in cuisine_list:
                    if cuisine:
                        all_cuisines.add(cuisine.lower().strip())
        
        return {'all_cuisines': sorted(all_cuisines)}
    
    def build_location_patterns(self) -> Dict[str, Set[str]]:
        all_locations = set()
        
        if 'entitas_lokasi' in self.df.columns:
            for location in self.df['entitas_lokasi'].dropna():
                if location:
                    all_locations.add(location.lower().strip())
        
        if 'location' in self.df.columns:
            for location in self.df['location'].dropna():
                if location:
                    location_parts = str(location).lower().split(',')
                    for part in location_parts:
                        clean_part = part.strip()
                        if clean_part and len(clean_part) > 3:
                            all_locations.add(clean_part)
        
        return {'all_locations': sorted(all_locations)}
    
    def build_menu_patterns(self) -> Dict[str, Set[str]]:
        all_menu_items = set()
        
        if 'entitas_menu' in self.df.columns:
            for menu in self.df['entitas_menu'].dropna():
                menu_list = self._parse_list_field(menu)
                for item in menu_list:
                    if item:
                        all_menu_items.add(item.lower().strip())
        
        return {'all_menu_items': sorted(all_menu_items)}
    
    def build_preference_patterns(self) -> Dict[str, Set[str]]:
        all_preferences = set()
        
        if 'entitas_preferensi' in self.df.columns:
            for prefs in self.df['entitas_preferensi'].dropna():
                pref_list = self._parse_list_field(prefs)
                for pref in pref_list:
                    if pref:
                        all_preferences.add(pref.lower().strip())
        
        if 'preferences' in self.df.columns:
            for prefs in self.df['preferences'].dropna():
                pref_list = self._parse_list_field(prefs)
                for pref in pref_list:
                    if pref:
                        all_preferences.add(pref.lower().strip())
        
        return {'all_preferences': sorted(all_preferences)}
    
    def build_feature_patterns(self) -> Dict[str, Set[str]]:
        all_features = set()
        
        if 'entitas_features' in self.df.columns:
            for features in self.df['entitas_features'].dropna():
                feature_list = self._parse_list_field(features)
                for feature in feature_list:
                    if feature:
                        all_features.add(feature.lower().strip())
        
        if 'features' in self.df.columns:
            for features in self.df['features'].dropna():
                feature_list = self._parse_list_field(features)
                for feature in feature_list:
                    if feature:
                        all_features.add(feature.lower().strip())
        
        return {'all_features': sorted(all_features)}
    
    def build_all_patterns(self) -> Dict[str, Dict]:
        if self.df is None:
            self.load_data()
        
        self.entity_patterns = {
            'cuisines': self.build_cuisine_patterns(),
            'locations': self.build_location_patterns(),
            'menu_items': self.build_menu_patterns(),
            'preferences': self.build_preference_patterns(),
            'features': self.build_feature_patterns()
        }
        
        return self.entity_patterns
    
    def get_flattened_patterns(self) -> Dict[str, List[str]]:
        if self.entity_patterns is None:
            self.build_all_patterns()
        
        return {
            'cuisine': self.entity_patterns['cuisines']['all_cuisines'],
            'location': self.entity_patterns['locations']['all_locations'],
            'menu': self.entity_patterns['menu_items']['all_menu_items'],
            'mood': self.entity_patterns['preferences']['all_preferences'],
            'features': self.entity_patterns['features']['all_features']
        }
    
    def save_patterns_to_file(self, output_path: str = None):
        if output_path is None:
            base_dir = Path(__file__).parent.parent
            output_path = base_dir / "config" / "auto_entity_patterns.py"
        
        if self.entity_patterns is None:
            self.build_all_patterns()
        
        patterns = self.get_flattened_patterns()
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write('"""Auto-generated entity patterns from restaurant data"""\n\n')
            
            for key, values in patterns.items():
                f.write(f'{key.upper()}_PATTERNS = [\n')
                for value in values:
                    f.write(f'    "{value}",\n')
                f.write(']\n\n')

if __name__ == "__main__":
    builder = EntityBuilder()
    patterns = builder.build_all_patterns()
    builder.save_patterns_to_file()
