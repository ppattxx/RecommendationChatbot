"""
Script to enrich dataset with auto-generated entities
"""

import pandas as pd
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from config.settings import RESTAURANTS_ENTITAS_CSV, SYNONYM_MAP

def enrich_restaurant_entities(df):
    """Auto-annotate missing entities from about text"""
    
    # Cuisine to food mapping
    CUISINE_FOOD_MAP = {
        'Italian': ['pizza', 'pasta', 'risotto', 'lasagna'],
        'Japanese': ['sushi', 'ramen', 'tempura', 'teriyaki'],
        'Mexican': ['taco', 'burrito', 'quesadilla', 'nachos'],
        'American': ['burger', 'steak', 'bbq', 'wings'],
        'Chinese': ['noodles', 'dim sum', 'fried rice', 'dumplings'],
        'Thai': ['pad thai', 'curry', 'tom yum'],
        'Indonesian': ['nasi goreng', 'sate', 'rendang', 'gado-gado'],
        'Asian': ['asian', 'noodles', 'rice', 'stir fry'],
        'Mediterranean': ['mediterranean', 'seafood', 'salad'],
        'Seafood': ['seafood', 'fish', 'shrimp', 'lobster'],
    }
    
    # Meal time patterns
    MEAL_PATTERNS = {
        'breakfast': ['breakfast', 'sarapan', 'morning', 'pagi'],
        'lunch': ['lunch', 'makan siang', 'noon'],
        'dinner': ['dinner', 'makan malam', 'evening', 'supper'],
        'brunch': ['brunch']
    }
    
    for idx, row in df.iterrows():
        about_lower = str(row['about']).lower() if pd.notna(row['about']) else ""
        name_lower = str(row['name']).lower()
        
        # Enrich jenis_makanan from cuisines
        current_jenis_makanan = eval(row['entitas_jenis_makanan']) if pd.notna(row['entitas_jenis_makanan']) and row['entitas_jenis_makanan'] != '[]' else []
        cuisines = eval(row['cuisines']) if pd.notna(row['cuisines']) and row['cuisines'] != '[]' else []
        
        for cuisine in cuisines:
            if cuisine in CUISINE_FOOD_MAP:
                for food in CUISINE_FOOD_MAP[cuisine]:
                    if food not in current_jenis_makanan:
                        current_jenis_makanan.append(food)
        
        # Extract food keywords from about and name
        for main_term, synonyms in SYNONYM_MAP.items():
            for synonym in synonyms:
                if synonym in about_lower or synonym in name_lower:
                    if main_term not in current_jenis_makanan:
                        current_jenis_makanan.append(main_term)
                    if synonym not in current_jenis_makanan:
                        current_jenis_makanan.append(synonym)
        
        df.at[idx, 'entitas_jenis_makanan'] = str(list(set(current_jenis_makanan)))
        
        # Enrich preferences with meal times
        current_preferences = eval(row['entitas_preferensi']) if pd.notna(row['entitas_preferensi']) and row['entitas_preferensi'] != '[]' else []
        
        for meal, patterns in MEAL_PATTERNS.items():
            if any(pattern in about_lower for pattern in patterns):
                if meal not in current_preferences:
                    current_preferences.append(meal)
        
        # Add common descriptors
        if 'romantic' in about_lower or 'romantis' in about_lower:
            if 'romantis' not in current_preferences:
                current_preferences.append('romantis')
        
        if 'family' in about_lower or 'keluarga' in about_lower:
            if 'keluarga' not in current_preferences:
                current_preferences.append('keluarga')
        
        if 'view' in about_lower or 'pemandangan' in about_lower or 'sunset' in about_lower:
            if 'pemandangan' not in current_preferences:
                current_preferences.append('pemandangan')
        
        if 'cheap' in about_lower or 'affordable' in about_lower or 'murah' in about_lower:
            if 'murah' not in current_preferences:
                current_preferences.append('murah')
        
        if 'fresh' in about_lower:
            if 'fresh' not in current_preferences:
                current_preferences.append('fresh')
        
        df.at[idx, 'entitas_preferensi'] = str(list(set(current_preferences)))
    
    return df

def main():
    print("Loading dataset...")
    df = pd.read_csv(RESTAURANTS_ENTITAS_CSV)
    
    print(f"Original dataset: {len(df)} restaurants")
    print("\nEnriching entities...")
    
    df_enriched = enrich_restaurant_entities(df)
    
    # Save enriched dataset
    output_path = RESTAURANTS_ENTITAS_CSV
    df_enriched.to_csv(output_path, index=False)
    
    print(f"\nEnriched dataset saved to: {output_path}")
    print("\nSample of enriched entities:")
    
    # Show sample
    for idx in range(min(5, len(df_enriched))):
        print(f"\n{idx+1}. {df_enriched.iloc[idx]['name']}")
        print(f"   Cuisines: {df_enriched.iloc[idx]['cuisines']}")
        print(f"   Jenis Makanan: {df_enriched.iloc[idx]['entitas_jenis_makanan']}")
        print(f"   Preferensi: {df_enriched.iloc[idx]['entitas_preferensi']}")
    
    print("\nDataset enrichment completed!")

if __name__ == "__main__":
    main()
