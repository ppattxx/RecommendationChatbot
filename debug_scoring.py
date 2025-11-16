"""
Debug script to check location scoring for restaurants
"""
import pandas as pd

# Load data
df = pd.read_csv('data/restaurants_entitas.csv')

# Test restaurants
test_restaurants = [
    'The Kliff',
    'Danima Restaurant', 
    'Pasta Pojok Senggigi',
    'Puri Mas Beachfront Restaurant',
    "Nuf'said Warung"
]

# User query: "restoran di senggigi"
user_location = 'senggigi'

print("=" * 80)
print("LOCATION SCORING DEBUG")
print("=" * 80)
print(f"User Query: 'restoran di senggigi yang enak'\n")
print(f"Expected: Only restaurants in Senggigi should have positive bonus\n")
print("=" * 80)

for restaurant_name in test_restaurants:
    row = df[df['name'] == restaurant_name]
    
    if not row.empty:
        row = row.iloc[0]
        location = str(row['location']).lower()
        
        # Calculate bonus (simplified from chatbot_service.py)
        bonus = 0.0
        location_match = False
        
        if user_location in location:
            bonus += 1.5  # Strong bonus for location match
            location_match = True
        else:
            bonus -= 2.0  # Strong penalty for location mismatch
        
        # Simulate preference boost (example values)
        preference_boost = 0.3 if 'Italian' in str(row['cuisines']) else 0.1
        
        # Simulate TF-IDF similarity (example)
        similarity = 0.15
        
        # Rating factor
        rating_factor = float(row['rating']) / 50.0
        
        # Total score
        total_score = similarity + bonus + (preference_boost * 1.5) + rating_factor
        
        status = "✅ MATCH" if location_match else "❌ MISMATCH"
        
        print(f"\n{restaurant_name}")
        print(f"  Location: {row['location']}")
        print(f"  Status: {status}")
        print(f"  ---")
        print(f"  Similarity Score: {similarity:.3f}")
        print(f"  Location Bonus:   {bonus:+.2f}")
        print(f"  Preference Boost: {preference_boost:.3f} (x1.5 = {preference_boost*1.5:.3f})")
        print(f"  Rating Factor:    {rating_factor:.3f}")
        print(f"  ---")
        print(f"  TOTAL SCORE:      {total_score:.3f}")
        print(f"  Expected Rank:    {'HIGH' if location_match else 'LOW (should be filtered)'}")
    else:
        print(f"\n{restaurant_name}: NOT FOUND in CSV")

print("\n" + "=" * 80)
print("CONCLUSION:")
print("=" * 80)
print("❌ Restaurants NOT in Senggigi should have NEGATIVE total score (< 0)")
print("✅ Restaurants IN Senggigi should have POSITIVE total score (> 0)")
print("=" * 80)
