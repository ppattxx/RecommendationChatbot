"""Quick test to debug the recommendations endpoint error"""
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

import traceback

print("=" * 60)
print("Testing Recommendations Route")
print("=" * 60)

try:
    # Import and test
    from backend.routes.recommendations_routes import get_recommendation_engine, MockRecommendationEngine
    
    print("\n1. Testing get_recommendation_engine()...")
    engine = get_recommendation_engine()
    print(f"   Engine type: {type(engine)}")
    
    if isinstance(engine, MockRecommendationEngine):
        print(f"\n2. Testing MockRecommendationEngine...")
        print(f"   Loaded restaurants: {len(engine.restaurants_data)}")
        
        if engine.restaurants_data:
            print(f"\n   First restaurant:")
            for k, v in list(engine.restaurants_data[0].items())[:5]:
                print(f"      {k}: {v}")
        
        print(f"\n3. Testing get_personalized_recommendations()...")
        recommendations = engine.get_personalized_recommendations(limit=5)
        print(f"   Got {len(recommendations)} recommendations")
        
    else:
        print("\n2. Using ContentBasedRecommendationEngine")
        print(f"   TF-IDF matrix shape: {engine.tfidf_matrix.shape if hasattr(engine, 'tfidf_matrix') else 'N/A'}")
        
        print(f"\n3. Testing get_recommendations()...")
        recommendations = engine.get_recommendations("pizza", top_n=5)
        print(f"   Got {len(recommendations)} recommendations")
    
    print("\n" + "=" * 60)
    print("✓ ALL TESTS PASSED!")
    print("=" * 60)
    
except Exception as e:
    print(f"\n✗ ERROR: {type(e).__name__}: {e}")
    print("\nFull traceback:")
    traceback.print_exc()
