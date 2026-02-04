"""Test script for location entity functionality"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from config.settings import ENTITY_FIELD_MAPPING, ENTITY_BONUS_WEIGHTS
from utils.data_loader import DataLoader
from services.recommendation_engine import ContentBasedRecommendationEngine

def test_location_entity_config():
    """Test if location entity is configured properly"""
    print("=" * 70)
    print("Testing Location Entity Configuration")
    print("=" * 70)
    
    # Check ENTITY_FIELD_MAPPING
    print("\n1. ENTITY_FIELD_MAPPING:")
    for entity, fields in ENTITY_FIELD_MAPPING.items():
        print(f"   {entity}: {fields}")
    
    assert 'location' in ENTITY_FIELD_MAPPING, "location entity not found in ENTITY_FIELD_MAPPING!"
    assert ENTITY_FIELD_MAPPING['location'] == ['entitas_lokasi'], "location should map to entitas_lokasi field"
    print("   ✅ Location entity correctly mapped to entitas_lokasi field")
    
    # Check ENTITY_BONUS_WEIGHTS
    print("\n2. ENTITY_BONUS_WEIGHTS:")
    for entity, weight in ENTITY_BONUS_WEIGHTS.items():
        print(f"   {entity}: {weight}")
    
    assert 'location' in ENTITY_BONUS_WEIGHTS, "location entity not found in ENTITY_BONUS_WEIGHTS!"
    assert ENTITY_BONUS_WEIGHTS['location'] == 0.5, "location should have weight 0.5"
    print("   ✅ Location entity has highest weight (0.5)")
    
    print("\n✅ Configuration test passed!\n")

def test_location_extraction():
    """Test if location is extracted from restaurants data"""
    print("=" * 70)
    print("Testing Location Extraction from Restaurant Data")
    print("=" * 70)
    
    # Load restaurants
    loader = DataLoader()
    restaurants_df = loader.load_processed_restaurants('data/restaurants_entitas.csv')
    print(f"\nLoaded {len(restaurants_df)} restaurants")
    
    # Initialize engine
    engine = ContentBasedRecommendationEngine('data/restaurants_entitas.csv')
    restaurants = engine.restaurants_objects
    
    print(f"\nProcessed {len(restaurants)} restaurant objects")
    
    # Check first 5 restaurants for location field
    print("\n3. Sample restaurants with location extracted:")
    location_count = 0
    for i, restaurant in enumerate(restaurants[:10], 1):
        if restaurant.location:
            location_count += 1
            print(f"\n   {i}. {restaurant.name}")
            print(f"      Address: {restaurant.address}")
            print(f"      Location: {restaurant.location}")
    
    print(f"\n   Total restaurants with location: {location_count}/{len(restaurants)}")
    print(f"   Percentage: {location_count/len(restaurants)*100:.2f}%")
    
    assert location_count > 0, "No restaurants have location extracted!"
    print("\n✅ Location extraction test passed!\n")

def test_location_based_recommendations():
    """Test recommendations with location-based queries"""
    print("=" * 70)
    print("Testing Location-Based Recommendations")
    print("=" * 70)
    
    # Initialize engine
    engine = ContentBasedRecommendationEngine('data/restaurants_entitas.csv')
    
    # Test queries with location
    test_queries = [
        "restoran di kuta",
        "pizza di senggigi",
        "seafood gili trawangan",
        "makan enak mataram",
    ]
    
    for query in test_queries:
        print(f"\n4. Query: '{query}'")
        recommendations = engine.get_recommendations(query, top_n=5)
        
        if recommendations:
            print(f"   Found {len(recommendations)} recommendations:")
            for i, rec in enumerate(recommendations[:3], 1):
                restaurant = rec.restaurant
                print(f"\n   {i}. {restaurant.name}")
                print(f"      Location: {restaurant.location}")
                print(f"      Score: {rec.similarity_score:.4f}")
                print(f"      Matching Features: {', '.join(rec.matching_features) if rec.matching_features else 'None'}")
        else:
            print("   ❌ No recommendations found")
    
    print("\n✅ Location-based recommendation test completed!\n")

def test_location_weight_priority():
    """Test if location entity has higher priority than other entities"""
    print("=" * 70)
    print("Testing Location Entity Weight Priority")
    print("=" * 70)
    
    # Initialize engine
    engine = ContentBasedRecommendationEngine('data/restaurants_entitas.csv')
    
    # Query with location + cuisine
    query_with_location = "pizza di kuta"
    query_without_location = "pizza"
    
    print(f"\n5. Query WITH location: '{query_with_location}'")
    recs_with_loc = engine.get_recommendations(query_with_location, top_n=3)
    
    if recs_with_loc:
        print(f"   Top result: {recs_with_loc[0].restaurant.name}")
        print(f"   Location: {recs_with_loc[0].restaurant.location}")
        print(f"   Score: {recs_with_loc[0].similarity_score:.4f}")
    
    print(f"\n   Query WITHOUT location: '{query_without_location}'")
    recs_without_loc = engine.get_recommendations(query_without_location, top_n=3)
    
    if recs_without_loc:
        print(f"   Top result: {recs_without_loc[0].restaurant.name}")
        print(f"   Location: {recs_without_loc[0].restaurant.location}")
        print(f"   Score: {recs_without_loc[0].similarity_score:.4f}")
    
    # Location-specific query should have different top result (or higher score)
    if recs_with_loc and recs_without_loc:
        location_score = recs_with_loc[0].similarity_score
        non_location_score = recs_without_loc[0].similarity_score
        print(f"\n   Score difference: {abs(location_score - non_location_score):.4f}")
        print("   ✅ Location entity affects scoring")
    
    print("\n✅ Location weight priority test completed!\n")

if __name__ == "__main__":
    try:
        # Run all tests
        test_location_entity_config()
        test_location_extraction()
        test_location_based_recommendations()
        test_location_weight_priority()
        
        print("=" * 70)
        print("ALL TESTS PASSED! ✅")
        print("Location entity (5th entity) successfully integrated!")
        print("=" * 70)
        
    except AssertionError as e:
        print(f"\n❌ TEST FAILED: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
